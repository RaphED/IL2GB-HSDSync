import tkinter as tk
from tkinter import messagebox, ttk
import requests
from urllib.parse import urlparse
import threading

from pythonServices.subscriptionsService import importNewCollection


class CollectionURLDialog:
    def __init__(self, parent=None, title="Add new collection from URL"):
        self.result = None
        self.dialog = tk.Toplevel(parent) if parent else tk.Tk()
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        
        # Center the window
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        # Focus on the entry field
        self.url_entry.focus_set()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Label
        ttk.Label(main_frame, text="Copy/Paste URL from HSD website").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Entry for URL
        self.url_entry = ttk.Entry(main_frame, width=50)
        self.url_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.url_entry.bind('<Return>', lambda e: self.validate_url())
        
        # Frame for buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Buttons
        self.validate_btn = ttk.Button(button_frame, text="Validate", command=self.validate_url)
        self.validate_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.RIGHT)
        
        # Progress bar (hidden by default)
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        self.progress.grid_remove()  # Hide initially
        
        # Configure resizing
        main_frame.columnconfigure(0, weight=1)
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
    
    def is_valid_url(self, url):
        """Check if URL has valid format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def load_collection_from_URL(self, url):
        """Load collection from the URL"""
        try:
            return importNewCollection(url)
        except requests.exceptions.RequestException:
            #TODO : add logs
            return None
    
    def validate_url(self):
        """Validate entered URL"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return
        
        # Format validation
        test_url = url if url.startswith(('http://', 'https://')) else 'https://' + url
        if not self.is_valid_url(test_url):
            messagebox.showerror("Error", "Invalid URL format.")
            return
        
        # Disable button and show progress bar
        self.validate_btn.config(state='disabled')
        self.progress.grid()
        self.progress.start()
        
        # Check URL existence in separate thread
        thread = threading.Thread(target=self.load_collection_from_URL_thread, args=(url,))
        thread.daemon = True
        thread.start()
    
    def load_collection_from_URL_thread(self, url):
        """Thread to check URL without blocking interface"""
        loaded_collection = self.load_collection_from_URL(url)
        
        # Schedule interface update in main thread
        self.dialog.after(0, self.on_collection_loaded, url, loaded_collection)
    
    def on_collection_loaded(self, url, loaded_collection):
        """Callback called after URL verification"""
        # Stop progress bar and hide it
        self.progress.stop()
        self.progress.grid_remove()
        self.validate_btn.config(state='normal')
        
        if loaded_collection is not None:
            self.result = loaded_collection
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", f"URL '{url}' is not accessible.")
    
    def on_cancel(self):
        """Dialog cancellation"""
        self.result = None
        self.dialog.destroy()
    
    def show(self):
        """Show dialog and return validated URL or None"""
        self.dialog.wait_window()
        return self.result


# Utility function to easily use the dialog
def ask_collection_url(parent=None):
    """
    Display a dialog box to enter a URL.
    
    Args:
        parent: Parent window (optional)
    
    Returns:
        str: Validated URL or None if cancelled
    """
    dialog = CollectionURLDialog(parent)
    return dialog.show()