import synchronizer
import configurationService
from subscriptionService import isSubcriptionFolderEmpty

def performPreExecutionChecks():

    #check conf file is generated
    if not configurationService.configurationFileExists():
        printWarning("No configuration file found")
        #and help the user to generate a new one
        generateConfFileWithConsole()

    #check the game directory is properly parametered
    if not configurationService.checkConfParamIsValid("IL2GBGameDirectory"):
        raise Exception(
            f"Bad IL2 Game directory, current game path is set to : {configurationService.getConf("IL2GBGameDirectory")}\n"
            f"Change value in configuration file {configurationService.config_file}"
        )
    
def generateConfFileWithConsole():
    printWarning("A new Configuration file is about to be generated")
    #at first create a conf file with default params
    newConf = configurationService.generateConfFile()

    
    print("Please wait while trying to find IL2 directory on your HDDs...")
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

    print("IS3 provides two modes :\n - (a) keep all downloaded skins\n - (b) remove all skins and keep only the ones you are subscripted to.")
    deletionMode = input("What mode do you want ? (a) or (b) ? ").lower()
    while True:
        if deletionMode == "a":
            configurationService.update_config_param("autoRemoveUnregisteredSkins", False)
            break
        elif deletionMode == "b":
            configurationService.update_config_param("autoRemoveUnregisteredSkins", True)
            break
        else:
            printError("Unknown anwser. Please anwser a or b")

    printSuccess("Configuration performed with success")
    
def printError(text):
    print("\033[91m{}\033[00m".format(text))

def printWarning(text):
    print("\033[93m{}\033[00m".format(text))

def printSuccess(text):
    print("\033[92m{}\033[00m".format(text))

######### MAIN ###############

try:
    performPreExecutionChecks()

    if isSubcriptionFolderEmpty():
        printWarning("Subscription folder is empty.\nAdd .is3 file(s) to subscribe to any skins collection")

    printWarning("SCAN launched. Please wait...")
    #once the prec checks passed, perform the global scan
    scanResult = synchronizer.scanSkins()
    printSuccess("SCAN finished")
    print(scanResult.toString())
    

    #then as the user for the update if any
    if scanResult.IsSyncUpToDate():
        printSuccess("All skins are up to date.")
    else:
        while True:
            
            answer = input("Do you want to perform the update ? (y) yes, (n) no : ").lower()
            
            if answer == "y":
                printSuccess("||||||||| START SYNC ||||||||")
                synchronizer.updateAll(scanResult)
                printSuccess("|||||||||  END SYNC  ||||||||")
                break
            elif answer == "n":
                print("No skin synchronization performed.")
                break
            else:
                print("Invalid answer, try again")

    printSuccess("I3S ended properly.")

except Exception as e:
    printError(e)
    printError("I3S ended with an error.")

input("Press any key to quit program... ")