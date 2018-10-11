import unittest
import pdb
import os

import pyflip as flp

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


if __name__ == '__main__':
    unittest.main()
    # t = Tests()
    # t.test4()



# print(m.objective.name, m.objective, m.objective.value(soln))
# for var_name, var in m.variables.items():
#     print(var_name, var.value(soln))
# for con_name, con in m.constraints.items():
#     print(f'{con_name}: {con.lhs} {con.mid} {con.rhs}')
#     print(f'{con.lhs.value(soln)} {con.mid} {con.rhs.value(soln)}')
