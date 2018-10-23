from collections import OrderedDict

class ParameterSet(OrderedDict):
    def __init__(self, solver_mapping=None):
        super().__init__()

        self.solver_mapping = solver_mapping if solver_mapping is not None else {}
        #  OrderedDict() # keys are solver param names, values are Parameter objects

    def __repr__(self):
        return '\n ' + '\n '.join([f'{k}={v}' for k, v in self.items()])

    def set_pyflip_params(self, pyflip_param_dict, auto_include=True):
        """
        :param pyflip_param_dict: dictionary of universal params
        """
        for pyflip_param_name, value in pyflip_param_dict.items():
            if pyflip_param_name in self.solver_mapping:
                solver_param_name = self.solver_mapping[pyflip_param_name]

            elif not auto_include: # no explicit mapping is OK in this casew
                solver_param_name = pyflip_param_name

            else:
                raise KeyError(f'No known mapping for pyflip param "{pyflip_param_name}" with this solver')

            self[solver_param_name] = Parameter(value, solver_param_name, pyflip_param_name, auto_include=auto_include)

    def set_solver_params(self, solver_param_dict, auto_include=True):
        """
        :param solver_param_dict: dictionary of solver-specific params
        """
        for solver_param_name, value in solver_param_dict.items():
            self[solver_param_name] = Parameter(value, solver_param_name, auto_include=auto_include)

    def value_by_pyflip_name(self, pyflip_name):
        for param in self.values():
            if param.pyflip_name == pyflip_name:
                return param.value

        raise RuntimeError(f'Cannot find a parameter with name {pyflip_name}')

# use namedtuple here?
class Parameter:
    def __init__(self, value, solver_name, pyflip_name=None, auto_include=True):
        self.value = value
        self.solver_name = solver_name
        self.pyflip_name = pyflip_name
        self.auto_include = auto_include

    def __repr__(self):
        return str(self.value)