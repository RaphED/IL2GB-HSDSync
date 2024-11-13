import synchronizer
import configurationService
from subscriptionService import isSubcriptionFolderEmpty

def performPreExecutionChecks():

    #check the game directory is properly parametered
    if not configurationService.checkConfParamIsValid("IL2GBGameDirectory"):
        raise Exception(
            f"Bad IL2 Game directory, current game path is set to : {configurationService.getConf("IL2GBGameDirectory")}\n"
            f"Change value in configuration file {configurationService.config_file}"
        )

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

    #once the prec checks passed, perform the global scan
    scanResult = synchronizer.scanSkins()
    print(scanResult.toString())

    #then as the user for the update if any
    if scanResult.IsSyncUpToDate():
        printSuccess("All skins are up to date.")
    else:
        while True:
            
            answer = input("Do you want to perform the update ? (y) yes, (n) no : ").lower()
            
            if answer == "y":
                printSuccess("|||||||| START SYNC ||||||||")
                synchronizer.updateAll(scanResult)
                printSuccess("|||||||| END OF SYNC |||||||")
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