import sys

import Services.loggingService as loggingService
from Services.versionManager import isCurrentVersionUpToDate
import Services.updateService as updateService

from GUI.mainGUI import runMainGUI
from GUI.updaterGUI import runUpdaterGUI
from GUI.crashGUI import runCrashGUI

######### MAIN ###############
if __name__ == "__main__":

    force_update = False
    updater_mode = False
    no_update = False
    update_withPrerelease = False
    debug_mode = False

    for arg in sys.argv[1:]:
        if arg == '-updater':
            updater_mode = True
        elif arg == '-no-update':
            no_update = True
        elif arg == '-force-update':
            force_update = True
        elif arg == '-prerelease':
            update_withPrerelease = True
        elif arg == '-debug':
            debug_mode = True
    
    #INITIALISE LOGS
    loggingService.initialise_logger(debug_mode=debug_mode)

    try:
        #Check if an update has to be launched
        if not no_update and not isCurrentVersionUpToDate(prerelease = update_withPrerelease) or force_update:
            updateService.downloadAndRunUpdater(prerelease = update_withPrerelease)
        #UPDATER MODE
        elif updater_mode:
            runUpdaterGUI(update_withPrerelease)
        #NORMAL MODE
        else:
            runMainGUI()
    except Exception as e:
        loggingService.error(e)
        runCrashGUI(exception=e)