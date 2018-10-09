from abc import ABC, abstractmethod
import time
import shutil
import subprocess
import os
import pdb

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
    def __init__(self, pyflip_parameters, solver_parameters):
        super().__init__()

        self.parameters = {}
        self.set_pyflip_parameters(pyflip_parameters)
        self.set_solver_parameters(solver_parameters)

    @property
    @abstractmethod
    def get_parameter_mapping(self):
        """
        define a dictionary mapping pyflip parameters into solver-specific paramters
        """
        pass

    def set_pyflip_parameters(self, pyflip_parameters):
        """
        :param parameters: dictionary of universal parameters
        """
        for param, val in pyflip_parameters.items():
            try:
                self.parameters[self.get_parameter_mapping[param]] = val
            except KeyError:
                raise KeyError(f'No known mapping for pyflip parameter "{param}" with {self.__class__.__name__} solver')


    def set_solver_parameters(self, parameters):
        """
        :param parameters: dictionary of solver-specific parameters
        """
        self.parameters.update(parameters)


class Run():
    """
    Solver run context Manager providing timer etc
    """
    def __init__(self, log_filename='log.log', parameters={}):
        self.log_filename = log_filename
        self.parameters = parameters

    def __enter__(self):
        self.log_fo = open(self.log_filename, 'w')
        self.log_fo.write('Run started\n')
        self.solve_duration = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.solve_duration = self.get_duration()
        self.log_fo.write('Run ended\n')
        self.log_fo.close()

    def get_duration(self):
        """
        :return: Seconds elapsed since start of run
        """
        return time.perf_counter()  - self.solve_duration


class IPSolver_CL(IPSolver, ABC):
    pass


class Gurobi_CL(IPSolver):
    def __init__(self, pyflip_parameters=None, solver_parameters=None, path_to_solver=None):
        """
        :param pyflip_parameters: Dictionary of allowable parameters
        :param solver_parameters: Dictionary of solver-specific parameters
        :param path_to_solver: Specify path to solver executable
        """
        super().__init__(pyflip_parameters or {}, solver_parameters or {})

        if path_to_solver is not None:
            if not os.access(path_to_solver, os.R_OK):
                raise RuntimeError(f'Provided path to solver {path_to_solver} is not valid executable')
        else:
            solver_bin = 'gurobi_cl'
            path_to_solver = shutil.which(solver_bin)
            if path_to_solver is None:
                raise RuntimeError(f'Could not find an executable {solver_bin} on system PATH')

        self.path_to_solver = path_to_solver

    @property
    def get_parameter_mapping(self):
        # http://www.gurobi.com/documentation/8.0/refman/parameters.html
        return {
            'time_limit': 'TimeLimit'
        }

    def solve(self, model, keep_files=False):
        # write lp file
        full_lp_filename = flp.write_lp_file(model)
        model_filename_stem = os.path.splitext(full_lp_filename)[0]
        self.parameters['ResultFile'] = f'{model_filename_stem}.sol'

        # run solver
        run = Run(parameters = self.parameters)
        with run:
            soln = {}
            run.log_fo.write(f'Its now {run.get_duration()}\n')
            time.sleep(0.2)
            run.log_fo.write(f'That went well after {run.get_duration()}\n')

            # build command
            args = [self.path_to_solver]
            for param, val in self.parameters.items():
                args.append(f'{param}={val}')
            args.append(full_lp_filename)

            cmd = ' '.join(args)
            print(cmd)


            run.log_fo.flush()
            subprocess.run(cmd, stdout=run.log_fo, stderr=run.log_fo)

            # black_hole = open(os.devnull, 'w')

        # read solution file
        soln = flp.Solution()
        with open(self.parameters['ResultFile'], 'r') as fo:
            for line in fo:
                split_line = line.split()
                if split_line[0] != '#':
                    soln.assign_var(*split_line)

        # delete files
        if not keep_files:
            os.remove(full_lp_filename)
            os.remove(self.parameters['ResultFile'])

        return soln, run

Gurobi = Gurobi_CL

class Cbc(IPSolver):
    def solve(self, model):
        pass


class Cplex(IPSolver):
    def solve(self, model):
        pass



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