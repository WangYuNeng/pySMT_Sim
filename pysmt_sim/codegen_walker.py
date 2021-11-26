import functools as ft
from collections import namedtuple
import re
from pysmt.shortcuts import Not
import pysmt.typing as types
import pysmt.operators as op
from pysmt.walkers import DagWalker

type_dict = {"Bool": "bool", "Int": "int", "Real": "double", "BV{}": "bit_vector<>"}
includes = ["\"bit_vector.h\"", "<cmath>", "<fstream>"]
Arg = namedtuple("Arg", ["name", "type"])

def get_type_str(formula):
    name = formula.get_type().basename
    if name in type_dict:
        return type_dict[name]
    # Search BV
    p = re.compile('BV\{\d+\}').match(name)
    if p is not None:
        return f"bit_vector<{formula.bv_width()}>"
    raise NotImplementedError

def legalize_symbol(symbol):
    return re.sub("[.<>]", "_", symbol)

def walk_variadic(evaluate, bv_type, op):
    def walk_op(self, formula, args, **kwargs):
        if len(args) == 1: # unary
            intermediate = f"({op}{args[0]})"
        else: # n-ary
            if bv_type == None:
                intermediate = "(" + f" {op} ".join(args) + ")"
            elif bv_type == "unsigned_int" or bv_type == "signed_int":
                bv_width = formula.bv_width()
                intermediate = "((" + f" {op} ".join([f"({bv_type}<{bv_width}>){arg}" for arg in args]) + ").get_bits())"
            else:
                assert False, "bv_type only accept None, signed_int, or unsigned_int"
        if evaluate:
            return self._create_new_var(formula, intermediate)
        else:
	        return intermediate
    return walk_op

def walk_unsupported(name):
    def walk_op(self, formula, args, **kwargs):
        print(name)
        raise NotImplementedError
    return walk_op

walk_evaluate = ft.partial(walk_variadic, True, None)
walk_intermediate = ft.partial(walk_variadic, False, None)
walk_evaluate_bv_signed = ft.partial(walk_variadic, True, "signed_int")
walk_evaluate_bv_unsigned = ft.partial(walk_variadic, True, "unsigned_int")
walk_intermediate_bv_signed = ft.partial(walk_variadic, False, "signed_int")
walk_intermediate_bv_unsigned = ft.partial(walk_variadic, False, "unsigned_int")

def walk_cpp_function(func_name):
    def walk_op(self, formula, args, **kwargs):
        intermediate = f"{func_name}(" + ", ".join(args) + ")"
        return intermediate
    return walk_op
