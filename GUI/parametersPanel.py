import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from GUI.Components.tooltip import Tooltip
from Services.configurationService import getConf, update_config_param, cockpitNotesModes, GAMES, getGameDirectory, setGameDirectory, checkGameInstallPath, isGameConfigured, tryToFindGamePath
from Services.filesService import getIconPath

# Icon displayed next to the path of each game
GAME_ICONS = {
    "IL2GB": "IL2.png",
    "IL2Korea": "IL2Korea.png",
}

class ParametersPanel:
    def __init__(self, root: tk, on_parameters_change=None):
        self.root = root
        self.on_parameters_change = on_parameters_change

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
        label.pack(side=tk.LEFT, fill="x", padx=5)
        params_label_frame = ttk.LabelFrame(root, labelwidget=label, padding=(5, 5))
        params_label_frame.pack(fill="both", padx=2, pady=2)
        
        # Path frame : one row per supported game
        path_frame = tk.Frame(params_label_frame)
        path_frame.pack(fill="x", pady=10)

        # Frame to contain icon, game name and path label (for better alignment)
        path_content_frame = tk.Frame(path_frame)
        path_content_frame.pack(fill="both", expand=True)
        path_content_frame.columnconfigure(2, weight=1)

        # widgets of each game row, by game code
        self.path_icon_images = {}
        self.path_labels = {}
        self.find_btns = {}
        for row, (game, game_info) in enumerate(GAMES.items()):
            # Game icon
            self.path_icon_images[game] = ImageTk.PhotoImage(Image.open(getIconPath(GAME_ICONS[game])).convert('RGBA').resize((24, 24), Image.Resampling.LANCZOS))
            tk.Label(path_content_frame, image=self.path_icon_images[game]).grid(row=row, column=0, padx=(0, 5), pady=2)

            tk.Label(path_content_frame, text=game_info["label"], anchor="w").grid(row=row, column=1, sticky="w", padx=(0, 5))

            # Clickable path label
            self.path_labels[game] = ttk.Label(path_content_frame,
                                    style="Path.TLabel",
                                    cursor="hand2")
            self.path_labels[game].grid(row=row, column=2, sticky="ew")
            Tooltip(self.path_labels[game], f"Click to specify the {game_info['label']} directory")

            # Auto-detect button (only shown when path is invalid)
            self.find_btns[game] = ttk.Button(path_content_frame, text="Auto-detect", command=lambda g=game: self.auto_find_path(g))
            # not gridded initially — shown only when path is invalid
            self.find_btns[game].grid(row=row, column=3, padx=(5, 0))
            self.find_btns[game].grid_remove()

            self.update_pathLabel(game)

        # Rest of the interface
        toggle_removeSkins_frame = tk.Frame(params_label_frame)
        toggle_removeSkins_frame.pack(fill="x", pady=10)
        self.toggle_removeSkins_var = tk.BooleanVar(value=getConf("autoRemoveUnregisteredSkins"))
        self.toggle_removeSkins_button = ttk.Checkbutton(toggle_removeSkins_frame, variable=self.toggle_removeSkins_var, onvalue=True, offvalue=False, command=self.modify_auto_remove)
        self.toggle_removeSkins_button.pack(side=tk.LEFT, padx=5)
        toggle_removeSkins_label = tk.Label(toggle_removeSkins_frame, text="Auto remove unregistered skins", anchor="w")
        toggle_removeSkins_label.pack(side=tk.LEFT, padx=0)
        Tooltip(toggle_removeSkins_label, text="Check to use HSD as the only custom skins manager - all other skins will be deleted")
        
        toggle_applyCensorship_frame = tk.Frame(params_label_frame)
        toggle_applyCensorship_frame.pack(fill="x", pady=10)
        self.toggle_applyCensorship_var = tk.BooleanVar(value=getConf("applyCensorship"))
        self.toggle_applyCensorship_button = ttk.Checkbutton(toggle_applyCensorship_frame, variable=self.toggle_applyCensorship_var, onvalue=True, offvalue=False, command=self.modify_apply_censorship)
        self.toggle_applyCensorship_button.pack(side=tk.LEFT, padx=5)
        toggle_applyCensorship_label = tk.Label(toggle_applyCensorship_frame, text="Apply censorship", anchor="w")
        toggle_applyCensorship_label.pack(side=tk.LEFT, padx=0)
        Tooltip(toggle_applyCensorship_label, text="Check to download only the censored versions of skins - as specified in HSD")

        cokpit_note_frame = tk.Frame(params_label_frame)
        cokpit_note_frame.pack(fill="x", pady=10)
        self.cockpit_note_image = ImageTk.PhotoImage(Image.open(getIconPath("cokpit-note.png")).convert('RGBA').resize((24, 24), Image.Resampling.LANCZOS))
        self.icon_cokpitNote = tk.Label(cokpit_note_frame, image=self.cockpit_note_image)
        self.icon_cokpitNote.pack(side=tk.LEFT, padx=5)
        
        self.cokpitNote_dropdown = ttk.Combobox(
            cokpit_note_frame,
            values=[cockpitNotesModes[mode] for mode in cockpitNotesModes.keys()],
            state="readonly",
            width=50,
        )
        Tooltip(self.cokpitNote_dropdown, text="Select the cockpit photos collection - some include notes on the plane's operational limits")
        self.cokpitNote_dropdown.set(cockpitNotesModes[getConf("cockpitNotesMode")])
        self.cokpitNote_dropdown.pack(side=tk.LEFT, padx=5)
        self.cokpitNote_dropdown.bind("<<ComboboxSelected>>", self.on_cokpitNote_dropdown_change)

    def emit_collections_change(self):
        #external emit
        if self.on_parameters_change:
            self.root.after(0, self.on_parameters_change)
    
    def short_path(self, fullPath, maxLength=55):
        if len(fullPath) > maxLength:
            return f"{fullPath[:maxLength]}..."
        return fullPath
    
    def update_pathLabel(self, game):
        path_label = self.path_labels[game]
        if not isGameConfigured(game):
            #a game that is not configured is not an error: the player may not own it
            path_label.config(text="Not configured (click to set)", style="Path.TLabel")
            self.find_btns[game].grid()
            return

        path_label.config(text=self.short_path(getGameDirectory(game)))

        if checkGameInstallPath(game):
            path_label.configure(style="Path.TLabel")
            self.find_btns[game].grid_remove()
        else:
            path_label.configure(style="PathError.TLabel")
            self.find_btns[game].grid()

    def auto_find_path(self, game):
        found = tryToFindGamePath(game)
        if found:
            setGameDirectory(game, found)
            self.update_pathLabel(game)
            self.emit_collections_change()
        else:
            messagebox.showwarning("Not found", f"Could not automatically find the {GAMES[game]['label']} installation directory.")

    def modify_path(self, game):
        file_path = filedialog.askdirectory(
            initialdir=getGameDirectory(game) or None,
            title=f"Select your {GAMES[game]['label']} folder"
        )
        if len(file_path) > 0:
            setGameDirectory(game, file_path)
            self.update_pathLabel(game)
            self.emit_collections_change()
    
    def modify_auto_remove(self):
        update_config_param("autoRemoveUnregisteredSkins", self.toggle_removeSkins_var.get())
        self.emit_collections_change()

    def modify_apply_censorship(self):
        update_config_param("applyCensorship", self.toggle_applyCensorship_var.get())
        self.emit_collections_change()
    
    def on_cokpitNote_dropdown_change(self, event):
        #find the cokpit not mode associated to the text
        selected_mode = next(mode for mode in cockpitNotesModes.keys()
                           if cockpitNotesModes[mode] == self.cokpitNote_dropdown.get())
        update_config_param("cockpitNotesMode", selected_mode)
        self.cokpitNote_dropdown.selection_clear()
        self.emit_collections_change()

    def lock_actions(self):
        self.cokpitNote_dropdown.configure(state="disabled")
        self.toggle_applyCensorship_button.configure(state="disabled")
        self.toggle_removeSkins_button.configure(state="disabled")
        for path_label in self.path_labels.values():
            path_label.unbind("<Button-1>")

    def unlock_actions(self):
        self.cokpitNote_dropdown.configure(state="readonly")
        self.toggle_applyCensorship_button.configure(state="enabled")
        self.toggle_removeSkins_button.configure(state="enabled")
        # Click event configuration
        for game, path_label in self.path_labels.items():
            path_label.bind("<Button-1>", lambda e, g=game: self.modify_path(g))