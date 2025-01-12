import json
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
import os 
from pythonServices.filesService import getIconPath, getRessourcePath

from pythonServices.subscriptionService import getSubcriptionNameFromFileName, getSubscribeCollectionFromRawJson, saveSubscriptionFile
from pythonServices.remoteService import getSkinsCatalogFromSource
from ISSScanner import getSkinsFromSourceMatchingWithSubscribedCollections
from GUI.Components.clickableIcon import CliquableIcon

import tkinter as tk
from tkinter import ttk

class ISSFileEditorWindow:
    def __init__(self, parent: tk.Tk, on_close, iss_file_name=None):
        self.runningTask = None
        self.editting_item_id = None
        self.on_close = on_close

        # Create a Toplevel window
        self.window = tk.Toplevel(parent)
        self.window.title("ISS file editor")
        self.window.iconbitmap(getRessourcePath("iss.ico"))
        self.window.geometry("1500x800")

        style = ttk.Style()
        style.configure("Treeview", font=("Helvetica", 8))
        style.configure("Bundle.TFrame", background="#FFFFE0")
        style.configure("Bundle.TLabel", background="#FFFFE0")

        # Create main horizontal container
        main_container = ttk.Frame(self.window)
        main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Configure grid weights for the main container
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_columnconfigure(2, weight=1)

        # 1. Plane Selection Panel (Left)
        frame_planes = ttk.LabelFrame(main_container, text="Skins in the collection", padding=10)
        frame_planes.grid(row=0, column=0, sticky="nsew", padx=5)

        self.tree_selected_planes = ttk.Treeview(frame_planes, columns=("plane","IL2Group","SkinPack"), show="headings", height=30)
        self.tree_selected_planes.pack(fill="both", expand=True, padx=5, pady=5)

        self.tree_selected_planes.heading("plane", text="Title", anchor="w")
        self.tree_selected_planes.heading("IL2Group", text="IL2Group", anchor="w")
        self.tree_selected_planes.heading("SkinPack", text="SkinPack", anchor="w")

        #set colomn widths
        self.tree_selected_planes.column("plane", width=300, minwidth=200)  # Colonne Title plus large
        self.tree_selected_planes.column("IL2Group", width=150, minwidth=100)  # Colonne IL2Group moyenne
        self.tree_selected_planes.column("SkinPack", width=200, minwidth=150)  # Colonne SkinPack moyenne

        # 2. Criteria Panel (Middle)
        frame_criteria = ttk.LabelFrame(main_container, text="Collection Bundles", padding=10)
        frame_criteria.grid(row=0, column=1, sticky="nsew", padx=5)

        self.criteria_list_frame = ttk.Frame(frame_criteria)
        self.criteria_list_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(self.criteria_list_frame)
        scrollbar = ttk.Scrollbar(self.criteria_list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Packing des widgets
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame = scrollable_frame
        self.criteria_count = 0

        # 3. Explorer Panel (Right)
        frame_explorer = ttk.LabelFrame(main_container, text="HSD skins explorer", padding=10)
        frame_explorer.grid(row=0, column=2, sticky="nsew", padx=5)

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

        button_add_criteria = ttk.Button(frame_explorer_lower_panel, text="<- Add criteria to collection", style="Accent.TButton", command=self.add_criteria)
        button_add_criteria.pack()

        # Bottom controls (filename and save)
        frame_controls = ttk.Frame(self.window)
        frame_controls.pack(pady=10, fill="x", padx=10)

        button_save = ttk.Button(frame_controls, text="Save iss file", style="Accent.TButton", command=self.save_to_iss)
        button_save.pack(side=tk.RIGHT, padx=5)
        self.filename_var = tk.StringVar()
        entry_filename = ttk.Entry(frame_controls, textvariable=self.filename_var)
        if iss_file_name is not None:
            entry_filename.configure(state="disabled")
        entry_filename.pack(side=tk.RIGHT, padx=5, fill="x")
        ttk.Label(frame_controls, text="File name:").pack(side=tk.RIGHT)

        # Load existing file if editing
        self.edited_iss_fileName = iss_file_name
        if iss_file_name is not None:
            self.filename_var.set(getSubcriptionNameFromFileName(iss_file_name))
            subscriptionPath = os.path.join(os.getcwd(),"Subscriptions",iss_file_name)

            file = open(subscriptionPath, "r")
            rawJsonData = json.load(file)

            for rawSubscription in rawJsonData:
                criteria = rawSubscription.get("criteria", {})
                il2Group = criteria.get("IL2Group", "")
                skinPack = criteria.get("SkinPack", "")
                title = criteria.get("Title", "")

                self.add_criteria_to_list(il2Group=il2Group, skinPack=skinPack, title=title)

            threading.Thread(target=self.actualiseSelectedPlanes()).start()
    
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

    def add_criteria_to_list(self, il2Group="", skinPack="", title=""):
        criteria_frame = ttk.Frame(self.scrollable_frame, style="Bundle.TFrame")
        criteria_frame.pack(fill="x", padx=5, pady=5)

        criteria_frame.data = (il2Group, skinPack, title)
        criteria_frame.id = self.criteria_count
        self.criteria_count += 1
        
        label_text = ""
        if il2Group: label_text += f"IL2Group: {il2Group}\n"
        if skinPack: label_text += f"SkinPack: {skinPack}\n"
        if title: label_text += f"Title: {title}"
        
        label = ttk.Label(criteria_frame, text=label_text, style="Bundle.TLabel")
        label.pack(side="left", fill="x", expand=True)

        trashButton = CliquableIcon(
            root=criteria_frame, 
            icon_path=getIconPath("trash-can.png"),
            onClick=lambda o=criteria_frame: self.delete_bundle(o)
        )
        trashButton.pack(side=tk.BOTTOM)
        trashButton = CliquableIcon(
            root=criteria_frame, 
            icon_path=getIconPath("edit.png"),
            onClick=lambda o=criteria_frame: self.edit_bundle(o)
        )
        trashButton.pack(side=tk.BOTTOM)
        
        return criteria_frame

    def get_all_criteria(self):
        criteria = []
        for child in self.scrollable_frame.winfo_children():
            if hasattr(child, 'data'):
                criteria.append(child.data)
        return criteria

    def add_criteria(self):
        il2Group = self.entry_il2group.get()
        if len(il2Group) > 0: il2Group = "*" + il2Group.strip('*') + "*"
        
        skinPack = self.entry_skinPack.get()
        if len(skinPack) > 0: skinPack = "*" + skinPack.strip('*') + "*"
        
        title = self.entry_title.get()
        if len(title) > 0: title = "*" + title.strip('*') + "*"
        
        if title or il2Group or skinPack:
            if self.editting_item_id is None:
                self.add_criteria_to_list(il2Group, skinPack, title)
            else:
                for child in self.scrollable_frame.winfo_children():
                    if hasattr(child, 'id') and child.id == self.editting_item_id:
                        child.destroy()
                        self.add_criteria_to_list(il2Group, skinPack, title)
                self.editting_item_id = None
        
        threading.Thread(target=self.actualiseSelectedPlanes).start()

    def delete_bundle(self, bundle):
        for child in self.scrollable_frame.winfo_children():
            if hasattr(child, 'id') and child.id == bundle.id:
                child.destroy()
        self.criteria_count -= 1
        threading.Thread(target=self.actualiseSelectedPlanes).start()
    
    def edit_bundle(self, bundle):
        self.il2group_var.set(bundle.data[0])
        self.skinPack_var.set(bundle.data[1])
        self.title_var.set(bundle.data[2])
        self.editting_item_id = bundle.id
    
    def actualiseSelectedPlanes(self):
        criteria_list = self.get_all_criteria()
        rawjson = criteria_to_json(criteria_list)
        collections = getSubscribeCollectionFromRawJson(rawjson, "test")
        skins = getSkinsFromSourceMatchingWithSubscribedCollections("HSD", collections)
        
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

        # Convert treeview data to JSON and save to file
        data = criteria_to_json(self.get_all_criteria())  # Ensure this method returns the desired data as a dictionary or list
        try:
            saveSubscriptionFile(self.edited_iss_fileName, json_content=data)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the file: {str(e)}")
            return
                
        threading.Thread(target=self.close_async()).start()


    def close_async(self):
        time.sleep(0.5)
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

def criteria_to_json(criteria_list):
    result = []
    for criteria in criteria_list:
        il2Group, skinPack, title = criteria
        entry = {"source": "HSD", "criteria": {}}
        if il2Group:
            entry["criteria"]["IL2Group"] = il2Group
        if skinPack:
            entry["criteria"]["SkinPack"] = skinPack
        if title:
            entry["criteria"]["Title"] = title
        result.append(entry)
    return json.dumps(result)