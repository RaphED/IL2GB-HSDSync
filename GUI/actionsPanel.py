import tkinter as tk
from tkinter import ttk

class ActionPanel:

    def __init__(self, root: tk, scanCommand, syncCommand):
    
        self.root = root

        frame = tk.Frame(root)
        frame.pack(expand=True)

        self.ScanButton = ttk.Button(frame, text="Scan", style="Accent.TButton", command=scanCommand)
        self.ScanButton.pack(side=tk.LEFT, padx=10)

        self.SyncButton = ttk.Button(frame, text="Synchronize", style="Accent.TButton", command=syncCommand)
        self.SyncButton.pack(side=tk.LEFT, padx=10)
        self.lockSyncButton()

    def lockSyncButton(self):
        self.SyncButton["state"] = "disabled"
    
    def unlockSyncButton(self):
        self.SyncButton["state"] = "enabled"
    
