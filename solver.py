from abc import ABC, abstractmethod
import time
import shutil
import subprocess
import os
import io
import pdb
from collections import OrderedDict
from copy import deepcopy

import pyflip as flp


class Solver(ABC):
    """
    Non-IP methods (e.g. greedy heuristics) should be able to subclass this and implement the solve method
    """

    def __init__(self):
        self.name = self.__class__.__name__

    @abstractmethod
    def solve(self, model):
        # must return a Solution object and a Run object
        pass


class IPSolver(Solver, ABC):
    def __init__(self, pyflip_params, solver_params):
        super().__init__()

        self.params = flp.ParameterSet(self.param_mapping)
        self.params.set_pyflip_params(pyflip_params)
        self.params.set_solver_params(solver_params)

    @property
    @abstractmethod
    def param_mapping(self):
        """
        define a dictionary mapping pyflip params into solver-specific paramters
        """
        pass

    def set_params(self, param_dict, type='pyflip'):
        if type == 'pyflip':
            self.params.set_pyflip_params(param_dict)
        elif type == 'solver':
            self.params.set_solver_params(param_dict)


class IPSolverCL(IPSolver, ABC):
    def __init__(self, pyflip_params=None, solver_params=None, path_to_solver=None):
        """
        :param pyflip_params: Dictionary of allowable params
        :param solver_params: Dictionary of solver-specific params
        :param path_to_solver: Specify path to solver executable
        """
        super().__init__(pyflip_params or {}, solver_params or {})

        # Find command-line executable
        if path_to_solver is not None:
            if not os.access(path_to_solver, os.R_OK):
                raise RuntimeError(f'Provided path to solver {path_to_solver} is not valid executable')
        else:
            path_to_solver = shutil.which(self.solver_binary)
            if path_to_solver is None:
                raise RuntimeError(f'Could not find an executable {self.solver_binary} on system PATH')

        self.path_to_solver = path_to_solver

    @property
    @abstractmethod
    def solver_binary(self):
        pass

    def generate_run_params(self, full_lp_filename, log_filename, run_pyflip_params, run_solver_params):
        unique_run_id = os.path.splitext(full_lp_filename)[0]
        log_filename = log_filename if log_filename is not None else f'{unique_run_id}.log'
        soln_filename = f'{unique_run_id}.sol'

        run_params = deepcopy(self.params)
        if run_pyflip_params is not None:
            run_params.set_pyflip_params(run_pyflip_params)
        if run_solver_params is not None:
            run_params.set_solver_params(run_solver_params)
        run_params.set_pyflip_params({'output_lp_file': full_lp_filename}, auto_include=False)
        run_params.set_pyflip_params({'output_log_file': log_filename}, auto_include=False)
        run_params.set_pyflip_params({'output_soln_file': soln_filename})
        return run_params

    def delete_files(self, run_params, keep_log_file, keep_lp_file, keep_sol_file):
        if not keep_log_file:
            try:
                os.remove(run_params.value_by_pyflip_name('output_log_file'))
            except FileNotFoundError:
                pass
        if not keep_lp_file:
            try:
                os.remove(run_params.value_by_pyflip_name('output_lp_file'))
            except FileNotFoundError:
                pass
        if not keep_sol_file:
            try:
                os.remove(run_params.value_by_pyflip_name('output_soln_file'))
            except FileNotFoundError:
                pass


class GurobiCL(IPSolverCL):
    def __init__(self, pyflip_params=None, solver_params=None, path_to_solver=None):
        super().__init__(pyflip_params, solver_params, path_to_solver)

    @property
    def solver_binary(self):
        return 'gurobi_cl'

    @property
    def param_mapping(self):
        """
        :return: Solver-specific mapping
        """
        # http://www.gurobi.com/documentation/8.0/refman/params.html
        return OrderedDict((
            ('time_limit', 'TimeLimit'),
            ('output_soln_file', 'ResultFile'),
        ))

    @property
    def term_status_mapping(self):
        return {
            'Optimal solution found': flp.RunStatus.OPTIMAL,
            'Optimal objective': flp.RunStatus.OPTIMAL,
            'Model is infeasible': flp.RunStatus.INFEASIBLE,
            'Infeasible model': flp.RunStatus.INFEASIBLE,
            # 'Time limit reached': flp.RunStatus.TIMELIMIT,
            'Infeasible or unbounded model': flp.RunStatus.INFEASIBLE_OR_UNBOUNDED,
        }

    def read_output_files(self, run, model):
        soln = flp.Solution()
        try:
            with open(run.params.value_by_pyflip_name('output_soln_file'), 'r') as fo:
                for line in fo:
                    split_line = line.split()
                    if split_line[0] != '#':
                        soln.set_var(*split_line)
        except FileNotFoundError:
            print('No solution file generated by solver - see run log for details')

        # search in log output for termination status
        # this is potentially error-prone however is the only option for gurobi_cl
        for key, status in self.term_status_mapping.items():
            if any(l.startswith(key) for l in run.log[-8:]): # statuses are always in the last 8 lines
                run.term_status = status
                break

        if run.term_status is None:
            run.term_status = flp.RunStatus.UNKNOWN

        return soln

    def solve(self, model, keep_log_file=False, keep_lp_file=False, keep_sol_file=False, log_filename=None,
              run_pyflip_params=None, run_solver_params=None):
        # Generate LP file
        full_lp_filename = flp.write_lp_file(model)

        # Define run parameters, extended from solver parameters
        run_params = self.generate_run_params(full_lp_filename, log_filename, run_pyflip_params, run_solver_params)

        # Build command (solver-specific CLI)
        args = [self.path_to_solver]
        for param in run_params.values():
            if param.auto_include:
                # if param.value != '': #(key,value) parameter
                args.append(f'{param.solver_name}={param.value}')

        args.append(run_params.value_by_pyflip_name('output_lp_file'))
        cmd = ' '.join(args)
        run_params.set_pyflip_params({'cmd': cmd}, auto_include=False)

        # Run solver
        run = flp.Run(solver_name=self.name, params=run_params)
        with run:
            run.log_fo.flush()
            subprocess.run(cmd, stdout=run.log_fo, stderr=run.log_fo)

        # Read solution file and logfile (solver-specific)
        soln = self.read_output_files(run, model)

        # delete files
        self.delete_files(run_params, keep_log_file, keep_lp_file, keep_sol_file)

        return soln, run


