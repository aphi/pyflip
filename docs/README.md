# PyFlip

PyFlip is a simple and modern library for Linear and Integer Programming in Python 3, offering an API to advanced solvers.

A major focus is features which speed up the model development process, e.g. prototyping, debugging, profiling, and integrating with metaheuristic algorithms.

This project has been written from scratch in 2018, having been inspired by PuLP, CyLP, rust-lp-modeler, and JuMP.

For Python 3.6+. (Earlier 3.X versions will work if you use an f-string backport)

Feature requests and PRs are welcome.

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