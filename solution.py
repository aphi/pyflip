class Solution:
    def __init__(self, var_dict=None):
        self.var_dict = var_dict if var_dict is not None else {}

    def assign_var(self, var_name, val):
        self.var_dict[var_name] = float(val)
