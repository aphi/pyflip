import random
import time
import timeit
import functools

import pyflip as flp

def big_ip_model_1(solver):
    # Knapsack
    class Item:
        def __init__(self, name, value, size):
            self.name = str(name)
            self.value = value
            self.size = size
    class Bag:
        def __init__(self, name, size):
            self.name = str(name)
            self.size = size

    random.seed(0)
    N_ITEMS = 100
    N_BAGS = int(N_ITEMS / 4)
    items = [Item(i, random.randint(1, 100), random.randint(1, 50)) for i in range(N_ITEMS)]
    bags = [Bag(i, random.randint(50, 100)) for i in range(N_BAGS)]

    t = time.time()

    model = flp.Model()
    vars = {}
    for item in items:
        for bag in bags:
            v = flp.variable.Binary(f'v{item.name}_{bag.name}')
            vars[(item.name, bag.name)] = v
            model += v

    print('Vars added', time.time() - t)

    # obj_expr = sum(item.value * model.variables[f'v{item.name}_{bag.name}'] \
    #   for item in items for bag in bags)

    # obj_expr = flp.Expression.from_var_dict(dict(model.variables[f'v{item.name}_{bag.name}'], item.value) \
    #   for item in items for bag in bags)

    obj_expr = flp.tsum((item.value, model.variables[f'v{item.name}_{bag.name}']) \
      for item in items for bag in bags)
    model += flp.Objective('max', obj_expr)

    print('Objective added', time.time() - t)

    # Assign each item at most once
    for item in items:
        lhs_expr = flp.tsum((1, model.variables[f'v{item.name}_{bag.name}']) for bag in bags)
        model += flp.Constraint(lhs_expr, '<=', 1)

    # Fill bag at most to size
    for bag in bags:
        lhs_expr = flp.tsum((item.size, model.variables[f'v{item.name}_{bag.name}']) for item in items)
        model += flp.Constraint(lhs_expr, '<=', bag.size)

    print('Constraints added', time.time() - t)

    solver.set_params({'time_limit': 10})
    # solver.set_mipstart(soln)
    soln, run = solver.solve(model, keep_log_file=True, keep_lp_file=True, keep_sol_file=True)

    print('Solved', time.time() - t)

    print(flp.util.run_summary(run, soln, model))


def expression_generation():
    random.seed(0)
    N = 10000

    coefs = [random.randint(1,100) for _ in range(N)]
    vars = [flp.variable.Binary(f'v{i}') for i in range(N)]

    # obj_expr = sum([coef * var for (coef, var) in zip(coefs, vars)])
    # obj_expr = flp.tsum([(coef, var) for (coef, var) in zip(coefs, vars)])
    # obj_expr = flp.tsum((coef, var) for (coef, var) in zip(coefs, vars))
    obj_expr = flp.esum(coef * var for (coef, var) in zip(coefs, vars))

    # fastest way is to supply var_dict
    # obj_expr = flp.Expression.from_var_dict(dict((var.name, coef) for (coef, var) in zip(coefs, vars)))

def run():
    # print(timeit.timeit(expression_generation, number=20))
    # timeit.timeit(big_ip_model_1(solver), number=1)

    solvers = [
        flp.solver.Cbc,
        # flp.solver.Gurobi
    ]
    for solver in solvers:
        print(timeit.timeit(functools.partial(big_ip_model_1, solver()), number=1))

if __name__ == '__main__':
    run()