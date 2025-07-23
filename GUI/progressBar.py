import tkinter as tk
from tkinter import ttk

from Services.messageBrocker import MessageBrocker

class ProgressBar(ttk.Progressbar):

    def __init__(self, root: tk):

        super().__init__(root, orient="horizontal", mode="determinate", length=500)
        MessageBrocker.registerProgressHook(self.updateProgress)
        self["value"] = 0
        self["maximum"] = 100
    
    def updateProgress(self, progress: float):
        self["value"] = int(progress*100)
    
