import unittest
import pdb
import os

import pyflip as flp

class Tests(unittest.TestCase):

    def test1(self):
        v1 = flp.variable.Continuous('v1', 10, 20)
        v2 = flp.variable.Integer('v2', -10, 0)
        v3 = flp.variable.Binary('v3')

        expr = v1 + 2 * v2 - 3 * v3 + 3
        expr -= 10 * v2
        expr /= 2
        self.assertIsInstance(expr, flp.Expression)

    def test2(self):
        m = flp.Model()
        v1 = flp.variable.Continuous('v1', 10, 20)
        v2 = flp.variable.Integer('v2', -10, 0)
        v3 = flp.variable.Binary('v3')

        m.add_variables(*[v1, v2, v3])

        obj = flp.Objective('max', 3 * v1)
        m.add_objective(obj)

        # m += flp.Objective('max', 3 * v1)

        c = flp.Constraint(v1 + 3, '<=', v3)
        m.add_constraint(c)

        print(c.lhs, c.rhs)
        print(c._lhs, c._rhs)
        # m += flp.Constraint(v1, <=, v3)

        print(m)


    def test3(self):
        m = flp.Model()
        v1 = flp.variable.Continuous('v1', 10, 20)
        v2 = flp.variable.Integer('v2', -10)
        v3 = flp.variable.Binary('v3')
        v4 = flp.variable.Continuous('v4')

        m += v1, v2, v3, v4
        m += flp.Objective('max', 3 * v1)
        m += flp.Constraint(v1, '<=', v3)
        m += flp.Constraint(-v1 + v2, '>=', v3 / 3 - 7.5)

        print(m)
        full_lp_filename = flp.write_lp_file(m)
        os.remove(full_lp_filename)


    def test4(self):
        m = flp.Model()
        v1 = flp.variable.Continuous('v1', 10, 20)
        v2 = flp.variable.Integer('v2', -10)
        v3 = flp.variable.Binary('v3')
        v4 = flp.variable.Continuous('v4')

        m += v1, v2, v3, v4
        m += flp.Objective('max', 3 * v1)
        m += flp.Constraint(v1 + 2, '<=', 20 * v3)
        m += flp.Constraint(-v1 + v2, '>=', v3 / 3 - 7.5)
        m += flp.Constraint(sum([v1, v2, v3]), '>=', v3 / 3 - 7.5)

        s = flp.solver.Gurobi({'time_limit': 10})
        s.set_solver_parameters({'ZeroHalfCuts': 0})

        soln, run = s.solve(m)

        print(m.objective.name, m.objective.value(soln))
        for var_name, var in m.variables.items():
            print(var_name, var.value(soln))
        for con_name, con in m.constraints.items():
            print(f'{con_name}: {con.lhs} {con.mid} {con.rhs}')
            print(f'{con.lhs.value(soln)} {con.mid} {con.rhs.value(soln)}')


        # print(soln)
        # print(run.solve_duration)
        # print(run.parameters)

        # model.objective.value(soln)
        #
        full_lp_filename = flp.write_lp_file(m)
        os.remove(full_lp_filename)

# def setUp(self):
#     pass

# def tearDown(self):
#     pass

if __name__ == '__main__':
    unittest.main()
    # t = Tests()
    # t.test4()


#     v.value()
#
#     c.is_viol()
#
#
# # should be able to use the
# # should create auxiliary expressions that aren't part of the model
# # expr_of_interest = flp.Expression()
#
# expr_of_interest.value(soln)