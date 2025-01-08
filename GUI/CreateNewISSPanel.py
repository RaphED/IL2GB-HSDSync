from enum import Enum
import json
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
from pythonServices import localService 
from pythonServices.messageBrocker import MessageBrocker

from pythonServices.subscriptionService import getAllSubscribedCollectionByFileName, getSubscribeCollectionFromRawJson
from pythonServices.remoteService import getSkinsCatalogFromSource, getSpaceUsageOfRemoteSkinCatalog, RemoteSkin
from ISSScanner import getSkinsFromSourceMatchingWithSubscribedCollections, bytesToString

import tkinter as tk
from tkinter import ttk

class CreateNewISSPanel:
    def actualise_dynamic_planes(self):      
        il2Group = self.entry_il2group.get()
        skinPack = self.entry_skinPack.get()
        title = self.entry_title.get()
        comment = self.entry_comment.get()

        rawjson=element_to_json(comment, il2Group, skinPack, title)
        collections= getSubscribeCollectionFromRawJson(rawjson,"test")
        skins=getSkinsFromSourceMatchingWithSubscribedCollections("HSD", collections)
        
        # Add these slins to the view below so the user can see the implied skins
        self.tree_creating_criterias.delete(*self.tree_creating_criterias.get_children())

        for skin in skins:
            self.tree_creating_criterias.insert("", "end", values=(skin.getValue("name"),))
        print("We passed in the entire function so it didn't really destroy")
        self.runningTask=None

    def update_dynamic_list(self, *args):
        if self.runningTask:
            self.runningTask.stop()
            
        self.runningTask=threading.Thread(target=self.actualise_dynamic_planes()).start()

    def __init__(self, parent: tk.Tk,on_close,variable=None):
        self.runningTask=None
       

        self.editting_item_id=None

        self.on_close = on_close

        # Create a Toplevel window
        self.window = tk.Toplevel(parent)
        self.window.title("Create New ISS Subscription")
        self.window.geometry("1400x1200")

        # Call on_close when the window is closed

        # Top Inputs in a LabelFrame
        frame_inputs = ttk.LabelFrame(self.window, text="Filters/ Criterias :", padding=10)
        frame_inputs.pack(fill="x", padx=10, pady=5)
        
        frame_queries = ttk.Frame(frame_inputs, padding=5)
        frame_queries.grid(row=0, column=0, padx=5, pady=5)

     
        self.il2group_var = tk.StringVar()
        ttk.Label(frame_queries, text="il2Group:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_il2group = ttk.Entry(frame_queries, textvariable=self.il2group_var,width=20,)
        self.entry_il2group.grid(row=0, column=1, padx=5, pady=5)
        
        self.skinPack_var = tk.StringVar()
        ttk.Label(frame_queries, text="SkinPack").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.entry_skinPack = ttk.Entry(frame_queries,textvariable=self.skinPack_var, width=20)
        self.entry_skinPack.grid(row=0, column=3, padx=5, pady=5)        
        
        self.title_var = tk.StringVar()
        ttk.Label(frame_queries, text="Title").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.entry_title = ttk.Entry(frame_queries, textvariable=self.title_var, width=20)
        self.entry_title.grid(row=0, column=5, padx=5, pady=5)


        #Adding listening to input change       
        self.title_var.trace_add("write", self.update_dynamic_list)
        self.skinPack_var.trace_add("write", self.update_dynamic_list)
        self.il2group_var.trace_add("write", self.update_dynamic_list)


        #Planes of the current filters
        self.tree_creating_criterias = ttk.Treeview(frame_inputs, columns=("plane"), show="headings", height=10)
        self.tree_creating_criterias.grid(row=1, column=0, padx=5, pady=5)

        self.tree_creating_criterias.heading("plane", text="Planes matching live query")
        for plane in getSkinsCatalogFromSource("HSD"):
            self.tree_creating_criterias.insert("", "end", values=(plane.infos["Title"],))




        # Buttons and comment to add it
        frame_comment_and_button = ttk.Frame(frame_inputs, padding=5)
        frame_comment_and_button.grid(row=2,padx=5, pady=5)
        

        self.comment_var=tk.StringVar()
        ttk.Label(frame_comment_and_button, text="Comments :").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_comment = ttk.Entry(frame_comment_and_button,textvariable=self.comment_var, width=40)
        self.entry_comment.grid(row=0, column=1, padx=5, pady=5)


        button_add_param = ttk.Button(frame_comment_and_button, text="Save criterias", style="Accent.TButton", command=self.add_parameter)
        button_add_param.grid(row=0, column=3, columnspan=2, pady=5)


        # Treeview for Parameters in a LabelFrame
        frame_params = ttk.LabelFrame(self.window, text="Existing Parameters", padding=10)
        frame_params.pack(fill="x", padx=10, pady=5)

        columns = ("comment", "il2Group", "skinPack", "title")
        self.tree_params = ttk.Treeview(frame_params, columns=columns, show="headings")
        self.tree_params.pack(side="left", fill="x", expand=True)

        # Configure columns
        for col in columns:
            self.tree_params.column(col, width=150, anchor="center")  # Center text in column
            self.tree_params.heading(col, text=col.capitalize(), anchor="center")  # Left-align text in header

        button_delete_param = ttk.Button(frame_params, text="Delete", command=self.delete_parameter)
        button_delete_param.pack(side="right", padx=5)

        button_edit_param = ttk.Button(frame_params, text="Edit", command=self.edit_parameter)
        button_edit_param.pack(side="right", padx=5)
        # Plane Selection in a LabelFrame
        frame_planes = ttk.LabelFrame(self.window, text="Resulting plane list", padding=10)
        frame_planes.pack(fill="both", expand=True, padx=10, pady=5)

        

        self.tree_selected_planes = ttk.Treeview(frame_planes, columns=("plane"), show="headings", height=10)
        self.tree_selected_planes.grid(row=0, column=2, padx=5, pady=5)

        self.tree_selected_planes.heading("plane", text="Selected Planes")

        # Save button
        frame_controls = ttk.Frame(self.window)
        frame_controls.pack(pady=10, fill="both",side="bottom")

        # Label
        label_title = ttk.Label(frame_controls, text="File name:")
        label_title.grid(row=0, column=0, padx=5, pady=5)

        # Entry field
        self.filename_var=tk.StringVar()
        entry_filename = ttk.Entry(frame_controls, textvariable=self.filename_var)
        entry_filename.grid(row=0, column=1, padx=5, pady=5)

        # Button
        button_save = ttk.Button(frame_controls, text="Save to .ISS", style="Accent.TButton", command=self.save_to_iss)
        button_save.grid(row=0, column=2, padx=5, pady=5)
        # Populate sample planes

        self.variable=variable
        if variable!=None:
            self.filename_var.set(variable)
            subscriptionPath = os.path.join(os.getcwd(),"Subscriptions",variable)

            file = open(subscriptionPath, "r")
            rawJsonData = json.load(file)

            for rawSubscription in rawJsonData:
                criteria = rawSubscription.get("criteria", {})
                comment =  rawSubscription.get("comment", "")
                il2Group = criteria.get("IL2Group", "")
                skinPack = criteria.get("SkinPack", "")
                title = criteria.get("Title", "")

                self.tree_params.insert("", "end", values=(comment, il2Group, skinPack, title))

            threading.Thread(target=self.actualiseSelectedPlanes()).start()
    

    def add_parameter(self):
        comment = self.entry_comment.get()
        il2Group = self.entry_il2group.get()
        skinPack = self.entry_skinPack.get()
        title = self.entry_title.get()

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
            self.tree_selected_planes.insert("", "end", values=(skin.getValue("name"),))


    def save_to_iss(self):
        # Ensure the Subscriptions folder exists
        subscriptionPath = os.path.join(os.getcwd(), "Subscriptions")
        if not os.path.exists(subscriptionPath):
            messagebox.showwarning("Error : folder subscription not found !")
        
        # Get the filename
        filename = self.filename_var.get()
        if not filename.endswith(".iss"):
            filename += ".iss"
        file_path = os.path.join(subscriptionPath, filename)

        # Check if file already exists
        if os.path.exists(file_path) and self.variable!=filename:
            messagebox.showwarning("File Exists", f"The file '{filename}' already exists in the Subscriptions folder.")
            return

        # Convert treeview data to JSON and save to file
        data = treeview_to_json(self.tree_params)  # Ensure this method returns the desired data as a dictionary or list
        try:
            with open(file_path, "w") as json_file:
                json_file.write(data)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the file: {str(e)}")
                
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
