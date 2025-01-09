import tkinter as tk

class Tooltip:
    """
    A tooltip that appears when hovering over a widget.
    Features:
    - Appears after a delay
    - No flickering
    - Positioned below the widget
    - Can be styled
    """
    
    def __init__(self, widget, text, delay=100, 
                 bg="#ffffe0", fg="black", 
                 padx=5, pady=2,
                 font=None):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.style = {
            "background": bg,
            "foreground": fg,
            "relief": "solid",
            "borderwidth": 1,
            "padx": padx,
            "pady": pady,
            "font": font,
            "justify": "left"
        }
        
        self.tooltip_window = None
        self.schedule_id = None
        
        # Bind events
        self.widget.bind("<Enter>", self._schedule)
        self.widget.bind("<Leave>", self._hide)
        
    def _schedule(self, event=None):
        """Schedule the tooltip to appear after the delay"""
        self._unschedule()  # Cancel any existing schedule
        self.schedule_id = self.widget.after(self.delay, self._show)
        
    def _unschedule(self):
        """Cancel scheduled tooltip"""
        if self.schedule_id:
            self.widget.after_cancel(self.schedule_id)
            self.schedule_id = None
            
    def _show(self):
        """Display the tooltip window"""
        if self.tooltip_window:
            return
            
        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.overrideredirect(True)
        
        # Prevent tooltip from triggering enter/leave events
        self.tooltip_window.bind("<Enter>", lambda e: "break")
        self.tooltip_window.bind("<Leave>", lambda e: "break")
        
        # Create and pack the label
        label = tk.Label(self.tooltip_window, text=self.text, **self.style)
        label.pack()
        
        # Position the tooltip below the widget
        self._position_tooltip()
        
    def _position_tooltip(self):
        """Position the tooltip window below its widget"""
        if not self.tooltip_window:
            return
            
        # Get widget position
        x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Ensure tooltip stays within screen bounds
        screen_width = self.widget.winfo_screenwidth()
        tooltip_width = self.tooltip_window.winfo_reqwidth()
        if x + tooltip_width > screen_width:
            x = screen_width - tooltip_width
            
        self.tooltip_window.geometry(f"+{x}+{y}")
        
    def _hide(self, event=None):
        """Hide the tooltip window"""
        self._unschedule()
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
            
    def update_text(self, new_text):
        """Update the tooltip text"""
        self.text = new_text
        if self.tooltip_window:
            self._hide()
            self._show()