class CodeGenWalker(DagWalker):

    def __init__(self):
        super().__init__()
        self.var_cnt = {}
        self.code = []
        self.args = []
        self.headers = includes

    def gen_code(self, formula, file_name):
        ret = self.walk(formula)
        ret_type = get_type_str(formula)
        with open(file_name, 'w') as f:
            f.writelines([f"#include {header}\n" for header in self.headers])
            f.write("\nusing namespace std;\n")
            f.write("\nusing namespace bsim;\n")
            self.write_func(ret_type, ret, f)
            self.write_main(f)
            
    def write_func(self, func_type, ret_name, file):
        file.write(f"\n{func_type} formula (" + ", ".join([f"{arg.type} {arg.name}" for arg in self.args]) + ")\n")
        file.write("{\n")
        file.writelines([f"\t{code}\n" for code in self.code])
        file.write(f"\treturn {ret_name};\n")
        file.write("}\n")

    def write_main(self, file):
        file.write("\nint main (int argc, char **argv) {\n"
                    + "\tifstream in_file (argv[1]);\n"
                    + "\tofstream out_file (argv[2]);\n"
                    + "\tif (in_file.is_open() && out_file.is_open()) {\n"
                    + "\t\tint num_line;\n"
                    + "\t\tin_file >> num_line;\n"
                    + "\t\tfor (int i = 0; i < num_line; ++i) {\n")
        file.writelines([f"\t\t\t{arg.type} var_{i};\n" for i, arg in enumerate(self.args)])
        file.writelines([f"\t\t\tin_file >> var_{i};\n" for i, _ in enumerate(self.args)])
        file.write("\t\t\tout_file << formula(" + 
            ", ".join([f"var_{i}" for i, _ in enumerate(self.args)]) +
            ") << endl;\n"
        )
        file.write("\t\t}\n"
                    + "\t\tin_file.close();\n"
                    + "\t\tout_file.close();\n"
        	        + "\t}\n"
        	        + "\treturn 0;\n"
                    + "}\n"
        )

    def _create_new_var(self, formula, value):
        type_str = get_type_str(formula)
        try:
            self.var_cnt[type_str]
        except KeyError:
            self.var_cnt[type_str] = 0
        var = legalize_symbol(f"{type_str}{self.var_cnt[type_str]}")
        declare = f"{type_str} {var} = {value};"
        self.code.append(declare)
        self.var_cnt[type_str] += 1
        return var

    def walk_symbol(self, formula, **kwargs):
        type_str = get_type_str(formula)
        name = legalize_symbol(formula.symbol_name())
        self.args.append(Arg(name, type_str))
        return name

    def _walk_constant(self, formula, args, **kwargs):
        if formula.constant_type().is_bool_type():
            ret = str(formula.constant_value()).lower()
        elif formula.constant_type().is_real_type() or formula.constant_type().is_int_type():
            ret = str(formula.constant_value())
        elif formula.constant_type().is_bv_type():
            ret = f"(bit_vector<{formula.bv_width()}>)" + str(formula.constant_value())
        else:
            raise NotImplementedError
        return ret

    def walk_ite(self, formula, args, **kwargs):
        # ite(a, b, c) == a ? b : c
        value = f"{args[0]} ? {args[1]} : {args[2]};"
        return self._create_new_var(formula, value)

    def walk_implies(self, formula, args, **kwargs):
        # a->b == !a || b
        value = f"!{args[0]} || {args[1]};"
        return self._create_new_var(formula, value)

    def walk_pow(self, formula, args, **kwargs):
        intermediate = "(" + f"pow({args[0]}, {args[1]}) " + ")"
        return intermediate

    walk_real_constant = _walk_constant
    walk_int_constant = _walk_constant
    walk_bool_constant = _walk_constant
    walk_bv_constant = _walk_constant

    walk_not = walk_evaluate("!")
    walk_le = walk_evaluate("<=")
    walk_lt = walk_evaluate("<")
    walk_equals = walk_evaluate("==")
    walk_iff = walk_evaluate("==")
    walk_and = walk_evaluate("&&")
    walk_or = walk_evaluate("||")

    walk_div = walk_intermediate("/")
    walk_minus = walk_intermediate("-")
    walk_plus = walk_intermediate("+")
    walk_times = walk_intermediate("*")

    
    walk_bv_neg = walk_intermediate("~")
    walk_bv_or = walk_intermediate("|")
    walk_bv_and = walk_intermediate("&")
    walk_bv_xor = walk_intermediate("^")
    walk_bv_add = walk_intermediate_bv_unsigned("+")
    walk_bv_sub = walk_intermediate_bv_unsigned("-")
    walk_bv_udiv = walk_intermediate_bv_unsigned("/")
    walk_bv_mul = walk_intermediate_bv_unsigned("*")
    walk_bv_rol = walk_unsupported("walk_bv_rol")
    walk_bv_urem = walk_unsupported("walk_bv_urem")
    walk_bv_lshl = walk_intermediate("<<")
    walk_bv_ror = walk_unsupported("walk_bv_ror")
    walk_bv_sdiv = walk_intermediate_bv_signed("/")
    walk_bv_lshr = walk_intermediate(">>")
    walk_bv_ashr = walk_cpp_function("arithmetic_right_shift")
    walk_bv_srem = walk_unsupported("walk_bv_srem")
    walk_bv_zext = walk_unsupported("walk_bv_zext")
    walk_bv_concat = walk_cpp_function("concat")
    
    def walk_bv_extract(self, formula, args, **kwargs):
        # easier to handle args here than variadic function argument in c++
        bv_width = formula.bv_width()
        start = formula.bv_extract_start()
        end = formula.bv_extract_end()
        intermediate = f"extract<{bv_width}>({args[0]}, {start}, {end})"
        return intermediate

    walk_bv_sext = walk_unsupported("walk_bv_sext")
    walk_bv_ult = walk_intermediate_bv_unsigned("<")
    walk_bv_comp = walk_intermediate("==")
    walk_bv_slt = walk_intermediate_bv_signed("<")
    walk_bv_ule = walk_intermediate_bv_unsigned("<=")
    walk_bv_tonatural = walk_unsupported("walk_bv_tonatural")
    walk_bv_sle = walk_intermediate_bv_signed("<=")
    walk_array_store = walk_unsupported(walk_unsupported)
    walk_array_select = walk_unsupported(walk_unsupported)
    walk_toreal = walk_unsupported(walk_unsupported)
    walk_array_value = walk_unsupported(walk_unsupported)
    walk_quantifier = walk_unsupported(walk_unsupported)
    walk_function = walk_unsupported(walk_unsupported)
    walk_forall = walk_unsupported(walk_unsupported)
    walk_exists = walk_unsupported(walk_unsupported)