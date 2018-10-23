class Solution:
    def __init__(self, var_dict=None):
        self.var_dict = var_dict if var_dict is not None else {}

    def set_var(self, var_name, val):
        self.var_dict[var_name] = float(val)

    def get_val(self, var_name):
        try:
            return self.var_dict[var_name]
        except KeyError:
            raise KeyError(f'This solution does not include the variable {var_name}')

    def __repr__(self):
        return '\n'.join([f'{k}={v}' for k, v in self.var_dict.items()])