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


class CreateNewISSPanel:
    def __init__(self, parent: tk.Tk,on_close):
        # Create a Toplevel window
        self.window = tk.Toplevel(parent)
        self.window.title("Subscription Window")
        self.window.geometry("900x900")

        # Store the on_close callback
        self.on_close = on_close

        # Handle the closing event of the second window
        self.window.protocol("WM_DELETE_WINDOW", self._handle_close)

        def add_parameter():
            # Get input values
            name = entry_name.get()
            keyword = entry_keyword.get()
            category = combo_category.get()

            # Add to the treeview
            if name and keyword and category:
                tree_params.insert('', 'end', values=(name, keyword, category))

        def delete_parameter():
            selected_item = tree_params.selection()
            for item in selected_item:
                tree_params.delete(item)

        def add_plane():
            selected_items = tree_all_planes.selection()
            for item in selected_items:
                values = tree_all_planes.item(item, 'values')
                tree_selected_planes.insert('', 'end', values=values)

        def remove_plane():
            selected_items = tree_selected_planes.selection()
            for item in selected_items:
                tree_selected_planes.delete(item)

        # Top inputs
        frame_top = ttk.Frame(self.window)
        frame_top.pack(pady=10)

        ttk.Label(frame_top, text="Name of subscription:").grid(row=0, column=0)
        entry_name = tk.Entry(frame_top, width=20)
        entry_name.grid(row=0, column=1, padx=5)

        ttk.Label(frame_top, text="Keyword:").grid(row=1, column=0)
        entry_keyword = tk.Entry(frame_top, width=20)
        entry_keyword.grid(row=1, column=1, padx=5)

        ttk.Label(frame_top, text="Category:").grid(row=0, column=2)
        combo_category = ttk.Combobox(frame_top, values=["Category 1", "Category 2", "Category 3"], state="readonly")
        combo_category.grid(row=0, column=3, padx=5)

        button_add_param = ttk.Button(frame_top, text="Add Parameter to query", command=add_parameter)
        button_add_param.grid(row=1, column=2, columnspan=2)

        # Parameters treeview
        frame_params = ttk.Frame(self.window)
        frame_params.pack(pady=10)

        ttk.Label(frame_params, text="Existing Parameters:").pack(anchor="w")
        tree_params = ttk.Treeview(frame_params, columns=("name", "keyword", "category"), show="headings", height=5)
        tree_params.pack(side="left", fill="x")

        tree_params.heading("name", text="Name")
        tree_params.heading("keyword", text="Keyword")
        tree_params.heading("category", text="Category")

        button_delete_param = ttk.Button(frame_params, text="Delete", command=delete_parameter)
        button_delete_param.pack(side="right", padx=5)

        # Plane selection
        frame_planes = ttk.Frame(self.window)
        frame_planes.pack(pady=10)

        tree_all_planes = ttk.Treeview(frame_planes, columns=("plane"), show="headings", height=10)
        tree_all_planes.grid(row=0, column=0, padx=5)

        tree_all_planes.heading("plane", text="All Planes")

        button_add_plane = ttk.Button(frame_planes, text="Add Plane >>", command=add_plane)
        button_add_plane.grid(row=0, column=1)

        tree_selected_planes = ttk.Treeview(frame_planes, columns=("plane"), show="headings", height=10)
        tree_selected_planes.grid(row=0, column=2, padx=5)

        tree_selected_planes.heading("plane", text="Selected Planes")

        button_remove_plane = ttk.Button(frame_planes, text="<< Remove Plane", command=remove_plane)
        button_remove_plane.grid(row=1, column=1)

        # Save button
        button_save = ttk.Button(self.window, text="Save to .ISS", command=lambda: print("Saved!"))
        button_save.pack(pady=10)

        # Populate sample planes
        for plane in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]:
            tree_all_planes.insert('', 'end', values=(plane,))

        # Run the application

        



    def _handle_close(self):
        # Call the on_close callback
        if self.on_close:
            self.on_close()
        self.window.destroy()