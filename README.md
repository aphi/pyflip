#PyFlip

PyFlip is a simple and modern library for Linear and Integer Programming in Python 3, offering an API to advanced solvers.

A major focus is features which speed up the model development process, e.g. prototyping, debugging, profiling, and integrating with metaheuristic algorithms.

This project has been written from scratch in 2018, and was inspired by PuLP, CyLP, rust-lp-modeler, and JuMP.

Substantial further work is planned, including;
- Support for MIP starts
- Using a FFI to interact directly with solver objects, rather than via lp files (CyLP and JuMP do this well)
- Graphical presentation of solve process, built on solver logs
- Graphical representation of 2D & 3D polytopes using mplot3d
- Easily load a solution
- Model debugging: Explain why is model is infeasible.
- Model debugging: Why a model is unbounded
- Read in LP file
- vsum function for faster expression generation
- extend unit tests for other solvers



Expression handling
expr_of_interest = flp.Expression()
expr_of_interest.value(soln)
