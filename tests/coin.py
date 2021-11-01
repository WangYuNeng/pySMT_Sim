from pysmt.shortcuts import *
from pysmt.typing import *
from pysmt_sim.codegen_walker import CodeGenWalker

if __name__ == '__main__':
    n_penny = Symbol('n_penny', INT)
    n_nickel = Symbol('n_nickel', INT)
    n_dime = Symbol('n_dime', INT)

    domains = And([LE(n_penny, Int(3)), LE(n_nickel, Int(5)), LE(n_dime, Int(2)), GE(n_penny, Int(0)), GE(n_nickel, Int(0)), GE(n_dime, Int(0))])
    sum_comb = Plus([n_penny] + [n_nickel] * 5 + [n_dime] * 10)
    problem = Equals(sum_comb, Int(55))
    formula = And(domains, problem)
    
    walker = CodeGenWalker()
    walker.walk(formula)

    model = get_model(formula)