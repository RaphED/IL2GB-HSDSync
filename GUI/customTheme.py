"""
HSD Custom Dark Theme for tkinter/ttk
A modern dark theme with green accent colors
"""

from tkinter import ttk
import sys
import ctypes


class HSDDarkTheme:
    """Custom dark theme for HSD application"""
    
    # Color palette
    BG_DARKER = "#1a202c"        # Darker background (for titlebar)
    BG_DARK = "#2d3748"          # Main background
    BG_LIGHT = "#3a4556"         # Lighter background (for inputs, cards)
    BG_HOVER = "#4a5568"         # Hover state
    FG_PRIMARY = "#ffffff"       # Primary text color
    FG_SECONDARY = "#cbd5e0"     # Secondary text color
    FG_DISABLED = "#718096"      # Disabled text color
    ACCENT_PRIMARY = "#48bb78"   # Primary accent (green)
    ACCENT_HOVER = "#38a169"     # Accent hover state
    ACCENT_DARK = "#2f855a"      # Darker accent
    BORDER = "#4a5568"           # Border color
    ERROR = "#f56565"            # Error/invalid color
    SUCCESS = "#48bb78"          # Success messages (green)
    INFO = "#63b3ed"             # Info messages (blue)
    WARNING = "#ed8936"          # Warning messages (orange/chocolate)
    
    @staticmethod
    def _set_window_titlebar_color(root):
        """Set the Windows titlebar color to match the dark theme
        
        Args:
            root: The tkinter root window
        """
        if sys.platform != "win32":
            return  # Only works on Windows
        
        try:
            # Convert hex color to BGR format (Windows uses BGR instead of RGB)
            hex_color = HSDDarkTheme.BG_DARKER.lstrip('#')
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            bgr_color = b << 16 | g << 8 | r
            
            # Get window handle
            hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
            
            # DWMWA_CAPTION_COLOR = 35 (Windows 11)
            # DWMWA_USE_IMMERSIVE_DARK_MODE = 20 (Windows 10 dark mode)
            DWMWA_CAPTION_COLOR = 35
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            
            # Try to set caption color (Windows 11)
            try:
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    DWMWA_CAPTION_COLOR,
                    ctypes.byref(ctypes.c_int(bgr_color)),
                    ctypes.sizeof(ctypes.c_int)
                )
            except:
                pass
            
            # Try to enable dark mode (Windows 10/11)
            try:
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    DWMWA_USE_IMMERSIVE_DARK_MODE,
                    ctypes.byref(ctypes.c_int(1)),
                    ctypes.sizeof(ctypes.c_int)
                )
            except:
                pass
                
        except Exception:
            # Silently fail if the API is not available
            pass
    
    @staticmethod
    def apply(root):
        """Apply the custom dark theme to the application
        
        Args:
            root: The tkinter root window
        """
        style = ttk.Style(root)
        
        # Use 'clam' as base theme (works well for dark themes)
        style.theme_use('clam')
        
        # ===== GENERAL CONFIGURATION =====
        style.configure(".",
            background=HSDDarkTheme.BG_DARK,
            foreground=HSDDarkTheme.FG_PRIMARY,
            bordercolor=HSDDarkTheme.BORDER,
            darkcolor=HSDDarkTheme.BG_DARK,
            lightcolor=HSDDarkTheme.BG_LIGHT,
            troughcolor=HSDDarkTheme.BG_LIGHT,
            focuscolor=HSDDarkTheme.ACCENT_PRIMARY,
            selectbackground=HSDDarkTheme.ACCENT_PRIMARY,
            selectforeground=HSDDarkTheme.FG_PRIMARY,
            selectborderwidth=0,
            font=("Segoe UI", 9)
        )
        
        # ===== FRAME =====
        style.configure("TFrame",
            background=HSDDarkTheme.BG_DARK,
            borderwidth=0
        )
        
        # ===== LABEL =====
        style.configure("TLabel",
            background=HSDDarkTheme.BG_DARK,
            foreground=HSDDarkTheme.FG_PRIMARY,
            borderwidth=0
        )
        
        style.map("TLabel",
            foreground=[("disabled", HSDDarkTheme.FG_DISABLED)]
        )
        
        # ===== BUTTON =====
        style.configure("TButton",
            background=HSDDarkTheme.BG_LIGHT,
            foreground=HSDDarkTheme.FG_PRIMARY,
            bordercolor=HSDDarkTheme.BORDER,
            lightcolor=HSDDarkTheme.BG_LIGHT,
            darkcolor=HSDDarkTheme.BG_LIGHT,
            borderwidth=1,
            focuscolor=HSDDarkTheme.ACCENT_PRIMARY,
            padding=(10, 5),
            relief="flat"
        )
        
        style.map("TButton",
            background=[
                ("active", HSDDarkTheme.BG_HOVER),
                ("disabled", HSDDarkTheme.BG_DARK),
                ("pressed", HSDDarkTheme.BG_DARK)
            ],
            foreground=[
                ("disabled", HSDDarkTheme.FG_DISABLED)
            ],
            bordercolor=[
                ("active", HSDDarkTheme.ACCENT_PRIMARY),
                ("focus", HSDDarkTheme.ACCENT_PRIMARY)
            ]
        )
        
        # ===== ACCENT BUTTON (Primary action button) =====
        style.configure("Accent.TButton",
            background=HSDDarkTheme.ACCENT_PRIMARY,
            foreground=HSDDarkTheme.FG_PRIMARY,
            bordercolor=HSDDarkTheme.ACCENT_PRIMARY,
            lightcolor=HSDDarkTheme.ACCENT_PRIMARY,
            darkcolor=HSDDarkTheme.ACCENT_PRIMARY,
            borderwidth=1,
            padding=(10, 5),
            relief="flat"
        )
        
        style.map("Accent.TButton",
            background=[
                ("active", HSDDarkTheme.ACCENT_HOVER),
                ("disabled", HSDDarkTheme.BG_LIGHT),
                ("pressed", HSDDarkTheme.ACCENT_DARK)
            ],
            foreground=[
                ("disabled", HSDDarkTheme.FG_DISABLED)
            ]
        )
        
        # ===== LABELFRAME =====
        style.configure("TLabelframe",
            background=HSDDarkTheme.BG_DARK,
            foreground=HSDDarkTheme.FG_PRIMARY,
            bordercolor=HSDDarkTheme.BORDER,
            borderwidth=1,
            relief="solid"
        )
        
        style.configure("TLabelframe.Label",
            background=HSDDarkTheme.BG_DARK,
            foreground=HSDDarkTheme.FG_PRIMARY,
            font=("Segoe UI", 9, "bold")
        )
        
        # ===== ENTRY =====
        style.configure("TEntry",
            fieldbackground=HSDDarkTheme.BG_LIGHT,
            background=HSDDarkTheme.BG_LIGHT,
            foreground=HSDDarkTheme.FG_PRIMARY,
            bordercolor=HSDDarkTheme.BORDER,
            lightcolor=HSDDarkTheme.BG_LIGHT,
            darkcolor=HSDDarkTheme.BG_LIGHT,
            insertcolor=HSDDarkTheme.FG_PRIMARY,
            borderwidth=1,
            relief="solid"
        )
        
        style.map("TEntry",
            fieldbackground=[
                ("disabled", HSDDarkTheme.BG_DARK),
                ("readonly", HSDDarkTheme.BG_DARK)
            ],
            foreground=[
                ("disabled", HSDDarkTheme.FG_DISABLED)
            ],
            bordercolor=[
                ("focus", HSDDarkTheme.ACCENT_PRIMARY),
                ("active", HSDDarkTheme.ACCENT_PRIMARY)
            ]
        )
        
        # ===== COMBOBOX =====
        style.configure("TCombobox",
            fieldbackground=HSDDarkTheme.BG_LIGHT,
            background=HSDDarkTheme.BG_LIGHT,
            foreground=HSDDarkTheme.FG_PRIMARY,
            bordercolor=HSDDarkTheme.BORDER,
            lightcolor=HSDDarkTheme.BG_LIGHT,
            darkcolor=HSDDarkTheme.BG_LIGHT,
            arrowcolor=HSDDarkTheme.FG_PRIMARY,
            borderwidth=1,
            relief="solid"
        )
        
        style.map("TCombobox",
            fieldbackground=[
                ("disabled", HSDDarkTheme.BG_DARK),
                ("readonly", HSDDarkTheme.BG_LIGHT)
            ],
            foreground=[
                ("disabled", HSDDarkTheme.FG_DISABLED),
                ("readonly", HSDDarkTheme.FG_PRIMARY)
            ],
            bordercolor=[
                ("focus", HSDDarkTheme.ACCENT_PRIMARY),
                ("active", HSDDarkTheme.ACCENT_PRIMARY)
            ],
            selectbackground=[
                ("readonly", HSDDarkTheme.ACCENT_PRIMARY)
            ],
            selectforeground=[
                ("readonly", HSDDarkTheme.FG_PRIMARY)
            ]
        )
        
        # ===== CHECKBUTTON =====
        style.configure("TCheckbutton",
            background=HSDDarkTheme.BG_DARK,
            foreground=HSDDarkTheme.FG_PRIMARY,
            bordercolor=HSDDarkTheme.BORDER,
            indicatorbackground=HSDDarkTheme.BG_LIGHT,
            indicatorforeground=HSDDarkTheme.ACCENT_PRIMARY,
            focuscolor=HSDDarkTheme.ACCENT_PRIMARY
        )
        
        style.map("TCheckbutton",
            background=[
                ("active", HSDDarkTheme.BG_DARK)
            ],
            foreground=[
                ("disabled", HSDDarkTheme.FG_DISABLED)
            ],
            indicatorbackground=[
                ("selected", HSDDarkTheme.ACCENT_PRIMARY),
                ("active", HSDDarkTheme.BG_HOVER)
            ]
        )
        
        # ===== SCROLLBAR =====
        style.configure("Vertical.TScrollbar",
            background=HSDDarkTheme.BG_LIGHT,
            troughcolor=HSDDarkTheme.BG_DARK,
            bordercolor=HSDDarkTheme.BG_DARK,
            arrowcolor=HSDDarkTheme.FG_PRIMARY,
            borderwidth=0,
            relief="flat"
        )
        
        style.map("Vertical.TScrollbar",
            background=[
                ("active", HSDDarkTheme.ACCENT_PRIMARY),
                ("pressed", HSDDarkTheme.ACCENT_DARK)
            ]
        )
        
        style.configure("Horizontal.TScrollbar",
            background=HSDDarkTheme.BG_LIGHT,
            troughcolor=HSDDarkTheme.BG_DARK,
            bordercolor=HSDDarkTheme.BG_DARK,
            arrowcolor=HSDDarkTheme.FG_PRIMARY,
            borderwidth=0,
            relief="flat"
        )
        
        style.map("Horizontal.TScrollbar",
            background=[
                ("active", HSDDarkTheme.ACCENT_PRIMARY),
                ("pressed", HSDDarkTheme.ACCENT_DARK)
            ]
        )
        
        # ===== PROGRESSBAR =====
        style.configure("Horizontal.TProgressbar",
            background=HSDDarkTheme.ACCENT_PRIMARY,
            troughcolor=HSDDarkTheme.BG_LIGHT,
            bordercolor=HSDDarkTheme.BORDER,
            lightcolor=HSDDarkTheme.ACCENT_PRIMARY,
            darkcolor=HSDDarkTheme.ACCENT_PRIMARY,
            borderwidth=1,
            thickness=20
        )
        
        # ===== SEPARATOR =====
        style.configure("TSeparator",
            background=HSDDarkTheme.BORDER
        )
        
        # ===== TREEVIEW =====
        style.configure("Treeview",
            background=HSDDarkTheme.BG_LIGHT,
            foreground=HSDDarkTheme.FG_PRIMARY,
            fieldbackground=HSDDarkTheme.BG_LIGHT,
            bordercolor=HSDDarkTheme.BORDER,
            borderwidth=1,
            relief="solid"
        )
        
        style.configure("Treeview.Heading",
            background=HSDDarkTheme.BG_DARK,
            foreground=HSDDarkTheme.FG_PRIMARY,
            bordercolor=HSDDarkTheme.BORDER,
            relief="flat"
        )
        
        style.map("Treeview",
            background=[
                ("selected", HSDDarkTheme.ACCENT_PRIMARY)
            ],
            foreground=[
                ("selected", HSDDarkTheme.FG_PRIMARY)
            ]
        )
        
        style.map("Treeview.Heading",
            background=[
                ("active", HSDDarkTheme.BG_HOVER)
            ]
        )
        
        # ===== CUSTOM STYLES =====
        
        # Path label styles (from parametersPanel)
        style.configure("Path.TLabel",
            background=HSDDarkTheme.BG_DARK,
            foreground=HSDDarkTheme.ACCENT_PRIMARY,
            font=("Segoe UI", 9, "underline"),
            padding=5
        )
        
        style.configure("PathError.TLabel",
            background=HSDDarkTheme.ERROR,
            foreground=HSDDarkTheme.FG_PRIMARY,
            font=("Segoe UI", 9, "underline"),
            padding=5
        )
        
        # Set tk widget colors (for non-ttk widgets like Text, Canvas, etc.)
        root.option_add("*Background", HSDDarkTheme.BG_DARK)
        root.option_add("*Foreground", HSDDarkTheme.FG_PRIMARY)
        root.option_add("*selectBackground", HSDDarkTheme.ACCENT_PRIMARY)
        root.option_add("*selectForeground", HSDDarkTheme.FG_PRIMARY)
        root.option_add("*activeBackground", HSDDarkTheme.BG_HOVER)
        root.option_add("*activeForeground", HSDDarkTheme.FG_PRIMARY)
        root.option_add("*highlightBackground", HSDDarkTheme.BG_DARK)
        root.option_add("*highlightColor", HSDDarkTheme.ACCENT_PRIMARY)
        
        # Configure root window
        root.configure(background=HSDDarkTheme.BG_DARK)
        
        # Apply titlebar color (Windows only)
        root.update_idletasks()  # Ensure window is created
        HSDDarkTheme._set_window_titlebar_color(root)


def apply_theme(root):
    """Convenience function to apply the HSD dark theme
    
    Args:
        root: The tkinter root window
    """
    HSDDarkTheme.apply(root)


def apply_titlebar_color(window):
    """Apply dark titlebar color to any window (including Toplevel dialogs)
    
    Args:
        window: The tkinter window (Tk or Toplevel)
    """
    window.update_idletasks()
    HSDDarkTheme._set_window_titlebar_color(window)
