"""
LP Files
https://www.ibm.com/support/knowledgecenter/SSSA5P_12.5.0/ilog.odms.cplex.help/CPLEX/FileFormats/topics/LP.html
http://www.gurobi.com/documentation/8.0/refman/lp_format.html
"""
from math import isinf
from os import path

import pyflip as flp


def write_lp_file(model, filename, directory='.'):
    full_filename = path.join(directory, filename)

    with open(full_filename, 'w') as fp:

        # Title section
        fp.write(f'\ {model.name}\n')

        # Objective function
        fp.write(f'{model.objective.dir}\n')
        if model.objective.expr.var_dict:
            fp.write(f'  {model.objective.name}: {model.objective.expr}\n')
        else:
            fp.write(f'  {model.objective.name}:\n') # omit the constant (because it confuses gurobi_cl)

        # Constraints (printed in rearranged form)
        fp.write('subject to\n')
        for constraint in model.constraints.values():
            fp.write(f'  {constraint.name}: {constraint._lhs} {constraint.mid} {constraint._rhs}\n')

        # Variables
        # Sort variables
        bound_statements = []
        bound_free_statements = []
        general_statements = []
        binary_statements = []
        for variable in model.variables.values():
            # Integer variables
            if not variable.continuous:
                if variable.lower_bound == 0 and variable.upper_bound == 1:
                    binary_statements.append(f'  {variable.name}')
                    # Binary variables need not appear in bounds section
                    continue
                else:
                    general_statements.append(f'  {variable.name}')

            # Bounds section
            if isinf(variable.lower_bound) and isinf(variable.upper_bound):
                bound_free_statements.append(f'  {variable.name} free')
            else:
                bound_statements.append(f'  {variable.lower_bound} <= {variable.name} <= {variable.upper_bound}')

        fp.write('bounds\n')
        fp.write('\n'.join(bound_statements) + '\n')
        fp.write('\n'.join(bound_free_statements) + '\n')

        fp.write('general\n')
        fp.write('\n'.join(general_statements) + '\n')

        fp.write('binary\n')
        fp.write('\n'.join(binary_statements) + '\n')

        fp.write('end\n')

    return full_filename

def read_lp_file(model):
    #TODO
    raise NotImplementedError