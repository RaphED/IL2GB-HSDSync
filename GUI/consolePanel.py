import tkinter as tk
import re
from typing import List, Tuple, Dict

from pythonServices.messageBrocker import MessageBrocker

class ConsolePanel:
    def __init__(self, root: tk):
        self.root = root
        
        self.text_widget = tk.Text(self.root, wrap="char", height=15)
        self.text_widget.pack(expand=True, fill="both")
        
        # Configuration des tags pour le formatage
        self.text_widget.tag_configure("red", foreground="red")
        self.text_widget.tag_configure("green", foreground="green")
        self.text_widget.tag_configure("blue", foreground="blue")
        self.text_widget.tag_configure("orange", foreground="orange")
        self.text_widget.tag_configure("bold", font=("TkDefaultFont", 10, "bold"))
        self.text_widget.tag_configure("italic", font=("TkDefaultFont", 10, "italic"))

        MessageBrocker.registerConsoleHook(self.addLine)

    def parse_and_insert_text(self, text: str):
        """Parse le texte et insère avec les tags appropriés"""
        # Si pas de balises, insérer directement
        if '<' not in text:
            self.text_widget.insert(tk.END, text)
            return

        current_pos = 0
        current_tags = []  # Liste des tags actifs

        while current_pos < len(text):
            # Chercher la prochaine balise (ouvrante ou fermante)
            next_tag_pos = text.find('<', current_pos)
            
            if next_tag_pos == -1:
                # Plus de balises, insérer le reste du texte avec les tags courants
                remaining_text = text[current_pos:]
                if remaining_text:
                    self.text_widget.insert(tk.END, remaining_text, tuple(current_tags))
                break
            
            # Insérer le texte avant la balise avec les tags courants
            if next_tag_pos > current_pos:
                content = text[current_pos:next_tag_pos]
                self.text_widget.insert(tk.END, content, tuple(current_tags))
            
            # Traiter la balise
            if text[next_tag_pos:next_tag_pos+2] == '</':
                # Balise fermante
                end_pos = text.find('>', next_tag_pos)
                if end_pos == -1:
                    break
                tag = text[next_tag_pos+2:end_pos]
                if tag in current_tags:
                    current_tags.remove(tag)
                current_pos = end_pos + 1
            else:
                # Balise ouvrante
                end_pos = text.find('>', next_tag_pos)
                if end_pos == -1:
                    break
                tag = text[next_tag_pos+1:end_pos]
                current_tags.append(tag)
                current_pos = end_pos + 1
    
    def addLine(self, text):
        self.text_widget.config(state=tk.NORMAL)
        self.parse_and_insert_text(text)
        self.text_widget.insert(tk.END, "\n")
        self.text_widget.yview(tk.END)
        self.text_widget.config(state=tk.DISABLED)

    def clearPanel(self):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.config(state=tk.DISABLED)