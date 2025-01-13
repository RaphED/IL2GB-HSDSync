import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pythonServices.filesService import getIconPath, getRessourcePath

from pythonServices.subscriptionService import SubscribedCollection, getSubcriptionNameFromFileName, getSubscribeCollectionFromRawJson, getSubcriptionFilePathFromFileName, getSubscribedCollectionFromFilePath, saveSubscriptionFile
from pythonServices.remoteService import getSkinsCatalogFromSource
from ISSScanner import getSkinsFromSourceMatchingWithSubscribedCollections
from GUI.Components.clickableIcon import CliquableIcon

import tkinter as tk
from tkinter import ttk

class ISSFileEditorWindow:
    def __init__(self, root: tk.Tk, on_close, iss_file_name=None):
        self.root = root
        self.runningTask = None
        self.editting_collection_index = None
        self.on_close = on_close

        # Create a Toplevel window
        self.window = tk.Toplevel(self.root)
        self.window.title("ISS file editor")
        self.window.iconbitmap(getRessourcePath("iss.ico"))
        self.window.geometry("1500x800")

        style = ttk.Style()
        style.configure("Treeview", font=("Helvetica", 8))
        style.configure("Bundle.TFrame", background="#FFFFE0")
        style.configure("Bundle.TLabel", background="#FFFFE0")

        # Bottom controls (filename and save)
        frame_controls = ttk.Frame(self.window)
        frame_controls.pack(pady=10, fill="x", padx=10)

        ttk.Label(frame_controls, text="File name:").pack(side=tk.LEFT)
        self.filename_var = tk.StringVar()
        entry_filename = ttk.Entry(frame_controls, textvariable=self.filename_var)
        if iss_file_name is not None:
            entry_filename.configure(state="disabled")
        entry_filename.pack(side=tk.LEFT, padx=5, fill="x")
        button_save = ttk.Button(frame_controls, text="Save iss file", style="Accent.TButton", command=self.save_to_iss)
        button_save.pack(side=tk.LEFT, padx=5)

        # Create main horizontal container
        main_container = ttk.Frame(self.window)
        main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Configure grid weights for the main container
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_columnconfigure(2, weight=1)

        # 1. Catalog Explorer Panel (left)
        frame_explorer = ttk.LabelFrame(main_container, text="HSD skins explorer", padding=10)
        frame_explorer.grid(row=0, column=0, sticky="nsew", padx=5)

        # Queries frame
        frame_queries = ttk.Frame(frame_explorer)
        frame_queries.pack(fill="x", pady=5)

        # Title
        ttk.Label(frame_queries, text="Title").pack(anchor="w")
        self.title_var = tk.StringVar()
        self.entry_title = ttk.Entry(frame_queries, textvariable=self.title_var)
        self.entry_title.pack(fill="x", pady=2)

        # IL2Group
        ttk.Label(frame_queries, text="il2Group:").pack(anchor="w", pady=(10,0))
        self.il2group_var = tk.StringVar()
        self.entry_il2group = ttk.Entry(frame_queries, textvariable=self.il2group_var)
        self.entry_il2group.pack(fill="x", pady=2)

        # SkinPack
        ttk.Label(frame_queries, text="SkinPack").pack(anchor="w", pady=(10,0))
        self.skinPack_var = tk.StringVar()
        self.entry_skinPack = ttk.Entry(frame_queries, textvariable=self.skinPack_var)
        self.entry_skinPack.pack(fill="x", pady=2)

        self.title_var.trace_add("write", self.update_dynamic_list)
        self.skinPack_var.trace_add("write", self.update_dynamic_list)
        self.il2group_var.trace_add("write", self.update_dynamic_list)

        # Dynamic criteria tree
        self.tree_skin_explorer = ttk.Treeview(frame_explorer, columns=("plane","IL2Group","SkinPack"), show="headings", height=15)
        self.tree_skin_explorer.pack(fill="both", expand=True, pady=10)

        self.tree_skin_explorer.heading("plane", text="Title", anchor="w")
        self.tree_skin_explorer.heading("IL2Group", text="IL2Group", anchor="w")
        self.tree_skin_explorer.heading("SkinPack", text="SkinPack", anchor="w")

        self.tree_skin_explorer.column("plane", width=200, minwidth=200)  # Colonne Title plus large
        self.tree_skin_explorer.column("IL2Group", width=150, minwidth=150)  # Colonne IL2Group moyenne
        self.tree_skin_explorer.column("SkinPack", width=200, minwidth=150)  # Colonne SkinPack moyenne

        self.tree_skin_explorer.bind('<Double-1>', self.on_double_click_tree_skins_explorer)

        for plane in getSkinsCatalogFromSource("HSD"):
            self.tree_skin_explorer.insert("", "end", values=(plane.infos["Title"],plane.infos["IL2Group"],plane.infos["SkinPack"]))

        # Send to criteria panel
        frame_explorer_lower_panel = ttk.Frame(frame_explorer)
        frame_explorer_lower_panel.pack(fill="x", pady=10)

        button_add_bundle = ttk.Button(frame_explorer_lower_panel, text="Add these skins in a new bundle", style="Accent.TButton", command=self.add_SubcribeCollectionFromFilters)
        button_add_bundle.pack()

        # 2. Collection Bundle Panel (Middle)
        frame_criteria = ttk.LabelFrame(main_container, text="Collection Bundles", padding=10)
        frame_criteria.grid(row=0, column=1, sticky="nsew", padx=5)

        self.criteria_list_frame = ttk.Frame(frame_criteria)
        self.criteria_list_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(self.criteria_list_frame)
        scrollbar = ttk.Scrollbar(self.criteria_list_frame, orient="vertical", command=canvas.yview)
        self.frame_collection_bundle = ttk.Frame(canvas)

        self.frame_collection_bundle.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.frame_collection_bundle, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Packing des widgets
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # 3. Collection content
        frame_planes = ttk.LabelFrame(main_container, text="Skins in the collection", padding=10)
        frame_planes.grid(row=0, column=2, sticky="nsew", padx=5)

        self.tree_selected_planes = ttk.Treeview(frame_planes, columns=("plane","IL2Group","SkinPack"), show="headings", height=30)
        self.tree_selected_planes.pack(fill="both", expand=True, padx=5, pady=5)

        self.tree_selected_planes.heading("plane", text="Title", anchor="w")
        self.tree_selected_planes.heading("IL2Group", text="IL2Group", anchor="w")
        self.tree_selected_planes.heading("SkinPack", text="SkinPack", anchor="w")

        #set colomn widths
        self.tree_selected_planes.column("plane", width=300, minwidth=200)  # Colonne Title plus large
        self.tree_selected_planes.column("IL2Group", width=150, minwidth=100)  # Colonne IL2Group moyenne
        self.tree_selected_planes.column("SkinPack", width=200, minwidth=150)  # Colonne SkinPack moyenne       

        #the description of the collection content
        self.subscribedCollection = []
        
        # Load existing file if editing
        self.edited_iss_fileName = iss_file_name
        if self.edited_iss_fileName is not None:
            self.filename_var.set(getSubcriptionNameFromFileName(self.edited_iss_fileName))
            self.subscribedCollection = getSubscribedCollectionFromFilePath(getSubcriptionFilePathFromFileName(self.edited_iss_fileName))
            self.update_bundle_list()
    
    def actualise_dynamic_planes(self):
        il2Group = self.entry_il2group.get()
        if len(il2Group)>0 : il2Group="*"+il2Group.strip('*')+"*"
        
        skinPack = self.entry_skinPack.get()
        if len(skinPack)>0 : skinPack="*"+skinPack.strip('*')+"*"

        title = self.entry_title.get()
        if len(title)>0 : title="*"+title.strip('*')+"*"

        rawjson=element_to_json(il2Group, skinPack, title)
        collections= getSubscribeCollectionFromRawJson(rawjson,"test")
        skins=getSkinsFromSourceMatchingWithSubscribedCollections("HSD", collections)
        
        # Add these slins to the view below so the user can see the implied skins
        self.tree_skin_explorer.delete(*self.tree_skin_explorer.get_children())

        for skin in skins:
            self.tree_skin_explorer.insert("", "end", values=(skin.getValue("name"),skin.infos["IL2Group"],skin.infos["SkinPack"]))
        self.runningTask=None

    def update_dynamic_list(self, *args):
        if self.runningTask:
            self.runningTask.stop()
            
        self.runningTask=threading.Thread(target=self.actualise_dynamic_planes()).start()

    def on_double_click_tree_skins_explorer(self, event):
        # Get the selected item
        selected_item = self.tree_skin_explorer.selection()
        if not selected_item:
            return
        
        # Get values from the selected row
        values = self.tree_skin_explorer.item(selected_item[0])["values"]
        
        # Update the entry fields
        self.title_var.set(values[0])  # Title
        self.il2group_var.set(values[1])  # IL2Group
        self.skinPack_var.set(values[2])  # SkinPack

    def update_bundle_list(self):
        #clear the list
        for child in self.frame_collection_bundle.winfo_children():
            child.destroy()

        for index, collection in enumerate(self.subscribedCollection):

            criteria_frame = ttk.Frame(self.frame_collection_bundle, style="Bundle.TFrame")
            criteria_frame.pack(fill="x", padx=5, pady=5)

            il2Group=collection.criteria.get("IL2Group", ""),
            skinPack=collection.criteria.get("SkinPack", "")
            title=collection.criteria.get("Title", "")
            
            label_text = ""
            if il2Group: label_text += f"IL2Group: {il2Group}\n"
            if skinPack: label_text += f"SkinPack: {skinPack}\n"
            if title: label_text += f"Title: {title}"
            
            label = ttk.Label(criteria_frame, text=label_text, style="Bundle.TLabel")
            label.pack(side="left", fill="x", expand=True)

            trashButton = CliquableIcon(
                root=criteria_frame, 
                icon_path=getIconPath("trash-can.png"),
                onClick=lambda i=index: self.remove_SubcribeCollection(i) #use the index of the collection
            )
            trashButton.pack(side=tk.BOTTOM)
            trashButton = CliquableIcon(
                root=criteria_frame, 
                icon_path=getIconPath("edit.png"),
                onClick=lambda i=index: self.edit_SubcribeCollection(i) #use the index of the collection
            )
            trashButton.pack(side=tk.BOTTOM)

        self.root.after(0, self.actualise_subscription_skins)
    
    def add_SubcribeCollectionFromFilters(self):
        
        newCollection = SubscribedCollection(
            source="HSD",
            subcriptionName="",
            criteria= dict[str,str]()
        )
        il2Group = self.entry_il2group.get()
        if len(il2Group) > 0:
            newCollection.criteria["IL2Group"] = "*" + il2Group.strip('*') + "*"
        skinPack = self.entry_skinPack.get()
        if len(skinPack) > 0:
            newCollection.criteria["SkinPack"] = "*" + skinPack.strip('*') + "*"
        title = self.entry_title.get()
        if len(il2Group) > 0:
            newCollection.criteria["Title"] = "*" + title.strip('*') + "*"

        #do not add anything if no criteria
        if not title and not il2Group and not skinPack:
            messagebox.showerror("Cannot add bundle", "You cannot add an empty bundle")
            return

        self.subscribedCollection.append(newCollection)

        self.root.after(0, self.update_bundle_list)

    def remove_SubcribeCollection(self, collection_index):
        self.subscribedCollection.pop(collection_index)
        self.root.after(0, self.update_bundle_list)
    
    def edit_SubcribeCollection(self, collection_index):
        self.il2group_var.set(self.subscribedCollection[collection_index].criteria["IL2Group"])
        self.skinPack_var.set(self.subscribedCollection[collection_index].criteria["SkinPack"])
        self.title_var.set(self.subscribedCollection[collection_index].criteria["Title"])
        self.editting_collection_index = collection_index
    
    def actualise_subscription_skins(self):
        skins = getSkinsFromSourceMatchingWithSubscribedCollections("HSD", self.subscribedCollection)
        
        self.tree_selected_planes.delete(*self.tree_selected_planes.get_children())
        
        for skin in skins:
            self.tree_selected_planes.insert("", "end", values=(skin.getValue("name"), skin.infos["IL2Group"], skin.infos["SkinPack"]))


    def save_to_iss(self):
        
        #generate the file name if we are in creation mode
        if self.edited_iss_fileName is None:
            self.edited_iss_fileName = self.filename_var.get() + ".iss"
        
        if self.filename_var.get() == "":
            messagebox.showerror("Collection name is required", "Please set a collection name before saving your file")
            return

        try:
            saveSubscriptionFile(self.edited_iss_fileName, subscribedCollections=self.subscribedCollection)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the file: {str(e)}")
            return

        self.root.after(500, self.close_window)

    def close_window(self):
        self.window.destroy()
        self.on_close()


def element_to_json(il2Group, skinPack, title):   
    result = []
    entry = {"source": "HSD", "criteria": {}}
    if il2Group:
        entry["criteria"]["IL2Group"] = il2Group
    if skinPack:
        entry["criteria"]["SkinPack"] = skinPack
    if title:
        entry["criteria"]["Title"] = title
    result.append(entry)
    return json.dumps(result)
