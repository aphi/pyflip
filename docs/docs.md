# PyFlip

## Example 1

```python
>>> model = flp.Model('FactoryOptimisation')
```

```python
>>> x_1 = flp.variable.Continuous('x_1', 0, 5)
>>> x_2 = flp.variable.Continuous('x_2', 0, 5)
>>> model += x_1, x_2
```

```python
>>> model += flp.Objective('max', x_1 + 2*x_2, name='Profit')
```

```python
>>> model += flp.Constraint(x_1 + 5*x_2, '<=', 25, name='Machine_1')
>>> model += flp.Constraint(5*x_1 + 2*x_2, '<=', 35, name='Machine_2')
```


##### Model
```python
>>> print(model)
```
```
FactoryOptimisation with 2 vars, 2 cons
Profit: max 1.0 x_1 + 1.0 x_2
Machine_1: 1.0 x_1 + 5.0 x_2 <= +25.0
Machine_2: 5.0 x_1 + 2.0 x_2 <= +35.0
x_1(Continuous)[0,5]
x_2(Continuous)[0,5]
```

##### Solve
```python
>>> s = flp.solver.Cbc({'time_limit': 10})
>>> soln, run = s.solve(model)
```

##### Solution
```
>>> print(model.objective.expr.value(soln))
>>> print(soln)
```
```
13.0
x_1=5.0
x_2=4.0
```