import tkinter as tk
from tkinter import ttk

from pythonServices.messageBrocker import MessageBrocker

class ProgressBar:

    def __init__(self, root: tk):

        self.root = root
        self.bar = ttk.Progressbar(self.root, orient="horizontal", mode="determinate", length=500)
        self.bar.pack(side=tk.TOP, padx=10, pady=10)
        MessageBrocker.registerProgressHook(self.updateProgress)
        self.bar["value"] = 0
        self.bar["maximum"] = 100
    
    def updateProgress(self, progress: float):
        self.bar["value"] = int(progress*100)
    
