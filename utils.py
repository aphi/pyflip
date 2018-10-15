"""
Utility functions and constant values
"""

EPS = 1E-9

def sign(val):
    return '+' if val >= 0 else '-'

def run_summary(run, soln, model):
    if model.is_feasible(soln):
        solution_status = f'Solution found with objective value {model.objective.expr.value(soln)}'
    else:
        solution_status = 'No feasible solution found'
    return \
f'''Model '{model.name}' with {model.num_vars()} variables and {model.num_cons()} constraints
{solution_status}
Solver '{run.solver_name}' terminated after {run.solve_duration:.3f} sec with status '{run.term_status}'
'''