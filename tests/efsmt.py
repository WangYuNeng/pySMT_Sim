# EF-SMT solver implementation
#
# This example shows:
#  1. How to combine 2 different solvers
#  2. How to extract information from a model
#
from pysmt.shortcuts import Solver, get_model
from pysmt.shortcuts import Symbol, Bool, Real, Implies, And, Not, Equals
from pysmt.shortcuts import GT, LT, LE, Minus, Times
from pysmt.logics import AUTO, QF_LRA
from pysmt.typing import REAL
from pysmt.exceptions import SolverReturnedUnknownResultError
from pysmt_sim.codgen_mgr import CodeGenMgr

def efsmt(y, phi, logic=AUTO, maxloops=None,
          esolver_name=None, fsolver_name=None,
          verbose=False):
    """Solves exists x. forall y. phi(x, y)"""

    y = set(y)
    x = phi.get_free_variables() - y

    mgr = CodeGenMgr()
    mgr.gen_code(phi, "cpp/efsmt.cpp")
    mgr.compile()
    y_pattern = []
    allsat = True

    with Solver(logic=logic, name=esolver_name) as esolver:

        esolver.add_assertion(Bool(True))
        loops = 0
        while maxloops is None or loops <= maxloops:
            loops += 1

            eres = esolver.solve()
            if not eres:
                return False
            else:
                tau = {v: esolver.get_value(v) for v in x}
                sub_phi = phi.substitute(tau).simplify()
                if verbose: print("%d: Tau = %s" % (loops, tau))

                if len(y_pattern) != 0:
                    mgr.clear_pattern()
                    mgr.add_pattern([{**tau, **p} for p in y_pattern])
                    mgr.sim()
                    allsat = mgr.check_allsat()

                if allsat:
                    fmodel = get_model(Not(sub_phi),
                                   logic=logic, solver_name=fsolver_name)
                    if fmodel is None:
                        return tau
                if not allsat or fmodel is not None:
                    sigma = {v: fmodel[v] for v in y}
                    y_pattern.append(sigma)
                    sub_phi = phi.substitute(sigma).simplify()
                    if verbose: print("%d: Sigma = %s" % (loops, sigma))
                    esolver.add_assertion(sub_phi)

        raise SolverReturnedUnknownResultError


def run_test(y, f):
    print("Testing " + str(f))
    try:
        res = efsmt(y, f, logic=QF_LRA, maxloops=20, verbose=True)
        if res == False:
            print("unsat")
        else:
            print("sat : %s" % str(res))
    except SolverReturnedUnknownResultError:
        print("unknown")
    print("\n\n")


def main():
    x,y = [Symbol(n, REAL) for n in "xy"]
    f_sat = Implies(And(GT(y, Real(0)), LT(y, Real(10))),
                    LT(Minus(y, Times(x, Real(2))), Real(7)))

    f_incomplete = And(GT(x, Real(0)), LE(x, Real(10)),
                       Implies(And(GT(y, Real(0)), LE(y, Real(10)),
                                   Not(Equals(x, y))),
                               GT(y, x)))

    run_test([y], f_sat)
    run_test([y], f_incomplete)


if __name__ == "__main__":
    main()