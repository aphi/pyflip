import time
import matplotlib.pyplot as plt
import re
import os

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