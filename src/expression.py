from copy import copy
from numbers import Number

import pyflip as flp

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

        elif isinstance(val, flp.Variable):
            self.var_dict = {val.name: 1.0}
            self.constant = 0.0

        elif isinstance(val, Expression):
            self.var_dict = copy(val.var_dict)
            self.constant = copy(val.constant)

        else:
            raise NotImplementedError(f'Cannot generate an Expression from {type(val)}')

    @classmethod
    def from_var_dict(cls, var_dict=None, constant=0.0):
        self = cls(constant)
        if var_dict is not None:
            self.var_dict = var_dict

        return self

    def var_names(self):
        return self.var_dict.keys()

    def value(self, soln=None):
        tot_value = self.constant
        for var_name, coef in self.var_dict.items():
            val = soln.get_val(var_name)
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
            if var_name in copied_e.var_dict:
                copied_e.var_dict[var_name] += coef
            else:
                copied_e.var_dict[var_name] = coef


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

    def __iadd__(self, other):
        # merge other_e into copied_e
        for var_name, coef in other.var_dict.items():
            if var_name in other.var_dict:
                self.var_dict[var_name] += coef
            else:
                self.var_dict[var_name] = coef

        self.constant += other.constant

        return self

    def __repr__(self):
        terms = []

        # variables
        if self.var_dict:
            var_iter = iter(self.var_dict.items())
            (var_name, coef) = next(var_iter)
            terms.append(f'{coef} {var_name}')

            for (var_name, coef) in var_iter:
                terms.append(f'{flp.util.sign(coef)} {abs(coef)} {var_name}')

        # constant
        if (not self.var_dict): # when there are no variables, always print (even if zero)
            terms.append(f'{flp.util.sign(self.constant)}{abs(self.constant)}')
        elif (abs(self.constant) > flp.util.EPS): # when there are variables only print when nonzero
            terms.append(f'{flp.util.sign(self.constant)} {abs(self.constant)}')

        return ' '.join(terms)


def tsum(term_iterable):
    """
    Term sum
    :param term_iterable:
    :return:
    """

    var_dict = {}
    for (coef, var) in term_iterable:
        if coef not in var_dict:
            var_dict[var.name] = coef
        else:
            var_dict[var.name] += coef

    return Expression.from_var_dict(var_dict, 0)

def esum(expr_iterable):
    """
    Expression sum
    :param term_iterable:
    :return:
    """

    var_dict = {}
    constant = 0
    for expr in expr_iterable:
        for (var_name, coef) in expr.var_dict.items():
            if coef not in var_dict:
                var_dict[var_name] = coef
            else:
                var_dict[var_name] += coef

        constant += expr.constant

    return Expression.from_var_dict(
        var_dict,
        constant
    )