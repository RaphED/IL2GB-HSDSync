import tkinter as tk
from tkinter import messagebox, ttk
import threading
import webbrowser
import os

from Services.remoteService import RemoteCollection, getRemoteCollectionsCatalog
from GUI.Components.clickableIcon import CliquableIcon
import Services.subscriptionsService as SubscriptionsService


class CollectionURLDialog:
    def __init__(self, parent=None, title="Search for new collections"):
        self.result = None
        self.dialog = tk.Toplevel(parent) if parent else tk.Tk()
        self.dialog.title(title)
        self.dialog.geometry("800x600")
        self.dialog.resizable(True, True)
        
        # Center the window
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.collections = []
        self.filtered_collections = []
        
        self.setup_ui()
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # Start loading collections
        self.load_collections()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Label
        ttk.Label(main_frame, text="Select collections to subscribe to:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Search/Filter frame
        filter_frame = ttk.Frame(main_frame)
        filter_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_entry = ttk.Entry(filter_frame, width=50)
        self.filter_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.filter_entry.bind('<KeyRelease>', lambda e: self.apply_filter())
        
        # Treeview for collections
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame, columns=('name', 'creator', 'skins', 'size'), 
                                  show='tree headings', selectmode='extended', 
                                  yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Bind double-click to subscribe to single collection
        self.tree.bind('<Double-Button-1>', self.on_double_click)
        
        # Column configuration
        self.tree.column('#0', width=30, stretch=False, anchor=tk.CENTER)
        self.tree.column('name', width=250, anchor=tk.W)
        self.tree.column('creator', width=150, anchor=tk.W)
        self.tree.column('skins', width=80, anchor=tk.CENTER)
        self.tree.column('size', width=100, anchor=tk.E)
        
        # Column headings
        self.tree.heading('#0', text='', anchor=tk.CENTER)
        self.tree.heading('name', text='Name', anchor=tk.W)
        self.tree.heading('creator', text='Creator', anchor=tk.W)
        self.tree.heading('skins', text='Skins', anchor=tk.CENTER)
        self.tree.heading('size', text='Size', anchor=tk.E)
        
        # Store icons to prevent garbage collection
        self.collection_icons = {}
        
        # Progress bar (hidden by default)
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.progress.grid_remove()  # Hide initially
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Loading collections...")
        self.status_label.grid(row=4, column=0, sticky=tk.W, pady=(0, 10))
        
        # Frame for buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, sticky=(tk.W, tk.E))
        
        # Buttons
        self.validate_btn = ttk.Button(button_frame, text="Subscribe to selected", command=self.validate_selection, state='disabled')
        self.validate_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.RIGHT)
        
        # Configure resizing
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
    
    def format_size(self, size_in_bytes):
        """Format size in bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_in_bytes < 1024.0:
                return f"{size_in_bytes:.1f} {unit}"
            size_in_bytes /= 1024.0
        return f"{size_in_bytes:.1f} TB"
    
    def load_collections(self):
        """Load collections from remote service"""
        self.progress.grid()
        self.progress.start()
        self.validate_btn.config(state='disabled')
        
        # Load in separate thread
        thread = threading.Thread(target=self.load_collections_thread)
        thread.daemon = True
        thread.start()
    
    def load_collections_thread(self):
        """Thread to load collections without blocking interface"""
        try:
            collections = getRemoteCollectionsCatalog()
            self.dialog.after(0, self.on_collections_loaded, collections, None)
        except Exception as e:
            self.dialog.after(0, self.on_collections_loaded, None, str(e))
    
    def on_collections_loaded(self, collections, error):
        """Callback called after collections are loaded"""
        self.progress.stop()
        self.progress.grid_remove()
        
        if error:
            self.status_label.config(text=f"Error loading collections: {error}")
            messagebox.showerror("Error", f"Failed to load collections:\n{error}")
            return
        
        self.collections = collections
        self.filtered_collections = collections
        self.populate_tree()
        self.status_label.config(text=f"{len(collections)} collection(s) available")
        self.validate_btn.config(state='normal')
        
        # Focus on filter entry
        self.filter_entry.focus_set()
    
    def populate_tree(self):
        """Populate tree with collections"""
        # Clear existing items and icons
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.collection_icons.clear()
        
        # Add collections
        for collection in self.filtered_collections:
            size_str = self.format_size(collection.size_in_b_unrestricted())
            self.tree.insert('', tk.END, iid=str(collection.id()),
                           values=(collection.name(), collection.creator(), 
                                  collection.skin_count(), size_str))
        
        # Add clickable icons for each collection
        self.tree.update_idletasks()
        self.add_collection_icons()
    
    def add_collection_icons(self):
        """Add clickable icons to open collection URLs in browser"""
        icon_path = os.path.join("Ressources", "icons", "magnifying-glass.png")
        
        for item_id in self.tree.get_children():
            # Get collection by ID
            collection = next((c for c in self.filtered_collections if str(c.id()) == item_id), None)
            if collection:
                # Get position of the item in the tree
                bbox = self.tree.bbox(item_id, '#0')
                if bbox:
                    x, y, width, height = bbox
                    # Create clickable icon (18x18 size)
                    icon = CliquableIcon(
                        self.tree,
                        icon_path=icon_path,
                        tooltip_text="Open collection in browser",
                        onClick=lambda url=collection.browser_URL(): webbrowser.open(url),
                        opacityFactor=200,
                        onMouseOverOpacityFactor=255,
                        icon_size=18
                    )
                    # Place the icon in the first column, centered
                    icon.place(x=x + (width - 18) // 2, y=y + (height - 18) // 2)
                    # Store reference to prevent garbage collection
                    self.collection_icons[item_id] = icon
    
    def apply_filter(self):
        """Apply filter to collections list"""
        filter_text = self.filter_entry.get().lower().strip()
        
        if not filter_text:
            self.filtered_collections = self.collections
        else:
            self.filtered_collections = [
                c for c in self.collections
                if (filter_text in c.name().lower() or 
                    filter_text in c.creator().lower() or
                    filter_text in c.description().lower())
            ]
        
        self.populate_tree()
        self.status_label.config(text=f"{len(self.filtered_collections)} of {len(self.collections)} collection(s)")
    
    def on_double_click(self, event):
        """Handle double-click on a collection to subscribe to it"""
        # Get the item under cursor
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        # Get the collection
        collection_id = int(item)
        collection = next((c for c in self.collections if c.id() == collection_id), None)
        
        if not collection:
            return
        
        # Subscribe to this single collection
        self.validate_btn.config(state='disabled')
        self.progress.grid()
        self.progress.start()
        self.status_label.config(text=f"Subscribing to {collection.name()}...")
        
        # Subscribe in separate thread
        thread = threading.Thread(target=self.subscribe_collections_thread, args=([collection],))
        thread.daemon = True
        thread.start()
    
    def validate_selection(self):
        """Validate selected collections"""
        selected_items = self.tree.selection()
        
        if not selected_items:
            messagebox.showwarning("No selection", "Please select at least one collection.")
            return
        
        # Get selected collection IDs
        selected_ids = [int(item) for item in selected_items]
        
        # Get full collection objects
        selected_collections = [c for c in self.collections if c.id() in selected_ids]
        
        # Disable button and show progress bar
        self.validate_btn.config(state='disabled')
        self.progress.grid()
        self.progress.start()
        self.status_label.config(text=f"Subscribing to {len(selected_collections)} collection(s)...")
        
        # Subscribe in separate thread
        thread = threading.Thread(target=self.subscribe_collections_thread, args=(selected_collections,))
        thread.daemon = True
        thread.start()
    
    def subscribe_collections_thread(self, collections):
        """Thread to subscribe to collections without blocking interface"""
        try:
            for collection in collections:
                SubscriptionsService.importNewCollection(collection.api_URL())
            self.dialog.after(0, self.on_subscription_completed, collections, None)
        except Exception as e:
            self.dialog.after(0, self.on_subscription_completed, None, str(e))
    
    def on_subscription_completed(self, collections, error):
        """Callback called after subscription process"""
        # Stop progress bar and hide it
        self.progress.stop()
        self.progress.grid_remove()
        self.validate_btn.config(state='normal')
        
        if error:
            self.status_label.config(text="Error during subscription")
            messagebox.showerror("Error", f"Failed to subscribe to collections:\n{error}")
        else:
            self.result = collections
            self.dialog.destroy()
    
    def on_cancel(self):
        """Dialog cancellation"""
        self.result = None
        self.dialog.destroy()
    
    def show(self):
        """Show dialog and return selected collections or None"""
        self.dialog.wait_window()
        return self.result


# Utility function to easily use the dialog
def ask_collection_url(parent=None):
    """
    Display a dialog box to select collections.
    
    Args:
        parent: Parent window (optional)
    
    Returns:
        list: List of selected RemoteCollection objects or None if cancelled
    """
    dialog = CollectionURLDialog(parent)
    return dialog.show()