import tkinter as tk
from tkinter import ttk
import webbrowser

from GUI.Components.clickableIcon import CliquableIcon
from GUI.Components.tooltip import Tooltip
from pythonServices.filesService import getIconPath
from pythonServices.subscriptionService import SubscribedCollection

class ProxyLink(ttk.Label):
    def __init__(self, parent, url, command=None, max_lenght = 30):
        
        displayed_url = url
        if len(displayed_url)>max_lenght:
            displayed_url = f"...{url[len(displayed_url)-max_lenght:]}"
        
        super().__init__(
            parent,
            text=displayed_url,
            cursor="hand2",
            style="ProxyLink.TLabel"
        )
        if command:
            self.bind("<Button-1>", lambda e: command(url))
        
        # Style pour simuler un lien
        style = ttk.Style()
        style.configure(
            "ProxyLink.TLabel",
            foreground="blue",
            background="#f8f9fa",
            font=("Courier", 9, "underline")
        )
        Tooltip(self,text=url)

class CollectionBundleCard(ttk.Frame):
    def __init__(self, root, collection: SubscribedCollection, width=40, on_remove_bundle=None, on_select_bundle=None):
        super().__init__(root)
        
        # Configuration du style de la carte
        style = ttk.Style()
        style.configure(
            "Bundle.TFrame",
            background="#f8f9fa",
            relief="raised",
            borderwidth=2
        )
        style.configure(
            "BundleContent.TLabel",
            background="#f8f9fa",
            font=("Helvetica", 9),
            wraplength=width * 7 # Approximation pour la largeur du texte
        )
        
        self.configure(style="Bundle.TFrame", padding=5)
        self.collection = collection
        self.on_remove_bundle = on_remove_bundle
        self.on_select_bundle = on_select_bundle
        
        # Proxy section
        if self.collection.proxy_chain:
            self.proxy_frame = ttk.Frame(self)
            self.proxy_frame.pack(fill="x", padx=2, pady=(0, 5))
            
            for proxy in self.collection.proxy_chain:
                proxy_container = ttk.Frame(self.proxy_frame)
                proxy_container.pack(fill="x", pady=1)
                
                ttk.Label(
                    proxy_container,
                    text="Proxy: "
                ).pack(side="left")
                
                ProxyLink(
                    proxy_container,
                    url=proxy,
                    command=self.on_proxy_click
                ).pack(side="left")
        
        # Criteria section
        if self.collection.criteria:
            self.criteria_frame = ttk.Frame(self)
            self.criteria_frame.pack(fill="x", padx=2)
            
            for criterion, value in self.collection.criteria.items():
                criterion_label = ttk.Label(
                    self.criteria_frame,
                    text=f"{criterion}: {value}"
                )
                criterion_label.pack(fill="x", pady=1)
        
        # Delete button - not available if proxy
        if len(self.collection.proxy_chain) == 0 and self.on_remove_bundle:
            self.trash_button = CliquableIcon(
                root=self,
                icon_path=getIconPath("trash-can.png"),
                tooltip_text="Remove bundle",
                onClick=self.on_remove_bundle
            )
            self.trash_button.pack(side="right", padx=5, pady=5)
        
        # Main click on the component
        if self.on_select_bundle:
            self.bind('<Button-1>', self.on_bundle_click)
            Tooltip(self, "Click on this bundle to copy it in the filters", delay=500)
    
    def on_proxy_click(self, proxy_path):
        webbrowser.open(proxy_path)
        #stop click propagation
        return "break"
    
    def on_bundle_click(self, event=None):
        if self.on_select_bundle:
            self.on_select_bundle()