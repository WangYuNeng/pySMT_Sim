import pysmt.typing as types
import pysmt.operators as op
from pysmt.walkers import DagWalker

from pysmt_sim.decorator import debug

class CodeGenWalker(DagWalker):

    def __init__(self):
        super().__init__()

    @debug
    def walk_not(self, formula, args, **kwargs):
        return

    @debug
    def walk_symbol(self, formula, **kwargs):
        return

    @debug
    def walk_ite(self, formula, args, **kwargs):
        return

    @debug
    def walk_real_constant(self, formula, **kwargs):
        return

    @debug
    def walk_int_constant(self, formula, **kwargs):
        return

    @debug
    def walk_bool_constant(self, formula, **kwargs):
        return

    @debug
    def walk_quantifier(self, formula, args, **kwargs):
        return

    @debug
    def walk_toreal(self, formula, args, **kwargs):
        return

    @debug
    def _z3_func_decl(self, func_name):
        return

    @debug
    def walk_function(self, formula, args, **kwargs):
        return

    @debug
    def walk_bv_constant(self, formula, **kwargs):
        return

    @debug
    def walk_bv_extract(self, formula, args, **kwargs):
        return

    @debug
    def walk_bv_not(self, formula, args, **kwargs):
        return

    @debug
    def walk_bv_neg(self, formula, args, **kwargs):
        return

    @debug
    def walk_bv_rol(self, formula, args, **kwargs):
        return

    @debug
    def walk_bv_ror(self, formula, args, **kwargs):
        return

    @debug
    def walk_bv_zext(self, formula, args, **kwargs):
        return

    @debug
    def walk_bv_sext (self, formula, args, **kwargs):
        return

    @debug
    def walk_bv_comp(self, formula, args, **kwargs):
        return

    @debug
    def walk_bv_tonatural(self, formula, args, **kwargs):
        return

    @debug
    def walk_array_select(self, formula, args, **kwargs):
        return

    @debug
    def walk_array_store(self, formula, args, **kwargs):
        return

    @debug
    def walk_array_value(self, formula, args, **kwargs):
        return

    @debug
    def make_walk_nary(func):
        def walk_nary(self, formula, args, **kwargs):
            func()
            return
        return walk_nary

    @debug
    def make_walk_binary(func):
        def walk_binary(self, formula, args, **kwargs):
            func()
            return
        return walk_binary
        
    @debug
    def empty_func():
        return

    walk_and     = make_walk_nary(empty_func)
    walk_or      = make_walk_nary(empty_func)
    walk_plus    = make_walk_nary(empty_func)
    walk_times   = make_walk_nary(empty_func)
    walk_minus   = make_walk_nary(empty_func)
    walk_implies = make_walk_binary(empty_func)
    walk_le      = make_walk_binary(empty_func)
    walk_lt      = make_walk_binary(empty_func)
    walk_equals  = make_walk_binary(empty_func)
    walk_iff     = make_walk_binary(empty_func)
    walk_pow     = make_walk_binary(empty_func)
    walk_div     = make_walk_binary(empty_func)
    walk_bv_ult  = make_walk_binary(empty_func)
    walk_bv_ule  = make_walk_binary(empty_func)
    walk_bv_slt  = make_walk_binary(empty_func)
    walk_bv_sle  = make_walk_binary(empty_func)
    walk_bv_concat = make_walk_binary(empty_func)
    walk_bv_or   = make_walk_binary(empty_func)
    walk_bv_and  = make_walk_binary(empty_func)
    walk_bv_xor  = make_walk_binary(empty_func)
    walk_bv_add  = make_walk_binary(empty_func)
    walk_bv_sub  = make_walk_binary(empty_func)
    walk_bv_mul  = make_walk_binary(empty_func)
    walk_bv_udiv = make_walk_binary(empty_func)
    walk_bv_urem = make_walk_binary(empty_func)
    walk_bv_lshl = make_walk_binary(empty_func)
    walk_bv_lshr = make_walk_binary(empty_func)
    walk_bv_sdiv = make_walk_binary(empty_func)
    walk_bv_srem = make_walk_binary(empty_func)
    walk_bv_ashr = make_walk_binary(empty_func)
    walk_exists = walk_quantifier
    walk_forall = walk_quantifier