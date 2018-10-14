import unittest
import random
import pdb
import os
import time

import pyflip as flp



def solution_summary(m, soln):
    print (len(m.variables))
    print (m.objective.value(soln))
    # print(m.objective.name, m.objective, m.objective.value(soln))
    # for var_name, var in m.variables.items():
    #     print(var_name, var.value(soln))
    # for con_name, con in m.constraints.items():
    #     print(f'{con_name}: {con.lhs} {con.mid} {con.rhs}')
    #     print(f'{con.lhs.value(soln)} {con.mid} {con.rhs.value(soln)}')



def lp_model_1():
    m = flp.Model()
    v1 = flp.variable.Continuous('v1', 10, 20)
    v2 = flp.variable.Continuous('v2', 10, 20)

    m += v1, v2
    m += flp.Objective('max', sum([v1 + v2]))
    m += flp.Constraint(v2, '<=', -2 * v1 + 50)

    return m

def ip_model_1():
    m = flp.Model()
    v1 = flp.variable.Binary('v1')
    v2 = flp.variable.Integer('v2')

    m += v1, v2
    m += flp.Objective('min', v2)
    m += flp.Constraint(v2, '>=', -1.5 * v1 - 1)
    m += flp.Constraint(v2, '>=', 2.5 * v1 - 5)

    return m

def big_ip_model_1():
    model = flp.Model()

    # knapsack
    class Item:
        def __init__(self, name, value, size):
            self.name = str(name)
            self.value = value
            self.size = size
    class Bag:
        def __init__(self, name, size):
            self.name = str(name)
            self.size = size

    import random
    random.seed(0)
    N_ITEMS = 40
    N_BAGS = int(N_ITEMS / 4)
    t = time.time()

    items = [Item(i, random.randint(1, 100), random.randint(1, 50)) for i in range(N_ITEMS)]
    bags = [Bag(i, random.randint(50, 100)) for i in range(N_BAGS)]

    print(0, time.time() - t)

    vars = {}
    for item in items:
        for bag in bags:
            v = flp.variable.Binary(f'v{item.name}_{bag.name}')
            vars[(item.name, bag.name)] = v
            model += v

    print(1, time.time() - t)

    # obj_expr = sum(item.value * model.variables[f'v{item.name}_{bag.name}'] \
    #   for item in items for bag in bags)

    # obj_expr = flp.Expression.from_var_dict(dict(model.variables[f'v{item.name}_{bag.name}'], item.value) \
    #   for item in items for bag in bags)

    obj_expr = flp.tsum((item.value, model.variables[f'v{item.name}_{bag.name}']) \
      for item in items for bag in bags)
    model += flp.Objective('max', obj_expr)

    print(2, time.time() - t)

    # Assign each item at most once
    for item in items:
        lhs_expr = flp.tsum((1, model.variables[f'v{item.name}_{bag.name}']) for bag in bags)
        model += flp.Constraint(lhs_expr, '<=', 1)

    # Fill bag at most to size
    for bag in bags:
        lhs_expr = flp.tsum((item.size, model.variables[f'v{item.name}_{bag.name}']) for item in items)
        model += flp.Constraint(lhs_expr, '<=', bag.size)

    print(3, time.time() - t)

    s = flp.solver.Cbc({'time_limit': 20})
    soln, run = s.solve(model,keep_lp_file=True,keep_sol_file=True)

    print(4, time.time() - t)

    solution_summary(model, soln)


