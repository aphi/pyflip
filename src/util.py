"""
Utility functions and constant values
"""
from uuid import uuid4
from time import strftime

EPS = 1E-6

def sign(val):
    return '+' if val >= 0 else '-'

def unique_name(prefix='', trunc_uuid_len=0):
    time_str = strftime('%Y_%m_%d-%H_%M_%S')
    hex_uuid = uuid4().hex[-trunc_uuid_len:]
    if prefix:
        return f'{prefix}-{time_str}-{hex_uuid}'
    else:
        return f'{time_str}-{hex_uuid}'

def verify_valid_name(name):
    if not isinstance(name, str):
        raise RuntimeError(f'Names must be strings, not "{type(name)}"')
    elif not name.isidentifier():
        raise RuntimeError(f'Name "{name}" is an invalid identifier')
    return


def run_summary(run, soln, model):
    if model.is_feasible(soln):
        solution_status = f'Solution found with objective value {model.objective.expr.value(soln)}'
    else:
        solution_status = 'No feasible solution found'
    return \
f'''Model '{model.name}' with {model.num_vars()} variables and {model.num_cons()} constraints
{solution_status}
Solver '{run.solver_name}' terminated after {run.solve_duration:.3f} sec with status '{run.term_status.value}\''''


def model_soln_summary(run, soln, model):
    summary = []
    summary.append(f'{model.name} solution')
    for var_name, var in model.variables.items():
        summary.append(f'{var_name} = {var.value(soln)}')

    summary.append(f'{model.objective} = {model.objective.value(soln)}')

    for con_name, con in model.constraints.items():
        summary.append(f'{con}')
        summary.append(f'  {con.lhs.value(soln)} {con.mid} {con.rhs.value(soln)}')

    return '\n'.join(summary)