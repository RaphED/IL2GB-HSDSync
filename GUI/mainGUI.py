
from tkinter import ttk, filedialog, messagebox
import tkinter as tk
import os
import shutil
from threading import Thread

from pythonServices.configurationService import getConf, update_config_param, allowedCockpitNotesModes
from pythonServices.subscriptionService import getAllSubscribedCollectionByFileName
from pythonServices.filesService import getRessourcePath
from synchronizer import getSkinsMatchingWithSubscribedCollection, getSpaceUsageOfRemoteSkinCatalog, bytesToString

class mainGUI:
    #g_text_widget=None
    def __init__(self, synchronizeMainCallBack):

        #register the callback
        #TODO : remove the callback ?
        self.synchronizeMainCallBack = synchronizeMainCallBack

        #initialise tinker compotent (why root ??)
        self.root = tk.Tk()

        self.root.iconbitmap(getRessourcePath("iss.ico"))

        style = ttk.Style(self.root)
        
        self.root.tk.call("source",getRessourcePath("forest-light.tcl"))
        style.theme_use("forest-light")

        self.root.title("InterSquadron Skin Synchronizer")
        self.root.geometry("500x540")

        # Create a Label widget to display text above the Treeview
        subscription_label_frame = tk.Frame(self.root)
        subscription_label_frame.pack(fill="both",padx=2, pady=2)
        self.label = tk.Label(subscription_label_frame, text="Subscriptions :", font=("Arial", 10,"bold","underline"))
        self.label.pack(side="left", fill="x",padx=5)  # Add some padding above the Treeview

        # Create and pack the Treeview widget with the custom style
        self.tree = ttk.Treeview(self.root, show="tree" )#, style="Custom.Treeview")
        self.tree.pack(fill="both",  padx=5, pady=5)
        
        # Add hierarchical data to the Treeview
        self.populate_tree()
        # Bind a selection event to the Treeview
        self.tree.bind("<<TreeviewSelect>>", self.on_item_selected)

        # Create buttons in a frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="both", pady=2)

        # Add background color to the button frame for visibility
        self.add_button = ttk.Button(button_frame, text="Import", command=self.add_item)
        self.add_button.pack(side="left", padx=10, pady=5)

        self.delete_button = ttk.Button(button_frame, text="Delete", command=self.delete_item)
        self.delete_button.pack(side="left", padx=5, pady=5)

        self.switch_state_button = ttk.Button(button_frame, text="Activate/Disable", command=self.switch_state)
        self.switch_state_button.pack(side="left", padx=5, pady=5)
        



        #Part of params :
        params_label_frame = tk.Frame(self.root)
        params_label_frame.pack(fill="both",padx=2, pady=2)
        self.param_label = tk.Label(params_label_frame, text="Parameters :", font=("Arial", 10,"bold","underline"))
        self.param_label.pack(side="left", fill="x",padx=5)  # Add some padding above the Treeview

        path_frame = tk.Frame(self.root)
        path_frame.pack(fill="x", pady=5)
        self.path_label = tk.Label(path_frame, text=self.short_path(getConf("IL2GBGameDirectory")), anchor="w")
        self.path_label.pack(side="left", fill="x", expand=True, padx=5)
        self.path_button = ttk.Button(path_frame, text="Modify", command=self.modify_path)
        self.path_button.pack(side="right", padx=5)

        # Toggle Switch
        toggle_frame = tk.Frame(self.root)
        toggle_frame.pack(fill="x", pady=5)
        tk.Label(toggle_frame, text="Auto remove unregistered skins", anchor="w").pack(side="left", padx=5)
        self.toggle_var = tk.BooleanVar(value=getConf("autoRemoveUnregisteredSkins"))
        self.toggle_button = ttk.Checkbutton(toggle_frame, variable=self.toggle_var, onvalue=True, offvalue=False, command=self.modify_auto_remove)
        self.toggle_button.pack(side="right", padx=5)

        # Dropdown Menu
        dropdown_frame = tk.Frame(self.root)
        dropdown_frame.pack(fill="x", pady=5)
        tk.Label(dropdown_frame, text="Cockpit Photo", anchor="w").pack(side="left", padx=5)
        self.dropdown_var = tk.StringVar(value=getConf("cockpitNotesMode"))
        self.dropdown = ttk.Combobox(
            dropdown_frame,
            textvariable=self.dropdown_var,
            values=allowedCockpitNotesModes,
            state="readonly",
        )
        self.dropdown.pack(side="right", padx=5)
        self.dropdown.bind("<<ComboboxSelected>>", self.on_dropdown_change)

        button2_frame = ttk.Frame(self.root)
        button2_frame.pack(fill="both", pady=2)
        self.start_sync_button = ttk.Button(button2_frame, text="StartSync !", style="Accent.TButton", command=self.start_sync)
        self.start_sync_button.pack(padx=10, pady=10)

    def run(self):
        return self.root.mainloop()
    
    def short_path(self,fullPath, maxLength = 50):
        if len(fullPath) > maxLength:
            return f"{fullPath[:maxLength]}..."
        return fullPath
    
    def modify_path(self):
        file_path = filedialog.askdirectory(
            initialdir=getConf("IL2GBGameDirectory"),
            title="Select a folder"
        )
        if len(file_path)>0:
            update_config_param("IL2GBGameDirectory",file_path)
            self.path_label.config(text=self.short_path(file_path))

    def modify_auto_remove(self):
        lebooleanquejeveux=self.toggle_var.get()
        update_config_param("autoRemoveUnregisteredSkins", lebooleanquejeveux)

    def on_dropdown_change(self, event):
        """Handle dropdown value change."""
        selected_value = self.dropdown_var.get()
        update_config_param("cockpitNotesMode", selected_value)

        

    def start_sync(self):
        # TODO ERIC faire plus propre
        # global g_text_widget
        # """Open a new window with terminal-like functionality."""
        # terminal = tk.Toplevel(self.root)  # Create a new Toplevel window
        # terminal.title("Syncro des skins :")
        # terminal.geometry("400x300")

        # # Create a Text widget for displaying terminal output
        # text_widget = tk.Text(terminal, wrap="word", height=15, width=50)
        # text_widget.pack(expand=True, fill="both")
        # text_widget.config(state=tk.DISABLED)  # Disable editing
        # g_text_widget = text_widget
        # # Simulate terminal output
        # # self.print_to_terminal(f"Début de la syncro!")

        # #The main core function :

        Thread(target=self.synchronizeMainCallBack(), daemon=True).start()

    # TODO ERIC faire plus propre
    # def print_to_terminal(self, text):
    #     global g_text_widget
    #     text_widget = g_text_widget
    #     """Add text to the terminal output in the Text widget."""
    #     text_widget.config(state=tk.NORMAL)  # Enable editing
    #     text_widget.insert(tk.END, text + "\n")  # Insert text
    #     text_widget.yview(tk.END)  # Auto-scroll to the end
    #     text_widget.config(state=tk.DISABLED)  # Disable editing again

    def switch_state(self):
        selected_item = self.tree.selection()
        if selected_item:  # Ensure something is selected
            for item in selected_item:
                parent = self.tree.parent(item)  # Get the parent of the selected item
                if parent == "":  # Top-level items have an empty string as their parent
                    colelctionLabel = self.tree.item(item, 'text') 
                    collectionName = mainGUI.getCollectionNameFromTreeLabel(colelctionLabel)
                    isDisabled = colelctionLabel.endswith("DISABLED")
                    withoutExtensionFileName = os.path.join("Subscriptions", collectionName)
                    if isDisabled:
                        os.rename(withoutExtensionFileName+'.iss.disabled',withoutExtensionFileName+'.iss')
                    else:
                        os.rename(withoutExtensionFileName+'.iss',withoutExtensionFileName+'.iss.disabled')

                    for item in self.tree.get_children():
                        self.tree.delete(item)

                    self.populate_tree()
                    


    def add_item(self):
        file_path = filedialog.askopenfilename(
            title="Select a File",
            filetypes=[("Subscriptions","*.iss")]
        )
        if file_path:  # Ensure the user selected a file
            # Ensure the 'Subscriptions' folder exists
            subscriptions_folder = "Subscriptions"
            os.makedirs(subscriptions_folder, exist_ok=True)

            # Copy the selected file to the 'Subscriptions' folder
            file_name = os.path.basename(file_path)  # Extract the file name
            destination_path = os.path.join(subscriptions_folder, file_name)
            shutil.copy(file_path, destination_path)

            # Add the file name to the Treeview// refresh like a *turd*
            for item in self.tree.get_children():
                self.tree.delete(item)

            self.populate_tree()

    def delete_item(self):
        selected_item = self.tree.selection()
        if selected_item:  # Ensure something is selected
            for item in selected_item:
                parent = self.tree.parent(item)  # Get the parent of the selected item
                if parent == "":  # Top-level items have an empty string as their parent
                    answer = messagebox.askyesno(title='confirmation',
                    message='Are you sure you want to delete this subscription ?')
                    if answer:
                        file_name = self.tree.item(item, 'text')
                        colelctionLabel = self.tree.item(item, 'text') 
                        collectionName = mainGUI.getCollectionNameFromTreeLabel(colelctionLabel)
                        isDisabled = colelctionLabel.endswith("DISABLED")
                        withoutExtensionFileName = os.path.join("Subscriptions", collectionName)
                        if isDisabled:
                            os.remove(withoutExtensionFileName + ".iss.disabled")
                        else:
                            os.remove(withoutExtensionFileName + ".iss")

                        for item in self.tree.get_children():
                            self.tree.delete(item)

                        self.populate_tree()
                else:
                    # TODO Thinking about planes you don't want and might have an exclusion list :)
                    print(f"Cannot delete item: {item}. Only top-level items can be deleted.")
        else:
            print("No item selected to delete.")


    def on_item_selected(self, event):
        """Handle the selection event."""
        selected_item = self.tree.selection()            

    #TODO : Quite temporary solution before handling properly objects instead of strings and titles
    treeLabelSeparator = "\t\t"
    def buildCollectionTreeLabel(catalogName,catalogSize = 0, isDisabled = False ):
        if isDisabled:
            return f"{catalogName}{mainGUI.treeLabelSeparator}DISABLED"
        else:
            return f"{catalogName}{mainGUI.treeLabelSeparator}({bytesToString(catalogSize)})"

    def getCollectionNameFromTreeLabel(treeLabel: str):
        splits = treeLabel.split(f"{mainGUI.treeLabelSeparator}")
        collectionName = splits[0]
        return collectionName

    def populate_tree(self):

        collectionByNameSubscribeFile = getAllSubscribedCollectionByFileName()
        """Populates the Treeview with nested data."""
        for ISSFile in collectionByNameSubscribeFile.keys():
            skinCollection = []
            for collection in collectionByNameSubscribeFile[ISSFile]:
                skinCollection += getSkinsMatchingWithSubscribedCollection(collection)
            
            #TODO : make it work for multiple sources
            catalogSize=getSpaceUsageOfRemoteSkinCatalog("HSD",skinCollection)
            #parent_id = self.tree.insert("", "end", text=key + "\t\t(" + synchronizer.bytesToString(catalogSize) + ")")  # Add main item
            parent_id = self.tree.insert("", "end", text=mainGUI.buildCollectionTreeLabel(ISSFile, catalogSize=catalogSize))  # Add main item
            for skin in skinCollection:
                self.tree.insert(parent_id, "end", text=skin['Title'])  # Add sub-items

        subscriptionPath = os.path.join(os.getcwd(),"Subscriptions")

        disabledElements = list()
        #create subsciption path of not exists
        for root, dirs, files in os.walk(subscriptionPath):
            for file in files:
                if file.endswith(".iss.disabled"): #We only consider files with iss extension
                    disabledElements.append( file[:file.find(".iss.disabled")])

        for disabledElement in disabledElements:
            self.tree.insert("", "end", text=mainGUI.buildCollectionTreeLabel(disabledElement, isDisabled=True))
                 