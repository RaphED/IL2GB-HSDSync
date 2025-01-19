import threading
import re
import tkinter as tk
from tkinter import ttk, messagebox
from pythonServices.filesService import getRessourcePath

from pythonServices.subscriptionService import SubscribedCollection, getSubcriptionNameFromFileName, getSubcriptionFilePathFromFileName, getSubscribedCollectionFromFilePath, saveSubscriptionFile
from ISSScanner import getSkinsFromSourceMatchingWithSubscribedCollections
from GUI.Components.skinsListView import SkinsListView
from GUI.Components.tooltip import Tooltip
from GUI.Components.collectionBundleCard import CollectionBundleCard

import tkinter as tk
from tkinter import ttk

class ISSFileEditorWindow:
    def __init__(self, root: tk.Tk, on_close, iss_file_name=None):
        self.root = root
        self.runningTask = None
        self.on_close = on_close

        # Create a Toplevel window
        self.window = tk.Toplevel(self.root)
        self.window.title("ISS file editor")
        self.window.iconbitmap(getRessourcePath("iss.ico"))
        self.window.geometry("1500x800")

        style = ttk.Style()
        style.configure("Bundle.TFrame",
            background="#f8f9fa",
            relief="raised",
            borderwidth=2,
        )
        style.configure("Bundle.TLabel", 
            font=("Helvetica", 9),
            background="#f8f9fa",
            padding=(5, 2)
        )

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
        self.explorer_temp_collection = SubscribedCollection(
            source="HSD",
            subcriptionName="explorer_temp_collection"
        )

        frame_explorer = ttk.LabelFrame(main_container, text="HSD skins explorer", padding=10)
        frame_explorer.grid(row=0, column=0, sticky="nsew", padx=5)
        # add filters
        self.frame_explorer_filters = ttk.Frame(frame_explorer)
        self.frame_explorer_filters.pack(fill="x", pady=5)
        
        self.explorer_filters_values = dict[str, tk.StringVar]()
        self.add_research_filter("Title")
        self.add_research_filter("IL2Group")
        self.add_research_filter("SkinPack")

        # Dynamic criteria tree
        self.explorer_skins_list = SkinsListView(frame_explorer, on_skin_double_click=self.on_double_click_tree_skins_explorer)
        self.explorer_skins_list.pack(fill="both", expand=True, pady=10)
        Tooltip(self.explorer_skins_list, "Double click on an line to copy it in the filters")

        # Send to criteria panel
        frame_explorer_lower_panel = ttk.Frame(frame_explorer)
        frame_explorer_lower_panel.pack(fill="x", pady=5)
        
        self.button_add_bundle = ttk.Button(frame_explorer_lower_panel, text="Add these skins in a new bundle", style="Accent.TButton", command=self.add_SubcribeCollectionFromFilters)
        self.button_add_bundle.pack(side=tk.RIGHT)

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

        # 3. Subscription content
        frame_subcription_content = ttk.LabelFrame(main_container, text="Skins in the collection", padding=10)
        frame_subcription_content.grid(row=0, column=2, sticky="nsew", padx=5)

        self.subsciption_skins_list = SkinsListView(frame_subcription_content)
        self.subsciption_skins_list.pack(fill="both", expand=True, pady=10)

        #the description of the collection content
        self.subscribedCollection = []
        
        # Load existing file if editing
        self.edited_iss_fileName = iss_file_name
        if self.edited_iss_fileName is not None:
            self.filename_var.set(getSubcriptionNameFromFileName(self.edited_iss_fileName))
            self.subscribedCollection = getSubscribedCollectionFromFilePath(getSubcriptionFilePathFromFileName(self.edited_iss_fileName))
            self.update_bundle_list()

        #initialise the research list will all skins
        self.root.after(0, self.actualise_explorer_result)
    
    def add_research_filter(self, criterion):
        
        ttk.Label(self.frame_explorer_filters, text=criterion).pack(anchor="w")
        self.explorer_filters_values[criterion] = tk.StringVar()
        ttk.Entry(self.frame_explorer_filters, textvariable=self.explorer_filters_values[criterion]).pack(fill="x", pady=2)

        #What for the entry modification to update explorer candidates
        self.explorer_filters_values[criterion].trace_add("write", self.update_temp_collection_from_filters)

    def update_collection_criteria_from_filter_values(self, collection: SubscribedCollection):
        for filter_criterion in self.explorer_filters_values.keys():
            #calculate the new criteria value
            new_criteria_value = None
            if self.explorer_filters_values[filter_criterion].get():
                # We have a value. Implicitely add wildcards
                new_criteria_value = '*' + self.explorer_filters_values[filter_criterion].get() + '*'

            #remove the value from the criteria is present and filter is empty
            if new_criteria_value is None and collection.criteria.get(filter_criterion):
                del collection.criteria[filter_criterion]
            #otherwise set the value
            if new_criteria_value is not None:
                collection.criteria[filter_criterion] = new_criteria_value

    def set_filters_from_collection_criteria(self, collection: SubscribedCollection):
        for filter_criterion in self.explorer_filters_values.keys():
            criteria_value = collection.criteria.get(filter_criterion)
            if criteria_value is None:
                self.explorer_filters_values[filter_criterion].set("")
            else:
                #remove potential wildcards
                if criteria_value.startswith('*'):
                    criteria_value = criteria_value[1:]
                if criteria_value.endswith('*'):
                    criteria_value = criteria_value[:-1]
                self.explorer_filters_values[filter_criterion].set(criteria_value)

    def actualise_explorer_result(self):
        skins=getSkinsFromSourceMatchingWithSubscribedCollections("HSD", [self.explorer_temp_collection])
        self.explorer_skins_list.loadSkinsList(skins)

        self.button_add_bundle["state"] = "disabled"
        self.button_add_bundle.configure(style='')
        for filter in self.explorer_filters_values.keys():
            if self.explorer_filters_values[filter].get() != "":
                self.button_add_bundle.configure(style="Accent.TButton")
                self.button_add_bundle["state"] = "enabled"
                break

        self.runningTask=None

    def update_temp_collection_from_filters(self, *args):
        self.update_collection_criteria_from_filter_values(self.explorer_temp_collection)

        if self.runningTask:
            self.runningTask.stop()

        self.runningTask=threading.Thread(target=self.actualise_explorer_result()).start()

    def on_double_click_tree_skins_explorer(self, object: dict[str, str]):
        # Update the entry fields (and escape any special caracter regarding reg expressions)
        self.explorer_filters_values["Title"].set(re.escape(object["Title"]).replace("\\ ", " "))
        self.explorer_filters_values["IL2Group"].set(re.escape(object["IL2Group"]).replace("\\ ", " ")) 
        self.explorer_filters_values["SkinPack"].set(re.escape(object["SkinPack"]).replace("\\ ", " "))

    def update_bundle_list(self):
        #clear the list
        for child in self.frame_collection_bundle.winfo_children():
            child.destroy()

        for index, collection in enumerate(self.subscribedCollection):

            CollectionBundleCard(
                root=self.frame_collection_bundle,
                collection=collection,
                on_remove_bundle=lambda i=index: self.remove_SubcribeCollection(i), #use the index of the collection
                on_copy_bundle=lambda c=collection: self.load_SubcribeCollection_in_filters(c)
            ).pack(fill="x", padx=5, pady=5)
        
        self.root.after(0, self.actualise_subscription_skins_list)
    
    def add_SubcribeCollectionFromFilters(self):
        
        newCollection = SubscribedCollection(
            source="HSD",
            subcriptionName="",
            criteria= dict[str,str]()
        )

        self.update_collection_criteria_from_filter_values(newCollection)

        self.subscribedCollection.append(newCollection)

        self.root.after(0, self.update_bundle_list)

    def remove_SubcribeCollection(self, collection_index):
        self.subscribedCollection.pop(collection_index)
        self.root.after(0, self.update_bundle_list)
    
    def load_SubcribeCollection_in_filters(self, collection: SubscribedCollection):
        self.set_filters_from_collection_criteria(collection)
        self.root.after(0, self.actualise_explorer_result)
    
    def actualise_subscription_skins_list(self):
        skins = getSkinsFromSourceMatchingWithSubscribedCollections("HSD", self.subscribedCollection)
        self.subsciption_skins_list.loadSkinsList(skins)

    def save_to_iss(self):
        
        if self.filename_var.get() == "":
            messagebox.showerror("Collection name is required", "Please set a collection name before saving your file", parent=self.window)
            return
        
        #generate the file name if we are in creation mode
        if self.edited_iss_fileName is None:
            self.edited_iss_fileName = self.filename_var.get() + ".iss"
        
        try:
            saveSubscriptionFile(self.edited_iss_fileName, subscribedCollections=self.subscribedCollection)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the file: {str(e)}", parent=self.window)
            return

        self.root.after(500, self.close_window)

    def close_window(self):
        self.window.destroy()
        self.on_close()