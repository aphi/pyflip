import matplotlib.pyplot as plt
from time import perf_counter
from enum import Enum

import pyflip as flp

class Run:
    """
    Solver run context Manager providing timer etc
    """
    def __init__(self, name_prefix='', solver_name='', params=None):
        self.name = flp.utils.unique_name(name_prefix, trunc_uuid_len=6)
        self.solver_name = solver_name
        self.params = params if params is not None else {}
        self.term_status = None
        self.log = '' # only filled at completion

    def __enter__(self):
        self.log_filename = self.params.value_by_pyflip_name('output_log_file')

        self.log_fo = open(self.log_filename, 'w')
        self.log_fo.write('Run started\n')
        self.solve_duration = perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.solve_duration = self.get_duration()
        self.log_fo.write('Run ended\n')
        self.log_fo.close()

        # we need to save the contents of the log.
        # ideally there would be a split stream way to do this,
        # however this is a workaround
        with open(self.log_filename, 'r') as fo:
            self.log = fo.read().splitlines()

    # def write(self, msg):
    #     self.log_fo.write(msg)


    def get_duration(self):
        """
        :return: Seconds elapsed since start of run
        """
        return perf_counter()  - self.solve_duration


class RunStatus(Enum):
    OPTIMAL = 'Optimal'
    INFEASIBLE = 'Infeasible'
    UNBOUNDED = 'Unbounded'
    INFEASIBLE_OR_UNBOUNDED = 'Infeasible or Unbounded'
    TIMELIMIT = 'Time limit reached'
    UNKNOWN = 'Unknown'
