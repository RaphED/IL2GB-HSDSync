import tkinter as tk
from tkinter import ttk

class ResizeGrip(ttk.Frame):
    def __init__(self, master, canvas, min_height=100, max_height=500, on_after_resize = None):
        super().__init__(master, height=8)
        self.canvas = canvas
        self.min_height = min_height
        self.max_height = max_height
        self.on_after_resize = on_after_resize
        
        # Créer deux lignes horizontales pour visualiser la poignée
        self.separator = ttk.Separator(self, orient='horizontal')
        self.separator.pack(fill='x', pady=1)
        self.separator = ttk.Separator(self, orient='horizontal')
        self.separator.pack(fill='x', pady=1)
        
        # Configuration du curseur et des événements
        self.configure(cursor='sb_v_double_arrow', padding=3)
        self.bind('<Button-1>', self.start_resize)
        self.bind('<B1-Motion>', self.do_resize)
        
        # Variables pour le redimensionnement
        self.y = 0
        self.original_height = self.canvas.winfo_height()
    
    def start_resize(self, event):
        self.y = event.y_root
        self.original_height = self.canvas.winfo_height()
    
    def do_resize(self, event):
        delta_y = event.y_root - self.y
        new_height = self.original_height + delta_y
        
        # Limiter la hauteur entre min_height et max_height
        new_height = max(self.min_height, min(new_height, self.max_height))
        
        self.canvas.configure(height=new_height)

        if self.on_after_resize is not None:
            self.after(0, self.on_after_resize)