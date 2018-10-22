"""
Utility functions and constant values
"""
from uuid import uuid4
from time import strftime

EPS = 1E-9

def sign(val):
    return '+' if val >= 0 else '-'

def unique_name(prefix='', trunc_uuid_len=0):
    time_str = strftime('%Y_%m_%d-%H_%M_%S')
    hex_uuid = uuid4().hex[-trunc_uuid_len:]
    if prefix:
        return f'{prefix}-{time_str}-{hex_uuid}'
    else:
        return f'{time_str}-{hex_uuid}'

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


# more comprehensive run summary

# print(m.objective.name, m.objective, m.objective.value(soln))
# for var_name, var in m.variables.items():
#     print(var_name, var.value(soln))
# for con_name, con in m.constraints.items():
#     print(f'{con_name}: {con.lhs} {con.mid} {con.rhs}')
#     print(f'{con.lhs.value(soln)} {con.mid} {con.rhs.value(soln)}')


# model.assess