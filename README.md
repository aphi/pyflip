#PyFlip

PyFlip is a simple and modern library for Linear and Integer Programming in Python 3, offering an API to advanced solvers.

A major focus is features which speed up the model development process, e.g. prototyping, debugging, profiling, and integrating with metaheuristic algorithms.

This project has been written from scratch in 2018, and was inspired by PuLP, CyLP, rust-lp-modeler, and JuMP.


Feature requests are welcome.


Substantial further work is planned, including;
- Support for MIP starts
- Graphical presentation of solve process, built on solver logs
- Read in LP file
- Easily load and test candidate solutions w.r.t. objective and constraints model.assess(soln)
    - very useful for debugging a formulation
    - useful to implement basic heuristics operating on variables (e.g. a known transformation between two solutions in variable-space, e.g. a configuration shuffle)
- Using a FFI to interact directly with solver objects, rather than via lp files (CyLP and JuMP do this well)
- Graphical representation of 2D & 3D polytopes using mplot3d
- Model debugging: Explain why is model is infeasible.
- Model debugging: Why a model is unbounded
- vsum function for faster expression generation
- extend unit tests for other solvers



Expression handling
expr_of_interest = flp.Expression()
expr_of_interest.value(soln)
