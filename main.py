import synchronizer
import configurationService

#check the game directory is properly parametered
if not configurationService.checkConfParamIsValid("IL2GBGameDirectory"):
    raise Exception(f"Bad IL2 Game directory, change configuration file (actual : {configurationService.getConf("IL2GBGameDirectory")})")

scanResult = synchronizer.scanSkins()
print(scanResult.toString())

if scanResult.IsSyncUpToDate():
   print("All skins are up to date. Program end.")
else:
    while True:
        
        answer = input("Do you want to perform the update ? (y) yes, (n) no : ").lower()
        
        if answer == "y":
            print("|||||||| Start skins synchronization ||||||||")
            synchronizer.updateAll(scanResult)
            break
        elif answer == "n":
            print("No skin synchronization performed. Program end.")
            break
        else:
            print("Invalid answer, try again")