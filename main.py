import os
import shutil
import subprocess
import sys
from tkinter import filedialog, messagebox, simpledialog
import requests
import tkinter as tk
from tkinter import ttk
import synchronizer
import pythonServices.configurationService as configurationService
from pythonServices.subscriptionService import SubscribedCollection, isSubcriptionFolderEmpty, getAllSubscribedCollection
from packaging.version import Version


VERSION="2.0.0.0"
API_URL = f"https://api.github.com/repos/RaphED/IL2GB-inter-squadrons-skins-synchronizer/releases/latest"

collectionByNameSubscribeFile=dict() #str,list[SubscribedCollection])

def performPreExecutionChecks():

    #check conf file is generated
    if not configurationService.configurationFileExists():
        printWarning("No configuration file found")
        #and help the user to generate a new one
        generateConfFileWithConsole()

    #check the game directory is properly parametered
    if not configurationService.checkConfParamIsValid("IL2GBGameDirectory"):
        raise Exception(
            f"Bad IL2 Game directory, current game path is set to : {configurationService.getConf("IL2GBGameDirectory")}\n"
            f"Change value in configuration file {configurationService.config_file}"
        )
    
def generateConfFileWithConsole():
    printWarning("A new Configuration file is about to be generated")
    #at first create a conf file with default params
    newConf = configurationService.generateConfFile()

    
    print("Please wait while trying to find IL2 directory on your HDDs...")
    foundIL2Path = configurationService.tryToFindIL2Path()
    #foundIL2Path = None
    if foundIL2Path is None:
        printError("Cannot find IL2 path")
        while True:
            manualPath = input("Please provide manually the path of your IL2 install directory : ")
            if configurationService.checkIL2InstallPath(manualPath):
                printSuccess("IL2 path found")
                foundIL2Path = manualPath
                break
            else:
                printError("Cannot identiry that directory as the main IL2 path")
                print("Please try again")
    else:
        printSuccess("IL2 path found")
    
    configurationService.update_config_param("IL2GBGameDirectory", foundIL2Path)

    print("ISS provides two modes :\n - (a) keep all downloaded skins\n - (b) remove all skins and keep only the ones you are subscripted to.")
    deletionMode = input("What mode do you want ? (a) or (b) ? ").lower()
    while True:
        if deletionMode == "a":
            configurationService.update_config_param("autoRemoveUnregisteredSkins", False)
            break
        elif deletionMode == "b":
            configurationService.update_config_param("autoRemoveUnregisteredSkins", True)
            break
        else:
            printError("Unknown anwser. Please anwser a or b")

    printSuccess("Configuration performed with success")
    
def printError(text):
    print("\033[91m{}\033[00m".format(text))

def printWarning(text):
    print("\033[93m{}\033[00m".format(text))

def printSuccess(text):
    print("\033[92m{}\033[00m".format(text))



