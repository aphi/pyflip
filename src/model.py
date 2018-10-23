from itertools import count
from enum import Enum
from collections import Iterable

import pyflip as flp
from .variable import Variable

class Model:
    counter = count()
    def __init__(self, name=None):
        if name is None:
            name = f'Model_{next(Model.counter)}'

        flp.util.verify_valid_name(name)
        self.name = name
        self.variables = {}
        self.objective = Objective()
        self.constraints = {}

    def add_variables(self, *variables, overwrite=False):
        """
        :param variables: a pyflip.variable.Variable object, or iterable
        :param substitute: boolean for whether to allow overwriting existing model variables (by name)
        """
        for variable in variables:
            if (variable.name not in self.variables) or overwrite:
                self.variables[variable.name] = variable
            else:
                raise RuntimeError(f'A variable named {variable.name} already exists in this model')

    def add_objective(self, objective):
        """
        :param objective: a pyflip.Objective object
        """
        self.test_defined_variables(objective.expr)
        self.objective = objective

    def add_constraints(self, *constraints, overwrite=False):
        """
        :param constraint: a pyflip.Constraint object, or iterable
        :param substitute: boolean for whether to allow overwriting existing model constraints (by name)
        """
        for constraint in constraints:
            if (constraint.name not in self.constraints) or overwrite:
                self.test_defined_variables(constraint.lhs)
                self.test_defined_variables(constraint.rhs)
                self.constraints[constraint.name] = constraint
            else:
                raise RuntimeError(f'A constraint named {constraint.name} already exists in this model')

    def test_defined_variables(self, expr):
        """
        Tests that all variables using in an expression are defined in the model
        :param expr:
        """
        for var_name in expr.var_names():
            if var_name not in self.variables:
                raise RuntimeError(f'Unrecognised variable {var_name}. Variables must be added to model before a dependent constraint or objective')

    def is_feasible(self, soln):
        """
        Checks that this solution is feasible, i.e. satisfies all constraints
        :param soln: Solution object
        :return: boolean
        """
        return all(con.is_satisfied(soln) for con in self.constraints.values())

    def num_vars(self):
        return len(self.variables)

    def num_cons(self):
        return len(self.constraints)

    def __iadd__(self, other):
        """
        Define the 'model += object' interface
        """
        if isinstance(other, Iterable):
            first_element = next(iter(other))
            if isinstance(first_element, Variable):
                self.add_variables(*other)
            elif isinstance(first_element, Constraint):
                self.add_constraints(*other)
            else:
                return NotImplemented

        elif isinstance(other, Variable):
            self.add_variables(other)
        elif isinstance(other, Constraint):
            self.add_constraints(other)
        elif isinstance(other, Objective):
            self.add_objective(other)
        else:
            return NotImplemented

        return self

    def __repr__(self):
        lines = [f'{self.name} with {len(self.variables)} vars, {len(self.constraints)} cons']
        lines.append(str(self.objective))
        for constraint in self.constraints.values():
            lines.append(str(constraint))
        for variable in self.variables.values():
            lines.append(str(variable))
        return '\n'.join(lines)


class Objective:
    counter = count()
    def __init__(self, dir='min', expr=None, name=None):
        if name is None:
            name = f'obj_{next(Objective.counter)}'

        flp.util.verify_valid_name(name)

        self.expr = flp.Expression(expr) if expr is not None else flp.Expression()
        self.dir = dir
        self.name = name

    def value(self, soln):
        return self.expr.value(soln)

    def __repr__(self):
        return f'{self.name}: {self.dir} {self.expr}'


class Constraint:
    counter = count()
    def __init__(self, lhs=None, mid=None, rhs=None, name=None):
        if name is None:
            name = f'con_{next(Constraint.counter)}'

        flp.util.verify_valid_name(name)
        # flp.util.verify(mid, ConstraintEq)

        self.lhs = flp.Expression(lhs) if lhs is not None else flp.Expression()
        self.rhs = flp.Expression(rhs) if rhs is not None else flp.Expression()
        self.mid = mid if mid is not None else '<='
        self.name = name

        # rearrange constraint expressions
        self._lhs, self._rhs = flp.Expression.rearrange_ineq(lhs, rhs)
        # self._name = self.name.replace('')

    def is_satisfied(self, soln):
        """
        Check whether this constraint is satisfied in given solution
        :param soln: Solution object
        :return: boolean
        """
        lhs_value = self.lhs.value(soln)
        rhs_value = self.rhs.value(soln)
        return (self.mid == ConstraintEq.EQ.value and abs(lhs_value - rhs_value) <= flp.util.EPS) or \
            (self.mid == ConstraintEq.LEQ.value and lhs_value - rhs_value <= flp.util.EPS) or \
            (self.mid == ConstraintEq.GEQ.value and lhs_value - rhs_value >= -flp.util.EPS)


    def __repr__(self):
        return f'{self.name}: {self.lhs} {self.mid} {self.rhs}'


class ConstraintEq(Enum):
    LEQ = '<='
    EQ = '='
    GEQ = '>='