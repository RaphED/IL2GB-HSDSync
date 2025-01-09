import threading
from tkinter import ttk
import tkinter as tk
import logging
import webbrowser

from pythonServices.configurationService import configurationFileExists
from pythonServices.filesService import getRessourcePath, getIconPath, cleanTemporaryFolder

from GUI.collectionsPanel import CollectionsPanel
from GUI.parametersPanel import ParametersPanel
from GUI.consolePanel import ConsolePanel
from GUI.actionsPanel import ActionPanel
from GUI.progressBar import ProgressBar
from GUI.Components.clickableIcon import CliquableIcon
from GUI.firstLaunchGUI import runFirstLaunchGUI

import ISSsynchronizer
import ISSScanner
from pythonServices.messageBrocker import MessageBrocker

class MainGUI:
    
    def __init__(self, root):

        self.root = root

        self.root.iconbitmap(getRessourcePath("iss.ico"))

        style = ttk.Style(self.root)
        
        self.root.tk.call("source",getRessourcePath("forest-light.tcl"))
        style.theme_use("forest-light")
        
        self.root.title("InterSquadron Skin Synchronizer")
        self.root.geometry("850x600")
        
        # 1 - UPPER FRAME
        top_main_frame = tk.Frame(self.root)
        top_main_frame.pack(side="top", fill="both")
        # 1.1 - left upper frame
        left_upper_frame = tk.Frame(top_main_frame)
        left_upper_frame.pack(side="left", fill="both")

        #self.subscriptionsPanel = SubscriptionPanel(left_upper_frame)
        self.collectionsPanel = CollectionsPanel(
            left_upper_frame,
            on_loading_start=self.on_collections_loading_start,
            on_loading_complete=self.on_collections_loading_completed
        )

        # 1.2 - right upper frame
        right_upper_frame = tk.Frame(top_main_frame)
        right_upper_frame.pack(side="right", fill="both", expand=True)
                
        self.parametersPanel = ParametersPanel(right_upper_frame)
        self.actionPanel = ActionPanel(right_upper_frame, scanCommand = self.start_scan_async, syncCommand=self.start_synchronization_async)

        # 2 - BOTTOM FRAME
        #2.1 info bar
        info_bar = tk.Frame(self.root)
        info_bar.pack(fill="both")

        info_bar.grid_columnconfigure(0, weight=0)  # Left column
        info_bar.grid_columnconfigure(1, weight=1)  # Middle colum, takes all possible width
        info_bar.grid_columnconfigure(2, weight=0)  # Right
        info_bar.grid_rowconfigure(0)
        
        self.irreIcon = CliquableIcon(
            info_bar, 
            icon_path=getIconPath("irre-logo-32.png"),
            onClick=open_link_IRREWelcome,
            opacityFactor=10,
            onMouseOverOpacityFactor=255
        )
        self.progressBar = ProgressBar(info_bar)

        self.helpIcon = CliquableIcon(
            info_bar, 
            icon_path=getIconPath("help-32.png"), 
            tooltip_text="Online ISS documentation", 
            onClick=open_link_ISSDocumentation
        )
        
        self.irreIcon.grid(column=0, row=0, padx=5, pady=2)
        self.progressBar.grid(column=1, row=0, padx=5, pady=5)
        self.helpIcon.grid(column=2, row=0, padx=5, pady=2)
        
        bottom_main_frame = tk.Frame(self.root)
        bottom_main_frame.pack(side="bottom", fill="both", expand=True)

        self.consolePanel = ConsolePanel(bottom_main_frame)

        #OTHER STORED INFORMATION
        self.currentScanResult: ISSsynchronizer.ScanResult = None
        self.pendingProcessing= False

        #Once all components are declared, we can load the data
        #for the moment, only the collections are loaded
        self.root.after(0, self.collectionsPanel.loadCollections_async)

    #COMPONENTS LISTENERS
    def on_collections_loading_start(self):
        self.lock_components_actions()
        MessageBrocker.emitConsoleMessage("Please wait, collections are loading...")

    def on_collections_loading_completed(self):
        self.unlock_components_actions()
        MessageBrocker.emitConsoleMessage("Collections loaded, Scan is now available.")

    #MANAGE COMPONENTS ACTIONS
    def lock_components_actions(self):
        #collections panel
        self.collectionsPanel.lock_actions()
        #parameters panel
        self.parametersPanel.lock_actions()
        #Action panel
        self.actionPanel.lockScanButton()
        self.actionPanel.lockSyncButton()

    def unlock_components_actions(self):
        #collections panel
        self.collectionsPanel.unlock_actions()
        #parameters panel
        self.parametersPanel.unlock_actions()
        #Action panel
        self.actionPanel.unlockScanButton() #Scan button is always available
        if self.currentScanResult is None: #no scan performed
            self.actionPanel.lockSyncButton()
        elif self.currentScanResult.IsSyncUpToDate(): #scan reveal no update needed
            self.actionPanel.lockSyncButton()
        else: #otherwise we have a scan, and an sync to do
            self.actionPanel.unlockSyncButton()
    
    #SCAN RESULT DISPLAY
    def cleanScanResult(self):
        self.currentScanResult = None
        self.consolePanel.clearPanel()

    def displayScanResult(self):
        #Display the scan result in the console
        if self.currentScanResult is not None:
            self.consolePanel.addLine(self.currentScanResult.toString())

    #MAIN SCAN AND SYNC PROCESSES
    def start_scan(self):
        self.cleanScanResult()
        self.lock_components_actions()

        self.currentScanResult = ISSScanner.scanAll()

        self.displayScanResult()
        self.unlock_components_actions()

    def start_scan_async(self):
        threading.Thread(target=self.start_scan).start()
    
    def start_synchronization(self):
        if self.currentScanResult is None:
            logging.error("Sync launched with no scan result")
            return
        
        self.lock_components_actions()
        ISSsynchronizer.updateAll(self.currentScanResult)
        self.currentScanResult = None #the current scan is no more relevant
        self.unlock_components_actions()

    def start_synchronization_async(self):
        threading.Thread(target=self.start_synchronization).start()
#TOOLS

def open_link(link: str):
    webbrowser.open(link)

def open_link_ISSDocumentation():
    open_link("https://melodious-andesaurus-f9a.notion.site/IL2GB-Inter-squadron-Skin-Synchronizer-ISS-1477b1e5c2b8803db322d0daba993f94")

def open_link_IRREWelcome():
    open_link("https://www.lesirreductibles.com")

#MAIN RUN
def runMainGUI():
    
    #make sure the temporary folder is clean
    cleanTemporaryFolder()

    #check conf file is generated
    if not configurationFileExists():
        runFirstLaunchGUI()
    
    root = tk.Tk()
    mainGUI = MainGUI(root)

    root.mainloop()