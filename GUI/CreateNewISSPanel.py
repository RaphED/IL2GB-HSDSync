import json
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
import os 
from pythonServices.filesService import getRessourcePath

from pythonServices.subscriptionService import getSubcriptionNameFromFileName, getSubscribeCollectionFromRawJson, saveSubscriptionFile
from pythonServices.remoteService import getSkinsCatalogFromSource
from ISSScanner import getSkinsFromSourceMatchingWithSubscribedCollections

import tkinter as tk
from tkinter import ttk

class CreateNewISSPanel:
    def __init__(self, parent: tk.Tk, on_close, iss_file_name=None):
        self.runningTask = None
        self.editting_item_id = None
        self.on_close = on_close

        # Create a Toplevel window
        self.window = tk.Toplevel(parent)
        self.window.title("ISS file detail")
        self.window.iconbitmap(getRessourcePath("iss.ico"))
        self.window.geometry("1500x800")

        style = ttk.Style()
        style.configure("Treeview", font=("Helvetica", 8))

        # Create main horizontal container
        main_container = ttk.Frame(self.window)
        main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Configure grid weights for the main container
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_columnconfigure(2, weight=1)

        # 1. Plane Selection Panel (Left)
        frame_planes = ttk.LabelFrame(main_container, text="Resulting plane list", padding=10)
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

        # 2. Parameters Panel (Middle)
        frame_params = ttk.LabelFrame(main_container, text="Existing criterias", padding=10)
        frame_params.grid(row=0, column=1, sticky="nsew", padx=5)

        columns = ("comment", "il2Group", "skinPack", "title")
        self.tree_params = ttk.Treeview(frame_params, columns=columns, show="headings", height=25)
        self.tree_params.pack(fill="both", expand=True)

        # Add vertical scrollbar
        scrollbar = ttk.Scrollbar(frame_params, orient="vertical", command=self.tree_params.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree_params.configure(yscrollcommand=scrollbar.set)

        # Configure columns
        for col in columns:
            self.tree_params.column(col, width=100, anchor="center")
            self.tree_params.heading(col, text=col.capitalize(), anchor="center")

        button_frame = ttk.Frame(frame_params)
        button_frame.pack(fill="x", pady=5)
        
        button_delete_param = ttk.Button(button_frame, text="Delete", command=self.delete_parameter)
        button_delete_param.pack(side="right", padx=5)

        button_edit_param = ttk.Button(button_frame, text="Edit", command=self.edit_parameter)
        button_edit_param.pack(side="right", padx=5)

        # 3. Inputs Panel (Right)
        frame_inputs = ttk.LabelFrame(main_container, text="Filters/ Criterias :", padding=10)
        frame_inputs.grid(row=0, column=2, sticky="nsew", padx=5)

        # Queries frame
        frame_queries = ttk.Frame(frame_inputs)
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
        self.tree_creating_criterias = ttk.Treeview(frame_inputs, columns=("plane","IL2Group","SkinPack"), show="headings", height=15)
        self.tree_creating_criterias.pack(fill="both", expand=True, pady=10)

        self.tree_creating_criterias.heading("plane", text="Title", anchor="w")
        self.tree_creating_criterias.heading("IL2Group", text="IL2Group", anchor="w")
        self.tree_creating_criterias.heading("SkinPack", text="SkinPack", anchor="w")

        self.tree_creating_criterias.column("plane", width=200, minwidth=200)  # Colonne Title plus large
        self.tree_creating_criterias.column("IL2Group", width=150, minwidth=150)  # Colonne IL2Group moyenne
        self.tree_creating_criterias.column("SkinPack", width=200, minwidth=150)  # Colonne SkinPack moyenne

        for plane in getSkinsCatalogFromSource("HSD"):
            self.tree_creating_criterias.insert("", "end", values=(plane.infos["Title"],plane.infos["IL2Group"],plane.infos["SkinPack"]))

        # Comment and Save buttons
        frame_comment = ttk.Frame(frame_inputs)
        frame_comment.pack(fill="x", pady=10)

        self.comment_var = tk.StringVar()
        ttk.Label(frame_comment, text="Comments :").pack(side="left")
        self.entry_comment = ttk.Entry(frame_comment, textvariable=self.comment_var)
        self.entry_comment.pack(side="left", fill="x", expand=True, padx=5)

        button_add_param = ttk.Button(frame_comment, text="Save criterias", style="Accent.TButton", command=self.add_parameter)
        button_add_param.pack(side="right")

        # Bottom controls (filename and save)
        frame_controls = ttk.Frame(self.window)
        frame_controls.pack(pady=10, fill="x", padx=10)

        button_save = ttk.Button(frame_controls, text="Save to .ISS", style="Accent.TButton", command=self.save_to_iss)
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
                comment = rawSubscription.get("comment", "")
                il2Group = criteria.get("IL2Group", "")
                skinPack = criteria.get("SkinPack", "")
                title = criteria.get("Title", "")

                self.tree_params.insert("", "end", values=(comment, il2Group, skinPack, title))

            threading.Thread(target=self.actualiseSelectedPlanes()).start()
    
    def actualise_dynamic_planes(self):
        il2Group = self.entry_il2group.get()
        if len(il2Group)>0 : il2Group="*"+il2Group.strip('*')+"*"
        
        skinPack = self.entry_skinPack.get()
        if len(skinPack)>0 : skinPack="*"+skinPack.strip('*')+"*"

        title = self.entry_title.get()
        if len(title)>0 : title="*"+title.strip('*')+"*"

        comment = self.entry_comment.get()

        rawjson=element_to_json(comment, il2Group, skinPack, title)
        collections= getSubscribeCollectionFromRawJson(rawjson,"test")
        skins=getSkinsFromSourceMatchingWithSubscribedCollections("HSD", collections)
        
        # Add these slins to the view below so the user can see the implied skins
        self.tree_creating_criterias.delete(*self.tree_creating_criterias.get_children())

        for skin in skins:
            self.tree_creating_criterias.insert("", "end", values=(skin.getValue("name"),skin.infos["IL2Group"],skin.infos["SkinPack"]))
        self.runningTask=None

    def update_dynamic_list(self, *args):
        if self.runningTask:
            self.runningTask.stop()
            
        self.runningTask=threading.Thread(target=self.actualise_dynamic_planes()).start()

    def add_parameter(self):
        comment = self.entry_comment.get()
        
        il2Group = self.entry_il2group.get()
        if len(il2Group)>0 : il2Group="*"+il2Group.strip('*')+"*"
        
        skinPack = self.entry_skinPack.get()
        if len(skinPack)>0 : skinPack="*"+skinPack.strip('*')+"*"

        title = self.entry_title.get()
        if len(title)>0 : title="*"+title.strip('*')+"*"

        if title or il2Group or skinPack:
            if self.editting_item_id==None:
                self.tree_params.insert("", "end", values=(comment, il2Group, skinPack, title))
            else: 
                self.tree_params.item(self.editting_item_id, values=(comment, il2Group, skinPack, title))
                self.editting_item_id=None
        
        threading.Thread(target=self.actualiseSelectedPlanes()).start()


    def delete_parameter(self):
        selected_item = self.tree_params.selection()
        for item in selected_item:
            self.tree_params.delete(item)
        
        threading.Thread(target=self.actualiseSelectedPlanes()).start()

    
    def edit_parameter(self):
        selected_items = self.tree_params.selection()
        if len(selected_items)==1:
            for item_id in selected_items:
                item_data = self.tree_params.item(item_id)
                values = item_data["values"]
                self.editting_item_id=item_id
        self.il2group_var.set(values[1])
        self.skinPack_var.set(values[2])
        self.title_var.set(values[3])
        self.comment_var.set(values[0])


    
    def actualiseSelectedPlanes(self):
        rawjson=treeview_to_json(self.tree_params)
        collections= getSubscribeCollectionFromRawJson(rawjson,"test")
        skins=getSkinsFromSourceMatchingWithSubscribedCollections("HSD", collections)
        
        # Add these slins to the view below so the user can see the implied skins
        self.tree_selected_planes.delete(*self.tree_selected_planes.get_children())

        for skin in skins:
            self.tree_selected_planes.insert("", "end", values=(skin.getValue("name"),skin.infos["IL2Group"],skin.infos["SkinPack"]))


    def save_to_iss(self):
        
        #generate the file name if we are in creation mode
        if self.edited_iss_fileName is None:
            self.edited_iss_fileName = self.filename_var.get() + ".iss"
        
        if self.filename_var.get() == "":
            messagebox.showerror("Collection name is required", "Please set a collection name before saving your file")
            return

        # Convert treeview data to JSON and save to file
        data = treeview_to_json(self.tree_params)  # Ensure this method returns the desired data as a dictionary or list
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


def element_to_json(comment, il2Group, skinPack, title):   
    result = []
    entry = {"source": "HSD","comment": comment, "criteria": {}}
    if il2Group:
        entry["criteria"]["IL2Group"] = il2Group
    if skinPack:
        entry["criteria"]["SkinPack"] = skinPack
    if title:
        entry["criteria"]["Title"] = title
    result.append(entry)
    return json.dumps(result)

def treeview_to_json(treeview):
    rows = []
    for row_id in treeview.get_children():
        row_values = treeview.item(row_id)["values"]
        rows.append(row_values)

    result = []
    for row in rows:
        comment, il2Group, skinPack, title = row
        entry = {"source": "HSD","comment": comment, "criteria": {}}
        if il2Group:
            entry["criteria"]["IL2Group"] = il2Group
        if skinPack:
            entry["criteria"]["SkinPack"] = skinPack
        if title:
            entry["criteria"]["Title"] = title

        result.append(entry)

    return json.dumps(result)
