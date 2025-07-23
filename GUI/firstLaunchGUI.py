import tkinter as tk
import threading
import logging

from GUI.Components.splashScreen import SplashScreen
import Services.configurationService as configurationService



class FirstLaunchGUI:
    def __init__(self, root):
        self.root = root
        
        self.splash = SplashScreen(root, "SplashScreenFirstLaunch.jpg")
        #only display the splash screen
        root.withdraw()
        
        self.start_processing()

    def start_processing(self):

        processing_thread = threading.Thread(target=self.do_processing)
        processing_thread.start()

    def do_processing(self):
        
        mainProgress()

        self.root.after(0, self.processing_complete)

    def processing_complete(self):
        #Quit updater with the main process is finished
        self.root.destroy()

def runFirstLaunchGUI():
    root = tk.Tk()
    app = FirstLaunchGUI(root)
    root.mainloop()

def mainProgress():
    logging.info("FirstLaunch")
    configurationService.generateConfFile()
    logging.info("New configuration file generated")
    #Then get the IL2 path
    foundIL2Path = configurationService.tryToFindIL2Path()
    logging.info(f"IL2 found path {foundIL2Path}")
    if foundIL2Path is not None:
        configurationService.update_config_param("IL2GBGameDirectory", foundIL2Path)