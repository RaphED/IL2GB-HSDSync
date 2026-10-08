import tkinter as tk
import threading
import logging
import time

from GUI.Components.splashScreen import SplashScreen
import Services.configurationService as configurationService
from Services.filesService import getRessourcePath
from GUI.customTheme import apply_titlebar_color



class FirstLaunchGUI:
    def __init__(self, root):
        self.root = root
        
        self.splash = SplashScreen(root, "SplashScreenFirstLaunch.png")
        #only display the splash screen
        root.withdraw()
        
        self.start_processing()

    def start_processing(self):

        processing_thread = threading.Thread(target=self.do_processing)
        processing_thread.start()

    def do_processing(self):
        start_time = time.time()
        
        mainProgress()
        
        # Ensure minimum 3 seconds display time
        elapsed_time = time.time() - start_time
        min_display_time = 5.0
        if elapsed_time < min_display_time:
            time.sleep(min_display_time - elapsed_time)

        self.root.after(0, self.processing_complete)

    def processing_complete(self):
        #Quit updater with the main process is finished
        self.root.destroy()

def runFirstLaunchGUI():
    root = tk.Tk()
    try:
        root.iconbitmap(getRessourcePath("hsd.ico"))
    except:
        pass
    apply_titlebar_color(root)
    app = FirstLaunchGUI(root)
    root.mainloop()

def mainProgress():
    logging.info("FirstLaunch")
    configurationService.generateConfFile()
    logging.info("New configuration file generated")
    #Then get the path of each game
    for game in configurationService.GAMES.keys():
        foundGamePath = configurationService.tryToFindGamePath(game)
        logging.info(f"{game} found path {foundGamePath}")
        if foundGamePath is not None:
            configurationService.setGameDirectory(game, foundGamePath)