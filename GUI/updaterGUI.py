import tkinter as tk
import threading
import sys

from GUI.splashScreen import SplashScreen
import ISSupdater



class UpdaterGUI:
    def __init__(self, root, update_withPrerelease):
        self.root = root
        self.update_withPrerelease = update_withPrerelease
        
        self.splash = SplashScreen(root, "SplashScreenUpdater.jpg")
        #only display the splash screen
        root.withdraw()
        
        self.start_processing()

    def start_processing(self):

        processing_thread = threading.Thread(target=self.do_processing)
        processing_thread.start()

    def do_processing(self):
        
        #This is the main process
        ISSupdater.replaceAndLaunchMainExe(prerelease=self.update_withPrerelease)

        self.root.after(0, self.processing_complete)

    def processing_complete(self):
        #Quit updater with the main process is finished
        sys.exit()

def runUpdaterGUI(update_withPrerelease):
    root = tk.Tk()
    app = UpdaterGUI(root, update_withPrerelease)
    root.mainloop()