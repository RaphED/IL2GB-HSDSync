import synchronizer

scanResult = synchronizer.scanSkins()
print(scanResult.toString())

synchronizer.updateAll(scanResult)