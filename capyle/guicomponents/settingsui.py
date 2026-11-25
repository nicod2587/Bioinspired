import tkinter as tk


class _SettingsUI(tk.Frame):
    """Edits config.settings, a {name: value} dict the description fills in.

    bools get a checkbox, names in config.setting_choices a dropdown,
    everything else an entry converted back to the default's type.
    """

    def __init__(self, parent, ca_config):
        tk.Frame.__init__(self, parent)
        tk.Label(self, text="Settings:").grid(row=0, column=0, sticky=tk.W)
        choices = getattr(ca_config, 'setting_choices', {})
        self.vars = {}
        self.types = {}
        for row, (name, value) in enumerate(ca_config.settings.items(), 1):
            label = name.lower().replace('_', ' ')
            tk.Label(self, text=label).grid(row=row, column=0, sticky=tk.W)
            if isinstance(value, bool):
                var = tk.BooleanVar(value=value)
                widget = tk.Checkbutton(self, variable=var)
            elif name in choices:
                var = tk.StringVar(value=value)
                widget = tk.OptionMenu(self, var, *choices[name])
            else:
                var = tk.StringVar(value=str(value))
                widget = tk.Entry(self, textvariable=var, width=12)
            widget.grid(row=row, column=1, sticky=tk.W)
            self.vars[name] = var
            self.types[name] = type(value)
        self.defaults = dict(ca_config.settings)

    def get_value(self):
        """Raises ValueError naming the setting if an entry won't convert"""
        values = {}
        for name, var in self.vars.items():
            try:
                values[name] = self.types[name](var.get())
            except ValueError:
                raise ValueError("{} must be a {}, got '{}'".format(
                    name, self.types[name].__name__, var.get()))
        return values

    def set(self, settings):
        for name, value in settings.items():
            if name in self.vars:
                self.vars[name].set(value)

    def set_default(self):
        self.set(self.defaults)
