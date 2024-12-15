import sys
import pythonServices.configurationService as configurationService
from pythonServices.filesService import cleanTemporaryFolder

import logging
from versionManager import isCurrentVersionUpToDate
import ISSupdater

from GUI.mainGUI import runMainGUI
from GUI.updaterGUI import runUpdaterGUI

def performAtProgramLauchChecks():

    #make sure the temporary folder is clean -> do not do that due to update !
    cleanTemporaryFolder()

     #check conf file is generated
    if not configurationService.configurationFileExists():
        #at first create a conf file with default params
        logging.info("New configuration file generated")
        configurationService.generateConfFile()
        #Then get the IL2 path
        foundIL2Path = configurationService.tryToFindIL2Path()
        logging.info(f"IL2 found path {foundIL2Path}")
        if foundIL2Path is not None:
            configurationService.update_config_param("IL2GBGameDirectory", foundIL2Path)
        

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
        ISSupdater.downloadAndRunUpdater(prerelease = update_withPrerelease)
    #UPDATER MODE
    elif updater_mode:
        runUpdaterGUI(update_withPrerelease)
    #NORMAL MODE
    else:
        performAtProgramLauchChecks()
        runMainGUI()