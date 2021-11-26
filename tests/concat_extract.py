from pysmt.shortcuts import BVAdd, Equals, Symbol, BVConcat, BVExtract, get_model, BV, And, BVMul
from pysmt.typing import BV16
from pysmt_sim.codgen_mgr import CodeGenMgr

x = Symbol("x", BV16)
y = Symbol("y", BV16)

z1 = BVConcat(x, y)
z2 = BVExtract(z1, 0, 7)
z3 = BVExtract(z1, 10, 17)
const = BV(234, 8)
formula = Equals(BVAdd(z2, z3), const)
model = get_model(formula)
print(model)
mgr = CodeGenMgr()
mgr.gen_code(formula, "cpp/concat_extract.cpp")
mgr.compile()
mgr.add_pattern([{v: model.get_value(v) for v in [x, y]}])
mgr.sim()
print(mgr.check_allsat())