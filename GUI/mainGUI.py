import time
from tkinter import ttk
import tkinter as tk
from threading import Thread

from pythonServices.filesService import getRessourcePath

from GUI.SubscriptionsPanel import SubscriptionPanel
from GUI.parametersPanel import ParametersPanel
from GUI.consolePanel import ConsolePanel

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
        self.root.geometry("500x700")

        #Initialization of the main components
        self.subscriptionsPanel = SubscriptionPanel(self.root)
        self.parametersPanel = ParametersPanel(self.root)

        # Create buttons in a frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="both", pady=2)

        self.ScanButton = ttk.Button(button_frame, text="Scan", style="Accent.TButton", command=self.start_sync)
        self.ScanButton.pack(side="left", padx=10, pady=5)

        self.SyncButton = ttk.Button(button_frame, text="Synchronize", style="Accent.TButton", command=self.start_sync)
        self.SyncButton.pack(side="left", padx=10, pady=5)
        self.SyncButton["state"] = "disabled"

        self.consolePanel = ConsolePanel(self.root)
        self.consolePanel.addLine("TEST LINE !!!!!")

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

        self.consolePanel.addLine("TEST LINE 2")
        time.sleep(2)
        self.consolePanel.addLine("TEST LINE 3")
        time.sleep(2)
        self.consolePanel.addLine("TEST LINE 4")
        time.sleep(2)
        self.consolePanel.addLine("TEST LINE 5")
        #Thread(target=self.synchronizeMainCallBack(), daemon=True).start()

    
                