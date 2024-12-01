import tkinter as tk
from tkinter import ttk, filedialog

from pythonServices.configurationService import getConf, update_config_param, allowedCockpitNotesModes

class ParametersPanel:

    def __init__(self, root: tk):

        self.root = root

        label = ttk.Label(text="Parameters", font=("Arial", 10,"bold"))
        label.pack(side="left", fill="x",padx=5)  # Add some padding above the Treeview
        params_label_frame = ttk.LabelFrame(root, labelwidget=label, padding=(5, 5))
        params_label_frame.pack(fill="both",padx=2, pady=2)
        
        path_frame = tk.Frame(params_label_frame)
        path_frame.pack(fill="x", pady=5)
        self.path_label = tk.Label(path_frame, text=self.short_path(getConf("IL2GBGameDirectory")), anchor="w")
        self.path_label.pack(side="left", fill="x", expand=True, padx=5)
        self.path_button = ttk.Button(path_frame, text="Modify", command=self.modify_path)
        self.path_button.pack(side="right", padx=5)

        # Toggle Switch
        toggle_frame = tk.Frame(params_label_frame)
        toggle_frame.pack(fill="x", pady=5)
        tk.Label(toggle_frame, text="Auto remove unregistered skins", anchor="w").pack(side="left", padx=5)
        self.toggle_var = tk.BooleanVar(value=getConf("autoRemoveUnregisteredSkins"))
        self.toggle_button = ttk.Checkbutton(toggle_frame, variable=self.toggle_var, onvalue=True, offvalue=False, command=self.modify_auto_remove)
        self.toggle_button.pack(side="right", padx=5)

        # Dropdown Menu
        dropdown_frame = tk.Frame(params_label_frame)
        dropdown_frame.pack(fill="x", pady=5)
        tk.Label(dropdown_frame, text="Cockpit Photo", anchor="w").pack(side="left", padx=5)
        self.dropdown_var = tk.StringVar(value=getConf("cockpitNotesMode"))
        self.dropdown = ttk.Combobox(
            dropdown_frame,
            textvariable=self.dropdown_var,
            values=allowedCockpitNotesModes,
            state="readonly",
        )
        self.dropdown.pack(side="right", padx=5)
        self.dropdown.bind("<<ComboboxSelected>>", self.on_dropdown_change)

    def short_path(self,fullPath, maxLength = 50):
        if len(fullPath) > maxLength:
            return f"{fullPath[:maxLength]}..."
        return fullPath
    
    def modify_path(self):
        file_path = filedialog.askdirectory(
            initialdir=getConf("IL2GBGameDirectory"),
            title="Select a folder"
        )
        if len(file_path)>0:
            update_config_param("IL2GBGameDirectory",file_path)
            self.path_label.config(text=self.short_path(file_path))
    
    def modify_auto_remove(self):
        lebooleanquejeveux=self.toggle_var.get()
        update_config_param("autoRemoveUnregisteredSkins", lebooleanquejeveux)
    
    def on_dropdown_change(self, event):
        """Handle dropdown value change."""
        selected_value = self.dropdown_var.get()
        update_config_param("cockpitNotesMode", selected_value)