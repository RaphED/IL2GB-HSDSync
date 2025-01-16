
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
        self.on_remove_bundle = on_remove_bundle
        self.on_select_bundle = on_select_bundle

        label_text = get_bundle_label_content(collection, width)
        
        label = ttk.Label(self, text=label_text, style="Bundle.TLabel")
        label.pack(side="left", fill="x",expand=True, padx=5, pady=5)

        Tooltip(label, "Click on this bundle to copy it in the filters", delay=500)

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
            label.bind('<Button-1>', self.on_bundle_click)

    def on_bundle_click(self, event = None):
        if self.on_select_bundle is not None:
            self.on_select_bundle()
        
def get_bundle_label_content(collection: SubscribedCollection, width):
    label_text = ""
    for criterion in collection.criteria.keys():
        if label_text:
            label_text +="\n"
        label_text += f"{criterion}: {collection.criteria[criterion]}"

    #wrap content
    lines = label_text.splitlines()  # Divide the text per line
    wrapped_lines = [textwrap.fill(line, width) for line in lines]  # Wrap each line

    return "\n".join(wrapped_lines)