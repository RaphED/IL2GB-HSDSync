import tkinter as tk
from tkinter import ttk

from ISSScanner import bytesToString
from pythonServices.remoteService import RemoteSkin, getSpaceUsageOfRemoteSkinCatalog


class SkinsListView(ttk.Frame):
    def __init__(self, root, on_skin_double_click=None):
        super().__init__(root)
        self.root = root
        self.on_skin_double_click = on_skin_double_click

        
        style = ttk.Style()
        style.configure("Treeview", font=("Helvetica", 8))

        # Container principal qui doit s'étendre
        self.tree_frame = ttk.Frame(self)
        self.tree_frame.pack(fill="both", expand=True, pady=0)

        # Créer le treeview
        self.tree_skins = ttk.Treeview(self.tree_frame, columns=("plane","IL2Group","SkinPack"), 
                                  show="headings", height=15)
    
        # Créer la scrollbar
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree_skins.yview)
    
        # Configurer le treeview pour utiliser la scrollbar
        self.tree_skins.configure(yscrollcommand=self.scrollbar.set)
    
        # Placer les éléments avec la bonne géométrie
        self.scrollbar.pack(side="right", fill="y")
        self.tree_skins.pack(side="left", fill="both", expand=True)

        self.tree_skins.heading("plane", text="Title", anchor="w")
        self.tree_skins.heading("IL2Group", text="IL2Group", anchor="w")
        self.tree_skins.heading("SkinPack", text="SkinPack", anchor="w")

        self.tree_skins.column("plane", width=200, minwidth=200)  # Colonne Title plus large
        self.tree_skins.column("IL2Group", width=150, minwidth=150)  # Colonne IL2Group moyenne
        self.tree_skins.column("SkinPack", width=150, minwidth=150)  # Colonne SkinPack moyenne

        self.tree_skins.bind('<Double-1>', self.emit_double_click_on_collection)

        lower_panel = ttk.Frame(self)
        lower_panel.pack(fill="x", pady=5)

        self.skins_count_label = ttk.Label(lower_panel)
        self.skins_count_label.pack(side=tk.LEFT, padx=10)
        self.skins_size_label = ttk.Label(lower_panel)
        self.skins_size_label.pack(side=tk.LEFT, padx=10)

    def loadSkinsList(self, skins_list: list[RemoteSkin]):
        self.tree_skins.delete(*self.tree_skins.get_children())
        
        for skin in skins_list:
            self.tree_skins.insert("", "end", values=(skin.infos["Title"], skin.infos["IL2Group"], skin.infos["SkinPack"]))

        self.skins_count_label.configure(text=f"Skins count : {len(skins_list)}")
        self.skins_size_label.configure(text=f"({bytesToString(getSpaceUsageOfRemoteSkinCatalog(source="HSD", remoteSkinList=skins_list))})")

    def emit_double_click_on_collection(self, event):
        #no action if no callback
        if self.on_skin_double_click is None:
            return
        
        #no return if no element is selected
        selected_item = self.tree_skins.selection()
        if not selected_item:
            return
        
        values = self.tree_skins.item(selected_item[0])["values"]

        # Get values from the selected row
        object = {
            "Title": values[0],
            "IL2Group": values[1],
            "SkinPack": values[2]
        }

        self.root.after(0, lambda: self.on_skin_double_click(object))