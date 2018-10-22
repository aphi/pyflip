import unittest
from os import sys
from pathlib import Path

import pyflip as flp

class TestModels:
    @staticmethod
    def lp_model_1():
        model = flp.Model()
        v1 = flp.variable.Continuous('v1', 10, 20)
        v2 = flp.variable.Continuous('v2', 10, 20)

        model += v1, v2
        model += flp.Objective('max', sum([v1 + v2]))
        model += flp.Constraint(v2, '<=', -2 * v1 + 50)

        return model

    @staticmethod
    def ip_model_1():
        model = flp.Model()
        v1 = flp.variable.Binary('v1')
        v2 = flp.variable.Integer('v2')

        model += v1, v2
        model += flp.Objective('min', v2)
        model += flp.Constraint(v2, '>=', -1.5 * v1 - 1)
        model += flp.Constraint(v2, '>=', 2.5 * v1 - 5)

        return model

    @staticmethod
    def infeasible_lp_model_1():
        model = flp.Model()
        v1 = flp.variable.Continuous('v1')
        v2 = flp.variable.Continuous('v2')
        model += v1, v2

        model += flp.Constraint(v1 + v2, '<=', 1)
        model += flp.Constraint(v1, '>=', 2)
        model += flp.Constraint(v2, '>=', 2)

        return model

    @staticmethod
    def infeasible_ip_model_1():
        model = flp.Model()
        v1 = flp.variable.Binary('v1')
        v2 = flp.variable.Binary('v2')
        model += v1, v2

        model += flp.Constraint(v1 + v2, '<=', 1)
        model += flp.Constraint(v1, '>=', 0.1)
        model += flp.Constraint(v2, '>=', 0.1)

        return model

    @staticmethod
    def unbounded_lp_model_1():
        model = flp.Model()
        v1 = flp.variable.Continuous('v1')
        v2 = flp.variable.Continuous('v2')
        model += v1, v2

        model += flp.Objective('max', v1 + 2 * v2) ### TODO: ERROR CHECKING REQUIRED ON INPUT ARGUMENTS

        model += flp.Constraint(v1 + v2, '<=', 1)

        return model


class Tests(unittest.TestCase):
    universal_solver = flp.solver.Cbc

    def test_expressions_1(self):
        v1 = flp.variable.Continuous('v1', 10, 20)
        v2 = flp.variable.Integer('v2', -10, 0)
        v3 = flp.variable.Binary('v3')

        expr = v1 + 2 * v2 - 3 * v3 + 3
        expr -= 10 * v2
        expr /= 2
        self.assertIsInstance(expr, flp.Expression)

    def test_model_1(self):
        model = flp.Model()
        v1 = flp.variable.Continuous('v1', 10, 20)
        v2 = flp.variable.Integer('v2', -10, 0)
        v3 = flp.variable.Binary('v3')
        model.add_variables(*[v1, v2, v3])

        obj = flp.Objective('max', 3 * v1)
        model.add_objective(obj)

        c = flp.Constraint(v1 + 3, '<=', v3)
        model.add_constraints(c)

        self.assertIsInstance(model, flp.Model)
        self.assertEqual(3, model.num_vars())
        self.assertEqual(1, model.num_cons())

    def test_error_on_nonexistent_var_1(self):
        model = flp.Model()
        v1 = flp.variable.Continuous('v1', 10, 20)

        with self.assertRaises(RuntimeError):
            model += flp.Objective('max', v1)

    def test_write_to_file(self):
        model = flp.Model()
        v1 = flp.variable.Continuous('v1', 10, 20)
        v2 = flp.variable.Integer('v2', -10)
        v3 = flp.variable.Binary('v3')
        v4 = flp.variable.Continuous('v4')

        model.add_variables(v1, v2, v3, v4)
        model += flp.Objective('max', 3 * v1)
        model += flp.Constraint(v1, '<=', v3)
        model += flp.Constraint(-v1 + v2, '>=', v3 / 3 - 7.5)

        full_lp_filename = flp.write_lp_file(model, 'test.lp')
        p = Path(full_lp_filename)
        self.assertEqual(p.is_file(), True)
        p.unlink()

    def test_solve_lp_1(self):
        model = TestModels.lp_model_1()
        s = Tests.universal_solver({'time_limit': 10})

        soln, run = s.solve(model)

        self.assertEqual(run.term_status, flp.RunStatus.OPTIMAL)
        self.assertEqual(model.objective.value(soln), 35.0)
        self.assertEqual(model.variables['v1'].value(soln), 15.0)
        self.assertEqual(model.variables['v2'].value(soln), 20.0)

    def test_solve_ip_1(self):
        model = TestModels.ip_model_1()
        s = Tests.universal_solver({'time_limit': 10})
        soln, run = s.solve(model)

        self.assertEqual(run.term_status, flp.RunStatus.OPTIMAL)
        self.assertEqual(model.objective.value(soln), -2.0)
        self.assertEqual(model.variables['v1'].value(soln), 1.0)
        self.assertEqual(model.variables['v2'].value(soln), -2.0)

    def test_solve_relaxed_ip_1(self):
        model = TestModels.ip_model_1()

        for variable in model.variables.values():
            variable.continuous = True

        # more generally, can directly substitute a variable
        # m.add_variables(flp.variable.Integer('v1', 10, 20), overwrite=True)
        #
        # can use this to implement model.relax(). but it clobbers old state.
        # by just changing variable.constinuous, you can implement a model.unrelax

        s = Tests.universal_solver({'time_limit': 10})
        soln, run = s.solve(model)

        self.assertEqual(run.term_status, flp.RunStatus.OPTIMAL)
        self.assertEqual(model.objective.value(soln), -2.5)
        self.assertEqual(model.variables['v1'].value(soln), 1.0)
        self.assertEqual(model.variables['v2'].value(soln), -2.5)

    def test_solve_infeasible_1(self):
        model = TestModels.infeasible_ip_model_1()

        s = Tests.universal_solver({'time_limit': 10})
        soln, run = s.solve(model)

        self.assertIn(run.term_status, (flp.RunStatus.INFEASIBLE, flp.RunStatus.INFEASIBLE_OR_UNBOUNDED))

    def test_solve_infeasible_2(self):
        model = TestModels.infeasible_lp_model_1()

        s = Tests.universal_solver({'time_limit': 10})
        soln, run = s.solve(model)

        self.assertIn(run.term_status, (flp.RunStatus.INFEASIBLE, flp.RunStatus.INFEASIBLE_OR_UNBOUNDED))

    def test_solve_unbounded_1(self):
        model = TestModels.unbounded_lp_model_1()

        s = Tests.universal_solver({'time_limit': 10})
        soln, run = s.solve(model)

        self.assertIn(run.term_status, (flp.RunStatus.UNBOUNDED, flp.RunStatus.INFEASIBLE_OR_UNBOUNDED))

    def test_mipstart_1(self):
        model = TestModels.ip_model_1()

        mipstart = flp.Solution()
        mipstart.set_var('v1', 0)
        mipstart.set_var('v2', 10)

        s = Tests.universal_solver({'time_limit': 10})
        soln, run = s.solve(model, mipstart=mipstart, keep_log_file=True)

        # Loaded MIP start with objective 10
        # MIPStart values read for 2 variables


def run():
    this_module = sys.modules[__name__]
    unittest.main(this_module)

if __name__ == '__main__':
    run()
