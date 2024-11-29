import time
from tkinter import ttk
import tkinter as tk
from threading import Thread
import logging

from pythonServices.filesService import getRessourcePath

from GUI.SubscriptionsPanel import SubscriptionPanel
from GUI.parametersPanel import ParametersPanel
from GUI.consolePanel import ConsolePanel

import synchronizer

class mainGUI:
    
    #g_text_widget=None
    def __init__(self):

        #initialise tinker compotent (why root ??)
        self.root = tk.Tk()

        self.root.iconbitmap(getRessourcePath("iss.ico"))

        style = ttk.Style(self.root)
        
        self.root.tk.call("source",getRessourcePath("forest-light.tcl"))
        style.theme_use("forest-light")

        self.root.title("InterSquadron Skin Synchronizer")
        self.root.geometry("500x700")

        #Initialization of the main components
        self.subscriptionsPanel = SubscriptionPanel(self.root)
        self.parametersPanel = ParametersPanel(self.root)

        # Create buttons in a frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="both", pady=2)

        self.ScanButton = ttk.Button(button_frame, text="Scan", style="Accent.TButton", command=self.start_scan)
        self.ScanButton.pack(side="left", padx=10, pady=5)

        self.SyncButton = ttk.Button(button_frame, text="Synchronize", style="Accent.TButton", command=self.start_sync)
        self.SyncButton.pack(side="left", padx=10, pady=5)
        self.lockSyncButton()

        self.consolePanel = ConsolePanel(self.root)

        self.currentScanResult: synchronizer.ScanResult = None

    def lockSyncButton(self):
        self.SyncButton["state"] = "disabled"
    
    def unlockSyncButton(self):
        self.SyncButton["state"] = "enabled"

    def run(self):
        return self.root.mainloop()
    
    def updateScanResult(self, scanResult: synchronizer.ScanResult):
        self.currentScanResult = scanResult

        if scanResult is None:
            self.consolePanel.clearPanel()
            self.lockSyncButton()
        else:
            self.consolePanel.addLine(scanResult.toString())
            if scanResult.IsSyncUpToDate():
                self.lockSyncButton()
            else:
                self.unlockSyncButton()

            


    def start_scan(self):
        
        self.updateScanResult(None)
        scanResult = synchronizer.scanSkins()
        self.updateScanResult(scanResult)
        
        
    
    def start_sync(self):
        if self.currentScanResult is None:
            logging.error("Sync launched with no scan result")
            return
        
        synchronizer.updateAll(self.currentScanResult)
        self.consolePanel.addLine("SYNCHRONIZATION FINISHED")
        #once sync done, lock it
        self.lockSyncButton()

        #Thread(target=self.synchronizeMainCallBack(), daemon=True).start()

    
                