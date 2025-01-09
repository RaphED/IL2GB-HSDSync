import tkinter as tk
from tkinter import ttk, filedialog

from GUI.Components.clickableIcon import CliquableIcon
from GUI.Components.tooltip import Tooltip
from pythonServices.configurationService import getConf, update_config_param, allowedCockpitNotesModes, checkIL2InstallPath
from pythonServices.filesService import getIconPath

class ParametersPanel:
    def __init__(self, root: tk):
        self.root = root

        # Style configuration
        style = ttk.Style()
        style.configure("Path.TLabel",
                       cursor="hand2",
                       font=("Arial", 9, "underline"),
                       padding=5)
        style.configure("PathError.TLabel",
                       foreground="white",
                       background="#ff4d4d",
                       cursor="hand2",
                       font=("Arial", 9, "underline"),
                       padding=5)

        label = ttk.Label(text="Parameters", font=("Arial", 10, "bold"))
        label.pack(side="left", fill="x", padx=5)
        params_label_frame = ttk.LabelFrame(root, labelwidget=label, padding=(5, 5))
        params_label_frame.pack(fill="both", padx=2, pady=2)
        
        # Path frame with fixed height
        path_frame = tk.Frame(params_label_frame, height=30)
        path_frame.pack(fill="x", pady=5)
        path_frame.pack_propagate(False)  # Prevents automatic resizing
        
        # Frame to contain icon and label (for better alignment)
        path_content_frame = tk.Frame(path_frame)
        path_content_frame.pack(fill="both", expand=True)
        
        # Icon (path placeholder)
        self.icon_path = CliquableIcon(path_content_frame,
            icon_path=getIconPath("IL2.png"),
            onClick=self.modify_path
        )
        self.icon_path.pack(side="left", padx=5)
        
        # Clickable path label
        self.path_label = ttk.Label(path_content_frame, 
                                  style="Path.TLabel",
                                  cursor="hand2")
        self.path_label.pack(side="left", fill="x", expand=True)
        Tooltip(self.path_label, "Your IL2 Path. Click to modify")
        
        # Click event configuration
        self.path_label.bind("<Button-1>", lambda e: self.modify_path())
        
        self.update_pathLabel()

        # Rest of the interface
        toggle_removeSkins_frame = tk.Frame(params_label_frame)
        toggle_removeSkins_frame.pack(fill="x", pady=5)
        tk.Label(toggle_removeSkins_frame, text="Auto remove unregistered skins", anchor="w").pack(side="left", padx=5)
        self.toggle_removeSkins_var = tk.BooleanVar(value=getConf("autoRemoveUnregisteredSkins"))
        self.toggle_removeSkins_button = ttk.Checkbutton(toggle_removeSkins_frame, variable=self.toggle_removeSkins_var, onvalue=True, offvalue=False, command=self.modify_auto_remove)
        self.toggle_removeSkins_button.pack(side="right", padx=5)

        toggle_applyCensorship_frame = tk.Frame(params_label_frame)
        toggle_applyCensorship_frame.pack(fill="x", pady=5)
        tk.Label(toggle_applyCensorship_frame, text="Apply censorship", anchor="w").pack(side="left", padx=5)
        self.toggle_applyCensorship_var = tk.BooleanVar(value=getConf("applyCensorship"))
        self.toggle_applyCensorship_button = ttk.Checkbutton(toggle_applyCensorship_frame, variable=self.toggle_applyCensorship_var, onvalue=True, offvalue=False, command=self.modify_apply_censorship)
        self.toggle_applyCensorship_button.pack(side="right", padx=5)

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

    def short_path(self, fullPath, maxLength=55):
        if len(fullPath) > maxLength:
            return f"{fullPath[:maxLength]}..."
        return fullPath
    
    def update_pathLabel(self):
        currentIL2Path = getConf("IL2GBGameDirectory")
        self.path_label.config(text=self.short_path(currentIL2Path))
        
        if checkIL2InstallPath():
            self.path_label.configure(style="Path.TLabel")
        else:
            self.path_label.configure(style="PathError.TLabel")
    
    def modify_path(self):
        file_path = filedialog.askdirectory(
            initialdir=getConf("IL2GBGameDirectory"),
            title="Select your IL2 folder"
        )
        if len(file_path) > 0:
            update_config_param("IL2GBGameDirectory", file_path)
            self.update_pathLabel()
    
    def modify_auto_remove(self):
        update_config_param("autoRemoveUnregisteredSkins", self.toggle_removeSkins_var.get())

    def modify_apply_censorship(self):
        update_config_param("applyCensorship", self.toggle_applyCensorship_var.get())
    
    def on_dropdown_change(self, event):
        update_config_param("cockpitNotesMode", self.dropdown_var.get())