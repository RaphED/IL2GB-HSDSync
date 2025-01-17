
import textwrap
import tkinter as tk
from tkinter import ttk

from GUI.Components.clickableIcon import CliquableIcon
from GUI.Components.tooltip import Tooltip
from pythonServices.filesService import getIconPath
from pythonServices.subscriptionService import SubscribedCollection

class CollectionBundleCard(ttk.Frame):
    def __init__(self, root, collection: SubscribedCollection, width= 40, on_remove_bundle = None, on_select_bundle = None):
        
        style = ttk.Style()
        style.configure("Bundle.TFrame",
            background="#f8f9fa",
            relief="raised",
            borderwidth=2,
        )
        style.configure("Bundle.TLabel", 
            font=("Helvetica", 9),
            background="#f8f9fa",
            padding=(5, 2)
        )
        
        super().__init__(root, style="Bundle.TFrame")
        self.root = root
        self.collection = collection
        self.on_remove_bundle = on_remove_bundle
        self.on_select_bundle = on_select_bundle
        self.bundle_width = width
        
        self.label = ttk.Label(self, style="Bundle.TLabel")
        self.label.pack(side="left", fill="x",expand=True, padx=5, pady=5)

        Tooltip(self.label, "Click on this bundle to copy it in the filters", delay=500)

        #no trash if there is a proxy
        if len(self.collection.proxy_chain) == 0:
            trashButton = CliquableIcon(
                root=self, 
                icon_path=getIconPath("trash-can.png"),
                tooltip_text="Remove bundle",
                onClick=self.on_remove_bundle
            )
            trashButton.pack(side=tk.RIGHT, padx=2)
        # trashButton = CliquableIcon(
        #     root=bundle_frame, 
        #     icon_path=getIconPath("edit.png"),
        #     tooltip_text="Edit Bundle. Not yet developped...",
        #     disabled=True
        # )
        # trashButton.pack(side=tk.BOTTOM)

        #Click on the bundle send criteria to the filters
        if self.on_select_bundle is not None:
            self.label.bind('<Button-1>', self.on_bundle_click)

        self.after(0, self.update_content())

    def on_bundle_click(self, event = None):
        if self.on_select_bundle is not None:
            self.on_select_bundle()
        
    def update_content(self):
        self.set_bundle_label_content()
    
    def set_bundle_label_content(self):
        label_text = ""
        for proxy in self.collection.proxy_chain:
            label_text += f"Proxy: {proxy}\n"

        for criterion in self.collection.criteria.keys():
            if label_text:
                label_text +="\n"
            label_text += f"{criterion}: {self.collection.criteria[criterion]}"

        #wrap content
        lines = label_text.splitlines()  # Divide the text per line
        wrapped_lines = [textwrap.fill(line, self.bundle_width) for line in lines]  # Wrap each line

        self.label.configure(text="\n".join(wrapped_lines))