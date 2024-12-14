import tkinter as tk

from PIL import Image, ImageTk

from pythonServices.filesService import getRessourcePath

class SplashScreen:
    def __init__(self, root, imageFileName):
        self.root = root
        self.size_x = 600
        self.size_y = 300

        self.splash = tk.Toplevel()
        self.splash.overrideredirect(True)

        self.splash.geometry(f"{self.size_x}x{self.size_y}")

        # Créer un label pour l'image de chargement
        filepath = getRessourcePath(imageFileName)
        original_image = Image.open(filepath)
        self.loading_image = ImageTk.PhotoImage(original_image)
        self.image_label = tk.Label(self.splash, image=self.loading_image)
        self.image_label.pack()

        #Center Image
        self.center_window(self.splash, self.size_x, self.size_y)

    def center_window(self, window, width, height):
        # Obtenir les dimensions de l'écran
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Calculer la position pour centrer la fenêtre
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Positionner la fenêtre
        window.geometry(f'{width}x{height}+{x}+{y}')