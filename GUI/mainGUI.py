import time
from tkinter import ttk
import tkinter as tk
import logging

from pythonServices.filesService import getRessourcePath
from pythonServices.messageBus import MessageBus

from GUI.SubscriptionsPanel import SubscriptionPanel
from GUI.parametersPanel import ParametersPanel
from GUI.consolePanel import ConsolePanel
from GUI.actionsPanel import ActionPanel

import ISSsynchronizer
import ISSScanner

class mainGUI:
    
    def __init__(self):

        #initialise tinker compotent (why root ??)
        self.root = tk.Tk()

        self.root.iconbitmap(getRessourcePath("iss.ico"))

        style = ttk.Style(self.root)
        
        self.root.tk.call("source",getRessourcePath("forest-light.tcl"))
        style.theme_use("forest-light")

        self.root.title("InterSquadron Skin Synchronizer")
        self.root.geometry("800x600")
        
        # 1 - UPPER FRAME
        top_main_frame = tk.Frame(self.root)
        top_main_frame.pack(side="top", fill="both")
        # 1.1 - left upper frame
        left_upper_frame = tk.Frame(top_main_frame)
        left_upper_frame.pack(side="left", fill="both")

        self.subscriptionsPanel = SubscriptionPanel(left_upper_frame)

        # 1.2 - right upper frame
        right_upper_frame = tk.Frame(top_main_frame)
        right_upper_frame.pack(side="right", fill="both")
        
        self.parametersPanel = ParametersPanel(right_upper_frame)
        self.actionPanel = ActionPanel(right_upper_frame, scanCommand = self.start_scan, syncCommand=self.start_sync)

        # 2 - BOTTOM FRAME
        bottom_main_frame = tk.Frame(self.root)
        bottom_main_frame.pack(side="bottom", fill="both")

        self.consolePanel = ConsolePanel(bottom_main_frame)

        #OTHER STORED INFORMATION
        self.currentScanResult: ISSsynchronizer.ScanResult = None

        
    def run(self):
        return self.root.mainloop()
    
    def updateScanResult(self, scanResult: ISSsynchronizer.ScanResult):
        self.currentScanResult = scanResult

        if scanResult is None:
            self.consolePanel.clearPanel()
            self.actionPanel.lockSyncButton()
        else:
            MessageBus.emitMessage(scanResult.toString(), scanResult)
            if scanResult.IsSyncUpToDate():
                self.actionPanel.lockSyncButton()
            else:
                self.actionPanel.unlockSyncButton()

    def start_scan(self):
        self.updateScanResult(None)
        scanResult = ISSScanner.scanAll()
        self.updateScanResult(scanResult)
        self.consolePanel.updateFromMessageBus()
        
        
    
    def start_sync(self):
        if self.currentScanResult is None:
            logging.error("Sync launched with no scan result")
            return
        
        ISSsynchronizer.updateAll(self.currentScanResult)
        MessageBus.emitMessage("SYNCHRONIZATION FINISHED")

        self.consolePanel.updateFromMessageBus()
        #once sync done, lock it
        self.actionPanel.lockSyncButton()

    
                