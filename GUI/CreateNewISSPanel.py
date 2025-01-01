from enum import Enum
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import tk_async_execute as tae
import asyncio
from pythonServices import localService
from pythonServices.messageBrocker import MessageBrocker

from pythonServices.subscriptionService import getAllSubscribedCollectionByFileName
from pythonServices.remoteService import getSpaceUsageOfRemoteSkinCatalog, RemoteSkin
from ISSScanner import getSkinsFromSourceMatchingWithSubscribedCollections, bytesToString

import tkinter as tk
from tkinter import ttk


class CreateNewISSPanel:
    def __init__(self, parent: tk.Tk, on_close):
        self.on_close = on_close

        # Create a Toplevel window
        self.window = tk.Toplevel(parent)
        self.window.title("Create New ISS Subscription")
        self.window.geometry("1200x800")

        # Call on_close when the window is closed
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Top Inputs in a LabelFrame
        frame_inputs = ttk.LabelFrame(self.window, text="Subscription Details", padding=10)
        frame_inputs.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_inputs, text="Name of subscription:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_name = ttk.Entry(frame_inputs, width=20)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_inputs, text="Keyword:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_keyword = ttk.Entry(frame_inputs, width=20)
        self.entry_keyword.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_inputs, text="Category:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.combo_category = ttk.Combobox(frame_inputs, values=["Category 1", "Category 2", "Category 3"], state="readonly")
        self.combo_category.grid(row=0, column=3, padx=5, pady=5)

        button_add_param = ttk.Button(frame_inputs, text="Add Parameter to query", command=self.add_parameter)
        button_add_param.grid(row=1, column=2, columnspan=2, pady=5)

        # Treeview for Parameters in a LabelFrame
        frame_params = ttk.LabelFrame(self.window, text="Existing Parameters", padding=10)
        frame_params.pack(fill="x", padx=10, pady=5)

        self.tree_params = ttk.Treeview(frame_params, columns=("name", "keyword", "category"), show="headings", height=5)
        self.tree_params.pack(side="left", fill="x", expand=True)

        self.tree_params.heading("name", text="Name")
        self.tree_params.heading("keyword", text="Keyword")
        self.tree_params.heading("category", text="Category")

        button_delete_param = ttk.Button(frame_params, text="Delete", command=self.delete_parameter)
        button_delete_param.pack(side="right", padx=5)

        # Plane Selection in a LabelFrame
        frame_planes = ttk.LabelFrame(self.window, text="Plane Selection", padding=10)
        frame_planes.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree_all_planes = ttk.Treeview(frame_planes, columns=("plane"), show="headings", height=10)
        self.tree_all_planes.grid(row=0, column=0, padx=5, pady=5)

        self.tree_all_planes.heading("plane", text="All Planes")

        button_add_plane = ttk.Button(frame_planes, text="Add Plane >>", command=self.add_plane)
        button_add_plane.grid(row=0, column=1, padx=5)

        self.tree_selected_planes = ttk.Treeview(frame_planes, columns=("plane"), show="headings", height=10)
        self.tree_selected_planes.grid(row=0, column=2, padx=5, pady=5)

        self.tree_selected_planes.heading("plane", text="Selected Planes")

        button_remove_plane = ttk.Button(frame_planes, text="<< Remove Plane", command=self.remove_plane)
        button_remove_plane.grid(row=1, column=1, padx=5, pady=5)

        # Save button
        button_save = ttk.Button(self.window, text="Save to .ISS", command=self.save_to_iss)
        button_save.pack(pady=10)

        # Populate sample planes
        for plane in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]:
            self.tree_all_planes.insert("", "end", values=(plane,))

    def add_parameter(self):
        name = self.entry_name.get()
        keyword = self.entry_keyword.get()
        category = self.combo_category.get()

        if name and keyword and category:
            self.tree_params.insert("", "end", values=(name, keyword, category))

    def delete_parameter(self):
        selected_item = self.tree_params.selection()
        for item in selected_item:
            self.tree_params.delete(item)

    def add_plane(self):
        selected_items = self.tree_all_planes.selection()
        for item in selected_items:
            values = self.tree_all_planes.item(item, "values")
            self.tree_selected_planes.insert("", "end", values=values)

    def remove_plane(self):
        selected_items = self.tree_selected_planes.selection()
        for item in selected_items:
            self.tree_selected_planes.delete(item)

    def save_to_iss(self):
        print("Saved!")