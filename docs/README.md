# PyFlip

## Example 1

```python
>>> import pyflip as flp
```

Create a *Model* object
```python
>>> model = flp.Model('FactoryOptimisation')
```

Create *Continuous* variables bounded between 0 and 5.

Variables must be explicitly added to the model before being used in the objective or constraints.
```python
>>> x_1 = flp.variable.Continuous('x_1', 0, 5)
>>> x_2 = flp.variable.Continuous('x_2', 0, 5)
>>> model += x_1, x_2
```

Define an *Objective* by specifying a direction ('min' or 'max') and an expression.
```python
>>> model += flp.Objective('max', x_1 + 2*x_2, name='Profit')
```

Define *Constraint*s by specifying a left-hand-side expression, inequality, and right-hand-side expression.
```python
>>> model += flp.Constraint(x_1 + 5*x_2, '<=', 25, name='Machine_1')
>>> model += flp.Constraint(5*x_1 + 2*x_2, '<=', 35, name='Machine_2')
```

[Optional] Examine model object.
```
>>> print(model)
FactoryOptimisation with 2 vars, 2 cons
Profit: max 1.0 x_1 + 1.0 x_2
Machine_1: 1.0 x_1 + 5.0 x_2 <= +25.0
Machine_2: 5.0 x_1 + 2.0 x_2 <= +35.0
x_1(Continuous)[0,5]
x_2(Continuous)[0,5]
```

Specify the solver and a dictionary of solver parameters.
```python
>>> s = flp.solver.Cbc({'time_limit': 10})
```

Execute the solve command, which returns both a *Solution* and a *Run* object
```python
>>> soln, run = s.solve(model)
```

Inspect solution
```
>>> print(model.objective.expr.value(soln))
13.0
>>> print(soln)
x_1=5.0
x_2=4.0
```