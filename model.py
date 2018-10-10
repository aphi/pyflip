import os
from variable import Variable, Expression
from collections import Iterable

class Model:
    model_ctr = 0
    def __init__(self, name=None):
        if name is None:
            name = f'Model_{self.model_ctr}'
            Model.model_ctr += 1

        self.name = name
        self.variables = {}
        self.objective = Objective()
        self.constraints = {}

    def add_variables(self, *variables):
        for variable in variables:
            if variable.name not in self.variables:
                self.variables[variable.name] = variable
            else:
                raise RuntimeError(f'A variable named {variable.name} already exists in this model')

    def add_objective(self, objective):
        self.objective = objective

    def add_constraint(self, constraint):
        if constraint.name not in self.constraints:
            self.constraints[constraint.name] = constraint
        else:
            raise RuntimeError(f'A constraint named {constraint.name} already exists in this model')

    def __iadd__(self, other):
        if isinstance(other, Variable):
            self.add_variables(other)
        elif isinstance(other, Iterable):
            self.add_variables(*other)
        elif isinstance(other, Constraint):
            self.add_constraint(other)
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
    obj_ctr = 0
    def __init__(self, dir='min', expr=None, name=None):
        if name is None:
            name = f'obj_{self.obj_ctr}'
            Objective.obj_ctr += 1

        self.expr = Expression(expr) if expr is not None else Expression()
        self.dir = dir
        self.name = name

    def value(self, soln):
        return self.expr.value(soln)

    def __repr__(self):
        return f'{self.name}: {self.dir} {self.expr}'


class Constraint:
    con_ctr = 0
    def __init__(self, lhs=None, mid=None, rhs=None, name=None):
        if name is None:
            name = f'con_{self.con_ctr}'
            Constraint.con_ctr += 1

        self.lhs = Expression(lhs) if lhs is not None else Expression()
        self.rhs = Expression(rhs) if rhs is not None else Expression()
        self.mid = mid if mid is not None else '<='
        self.name = name

        # rearrange constraint expressions
        self._lhs, self._rhs = Expression.rearrange_ineq(lhs, rhs)


    def __repr__(self):
        return f'{self.name}: {self.lhs} {self.mid} {self.rhs}'

# # TODO: implement these useful methods
# c.is_satisfied() -> bool
# c.viol() -> negative of slack
# c.slack() -> qty. if neg this means the constraint is violated