class CbcCL(IPSolverCL):
    def __init__(self, pyflip_params=None, solver_params=None, path_to_solver=None):
        super().__init__(pyflip_params, solver_params, path_to_solver)

        # Set default parameters
        self.params.set_solver_params(OrderedDict((
           ('printingOptions', 'normal'),
           ('timeMode', 'elapsed')
        )))

    @property
    def solver_binary(self):
        return 'cbc'

    @property
    def param_mapping(self):
        """
        :return: Solver-specific mapping
        """
        # https://projects.coin-or.org/CoinBinary/export/1059/OptimizationSuite/trunk/Installer/files/doc/cbcCommandLine.pdf
        return OrderedDict((
            ('time_limit', 'seconds'),
            ('output_soln_file', 'solution')
        ))

    @property
    def term_status_mapping(self):
        return {
            'Optimal': flp.RunStatus.OPTIMAL,
            'Integer infeasible': flp.RunStatus.INFEASIBLE, # would another status code for this be helpful, or is it sufficient in the logs
            'Infeasible': flp.RunStatus.INFEASIBLE,
            'Stopped on time': flp.RunStatus.TIMELIMIT,
            'Unbounded': flp.RunStatus.UNBOUNDED
        }

    def read_output_files(self, run, model):
        soln = flp.Solution()
        with open(run.params.value_by_pyflip_name('output_soln_file'), 'r') as fo:
            first_line = next(fo)

            # get run status from solution file
            status_str = first_line.split('-')[0].strip()
            try:
                run.term_status = self.term_status_mapping[status_str]
            except KeyError:
                print(f'Unrecognized termination status: "{status_str}"')
                run.term_status = status_str

            for line in fo:
                split_line = line.split()
                soln.set_var(split_line[1], split_line[2])

        for var in model.variables.values():
            if var.name not in soln.var_dict:
                soln.set_var(var.name, 0.0)

        return soln

    def solve(self, model, keep_log_file=False, keep_lp_file=False, keep_sol_file=False, log_filename=None,
              run_pyflip_params=None, run_solver_params=None):
        # Generate LP file
        full_lp_filename = flp.write_lp_file(model)

        # Define run parameters, extended from solver parameters
        run_params = self.generate_run_params(full_lp_filename, log_filename, run_pyflip_params, run_solver_params)

        # Build command (solver-specific CLI)
        args = [self.path_to_solver, run_params.value_by_pyflip_name('output_lp_file')]
        for param in run_params.values():
            if param.auto_include:
                if param.value != '': #(key,value) parameter
                    if param.pyflip_name == 'output_soln_file':
                        args.append('solve')  # a hack required for CBC where the solve command must be before the solution file spec
                    args.append(f'{param.solver_name} {param.value}')
                else: # key-only parameter
                    args.append(f'{param.solver_name}')

        cmd = ' '.join(args)
        run_params.set_pyflip_params({'cmd': cmd}, auto_include=False)

        # Run solver
        run = flp.Run(solver_name=self.name, params=run_params)
        with run:
            run.log_fo.flush()
            p = subprocess.run(cmd, stdout=run.log_fo, stderr=run.log_fo)

        # Read solution file and logfile (solver-specific)
        soln = self.read_output_files(run, model)

        # delete files
        self.delete_files(run_params, keep_log_file, keep_lp_file, keep_sol_file)

        return soln, run


class Cplex(IPSolver):
    def solve(self, model):
        pass

# mapping (in the future there may be multiple solver options)
Gurobi = GurobiCL
Cbc = CbcCL
