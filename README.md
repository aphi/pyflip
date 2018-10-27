# PyFlip

[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)
[![Build status](https://ci.appveyor.com/api/projects/status/mgi67kkcrd9rg0hg?svg=true)](https://ci.appveyor.com/project/aphi/pyflip)

PyFlip is a simple and modern library for Linear and Integer Programming in Python 3, offering an API to advanced solvers.

A major focus is features which speed up the model development process, e.g. prototyping, debugging, profiling, and integrating with metaheuristic algorithms.

This project has been written from scratch in 2018, having been inspired by PuLP, CyLP, rust-lp-modeler, and JuMP.

For Python 3.6+. (Earlier 3.X versions will work if you use an f-string backport)

Feature requests and PRs are welcome.



                                                                   
## Getting Started

#### Installation

```
$ pip install pyflip
```

#### Testing

```
$ python -c "import pyflip; pyflip.test.unit_test.run()"
...........                                                           
----------------------------------------------------------------------
Ran 11 tests in 0.329s                                                
                                                                      
OK 
```

#### Usage Example 1

```python
>>> import pyflip as flp
```

Create a *Model* object
```python
>>> model = flp.Model('FactoryOptimisation')
```

Create *Continuous* variables bounded between 0 and 5.

```python
>>> x_1 = flp.variable.Continuous('x_1', 0, 5)
>>> x_2 = flp.variable.Continuous('x_2', 0, 5)
>>> model += x_1, x_2 # variables must be explicitly added to the model
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

##### See more complex examples in the [Documentation](docs/readme.md)


## Features & Roadmap

Current features:
- CBC and Gurobi support

- Fast expression handling
    - expr_of_interest = flp.Expression()
    - expr_of_interest.value(soln)

- Simple IP-to-LP relaxations, and unrelaxations

- Parameter management (TODO: show runs with multiple values exploring effect of cuts or other things)
( in machine learning this is called hyperparameter optimisation )

- MIP starts

Substantial further work is planned, including:
- Graphical presentation of solve process, built on solver logs
- Read in LP file
- Easily load and test candidate solutions w.r.t. objective and constraints model.assess(soln)
    - very useful for debugging a formulation
    - useful to implement basic heuristics operating on variables (e.g. a known transformation between two solutions in variable-space, e.g. a configuration shuffle)
- Using a FFI to interact directly with solver objects, rather than via lp files (CyLP and JuMP do this well)
- Graphical representation of 2D & 3D polytopes using mplot3d
- Model debugging: Explain why is model is infeasible.
- Model debugging: Why a model is unbounded
- refactor to use pathlib instead of older-style os calls
- run log buffering
- store lp files and sol files in a directory


Examples to follow soon. Knapsack with heuristic MIP start. parameter search.


Show off available objects. Run, Model, Solution