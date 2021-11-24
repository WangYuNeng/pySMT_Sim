import functools as ft
from collections import namedtuple
from pysmt.shortcuts import Not
import pysmt.typing as types
import pysmt.operators as op
from pysmt.walkers import DagWalker

type_dict = {"Bool": "bool", "Int": "int", "Real": "double"}
includes = ["\"bit_vector.h\"", "<cmath>", "<fstream>"]
Arg = namedtuple("Arg", ["name", "type"])

def get_type_str(formula):
    name = formula.get_type().basename
    if name in type_dict:
        return type_dict[name]
    raise NotImplementedError

def walk_variadic(evaluate, op):
    def walk_op(self, formula, args, **kwargs):
        if len(args) == 1: # unary
            intermediate = f"({op}{args[0]})"
        else: # n-ary
            intermediate = "(" + f" {op} ".join(args) + ")"
        if evaluate:
            type_str = get_type_str(formula)
            var = f"{type_str}{self.var_cnt[type_str]}"
            declare = f"{type_str} {var} = {intermediate};"
            self.code.append(declare)
            self.var_cnt[type_str] += 1
            return var
        else:
	        return intermediate
    return walk_op

def walk_unsupported():
    def walk_op(self, formula, args, **kwargs):
        raise NotImplementedError
    return walk_op

walk_evaluate = ft.partial(walk_variadic, True)
walk_intermediate = ft.partial(walk_variadic, False)

class CodeGenWalker(DagWalker):

    def __init__(self):
        super().__init__()
        self.var_cnt = {
            item: 0 for item in type_dict.values()
        }
        self.code = []
        self.args = []
        self.headers = includes

    def gen_code(self, formula, file_name):
        ret = self.walk(formula)
        ret_type = get_type_str(formula)
        with open(file_name, 'w') as f:
            f.writelines([f"#include {header}\n" for header in self.headers])
            f.write("\nusing namespace std;\n")
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
            	
    def walk_symbol(self, formula, **kwargs):
        type_str = get_type_str(formula)
        name = formula.symbol_name()
        self.args.append(Arg(name, type_str))
        return name

    def _walk_constant(self, formula, args, **kwargs):
        if formula.constant_type().is_bool_type():
            ret = str(formula.constant_value()).lower()
        elif formula.constant_type().is_real_type() or formula.constant_type().is_int_type():
            ret = str(formula.constant_value())
        else:
            raise NotImplementedError
        return ret

    def walk_ite(self, formula, args, **kwargs):
        # ite(a, b, c) == a ? b : c
        type_str = get_type_str(formula)
        var = f"{type_str}{self.var_cnt[type_str]}"
        declare = f"{type_str} {var} = {args[0]} ? {args[1]} : {args[2]};"
        self.code.append(declare)
        self.var_cnt[type_str] += 1
        return var

    def walk_implies(self, formula, args, **kwargs):
        # a->b == !a || b
        type_str = get_type_str(formula)
        var = f"{type_str}{self.var_cnt[type_str]}"
        declare = f"{type_str} {var} = !{args[0]} || {args[1]};"
        self.code.append(declare)
        self.var_cnt[type_str] += 1
        return var

    def walk_pow(self, formula, args, **kwargs):
        intermediate = "(" + f"pow({args[0]}, {args[1]}) " + ")"
        return intermediate

    walk_real_constant = _walk_constant
    walk_int_constant = _walk_constant
    walk_bool_constant = _walk_constant

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

    
    walk_bv_constant = walk_unsupported
    walk_bv_neg = walk_unsupported
    walk_bv_or = walk_unsupported
    walk_bv_and = walk_unsupported
    walk_bv_xor = walk_unsupported
    walk_bv_add = walk_unsupported
    walk_bv_sub = walk_unsupported
    walk_bv_udiv = walk_unsupported
    walk_bv_mul = walk_unsupported
    walk_bv_rol = walk_unsupported
    walk_bv_urem = walk_unsupported
    walk_bv_lshl = walk_unsupported
    walk_bv_ror = walk_unsupported
    walk_bv_sdiv = walk_unsupported
    walk_bv_lshr = walk_unsupported
    walk_bv_ashr = walk_unsupported
    walk_bv_srem = walk_unsupported
    walk_bv_zext = walk_unsupported
    walk_bv_extract = walk_unsupported
    walk_bv_concat = walk_unsupported
    walk_bv_sext = walk_unsupported
    walk_bv_ult = walk_unsupported
    walk_bv_comp = walk_unsupported
    walk_bv_slt = walk_unsupported
    walk_bv_ule = walk_unsupported
    walk_bv_tonatural = walk_unsupported
    walk_bv_sle = walk_unsupported
    walk_array_store = walk_unsupported
    walk_array_select = walk_unsupported
    walk_toreal = walk_unsupported
    walk_array_value = walk_unsupported
    walk_quantifier = walk_unsupported
    walk_function = walk_unsupported
    walk_forall = walk_unsupported
    walk_exists = walk_unsupported