def get_latest_release_info():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ISS")
        self.root.geometry("400x300")

        # Set up the style for the Treeview
        self.style = ttk.Style()
        self.style.configure("Custom.Treeview", background="lightblue", fieldbackground="lightblue")

        # Create and pack the Treeview widget with the custom style
        self.tree = ttk.Treeview(root, style="Custom.Treeview")
        self.tree.pack(fill="both", padx=5, pady=5)

        # Create buttons in a frame
        button_frame = tk.Frame(root, bg="lightgreen")
        button_frame.pack(fill="x", pady=5)

        # Add background color to the button frame for visibility
        self.add_button = tk.Button(button_frame, text="Add", command=self.add_item)
        self.add_button.pack(side="left", padx=5, pady=5)

        self.delete_button = tk.Button(button_frame, text="Delete", command=self.delete_item)
        self.delete_button.pack(side="left", padx=5, pady=5)

        self.switch_state_button = tk.Button(button_frame, text="Activer/Desactiver", command=self.switch_state)
        self.switch_state_button.pack(side="left", padx=5, pady=5)
        
        self.open_terminal_button = tk.Button(button_frame, text="StartSync !", command=self.open_terminal, background="#95de97")
        self.open_terminal_button.pack(side="left", padx=5, pady=5)
        
        # Add hierarchical data to the Treeview
        self.populate_tree()

        # Bind a selection event to the Treeview
        self.tree.bind("<<TreeviewSelect>>", self.on_item_selected)



    def open_terminal(self):
        """Open a new window with terminal-like functionality."""
        terminal = tk.Toplevel(self.root)  # Create a new Toplevel window
        terminal.title("Syncro des skins :")
        terminal.geometry("400x300")

        # Create a Text widget for displaying terminal output
        text_widget = tk.Text(terminal, wrap="word", height=15, width=50)
        text_widget.pack(expand=True, fill="both")
        text_widget.config(state=tk.DISABLED)  # Disable editing

        # Simulate terminal output
        self.print_to_terminal(text_widget, f"Début de la syncro!")

    def print_to_terminal(self, text_widget, text):
        """Add text to the terminal output in the Text widget."""
        text_widget.config(state=tk.NORMAL)  # Enable editing
        text_widget.insert(tk.END, text + "\n")  # Insert text
        text_widget.yview(tk.END)  # Auto-scroll to the end
        text_widget.config(state=tk.DISABLED)  # Disable editing again

    def switch_state(self):
        selected_item = self.tree.selection()
        if selected_item:  # Ensure something is selected
            for item in selected_item:
                parent = self.tree.parent(item)  # Get the parent of the selected item
                if parent == "":  # Top-level items have an empty string as their parent
                    file_name = self.tree.item(item, 'text') 
                    if file_name.find(" Size of total:") == -1:
                        file_name=file_name[:file_name.find(" DISABLED")]
                        file_path = os.path.join("Subscriptions", file_name+'.iss.disabled')
                        new_path= os.path.join("Subscriptions", file_name+'.iss')
                    else :
                        file_name=file_name[:file_name.find(" Size of total:")]
                        file_path = os.path.join("Subscriptions", file_name+'.iss')
                        new_path= os.path.join("Subscriptions", file_name+'.iss.disabled')

                    if os.path.exists(file_path):
                        os.rename(file_path,new_path)
                        for item in self.tree.get_children():
                            self.tree.delete(item)

                        self.populate_tree()
                    else:
                        print(f"File not found: {file_path}")



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
                        file_name=file_name[:file_name.find(" Size of total:")]
                        file_path = os.path.join("Subscriptions", file_name+'.iss')  # Path to the file in Subscriptions
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            for item in self.tree.get_children():
                                self.tree.delete(item)

                            self.populate_tree()
                        else:
                            print(f"File not found: {file_path}")
                else:
                    # TODO Thinking about planes you don't want and might have an exclusion list :)
                    print(f"Cannot delete item: {item}. Only top-level items can be deleted.")
        else:
            print("No item selected to delete.")



    def on_item_selected(self, event):
        """Handle the selection event."""
        selected_item = self.tree.selection()
        if selected_item:
            print(f"Selected item: {self.tree.item(selected_item)['text']}")


            
            
    def populate_tree(self):

        collectionByNameSubscribeFile.clear()
        """Populates the Treeview with nested data."""
        subscribedCollectionList = getAllSubscribedCollection()


        for collectionInSubscribes in subscribedCollectionList:
            if collectionInSubscribes.subcriptionName not in collectionByNameSubscribeFile:
                collectionByNameSubscribeFile[collectionInSubscribes.subcriptionName]=[]
            collectionByNameSubscribeFile[collectionInSubscribes.subcriptionName].append(collectionInSubscribes)

        sizePerSubscription = dict()
        for key in collectionByNameSubscribeFile:
            skinsLinkedCollectionBySubscribtionName=synchronizer.getSkinsFromSourceMatchingWithSubscribedCollections(collectionInSubscribes.source,collectionByNameSubscribeFile[key])

            toto=synchronizer.getSpaceUsageOfRemoteSkinCatalog(collectionInSubscribes.source,skinsLinkedCollectionBySubscribtionName)
            parent_id = self.tree.insert("", "end", text=key + " Size of total: " + synchronizer.bytesToString(toto))  # Add main item
            for skin in skinsLinkedCollectionBySubscribtionName:
                self.tree.insert(parent_id, "end", text=skin['Title'])  # Add sub-items

        subscriptionPath = os.path.join(os.getcwd(),"Subscriptions")

        disabledElements = list()
        #create subsciption path of not exists
        for root, dirs, files in os.walk(subscriptionPath):
            for file in files:
                if file.endswith(".iss.disabled"): #We only consider files with iss extension
                    disabledElements.append( file[:file.find(".iss.disabled")]+ " DISABLED")

        for disabledElement in disabledElements:
            self.tree.insert("", "end", text=disabledElement)
                             

   

