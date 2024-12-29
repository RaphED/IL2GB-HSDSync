import tkinter as tk
import threading
from PIL import Image, ImageTk
import requests

from pythonServices.filesService import getRessourcePath



class CrashGUI:
    def __init__(self, root, exception: Exception):
        self.root = root
        self.exception = exception

        self.root = root
        self.size_x = 900
        self.size_y = 600

        self.root.title("Catastrophic system failure !")
        self.root.geometry("900x600")
        
        filepath = getRessourcePath("Crash.jpg")
        original_image = Image.open(filepath)
        self.loading_image = ImageTk.PhotoImage(original_image)
        self.image_label = tk.Label(root, image=self.loading_image)
        self.image_label.pack()

        self.genericMessage = tk.Label(root, text="ISS has crashed",  font=("Arial", 18,"bold"), fg="red")
        self.genericMessage.pack()

        self.errorCause = tk.Label(root, text="",  font=("Arial", 12))
        self.errorCause.pack()
        self.errorDetail = tk.Label(root, text="",  font=("Arial", 12))
        self.errorDetail.pack()
        
        errorDetail = "Cause : Unkwown\nPlease consult log file iss.log if you iss folder"
        try:
            raise self.exception
        except requests.exceptions.ConnectionError:
            self.errorCause.config(text="Cause : No internet connection !")
        except Exception:
            self.errorCause.config(text="Cause : Unkown")
            self.errorDetail.config(text="Please consult log file (iss.log) in you iss folder")


def runCrashGUI(exception: Exception):
    root = tk.Tk()
    app = CrashGUI(root, exception)
    root.mainloop()