class Tests(unittest.TestCase):

    def test_expressions_1(self):
        v1 = flp.variable.Continuous('v1', 10, 20)
        v2 = flp.variable.Integer('v2', -10, 0)
        v3 = flp.variable.Binary('v3')

        expr = v1 + 2 * v2 - 3 * v3 + 3
        expr -= 10 * v2
        expr /= 2
        self.assertIsInstance(expr, flp.Expression)

    def test_model_1(self):
        m = flp.Model()
        v1 = flp.variable.Continuous('v1', 10, 20)
        v2 = flp.variable.Integer('v2', -10, 0)
        v3 = flp.variable.Binary('v3')
        m.add_variables(*[v1, v2, v3])

        obj = flp.Objective('max', 3 * v1)
        m.add_objective(obj)

        c = flp.Constraint(v1 + 3, '<=', v3)
        m.add_constraints(c)

        self.assertIsInstance(m, flp.Model)
        self.assertEqual(3, len(m.variables))
        self.assertEqual(1, len(m.constraints))

    def test_error_on_nonexistent_var_1(self):
        m = flp.Model()
        v1 = flp.variable.Continuous('v1', 10, 20)

        with self.assertRaises(RuntimeError):
            m += flp.Objective('max', v1)

    def test_write_to_file(self):
        m = flp.Model()
        v1 = flp.variable.Continuous('v1', 10, 20)
        v2 = flp.variable.Integer('v2', -10)
        v3 = flp.variable.Binary('v3')
        v4 = flp.variable.Continuous('v4')

        m.add_variables(v1, v2, v3, v4)
        m += flp.Objective('max', 3 * v1)
        m += flp.Constraint(v1, '<=', v3)
        m += flp.Constraint(-v1 + v2, '>=', v3 / 3 - 7.5)

        # print(m)
        full_lp_filename = flp.write_lp_file(m)
        os.remove(full_lp_filename)


    def test_solve_lp_1(self):
        m = lp_model_1()
        s = flp.solver.Cbc({'time_limit': 10})

        soln, run = s.solve(m)

        self.assertEqual(m.objective.value(soln), 35.0)
        self.assertEqual(m.variables['v1'].value(soln), 15.0)
        self.assertEqual(m.variables['v2'].value(soln), 20.0)

    def test_solve_ip_1(self):
        m = ip_model_1()
        s = flp.solver.Cbc({'time_limit': 10})
        soln, run = s.solve(m)

        self.assertEqual(m.objective.value(soln), -2.0)
        self.assertEqual(m.variables['v1'].value(soln), 1.0)
        self.assertEqual(m.variables['v2'].value(soln), -2.0)

    def test_solve_relaxed_ip_1(self):
        m = ip_model_1()

        for variable in m.variables.values():
            variable.continuous = True

        # more generally, can directly substitute a variable
        # m.add_variables(flp.variable.Integer('v1', 10, 20), overwrite=True)
        #
        # can use this to implement model.relax(). but it clobbers old state.
        # by just changing variable.constinuous, you can implement a model.unrelax

        s = flp.solver.Cbc({'time_limit': 10})
        soln, run = s.solve(m)

        self.assertEqual(m.objective.value(soln), -2.5)
        self.assertEqual(m.variables['v1'].value(soln), 1.0)
        self.assertEqual(m.variables['v2'].value(soln), -2.5)


    # def test_mipstart(self):
    #     m = ip_model_1()
    #
    #     for variable in m.variables.values():
    #         variable.continuous = True
    #
    #     s = flp.solver.Cbc({'time_limit': 10})
    #     soln, run = s.solve(m)
    #
    #     self.assertEqual(m.objective.value(soln), -2.5)
    #     self.assertEqual(m.variables['v1'].value(soln), 1.0)
    #     self.assertEqual(m.variables['v2'].value(soln), -2.5)


def test1():
    random.seed(0)
    N = 10000

    # import timeit
    # timeit.

    coefs = [random.randint(1,100) for _ in range(N)]
    vars = [flp.variable.Binary(f'v{i}') for i in range(N)]

    # obj_expr = sum([coef * var \
    #   for (coef, var) in zip(coefs, vars)])

    # obj_expr = sum([coef * var for (coef, var) in zip(coefs, vars)])
    # obj_expr = flp.tsum([(coef, var) for (coef, var) in zip(coefs, vars)])
    # obj_expr = flp.tsum((coef, var) for (coef, var) in zip(coefs, vars))

    obj_expr = flp.esum(coef * var for (coef, var) in zip(coefs, vars))


    # fastest way is to supply var_dict
    # obj_expr = flp.Expression.from_var_dict(dict((var.name, coef) for (coef, var) in zip(coefs, vars)))


def timeit():
    import timeit
    # print(timeit.timeit(test1, number=20))
    print(timeit.timeit(big_ip_model_1, number=1))


if __name__ == '__main__':
    # unittest.main()
    # t = Tests()
    # t.test_big_ip()

    timeit()

