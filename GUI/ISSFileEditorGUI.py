import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pythonServices.filesService import getIconPath, getRessourcePath

from pythonServices.remoteService import getSpaceUsageOfRemoteSkinCatalog
from pythonServices.subscriptionService import SubscribedCollection, getSubcriptionNameFromFileName, getSubcriptionFilePathFromFileName, getSubscribedCollectionFromFilePath, saveSubscriptionFile
from ISSScanner import bytesToString, getSkinsFromSourceMatchingWithSubscribedCollections
from GUI.Components.clickableIcon import CliquableIcon

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
        self.tree_skin_explorer = ttk.Treeview(frame_explorer, columns=("plane","IL2Group","SkinPack"), show="headings", height=15)
        self.tree_skin_explorer.pack(fill="both", expand=True, pady=10)

        self.tree_skin_explorer.heading("plane", text="Title", anchor="w")
        self.tree_skin_explorer.heading("IL2Group", text="IL2Group", anchor="w")
        self.tree_skin_explorer.heading("SkinPack", text="SkinPack", anchor="w")

        self.tree_skin_explorer.column("plane", width=200, minwidth=200)  # Colonne Title plus large
        self.tree_skin_explorer.column("IL2Group", width=150, minwidth=150)  # Colonne IL2Group moyenne
        self.tree_skin_explorer.column("SkinPack", width=200, minwidth=150)  # Colonne SkinPack moyenne

        self.tree_skin_explorer.bind('<Double-1>', self.on_double_click_tree_skins_explorer)

        # Send to criteria panel
        frame_explorer_lower_panel = ttk.Frame(frame_explorer)
        frame_explorer_lower_panel.pack(fill="x", pady=10)

        self.skins_explorer_count_label = tk.Label(frame_explorer_lower_panel)
        self.skins_explorer_count_label.pack(side=tk.LEFT)
        self.skins_explorer_size_label = tk.Label(frame_explorer_lower_panel)
        self.skins_explorer_size_label.pack(side=tk.LEFT)
        button_add_bundle = ttk.Button(frame_explorer_lower_panel, text="Add these skins in a new bundle", style="Accent.TButton", command=self.add_SubcribeCollectionFromFilters)
        button_add_bundle.pack(side=tk.RIGHT)

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

        self.tree_selected_planes = ttk.Treeview(frame_subcription_content, columns=("plane","IL2Group","SkinPack"), show="headings", height=30)
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

        frame_planes_bottom = ttk.Frame(frame_subcription_content)
        frame_planes_bottom.pack(fill="x", pady=10)

        self.skins_in_subscription_count_label = tk.Label(frame_planes_bottom)
        self.skins_in_subscription_count_label.pack(side=tk.LEFT)
        self.skins_in_subscription_size_label = tk.Label(frame_planes_bottom)
        self.skins_in_subscription_size_label.pack(side=tk.LEFT)
        
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
        
        # Add these slins to the view below so the user can see the implied skins
        self.tree_skin_explorer.delete(*self.tree_skin_explorer.get_children())

        for skin in skins:
            self.tree_skin_explorer.insert("", "end", values=(skin.infos["Title"],skin.infos["IL2Group"],skin.infos["SkinPack"]))
        
        self.skins_explorer_count_label.configure(text=f"Skins count : {len(skins)}")
        self.skins_explorer_size_label.configure(text=f"({bytesToString(getSpaceUsageOfRemoteSkinCatalog(source="HSD", remoteSkinList=skins))})")
        self.runningTask=None

    def update_temp_collection_from_filters(self, *args):
        self.update_collection_criteria_from_filter_values(self.explorer_temp_collection)

        if self.runningTask:
            self.runningTask.stop()

        self.runningTask=threading.Thread(target=self.actualise_explorer_result()).start()

    def on_double_click_tree_skins_explorer(self, event):
        # Get the selected item
        selected_item = self.tree_skin_explorer.selection()
        if not selected_item:
            return
        
        # Get values from the selected row
        values = self.tree_skin_explorer.item(selected_item[0])["values"]
        # Update the entry fields
        self.explorer_filters_values["Title"].set(values[0])
        self.explorer_filters_values["IL2Group"].set(values[1]) 
        self.explorer_filters_values["SkinPack"].set(values[2])

    def update_bundle_list(self):
        #clear the list
        for child in self.frame_collection_bundle.winfo_children():
            child.destroy()

        for index, collection in enumerate(self.subscribedCollection):

            criteria_frame = ttk.Frame(self.frame_collection_bundle, style="Bundle.TFrame")
            criteria_frame.pack(fill="x", padx=5, pady=5)

            il2Group=collection.criteria.get("IL2Group", "")
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
                tooltip_text="Remove bundle",
                onClick=lambda i=index: self.remove_SubcribeCollection(i) #use the index of the collection
            )
            trashButton.pack(side=tk.BOTTOM)
            trashButton = CliquableIcon(
                root=criteria_frame, 
                icon_path=getIconPath("edit.png"),
                tooltip_text="Edit Bundle. Desactivated as not yet developped",
                disabled=True
            )
            trashButton.pack(side=tk.BOTTOM)

            #Click on the bundle send criteria to the filters
            label.bind('<Button-1>', lambda event: self.load_SubcribeCollection_in_filters(collection))
        
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
        
        self.tree_selected_planes.delete(*self.tree_selected_planes.get_children())
        
        for skin in skins:
            self.tree_selected_planes.insert("", "end", values=(skin.infos["Title"], skin.infos["IL2Group"], skin.infos["SkinPack"]))
        
        self.skins_in_subscription_count_label.configure(text=f"Skins count : {len(skins)}")
        self.skins_in_subscription_size_label.configure(text=f"({bytesToString(getSpaceUsageOfRemoteSkinCatalog(source="HSD", remoteSkinList=skins))})")

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
