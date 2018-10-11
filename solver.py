from abc import ABC, abstractmethod
import time
import shutil
import subprocess
import os
import io
import pdb
from collections import OrderedDict

import pyflip as flp


class Solver(ABC):
    """
    Non-IP methods (e.g. greedy heuristics) should be able to subclass this and implement the solve method
    """

    def __init__(self):
        pass

    @abstractmethod
    def solve(self, model):
        # must return a Solution object and a Run object
        pass


class IPSolver(Solver, ABC):
    def __init__(self, pyflip_params, solver_params):
        super().__init__()

        self.params = OrderedDict() # keys are solver param names, values are Parameter objects
        self.set_pyflip_params(pyflip_params)
        self.set_solver_params(solver_params)

    @property
    @abstractmethod
    def param_mapping(self):
        """
        define a dictionary mapping pyflip params into solver-specific paramters
        """
        pass

    def set_pyflip_params(self, pyflip_param_dict):
        """
        :param pyflip_param_dict: dictionary of universal params
        """
        for pyflip_param_name, value in pyflip_param_dict.items():
            try:
                solver_param_name = self.param_mapping[pyflip_param_name]
            except KeyError:
                raise KeyError(f'No known mapping for pyflip param "{pyflip_param_name}" with {self.__class__.__name__} solver')

            self.params[solver_param_name] = Parameter(value, solver_param_name, pyflip_param_name)

    def set_solver_params(self, solver_param_dict):
        """
        :param solver_param_dict: dictionary of solver-specific params
        """
        for solver_param_name, value in solver_param_dict.items():
            self.params[solver_param_name] = Parameter(value, solver_param_name)

    def param_value_by_pyflip_name(self, pyflip_name):
        for param in self.params.values():
            if param.pyflip_name == pyflip_name:
                return param.value


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
        self.full_lp_filename = None # written when self.write_lp_file() is called

    @property
    @abstractmethod
    def solver_binary(self):
        pass

    def solver_write_lp_file(self, model):
        """
        Write lp file and set output file param
        """
        full_lp_filename = flp.write_lp_file(model)
        model_filename_stem = os.path.splitext(full_lp_filename)[0]
        self.set_pyflip_params({'output_file': f'{model_filename_stem}.sol'})
        self.full_lp_filename = full_lp_filename

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
        return {
            'time_limit': 'TimeLimit',
            'output_file': 'ResultFile'
        }

    def solve(self, model, keep_lp_file=False, keep_sol_file=False, log_filename='pyflip.log'):
        self.solver_write_lp_file(model)

        # Build command (solver-specific CLI)
        args = [self.path_to_solver]
        for param in self.params.values():
            args.append(f'{param.solver_name}={param.value}')
        args.append(self.full_lp_filename)
        cmd = ' '.join(args)
        print(cmd)

        # Run solver
        run = Run(log_filename, params=self.params)
        with run:
            run.log_fo.flush()
            subprocess.run(cmd, stdout=run.log_fo, stderr=run.log_fo)

        # Read solution file (solver-specific)
        soln = flp.Solution()
        with open(self.param_value_by_pyflip_name('output_file'), 'r') as fo:
            for line in fo:
                split_line = line.split()
                if split_line[0] != '#':
                    soln.assign_var(*split_line)

        #TODO: dumpster-dive logs to find out
        run.term_status = 'Unknown'

        # delete files
        if not keep_lp_file:
            os.remove(self.full_lp_filename)
        if not keep_sol_file:
            os.remove(self.param_value_by_pyflip_name('output_file'))

        return soln, run


class CbcCL(IPSolverCL):
    def __init__(self, pyflip_params=None, solver_params=None, path_to_solver=None):
        super().__init__(pyflip_params, solver_params, path_to_solver)

        # Set default parameters
        self.set_solver_params({
            'printingOptions': 'normal',
            'timeMode': 'elapsed',
        })

    @property
    def solver_binary(self):
        return 'cbc'

    @property
    def param_mapping(self):
        """
        :return: Solver-specific mapping
        """
        # https://projects.coin-or.org/CoinBinary/export/1059/OptimizationSuite/trunk/Installer/files/doc/cbcCommandLine.pdf
        return {
            'time_limit': 'sec',
            'output_file': 'solution'
        }

    def solve(self, model, keep_lp_file=False, keep_sol_file=False, log_filename='pyflip.log'):
        self.solver_write_lp_file(model)

        # Set model-specific parameters
        value_only_parameters = [] # parameters where key=value
        value_only_parameters.append(self.full_lp_filename)
        value_only_parameters.append("solve")

        # Build command (solver-specific CLI)
        args = [self.path_to_solver] + value_only_parameters
        for param in self.params.values():
            args.append(f'{param.solver_name} {param.value}')
        cmd = ' '.join(args)
        print(cmd)

        # Run solver
        run = Run(log_filename, params=self.params)
        with run:
            run.log_fo.flush()
            p = subprocess.run(cmd, stdout=run.log_fo, stderr=run.log_fo)

        # Read solution file (solver-specific)
        soln = flp.Solution()
        with open(self.param_value_by_pyflip_name('output_file'), 'r') as fo:
            first_line = next(fo)
            run.term_status = first_line.split()[0]
            for line in fo:
                split_line = line.split()
                soln.assign_var(split_line[1], split_line[2])

        # delete files
        if not keep_lp_file:
            os.remove(self.full_lp_filename)
        if not keep_sol_file:
            os.remove(self.param_value_by_pyflip_name('output_file'))

        return soln, run


class Cplex(IPSolver):
    def solve(self, model):
        pass



class Run():
    """
    Solver run context Manager providing timer etc
    """
    def __init__(self, log_filename, params=None):
        self.log_filename = log_filename if log_filename is not None else open(os.devnull, 'w')
        self.params = params if params is not None else {}
        self.term_status = None
        self.log = '' # only populated at completion

    def __enter__(self):
        self.log_fo = open(self.log_filename, 'w')
        self.log_fo.write('Run started\n')
        self.solve_duration = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.solve_duration = self.get_duration()
        self.log_fo.write('Run ended\n')
        self.log_fo.close()

        # we need to save the contents of the log.
        # ideally there would be a split stream way to do this,
        # however this is a workaround
        with open(self.log_filename, 'r') as fo:
            self.log = fo.readlines()


    # def write(self, msg):
    #     self.log_fo.write(msg)

    def get_duration(self):
        """
        :return: Seconds elapsed since start of run
        """
        return time.perf_counter()  - self.solve_duration


class Parameter:
    def __init__(self, value, solver_name, pyflip_name=None):
        self.value = value
        self.solver_name = solver_name
        self.pyflip_name = pyflip_name


# mapping (in the future there may be multiple solver options)
Gurobi = GurobiCL
Cbc = CbcCL


# class MySolver(Solver):
#     def solve(self, model):
#
#         for constraint in model.constraints:
#             constraint.mid = '='
#
#         s = Gurobi()
#         soln, run = s.solve(model)
#
#         run.log += 'ok'
#
#         return soln