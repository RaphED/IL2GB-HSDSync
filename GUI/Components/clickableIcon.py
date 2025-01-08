import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class CliquableIcon(tk.Label):
    def __init__(self, root, icon_path: str, 
                tooltip_text: str=None, #warning : cannot be used if onMouseOverOpacityFactor is set
                onClick=None,
                opacityFactor: int = 255, #opacity factor comes from 0 to 255
                onMouseOverOpacityFactor: int = 255, #warning, cannot have tooltip if activated
                disabled = False
            ):
        
        super().__init__(root, cursor="hand2")
        # Load and resize the icon
        image = Image.open(icon_path)
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        self.referenceImage = image.resize((24, 24), Image.Resampling.LANCZOS)  # Adjust size as needed

        # Precalculate original alpha to avoid recalculation
        self.original_alpha = self.referenceImage.split()[3]

        self.base_opacityFactor = opacityFactor
        self.disabled = disabled

        self.tooltip = None
        self.tooltip_text = tooltip_text
        self.onClickCommand = onClick

        #Fade parameters
        self.fade_after_id = None
        self.fade_ms = 2000
        self.fade_step_ms = 100
        self.onMouseOverOpacityFactor = onMouseOverOpacityFactor
        self.fade_step_opacityFactor = abs(self.onMouseOverOpacityFactor - self.base_opacityFactor) / (self.fade_ms / self.fade_step_ms)

        #BIND EVENTS
        
        if onClick is not None:
            self.bind('<Button-1>', self.runOnClickCommand)
        
        if tooltip_text is not None:
            self.bind('<Enter>', self.show_tooltip)
            self.bind('<Leave>', self.hide_tooltip)
        #todo : manage tooltip + fadein/out 
        if onMouseOverOpacityFactor != opacityFactor:
            self.bind('<Enter>', self.start_fade_in)
            self.bind('<Leave>', self.start_fade_out)

        self.displayIcon()

    def runOnClickCommand(self, event= None):
        if not self.disabled:
            self.onClickCommand()

    def displayIcon(self, opacityFactor = None):
        if opacityFactor is None:
            opacityFactor = self.base_opacityFactor
        
        #force an opacity factor if disabled
        if self.disabled:
            opacityFactor = 50

        self.current_opacityFactor = opacityFactor
        
        if self.current_opacityFactor == 255:
            #do not perform any calculation if opacity is full
            self.displayedImage = ImageTk.PhotoImage(self.referenceImage)
            self.configure(image=self.displayedImage)
        else:
            img_copy = self.referenceImage.copy()
            # get RGBA chanels
            r, g, b, a = img_copy.split()
            # Calculate new alpha channel by preserving transparenc
            new_alpha = self.original_alpha.point(lambda x: int(x * opacityFactor / 255))
            # Merge with the new alpha
            img_copy = Image.merge('RGBA', (r, g, b, new_alpha))
            self.displayedImage = ImageTk.PhotoImage(img_copy)
            self.configure(image=self.displayedImage)            

    def start_fade_in(self, event):
        if self.fade_after_id:
            self.after_cancel(self.fade_after_id)
        self.fade_to(self.onMouseOverOpacityFactor)
    
    def start_fade_out(self, event):
        if self.fade_after_id:
            self.after_cancel(self.fade_after_id)
        self.fade_to(self.base_opacityFactor)
    
    def fade_to(self, target_opacityFactor):
        if target_opacityFactor == self.current_opacityFactor:
            self.displayIcon(target_opacityFactor)
        else:
            next_opacity = self.current_opacityFactor
            if self.current_opacityFactor < target_opacityFactor:
                next_opacity = min(next_opacity + self.fade_step_opacityFactor, target_opacityFactor)
            else:
                next_opacity = max(next_opacity - self.fade_step_opacityFactor, target_opacityFactor)

            self.displayIcon(opacityFactor=next_opacity)
            self.fade_after_id = self.after(
                ms=self.fade_step_ms,
                func=lambda: self.fade_to(target_opacityFactor)
            )
    
    def show_tooltip(self, event=None):
        """Displays the tooltip"""
        x, y, _, _ = self.bbox("insert")
        x += self.winfo_rootx() + 25
        y += self.winfo_rooty() + 25
        
        # Create new window for tooltip
        self.tooltip = tk.Toplevel(self.master)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(self.tooltip, text=self.tooltip_text, 
            padding=4,
            justify='left',
            background="#ffffe0", 
            relief='solid', 
            borderwidth=1
        )
        label.pack()
    
    def hide_tooltip(self, event=None):
        """Hides the tooltip"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None