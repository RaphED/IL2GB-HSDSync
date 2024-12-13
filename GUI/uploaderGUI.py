import tkinter as tk
import threading
import sys

from PIL import Image, ImageTk

from pythonServices.filesService import getRessourcePath
import ISSupdater

class UploaderGUI:
    def __init__(self, root):
        self.root = root
        self.size_x = 600
        self.size_y = 300

        root.geometry(f"{self.size_x}x{self.size_y}")

        # Créer un label pour l'image de chargement
        filepath = getRessourcePath("downloadSplashScreen.jpg")
        original_image = Image.open(filepath)
        self.loading_image = ImageTk.PhotoImage(original_image)
        self.image_label = tk.Label(root, image=self.loading_image)
        self.image_label.pack(pady=10)

        #Center Image
        self.center_window(self.root, self.size_x, self.size_y)

        # Démarrer le traitement en arrière-plan
        self.start_processing()

    def start_processing(self):

        # Créer un thread pour le traitement
        processing_thread = threading.Thread(target=self.do_processing)
        processing_thread.start()

    def do_processing(self):

        ISSupdater.replaceAndLaunchMainExe(prerelease=False)

        # Mettre à jour l'interface utilisateur depuis le thread principal
        self.root.after(0, self.processing_complete)

    def processing_complete(self):
        sys.exit()

    def center_window(self, window, width, height):
        # Obtenir les dimensions de l'écran
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Calculer la position pour centrer la fenêtre
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Positionner la fenêtre
        window.geometry(f'{width}x{height}+{x}+{y}')

def runUploaderGUI():
    root = tk.Tk()
    root.overrideredirect(True)
    app = UploaderGUI(root)
    root.mainloop()