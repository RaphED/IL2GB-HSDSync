
from tkinter import ttk
import tkinter as tk
from threading import Thread

from pythonServices.filesService import getRessourcePath

from GUI.SubscriptionsPanel import SubscriptionPanel
from GUI.parametersPanel import ParametersPanel

class mainGUI:
    
    #g_text_widget=None
    def __init__(self, synchronizeMainCallBack):

        #register the callback
        #TODO : remove the callback ?
        self.synchronizeMainCallBack = synchronizeMainCallBack

        #initialise tinker compotent (why root ??)
        self.root = tk.Tk()

        self.root.iconbitmap(getRessourcePath("iss.ico"))

        style = ttk.Style(self.root)
        
        self.root.tk.call("source",getRessourcePath("forest-light.tcl"))
        style.theme_use("forest-light")

        self.root.title("InterSquadron Skin Synchronizer")
        self.root.geometry("500x540")

        #Initialization of the main components
        self.subscriptionsPanel = SubscriptionPanel(self.root)
        self.parametersPanel = ParametersPanel(self.root)

        

        button2_frame = ttk.Frame(self.root)
        button2_frame.pack(fill="both", pady=2)
        self.start_sync_button = ttk.Button(button2_frame, text="StartSync !", style="Accent.TButton", command=self.start_sync)
        self.start_sync_button.pack(padx=10, pady=10)

    def run(self):
        return self.root.mainloop()
    

    def start_sync(self):
        # TODO ERIC faire plus propre
        # global g_text_widget
        # """Open a new window with terminal-like functionality."""
        # terminal = tk.Toplevel(self.root)  # Create a new Toplevel window
        # terminal.title("Syncro des skins :")
        # terminal.geometry("400x300")

        # # Create a Text widget for displaying terminal output
        # text_widget = tk.Text(terminal, wrap="word", height=15, width=50)
        # text_widget.pack(expand=True, fill="both")
        # text_widget.config(state=tk.DISABLED)  # Disable editing
        # g_text_widget = text_widget
        # # Simulate terminal output
        # # self.print_to_terminal(f"Début de la syncro!")

        # #The main core function :

        Thread(target=self.synchronizeMainCallBack(), daemon=True).start()

    # TODO ERIC faire plus propre
    # def print_to_terminal(self, text):
    #     global g_text_widget
    #     text_widget = g_text_widget
    #     """Add text to the terminal output in the Text widget."""
    #     text_widget.config(state=tk.NORMAL)  # Enable editing
    #     text_widget.insert(tk.END, text + "\n")  # Insert text
    #     text_widget.yview(tk.END)  # Auto-scroll to the end
    #     text_widget.config(state=tk.DISABLED)  # Disable editing again

    
                