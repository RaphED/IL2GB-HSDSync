import synchronizer

scanResult = synchronizer.scanSkins()
print(scanResult.toString())
print("|||||||| FILES UPDATE ||||||||")
synchronizer.updateAll(scanResult)