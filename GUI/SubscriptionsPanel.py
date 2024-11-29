import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil

from pythonServices.subscriptionService import getAllSubscribedCollectionByFileName
from pythonServices.remoteService import getSpaceUsageOfRemoteSkinCatalog
from ISSScanner import getSkinsMatchingWithSubscribedCollection, bytesToString

class SubscriptionPanel:

    def __init__(self, root: tk):
        
        self.root = root
        
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
            parent_id = self.tree.insert("", "end", text=buildCollectionTreeLabel(ISSFile, catalogSize=catalogSize))  # Add main item
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
            self.tree.insert("", "end", text=buildCollectionTreeLabel(disabledElement, isDisabled=True))

    def on_item_selected(self, event):
        """Handle the selection event."""
        selected_item = self.tree.selection()

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
                        collectionName = getCollectionNameFromTreeLabel(colelctionLabel)
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

    def switch_state(self):
        selected_item = self.tree.selection()
        if selected_item:  # Ensure something is selected
            for item in selected_item:
                parent = self.tree.parent(item)  # Get the parent of the selected item
                if parent == "":  # Top-level items have an empty string as their parent
                    colelctionLabel = self.tree.item(item, 'text') 
                    collectionName = getCollectionNameFromTreeLabel(colelctionLabel)
                    isDisabled = colelctionLabel.endswith("DISABLED")
                    withoutExtensionFileName = os.path.join("Subscriptions", collectionName)
                    if isDisabled:
                        os.rename(withoutExtensionFileName+'.iss.disabled',withoutExtensionFileName+'.iss')
                    else:
                        os.rename(withoutExtensionFileName+'.iss',withoutExtensionFileName+'.iss.disabled')

                    for item in self.tree.get_children():
                        self.tree.delete(item)

                    self.populate_tree()


#TODO : Quite temporary solution before handling properly objects instead of strings and titles
treeLabelSeparator = "\t\t"
def buildCollectionTreeLabel(catalogName,catalogSize = 0, isDisabled = False ):
    if isDisabled:
        return f"{catalogName}{treeLabelSeparator}DISABLED"
    else:
        return f"{catalogName}{treeLabelSeparator}({bytesToString(catalogSize)})"

def getCollectionNameFromTreeLabel(treeLabel: str):
    splits = treeLabel.split(f"{treeLabelSeparator}")
    collectionName = splits[0]
    return collectionName
                 