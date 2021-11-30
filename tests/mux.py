from pysmt.environment import push_env
from pysmt.shortcuts import *
from pysmt.typing import *
from pysmt_sim.codgen_mgr import CodeGenMgr

N = 5

if __name__ == "__main__":
    pos_in_row = [Symbol('pos@{}'.format(i), INT) for i in range(N)]

    bounded_pos = And(
        [
            And(
                GE(pos_in_row[i], Int(0)),
                LT(pos_in_row[i], Int(N))
            )
            for i in range(N)
        ]
    )
    no_shared_column = And([NotEquals(pos_in_row[i], pos_in_row[j]) for i in range(N) for j in range(i+1, N)])
    no_shared_diag_line = And(
        [
            And(
                NotEquals(pos_in_row[i], Plus(pos_in_row[j], Int(i-j))),
                NotEquals(pos_in_row[i], Minus(pos_in_row[j], Int(i-j)))
            ) for i in range(N) for j in range(i+1, N)
        ]
    )

    f1 = And(bounded_pos, no_shared_column, no_shared_diag_line)

    n_penny = Symbol('n_penny', INT)
    n_nickel = Symbol('n_nickel', INT)
    n_dime = Symbol('n_dime', INT)

    domains = And([LE(n_penny, Int(3)), LE(n_nickel, Int(5)), LE(n_dime, Int(2)), GE(n_penny, Int(0)), GE(n_nickel, Int(0)), GE(n_dime, Int(0))])
    sum_comb = Plus([n_penny] + [n_nickel] * 5 + [n_dime] * 10)
    problem = Equals(sum_comb, Int(55))
    f2 = And(domains, problem)

    sel = Symbol("sel", BOOL)
    formula = Ite(sel, f1, f2).simplify()
    
    mgr = CodeGenMgr()
    formula = formula.substitute({sel: Bool(False)}).simplify()
    mgr.gen_code(formula, "cpp/sel_0.cpp")

    