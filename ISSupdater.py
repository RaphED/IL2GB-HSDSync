import subprocess
import sys
import time
import os
import logging

from pythonServices.filesService import downloadFile, getTempFolderFullPath, copyFile
from versionManager import getLastRelease
import pythonServices.loggingService


def downloadLastReleaseFile(fileName, prerelease = False):
    release_info = getLastRelease(prerelease = prerelease)
    for asset in release_info["assets"]:
        if asset["name"] == fileName:
            return downloadFile(asset["browser_download_url"])
            
    #file not found
    raise Exception(f"Cannot find {fileName} in last release")


def runNewIndependantProcess(args):
    logging.info(f"Running new independant command : {args}")
    subprocess.Popen(
        args,  # Arguments to the updater
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

def downloadAndRunUpdater(prerelease = False):
    
    logging.info("Updater : Start download And Run updater")
    #download the last EXE
    newExePath = downloadLastReleaseFile("ISS.exe", prerelease = prerelease)
    #run the last updater in an independant process
    runNewIndependantProcess([newExePath, "-updater"])

def replaceAndLaunchMainExe(prerelease = False):
    logging.info("Updater : Replace and Launch Main Exe")

    try:
        printWarning("ISS autoupdater is running. Please wait for the program to restart...")
        
        newExeFilePath = os.path.join(getTempFolderFullPath(), "ISS.exe")
        #HACK : if the new exe is not there, rerun the download
        if not os.path.exists(newExeFilePath):
            logging.warning(f"Autoupdater Cannot find the last exe file at {newExeFilePath}")
            return downloadAndRunUpdater(prerelease = prerelease)
            
        #add a timer to make sure previous main exe is stopped
        #TODO : perform a while checker
        time.sleep(5)

        #copy the file next to the exe to replace with another name
        mainExeFilePath = os.path.join(os.path.curdir, "ISS.exe")
        
        copyFile(newExeFilePath, mainExeFilePath)

        #then run !
        runNewIndependantProcess([mainExeFilePath])

    except Exception as e:
        print(e)

if __name__ == "__main__":

    replaceAndLaunchMainExe()
