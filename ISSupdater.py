import subprocess
import sys
import time
import os

from pythonServices.filesService import downloadFile, moveFile
from versionManager import get_latest_release_info


def downloadLastReleaseFile(fileName):
    release_info = get_latest_release_info()
    for asset in release_info["assets"]:
        if asset["name"] == fileName:
            return downloadFile(asset["browser_download_url"])
            
    #file not found
    raise Exception(f"Cannot find {fileName} in last release")

def performAutoUpdate():
    
    #download the last updater
    updaterPath = downloadLastReleaseFile("ISSUpdater.exe")

    #run the last updater in an independant process
    runNewProcess(updaterPath)

    #KILL CURRENT PROCESS !
    sys.exit()

    #TODO : delete the installer file after update

def runNewProcess(filePath):
    subprocess.Popen(
        [filePath],  # Arguments to the updater
        shell=False,            # Don't use a shell to avoid unnecessary dependencies
        close_fds=True,         # Close file descriptors to detach from the parent process
        creationflags=subprocess.DETACHED_PROCESS if sys.platform == "win32" else 0  # Detach process on Windows
    )


def printError(text):
    print("\033[91m{}\033[00m".format(text))

def printWarning(text):
    print("\033[93m{}\033[00m".format(text))

def printSuccess(text):
    print("\033[92m{}\033[00m".format(text))


if __name__ == "__main__":

    try:
        printWarning("ISS autoupdater is running. Please wait for the program to restart...")
        #download the last exe
        newExePath = downloadLastReleaseFile("ISS.exe")

        #add a timer to make sure previous main exe is stopped
        #TODO : perform a while checker
        time.sleep(5)

        #replace with the last 
        newExePath = moveFile(newExePath, os.path.curdir)

        #then run !
        runNewProcess(newExePath)

    except Exception as e:
        print(e)
