import tkinter as tk
from tkinter import ttk
import threading
from tkinter import messagebox
import webbrowser

from GUI.Components.resizeGrip import ResizeGrip
from ISSScanner import bytesToString
from pythonServices.configurationService import getConf
from pythonServices.filesService import getIconPath
from pythonServices.subscriptionsService import SubscribedCollection, getAllSubcriptions, removeCollection, changeSubscriptionActivation
from GUI.Components.clickableIcon import CliquableIcon
from GUI.Components.collectionURLModal import ask_collection_url

class SubscriptionLine():
    def __init__(self, collection: SubscribedCollection):
        self.id = collection.id
        self.name = collection.name
        self.browserURL = collection.collectionURL #TODO : branch on the web UI instead of API
        self.active = collection.active
        self.size_in_b_unrestricted = collection.size_in_b_unrestricted
        self.size_in_b_restricted_only = collection.size_in_b_restricted_only

class CollectionsPanel():
    def __init__(self, root, on_loading_complete=None, on_loading_start=None, on_collections_change=None):
        self.root = root
        self.on_loading_complete = on_loading_complete
        self.on_loading_start = on_loading_start
        self.on_collections_change = on_collections_change
        self.subscriptionLines: list[SubscriptionLine] = []

        label = ttk.Label(text="Collections", font=("Arial", 10,"bold"))
        label.pack(side="left", fill="x",padx=5)
        collection_frame = ttk.LabelFrame(root, labelwidget=label, padding=(5, 5))
        collection_frame.pack(fill=tk.BOTH,padx=2, pady=2)

        collection_list_frame = ttk.Frame(collection_frame)
        collection_list_frame.pack(padx=0, pady=0)
        
        self.canvas = tk.Canvas(collection_list_frame)
        self.resize_grip = ResizeGrip(collection_list_frame, self.canvas, min_height=100, max_height=500, on_after_resize=self.on_resize)
        self.resize_grip.pack(fill='x', side='bottom')
        
        self.scrollbar = ttk.Scrollbar(collection_list_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.configure(height=152)
        

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Activate or desactivate mousewheel event
        self.canvas.bind('<Enter>', self._bind_mousewheel)
        self.canvas.bind('<Leave>', self._unbind_mousewheel)
        
        self.list_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.list_frame, anchor='nw')
        
        bottom_frame = tk.Frame(collection_frame)
        bottom_frame.pack(pady=0)
        self.import_button = ttk.Button(bottom_frame, text="Import new collection", command=self.import_new_collection)
        self.import_button.pack(side=tk.LEFT, pady=5, padx=10)
        
        self.list_frame.bind('<Configure>',
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        
        # Bind to check scrollbar visibility after content changes
        self.list_frame.bind('<Configure>', self._on_frame_configure)
        
        self.collections_buttons_registry:list[CliquableIcon] = []

    def emit_loading(self): 
        #local locks
        self.lock_actions()

        #external emit
        if self.on_loading_start:
            self.root.after(0, self.on_loading_start)

    def emit_loading_completed(self):
        #local unlocks
        self.unlock_actions()

        #external emit
        if self.on_loading_complete:
            self.root.after(0, self.on_loading_complete)
            
    def emit_collections_change(self):
        #external emit
        if self.on_collections_change:
            self.root.after(0, self.on_collections_change)

    def lock_actions(self):
        self.import_button["state"] = "disabled"
        for button in self.collections_buttons_registry:
            button.disable()

    def unlock_actions(self):
        self.import_button["state"] = "enabled"
        for button in self.collections_buttons_registry:
            button.enable()

    def loadCollections(self):
        
        self.emit_loading()
        
        #clear the collections
        self.subscriptionLines = []
        #This is the most time consuming part, as it has to download the remote catalog and the remote iss files
        for collection in getAllSubcriptions():
            self.subscriptionLines.append(SubscriptionLine(collection))
        
        self.root.after(0, self._update_list)
        self.emit_loading_completed()

    def loadCollections_async(self):
        threading.Thread(target=self.loadCollections).start()

    def _update_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        self.collections_buttons_registry = []

        for line in self.subscriptionLines:
            frame = ttk.Frame(self.list_frame)
            frame.pack(fill=tk.X, padx=5, pady=1)

            toggle_button = None
            if line.active:
                toggle_button = CliquableIcon(
                    root=frame,
                    icon_path=getIconPath("plain-circle.png"),
                    tooltip_text="Click to disable collection (won't be synchonised)",
                    onClick=lambda o=line: self._toggle_item(o)
                )
            else:
                toggle_button = CliquableIcon(
                    root=frame, 
                    icon_path=getIconPath("circle.png"),
                    tooltip_text="Click to activate collection",
                    onClick=lambda o=line: self._toggle_item(o)
                )
            toggle_button.pack(side=tk.LEFT, padx=2)
            self.collections_buttons_registry.append(toggle_button)
            
            #display the size corresponding to the current censorship parameter
            displayed_size = line.size_in_b_unrestricted
            if getConf("applyCensorship"):
                displayed_size = line.size_in_b_restricted_only

            text_line = f"{line.name} ({bytesToString(displayed_size)})"
            ttk.Label(frame, text=text_line, width=38).pack(side=tk.LEFT, padx=5)
            
            trash_button = CliquableIcon(
                root=frame, 
                icon_path=getIconPath("trash-can.png"),
                tooltip_text="Remove collection",
                onClick=lambda o=line: self._delete_item(o)
            )
            trash_button.pack(side=tk.RIGHT, padx=2)
            self.collections_buttons_registry.append(trash_button)
            
            edit_button = CliquableIcon(
                root=frame, 
                icon_path=getIconPath("magnifying-glass.png"),
                tooltip_text="See to collection on HSD website",
                onClick=lambda o=line: self._open_collection_on_browser(o)
            )
            edit_button.pack(side=tk.RIGHT, padx=2)
            self.collections_buttons_registry.append(edit_button)
        
        # Check scrollbar visibility after updating the list
        self.root.after(10, self._update_scrollbar_visibility)

    def _update_scrollbar_visibility(self):
        # Get the height of the content and the canvas
        content_height = self.list_frame.winfo_reqheight()
        canvas_height = self.canvas.winfo_height()
        
        # Show/hide scrollbar based on content height
        if content_height > canvas_height:
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
        else:
            self.scrollbar.pack_forget()
            self.canvas.configure(yscrollcommand=None)
            # Reset view to top when hiding scrollbar
            self.canvas.yview_moveto(0)

    def _on_frame_configure(self, event=None):
        # Update the scrollregion to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        
        # Check if scrolling is needed
        self._update_scrollbar_visibility()


    def import_new_collection(self):
        result = ask_collection_url(self.root)
        if result is not None:
            self.loadCollections_async()

    def _toggle_item(self, item: SubscriptionLine):
        if item.active:
            changeSubscriptionActivation(item.id, False)
            item.active = False
        else:
            changeSubscriptionActivation(item.id, True)
            item.active = True
        
        self._update_list()
        self.emit_collections_change()

    def _delete_item(self, item: SubscriptionLine):
        answer = messagebox.askyesno(title='confirmation',
                    message=f'Are you sure you want to delete "{item.name}" collection ?')
        if answer:
            removeCollection(item.id)
            self.subscriptionLines = [l for l in self.subscriptionLines if l.name != item.name]
            self._update_list()
            #only perform change if the collection is activated
            if item.active:
                self.emit_collections_change()

    def _open_collection_on_browser(self, item: SubscriptionLine):
        webbrowser.open(item.browserURL)

    #MOUSE EVENTS (for the scroll)
    def _bind_mousewheel(self, event):
        # Activer le scroll quand la souris entre dans le canvas
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _unbind_mousewheel(self, event):
        # Désactiver le scroll quand la souris quitte le canvas
        self.canvas.unbind_all("<MouseWheel>")
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_resize(self):
        self._update_scrollbar_visibility()