import synchronizer
import configurationService

#check the game directory is properly parametered
if not configurationService.checkConfParamIsValid("IL2GBGameDirectory"):
    raise Exception(f"Bad IL2 Game directory, change configuration file (actual : {configurationService.getConf("IL2GBGameDirectory")})")

scanResult = synchronizer.scanSkins()
print(scanResult.toString())

print("|||||||| FILES UPDATE ||||||||")
synchronizer.updateAll(scanResult)