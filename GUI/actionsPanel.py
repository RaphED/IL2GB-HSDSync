import tkinter as tk
from tkinter import ttk

class ActionPanel:

    def __init__(self, root: tk, scanCommand, syncCommand):
    
        self.root = root

        frame = tk.Frame(root)
        frame.pack(side=tk.RIGHT)

        self.ScanButton = ttk.Button(frame, text="Scan", style="Accent.TButton", command=scanCommand)
        self.ScanButton.pack(side=tk.LEFT, padx=10, pady=10)

        self.SyncButton = ttk.Button(frame, text="Synchronize", style="Accent.TButton", command=syncCommand)
        self.SyncButton.pack(side=tk.RIGHT, padx=10, pady=10)
        self.lockSyncButton()

    def lockSyncButton(self):
        self.SyncButton["state"] = "disabled"
        self.SyncButton.configure(style='')
    
    def unlockSyncButton(self):
        self.SyncButton.configure(style="Accent.TButton")
        self.SyncButton["state"] = "enabled"

    def lockScanButton(self):
        self.ScanButton["state"] = "disabled"
        self.ScanButton.configure(style='')
    
    def unlockScanButton(self):
        self.ScanButton.configure(style="Accent.TButton")
        self.ScanButton["state"] = "enabled"
        
        





