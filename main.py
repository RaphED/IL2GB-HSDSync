import sys
import pythonServices.configurationService as configurationService
from pythonServices.filesService import cleanTemporaryFolder

import logging
from versionManager import isCurrentVersionUpToDate
import ISSupdater

from GUI.mainGUI import runMainGUI
from GUI.updaterGUI import runUpdaterGUI

def performAtProgramLauchChecks():

    #make sure the temporary folder is clean ->x do not o that due to update !
    cleanTemporaryFolder()

     #check conf file is generated
    if not configurationService.configurationFileExists():
        printError("No configuration file found")
        #and help the user to generate a new one
        generateConfFileWithConsole()


def performPreScanChecks():

    #check the game directory is properly parametered
    if not configurationService.checkConfParamIsValid("IL2GBGameDirectory"):
        raise Exception(
            f"Bad IL2 Game directory, current game path is set to : {configurationService.getConf("IL2GBGameDirectory")}\n"
            f"Directory must be the main game directory, generally named 'IL-2 Sturmovik Battle of Stalingrad' and containing two folders 'bin' and 'data'\n"
            f"Change value in the GUI 'Parameters' section"
        )
    
def generateConfFileWithConsole():
    printWarning("A new Configuration file is about to be generated")
    #at first create a conf file with default params
    newConf = configurationService.generateConfFile()

    
    printWarning("Please wait while trying to find IL2 directory on your HDDs...")
    foundIL2Path = configurationService.tryToFindIL2Path()
    #foundIL2Path = None
    if foundIL2Path is None:
        printError("Cannot find IL2 path")
        while True:
            manualPath = input("Please provide manually the path of your IL2 install directory : ")
            if configurationService.checkIL2InstallPath(manualPath):
                printSuccess("IL2 path found")
                foundIL2Path = manualPath
                break
            else:
                printError("Cannot identiry that directory as the main IL2 path")
                print("Please try again")
    else:
        printSuccess("IL2 path found")
    
    configurationService.update_config_param("IL2GBGameDirectory", foundIL2Path)

    printSuccess("Configuration initialized with success")
    
def printError(text):
    print("\033[91m{}\033[00m".format(text))

def printWarning(text):
    print("\033[93m{}\033[00m".format(text))

def printSuccess(text):
    print("\033[92m{}\033[00m".format(text))

######### MAIN ###############
if __name__ == "__main__":

    force_update = False
    updater_mode = False
    update_withPrerelease = False
    debug_mode = False

    for arg in sys.argv[1:]:
        if arg == '-updater':
            updater_mode = True
        elif arg == '-force-update':
            force_update = True
        elif arg == '-prerelease':
            update_withPrerelease = True
        elif arg == '-debug':
            debug_mode = True
    
    #INITIALISE LOGS
    logLevel = logging.DEBUG
    if not debug_mode:
        logLevel = logging.INFO
 
    logging.basicConfig(
        filename='iss.log',       # Le fichier de log où les messages seront enregistrés
        level= logLevel,          # Le niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format='%(asctime)s - %(levelname)s - %(message)s',  # Format du message
        datefmt='%Y-%m-%d %H:%M:%S'    # Format de la date
    )
    
    
    #Check if an update has to be launched
    if not isCurrentVersionUpToDate(prerelease = update_withPrerelease) or force_update:
        printError("A new version of ISS has been found")
        printWarning("Please wait for the update and the automatic restart...")
        ISSupdater.downloadAndRunUpdater(prerelease = update_withPrerelease)
        sys.exit()
    
    if updater_mode:
        runUpdaterGUI(update_withPrerelease)
    else:
        performAtProgramLauchChecks()
        runMainGUI()