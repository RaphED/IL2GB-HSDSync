import subprocess
import sys
import requests
import synchronizer
import pythonServices.configurationService as configurationService
from pythonServices.subscriptionService import isSubcriptionFolderEmpty, getAllSubscribedCollection
from packaging.version import Version


VERSION="2.0.0.0"
API_URL = f"https://api.github.com/repos/RaphED/IL2GB-inter-squadrons-skins-synchronizer/releases/latest"

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

    print("ISS provides two modes :\n - (a) keep all downloaded skins\n - (b) remove all skins and keep only the ones you are subscripted to.")
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



def get_latest_release_info():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
    
######### MAIN ###############
if __name__ == "__main__":

    release_info = get_latest_release_info()
    if release_info:
        latest_version = release_info["tag_name"]
        current_version = Version(VERSION)
        remote_version = Version(latest_version)
        if remote_version > current_version:
            # Assuming the first asset is what we want
            assets = release_info.get("assets", [])
            if assets:
                download_url = assets[0]["browser_download_url"]
                try:
                        # Start the updater with the specified arguments
                        subprocess.Popen(
                            ["ISSupdater.exe"],  # Arguments to the updater
                            shell=False,            # Don't use a shell to avoid unnecessary dependencies
                            close_fds=True,         # Close file descriptors to detach from the parent process
                            creationflags=subprocess.DETACHED_PROCESS if sys.platform == "win32" else 0  # Detach process on Windows
                        )
                        sys.exit()  # Close the main application
                except Exception as e:
                    sys.exit(1)  # Exit with an error code    

try:
    performPreExecutionChecks()

    #CUSTOM PHOTOS SECTION
    cockpitNotesMode = configurationService.getConf("cockpitNotesMode")
    if cockpitNotesMode != "noSync":
        print(f"Custom photos scan mode : {cockpitNotesMode}")
        printWarning("Photos scan launched. Please wait...")
        scanResult = synchronizer.scanCustomPhotos()
        if len(scanResult) > 0:
            print("Some photos has to be updated :")
            print([customPhoto["aircraft"] for customPhoto in scanResult])
            while True:
                answer = input("Do you want to perform the update ? (y) yes, (n) no : ").lower()
                if answer == "y":
                    print("Update started...")
                    synchronizer.updateCustomPhotos(scanResult)
                    print("Update done")
                    break
                elif answer == "n":
                    print("ok no update")
                    break
                else:
                    print("Invalid answer, try again")        
        else:
            printSuccess("All custom photos are up to date")

    #SKINS SECTION
    if isSubcriptionFolderEmpty():
        printWarning("Subscription folder is empty.\nAdd .iss file(s) to subscribe to any skins collection")

    subscribedCollections = getAllSubscribedCollection()
    print("Subscribed collections : ")
    for collection in subscribedCollections:
        print(f"\t-{collection.subcriptionName}")

    printWarning("SKINS scan launched. Please wait...")
    #once the prec checks passed, perform the global scan
    scanResult = synchronizer.scanSkins()
    printSuccess("SKINS scan finished")
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