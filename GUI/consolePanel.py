import tkinter as tk

from pythonServices.messageBrocker import MessageBrocker

class ConsolePanel:
    def __init__(self, root: tk):
        self.root = root
        
        # Create a frame to hold both Text and Scrollbar
        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill="both")
        
        # Create Scrollbar widget
        self.scrollbar = tk.Scrollbar(self.frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create Text widget and connect it to Scrollbar
        self.text_widget = tk.Text(self.frame, wrap="char", height=15, 
                                 yscrollcommand=self.scrollbar.set)
        self.text_widget.pack(side=tk.LEFT, expand=True, fill="both")
        
        # Configure Scrollbar to scroll the Text widget
        self.scrollbar.config(command=self.text_widget.yview)
        
        # Configure tags for formatting
        self.text_widget.tag_configure("red", foreground="red")
        self.text_widget.tag_configure("green", foreground="green")
        self.text_widget.tag_configure("blue", foreground="blue")
        self.text_widget.tag_configure("chocolate", foreground="chocolate")
        self.text_widget.tag_configure("bold", font=("TkDefaultFont", 10, "bold"))
        self.text_widget.tag_configure("italic", font=("TkDefaultFont", 10, "italic"))

        MessageBrocker.registerConsoleHook(self.addLine)

    def parse_and_insert_text(self, text: str):
        """Parse text and insert with appropriate tags"""
        # If no tags, insert directly
        if '<' not in text:
            self.text_widget.insert(tk.END, text)
            return

        current_pos = 0
        current_tags = []  # List of active tags

        while current_pos < len(text):
            # Look for next tag (opening or closing)
            next_tag_pos = text.find('<', current_pos)
            
            if next_tag_pos == -1:
                # No more tags, insert remaining text with current tags
                remaining_text = text[current_pos:]
                if remaining_text:
                    self.text_widget.insert(tk.END, remaining_text, tuple(current_tags))
                break
            
            # Insert text before the tag with current tags
            if next_tag_pos > current_pos:
                content = text[current_pos:next_tag_pos]
                self.text_widget.insert(tk.END, content, tuple(current_tags))
            
            # Process the tag
            if text[next_tag_pos:next_tag_pos+2] == '</':
                # Closing tag
                end_pos = text.find('>', next_tag_pos)
                if end_pos == -1:
                    break
                tag = text[next_tag_pos+2:end_pos]
                if tag in current_tags:
                    current_tags.remove(tag)
                current_pos = end_pos + 1
            else:
                # Opening tag
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