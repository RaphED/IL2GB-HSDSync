import tkinter as tk
from tkinter import messagebox, ttk
import threading

from Services.remoteService import getRemoteCockpitNotesPacksCatalog, RemoteCockpitNotesPack
from Services.configurationService import getCockpitNotesPacks
from Services.filesService import getRessourcePath
from GUI.customTheme import apply_titlebar_color


class CockpitNotesPacksDialog:
    """Selection of the HSD cockpit notes packs to synchronize, by priority order"""

    def __init__(self, parent=None, title="Cockpit notes packs"):
        self.result = None
        self.dialog = tk.Toplevel(parent) if parent else tk.Tk()
        self.dialog.title(title)
        self.dialog.geometry("800x600")
        self.dialog.resizable(True, True)

        # Set window icon
        try:
            self.dialog.iconbitmap(getRessourcePath("hsd.ico"))
        except:
            pass  # Ignore if icon file not found

        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.catalog: list[RemoteCockpitNotesPack] = []
        # selected packs, by priority order: {"id", "title"} as stored in the configuration
        self.selected_packs: list[dict] = [dict(pack) for pack in getCockpitNotesPacks()]

        self.setup_ui()
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)

        # Apply dark titlebar
        apply_titlebar_color(self.dialog)

        self.populate_selected_tree()
        self.load_catalog()

    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # AVAILABLE PACKS
        ttk.Label(main_frame, text="Available packs (double-click to add):").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        filter_frame = ttk.Frame(main_frame)
        filter_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_entry = ttk.Entry(filter_frame, width=50)
        self.filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.filter_entry.bind('<KeyRelease>', lambda e: self.populate_catalog_tree())

        catalog_frame = ttk.Frame(main_frame)
        catalog_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        catalog_scrollbar = ttk.Scrollbar(catalog_frame)
        catalog_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.catalog_tree = ttk.Treeview(catalog_frame, columns=('title', 'creator', 'notes', 'size'),
                                         show='headings', selectmode='extended',
                                         yscrollcommand=catalog_scrollbar.set)
        self.catalog_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        catalog_scrollbar.config(command=self.catalog_tree.yview)
        self.catalog_tree.bind('<Double-Button-1>', lambda e: self.add_selected())
        self.setup_pack_columns(self.catalog_tree)

        catalog_actions = ttk.Frame(main_frame)
        catalog_actions.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.progress = ttk.Progressbar(catalog_actions, mode='indeterminate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.status_label = ttk.Label(catalog_actions, text="Loading packs...")
        self.status_label.pack(side=tk.LEFT, padx=(5, 0))
        self.add_btn = ttk.Button(catalog_actions, text="Add selected ↓", command=self.add_selected, state='disabled')
        self.add_btn.pack(side=tk.RIGHT)

        # SELECTED PACKS
        ttk.Label(main_frame, text="Synchronized packs, by priority: for each aircraft, the note of the first pack providing one is installed").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))

        selected_frame = ttk.Frame(main_frame)
        selected_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.selected_tree = ttk.Treeview(selected_frame, columns=('title', 'creator', 'notes', 'size'),
                                          show='headings', selectmode='browse', height=5)
        self.selected_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.setup_pack_columns(self.selected_tree)

        order_buttons = ttk.Frame(selected_frame)
        order_buttons.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        ttk.Button(order_buttons, text="Up", command=lambda: self.move_selected(-1)).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(order_buttons, text="Down", command=lambda: self.move_selected(1)).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(order_buttons, text="Remove", command=self.remove_selected).pack(fill=tk.X)

        # VALIDATION
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, sticky=(tk.W, tk.E))
        ttk.Button(button_frame, text="Save", command=self.on_validate).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.RIGHT)

        # Configure resizing
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=3)
        main_frame.rowconfigure(5, weight=1)
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)

    def setup_pack_columns(self, tree: ttk.Treeview):
        tree.column('title', width=300, anchor=tk.W)
        tree.column('creator', width=150, anchor=tk.W)
        tree.column('notes', width=80, anchor=tk.CENTER)
        tree.column('size', width=100, anchor=tk.E)
        tree.heading('title', text='Title', anchor=tk.W)
        tree.heading('creator', text='Creator', anchor=tk.W)
        tree.heading('notes', text='Notes', anchor=tk.CENTER)
        tree.heading('size', text='Size', anchor=tk.E)

    def format_size(self, size_in_bytes):
        """Format size in bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_in_bytes < 1024.0:
                return f"{size_in_bytes:.1f} {unit}"
            size_in_bytes /= 1024.0
        return f"{size_in_bytes:.1f} TB"

    def pack_values(self, pack: RemoteCockpitNotesPack):
        return (pack.title(), pack.creator_name(), pack.notes_count(), self.format_size(pack.size_in_b()))

    # CATALOG

    def load_catalog(self):
        self.progress.start()
        thread = threading.Thread(target=self.load_catalog_thread)
        thread.daemon = True
        thread.start()

    def load_catalog_thread(self):
        """Thread to load the catalog without blocking interface"""
        try:
            catalog = getRemoteCockpitNotesPacksCatalog()
            self.dialog.after(0, self.on_catalog_loaded, catalog, None)
        except Exception as e:
            self.dialog.after(0, self.on_catalog_loaded, None, str(e))

    def on_catalog_loaded(self, catalog, error):
        self.progress.stop()
        self.progress.pack_forget()

        if error:
            self.status_label.config(text=f"Error loading packs: {error}")
            messagebox.showerror("Error", f"Failed to load cockpit notes packs:\n{error}")
            return

        self.catalog = sorted(catalog, key=lambda pack: pack.title().lower())
        self.status_label.config(text=f"{len(self.catalog)} pack(s) available")
        self.add_btn.config(state='normal')
        self.populate_catalog_tree()
        # the details of the selected packs (creator, notes...) come from the catalog
        self.populate_selected_tree()
        self.filter_entry.focus_set()

    def populate_catalog_tree(self):
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)
        text_filter = self.filter_entry.get().lower()
        for pack in self.catalog:
            if text_filter and text_filter not in pack.title().lower() and text_filter not in pack.creator_name().lower():
                continue
            self.catalog_tree.insert('', tk.END, iid=str(pack.id()), values=self.pack_values(pack))

    # SELECTED PACKS

    def get_catalog_pack(self, pack_id) -> RemoteCockpitNotesPack | None:
        return next((pack for pack in self.catalog if pack.id() == pack_id), None)

    def populate_selected_tree(self, selected_id=None):
        for item in self.selected_tree.get_children():
            self.selected_tree.delete(item)
        for selected_pack in self.selected_packs:
            pack = self.get_catalog_pack(selected_pack["id"])
            if pack is not None:
                values = self.pack_values(pack)
            elif self.catalog:
                values = (f"{selected_pack['title']} (no longer available)", "", "", "")
            else:
                # catalog not loaded (yet)
                values = (selected_pack["title"], "", "", "")
            self.selected_tree.insert('', tk.END, iid=str(selected_pack["id"]), values=values)
        if selected_id is not None:
            self.selected_tree.selection_set(str(selected_id))

    def add_selected(self):
        selected_ids = [selected_pack["id"] for selected_pack in self.selected_packs]
        for item_id in self.catalog_tree.selection():
            pack = self.get_catalog_pack(int(item_id))
            if pack is not None and pack.id() not in selected_ids:
                self.selected_packs.append({"id": pack.id(), "title": pack.title()})
                selected_ids.append(pack.id())
        self.populate_selected_tree()

    def get_selected_index(self) -> int:
        selection = self.selected_tree.selection()
        if not selection:
            return -1
        return next(index for index, pack in enumerate(self.selected_packs) if str(pack["id"]) == selection[0])

    def move_selected(self, offset: int):
        index = self.get_selected_index()
        new_index = index + offset
        if index == -1 or new_index < 0 or new_index >= len(self.selected_packs):
            return
        pack = self.selected_packs.pop(index)
        self.selected_packs.insert(new_index, pack)
        self.populate_selected_tree(selected_id=pack["id"])

    def remove_selected(self):
        index = self.get_selected_index()
        if index == -1:
            return
        self.selected_packs.pop(index)
        self.populate_selected_tree()

    # VALIDATION

    def on_validate(self):
        self.result = self.selected_packs
        self.dialog.destroy()

    def on_cancel(self):
        self.result = None
        self.dialog.destroy()

    def show(self):
        """Show dialog and return the selected packs (None if cancelled)"""
        self.dialog.wait_window()
        return self.result


def ask_cockpit_notes_packs(parent=None):
    """Display the cockpit notes packs selection: returns the selected packs by priority order, or None if cancelled"""
    return CockpitNotesPacksDialog(parent).show()