######### MAIN ###############
if __name__ == "__main__":    

    release_info = get_latest_release_info()
    if release_info:
        latest_version = release_info["tag_name"]
        current_version = Version(VERSION)
        remote_version = Version(latest_version)
        if remote_version > current_version:
            # Assuming the first asset is what we want
            assets = release_info.get("assets", [])
            if assets:
                download_url = assets[0]["browser_download_url"]
                try:
                        # Start the updater with the specified arguments
                        subprocess.Popen(
                            ["ISSupdater.exe"],  # Arguments to the updater
                            shell=False,            # Don't use a shell to avoid unnecessary dependencies
                            close_fds=True,         # Close file descriptors to detach from the parent process
                            creationflags=subprocess.DETACHED_PROCESS if sys.platform == "win32" else 0  # Detach process on Windows
                        )
                        sys.exit()  # Close the main application
                except Exception as e:
                    sys.exit(1)  # Exit with an error code    
if(True):
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop() 
else:
    try:
        performPreExecutionChecks()

        #CUSTOM PHOTOS SECTION
        cockpitNotesMode = configurationService.getConf("cockpitNotesMode")
        if cockpitNotesMode != "noSync":
            print(f"Custom photos scan mode : {cockpitNotesMode}")
            printWarning("Photos scan launched. Please wait...")
            scanResult = synchronizer.scanCustomPhotos()
            if len(scanResult) > 0:
                print("Some photos has to be updated :")
                print([customPhoto["aircraft"] for customPhoto in scanResult])
                while True:
                    answer = input("Do you want to perform the update ? (y) yes, (n) no : ").lower()
                    if answer == "y":
                        print("Update started...")
                        synchronizer.updateCustomPhotos(scanResult)
                        print("Update done")
                        break
                    elif answer == "n":
                        print("ok no update")
                        break
                    else:
                        print("Invalid answer, try again")        
            else:
                printSuccess("All custom photos are up to date")

        #SKINS SECTION
        if isSubcriptionFolderEmpty():
            printWarning("Subscription folder is empty.\nAdd .iss file(s) to subscribe to any skins collection")

        subscribedCollections = getAllSubscribedCollection()
        print("Subscribed collections : ")
        for collection in subscribedCollections:
            print(f"\t-{collection.subcriptionName}")

        printWarning("SKINS scan launched. Please wait...")
        #once the prec checks passed, perform the global scan
        scanResult = synchronizer.scanSkins()
        printSuccess("SKINS scan finished")
        print(scanResult.toString())
        

        #then as the user for the update if any
        if scanResult.IsSyncUpToDate():
            printSuccess("All skins are up to date.")
        else:
            while True:
                
                answer = input("Do you want to perform the update ? (y) yes, (n) no : ").lower()
                
                if answer == "y":
                    printSuccess("||||||||| START SYNC ||||||||")
                    synchronizer.updateAll(scanResult)
                    printSuccess("|||||||||  END SYNC  ||||||||")
                    break
                elif answer == "n":
                    print("No skin synchronization performed.")
                    break
                else:
                    print("Invalid answer, try again")

        printSuccess("I3S ended properly.")

    except Exception as e:
        printError(e)
        printError("I3S ended with an error.")

    input("Press any key to quit program... ")