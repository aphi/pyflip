from abc import ABC, abstractmethod
from math import inf
from copy import copy
from numbers import Number
import pdb

from utils import sign, EPS

class Variable(ABC):
    # this doesn't subclass Expression because it's fundamentally a different purpose object
    var_ctr = 0

    @abstractmethod
    def __init__(self, name=None, continuous=True, lower_bound=-inf, upper_bound=inf):
        if name is None:
            name = 'var_{}'.format(self.var_ctr)
            Variable.var_ctr += 1
        elif not isinstance(name, str): #TODO: put these checks in a utility function in utils.py
            raise RuntimeError('Variable names must be strings, not "{}"'.format(type(name)))
        elif not name.isidentifier():
            raise RuntimeError('Variable name "{}" is an invalid identifier'.format(name))

        self.name = name
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.continuous = continuous

    def value(self, soln=None):
        return Expression(self).value(soln)

    def __neg__(self):
        return -Expression(self)

    def __add__(self, other):
        return Expression(self) + other

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.__add__(-other)

    def __rsub__(self, other):
        return (-self).__add__(other)

    def __mul__(self, other):
        return Expression(self) * other

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return Expression(self) / other

    def __repr__(self):
        return '{}({})[{}{}{}]'.format(
            self.name,
            type(self).__name__,
            self.lower_bound,
            ',' if self.continuous else '..',
            self.upper_bound)


class Continuous(Variable):
    def __init__(self, name=None, lower_bound=-inf, upper_bound=inf):
        super().__init__(name, True, lower_bound, upper_bound)


class Integer(Variable):
    def __init__(self, name=None, lower_bound=-inf, upper_bound=inf):
        super().__init__(name, False, lower_bound, upper_bound)


class Binary(Integer):
    def __init__(self, name=None):
        super().__init__(name, 0, 1)


class Expression:
    def __init__(self, val=None): # var_dict=None, constant=0.0
        # one option:
        # list of tuples/ each tuple is a TERM [(coef, var), (coef, var), ... ]
        # however, we need to check membership quickly

        # another option is a dict with variable names as keys
        # only holds names for speed of building expressions
        if val is None:
            self.var_dict = {}
            self.constant = 0.0

        elif isinstance(val, Number):
            self.var_dict = {}
            self.constant = float(val)

        elif isinstance(val, Variable):
            self.var_dict = {val.name: 1.0}
            self.constant = 0.0

        elif isinstance(val, Expression):
            self.var_dict = copy(val.var_dict)
            self.constant = copy(val.constant)

        else:
            raise NotImplementedError('Cannot generate an Expression from {}'.format(type(val)))

    @classmethod
    def from_var_dict(cls, var_dict=None, constant=0.0):
        self = cls(constant)
        if var_dict is not None:
            self.var_dict = var_dict

    def value(self, soln=None):
        tot_value = self.constant
        for var, coef in self.var_dict.items():
            val = soln.var_dict[var]  # try/except
            tot_value += coef * val

        return tot_value

    @classmethod
    def rearrange_ineq(cls, lhs_expr, rhs_expr):
        new_lhs = Expression(lhs_expr)
        new_lhs -= rhs_expr

        new_rhs = Expression(-new_lhs.constant)
        new_lhs.constant = 0

        return new_lhs, new_rhs

    def __neg__(self):
        return self.__mul__(-1)

    def __add__(self, other):
        copied_e = Expression(self)
        other_e = Expression(other)

        # merge other_e into copied_e
        for var_name, coef in other_e.var_dict.items():
            copied_e.var_dict.setdefault(var_name, 0.0)
            copied_e.var_dict[var_name] += coef

        copied_e.constant += other_e.constant

        return copied_e

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.__add__(-other)

    def __rsub__(self, other):
        return (-self).__add__(other)

    def __mul__(self, other):
        if isinstance(other, Number):
            copied_e = Expression(self)

            for var_name in copied_e.var_dict:
                copied_e.var_dict[var_name] *= other

            copied_e.constant *= other
            return copied_e

        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, Number):
            return self.__mul__(1 / other)

        return NotImplemented

        #TODO: implement this, and test efficiency. doesn't need to copy
        # def __iadd__(self, other):

    def __repr__(self):
        # terms = ['{:+}{}'.format(coef, var_name) for var_name, coef in self.var_dict.items()]
        # terms.append('{:+}'.format(self.constant))
        terms = []

        # variables
        if self.var_dict:
            var_iter = iter(self.var_dict.items())
            (var_name, coef) = next(var_iter)
            terms.append('{} {}'.format(coef, var_name))

            for (var_name, coef) in var_iter:
                terms.append('{} {} {}'.format(sign(coef), abs(coef), var_name))

        # constant
        if (not self.var_dict): # when there are no variables, always print (even if zero)
            terms.append('{}{}'.format(sign(self.constant), abs(self.constant)))
        elif (abs(self.constant) > EPS): # when there are variables only print when nonzero
            terms.append('{} {}'.format(sign(self.constant), abs(self.constant)))

        return ' '.join(terms)
