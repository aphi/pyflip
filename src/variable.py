from abc import ABC, abstractmethod
from math import inf
from copy import copy
from numbers import Number
from collections import namedtuple
from itertools import count

import pyflip as flp
from .expression import Expression

class Variable(ABC):
    # this doesn't subclass Expression because it's fundamentally a different purpose object
    counter = count()

    @abstractmethod
    def __init__(self, name=None, continuous=True, lower_bound=-inf, upper_bound=inf):
        if name is None:
            name = f'var_{next(Variable.counter)}'

        flp.util.verify_valid_name(name)
        self.name = name
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.continuous = continuous

        self._expr = Expression(self)

    def value(self, soln=None):
        return self._expr.value(soln)

    ''' Any magic method on a Variable returns the Expression representation '''
    def __neg__(self):
        return self._expr.__neg__()

    def __add__(self, other):
        return self._expr.__add__(other)

    def __radd__(self, other):
        return self._expr.__radd__(other)

    def __sub__(self, other):
        return self._expr.__sub__(other)

    def __rsub__(self, other):
        return self._expr.__rsub__(other)

    def __mul__(self, other):
        return self._expr.__mul__(other)

    def __rmul__(self, other):
        return self._expr.__rmul__(other)

    def __truediv__(self, other):
        return self._expr.__truediv__(other)

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