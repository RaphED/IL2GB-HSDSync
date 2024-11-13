import localService
from localService import getSpaceUsageOfLocalSkinCatalog
import remoteService
from remoteService import getSourceParam, getSpaceUsageOfRemoteSkinCatalog
import subscriptionService
from configurationService import getConf

class ScanResult:
    def __init__(self):
        self.subscribedSkins = dict[str, list]()
        self.missingSkins = dict[str, list]()
        self.toBeUpdatedSkins = dict[str, list]()
        self.toBeRemovedSkins= list()

    def appendMissingSkin(self, source, remoteSkinInfo):
        self.missingSkins[source].append(remoteSkinInfo)

    def appendToBeUpdateSkin(self, source, remoteSkinInfo):
        self.toBeUpdatedSkins[source].append(remoteSkinInfo)

    def appendToBeRemovedSkin(self, localSkinInfo):
        self.toBeRemovedSkins.append(localSkinInfo)

    def getUsedSources(self):
        return self.missingSkins.keys() | self.toBeUpdatedSkins.keys()
    
    def getDiskUsageStats(self):
        return {
            "subscribedSkinsSpace":{source:getSpaceUsageOfRemoteSkinCatalog(source, self.subscribedSkins[source]) for source in self.getUsedSources()},
            "missingSkinsSpace": {source:getSpaceUsageOfRemoteSkinCatalog(source, self.missingSkins[source]) for source in self.getUsedSources()},
            "toBeUpdatedSkinsSpace": {source:getSpaceUsageOfRemoteSkinCatalog(source, self.toBeUpdatedSkins[source]) for source in self.getUsedSources()},
            "toBeRemovedSkinsSpace": getSpaceUsageOfLocalSkinCatalog(self.toBeRemovedSkins),
        }
    
    def toString(self):
        returnString = ""

        diskSpaceStats = self.getDiskUsageStats()

        returnString += f"** Unregistered skins: ({bytesToString(diskSpaceStats["toBeRemovedSkinsSpace"])})\n"
        for skin in self.toBeRemovedSkins:
            returnString += f"\t- {skin['name']}\n"
        if len(self.toBeRemovedSkins) == 0:
            returnString +="- None -\n"

        for source in self.getUsedSources():
            returnString += f"*********** Sync with {source} ***********\n"
            returnString += f"** Missing skins: ({bytesToString(sum(diskSpaceStats["missingSkinsSpace"].values()))})\n"
            for skin in self.missingSkins[source]:
                returnString += f"\t- {skin[getSourceParam(source, "name")]}\n"
            if len(self.missingSkins[source]) == 0:
                returnString +="- None -\n"

            returnString += f"** To be updated skins: ({bytesToString(sum(diskSpaceStats["toBeUpdatedSkinsSpace"].values()))})\n"
            for skin in self.toBeUpdatedSkins[source]:
                returnString += f"\t- {skin[getSourceParam(source, "name")]}\n"
            if len(self.toBeUpdatedSkins[source]) == 0:
                returnString +="- None -\n"

        returnString += f"Total disk space usage : {bytesToString(sum(diskSpaceStats["subscribedSkinsSpace"].values()))}"

        return returnString
    
    def IsSyncUpToDate(self):
        if sum([len(self.missingSkins[source]) for source in self.missingSkins.keys()]) != 0:
            return False
        if sum([len(self.toBeUpdatedSkins[source]) for source in self.toBeUpdatedSkins.keys()]) != 0:
            return False
        if getConf("autoRemoveUnregisteredSkins") and len(self.toBeRemovedSkins) != 0:
            return False
        return True

def bytesToString(file_size_bytes: int):
    file_size_kb = file_size_bytes / 1024

    if file_size_kb < 1:
        return f"{file_size_bytes} B"

    file_size_mb = file_size_kb / 1024

    if file_size_mb < 1:
        return f"{file_size_kb:.2f} KB"
    
    file_size_gb = file_size_mb / 1024

    if file_size_gb < 1:
        return f"{file_size_mb:.2f} MB"
    
    return f"{file_size_gb:.2f} GB"

def scanSkins():
    
    scanResult = ScanResult()

    #get the local skins list in memory
    localSkinsCollection = localService.getSkinsList()

    #load all subscriptions
    subscribedCollectionList = subscriptionService.getAllSubscribedCollection()

    #identify the used sources
    usedSource = []
    for collection in subscribedCollectionList:
        if collection.source not in usedSource:
            usedSource.append(collection.source)
    
    #  and get all the skins from each source matching with the subscriptions
    for source in usedSource:
        scanResult.subscribedSkins[source] = list()
        for skin in remoteService.getSkinsCatalogFromSource(source):
            #check if the skin matches with a subcription
            for collection in subscribedCollectionList:
                if collection.source == source and collection.match(skin):
                    scanResult.subscribedSkins[source].append(skin)
                    break #to avoid to add multiple times the same skin
    
        
    
    
    #then, for each source, check if we can find the remote skin matching with the local skin
    for source in usedSource:
        
        #initialise result collections
        scanResult.missingSkins[source] = list()
        scanResult.toBeUpdatedSkins[source] = list()

        for remoteSkin in scanResult.subscribedSkins[source]:
            foundLocalSkin = None
            for localSkin in localSkinsCollection:
                #not the same A/C, no match
                if remoteSkin[getSourceParam(source, "aircraft")] != localSkin["aircraft"]:
                    continue
                
                #not the same skin main file, no match
                if remoteSkin[getSourceParam(source, "mainSkinFileName")] != localSkin["mainFileName"]:
                    continue
                
                #there is a match !
                foundLocalSkin = localSkin
                                
                #the skins is already there. Up to date ? 
                skinAsToBeUpdated = False

                #check main file md5
                if remoteSkin[getSourceParam(source, "mainFileMd5")] != localSkin["mainFileMd5"]:
                    skinAsToBeUpdated = True
                else:
                    #the main file is the same, but we have to look at the secondary file if any
                    secondarySkinFileName = remoteSkin.get(getSourceParam(source, "secondarySkinFileName"))
                    
                    #if there is a secondary file declared on the remote
                    if secondarySkinFileName is not None and secondarySkinFileName != "":
                        
                        #check if we can find the secondary on the local
                        if localSkin.get("secondaryFileName") is None:
                            skinAsToBeUpdated = True
                        #we have a secondary file, check the name is the same one (should always be)
                        elif remoteSkin[getSourceParam(source, "secondarySkinFileName")] != localSkin["secondaryFileName"]:
                            skinAsToBeUpdated = True
                        #check the md5 is the proper one
                        elif remoteSkin[getSourceParam(source, "secondaryFileMd5")] != localSkin["secondaryFileMd5"]:
                            skinAsToBeUpdated = True
                
                #if any modification has to be made, put the skin in the list to be updated
                if skinAsToBeUpdated:
                    scanResult.appendToBeUpdateSkin(source, remoteSkin)

                #and then no need to pursue the research as if we are there, we have found a match
                break
            
            if not foundLocalSkin:
                scanResult.appendMissingSkin(source, remoteSkin)

    #Then list all local skins not present in the remote skins
    for localSkin in localSkinsCollection:
        foundRemoteSkin = None
        #check in all sources
        for source in usedSource:
            for remoteSkin in scanResult.subscribedSkins[source]:
                if remoteSkin[getSourceParam(source, "aircraft")] == localSkin["aircraft"]: #prefiltering to optimize search
                    #TODO: Manage orphans skins
                    if remoteSkin[getSourceParam(source, "mainSkinFileName")] == localSkin["mainFileName"]:
                        foundRemoteSkin = remoteSkin
                        break
            if foundRemoteSkin is not None:
                break
        #the skin cannot be found in any source
        if foundRemoteSkin is None:
            scanResult.appendToBeRemovedSkin(localSkin)

    return scanResult


def updateRegisteredSkins(scanResult: ScanResult):
    
    for source in scanResult.getUsedSources():
        #import all missings skins
        for skin in scanResult.missingSkins[source]:
            updateSingleSkinFromRemote(source, skin)

        #import all to be updated skins
        for skin in scanResult.toBeUpdatedSkins[source]:
            updateSingleSkinFromRemote(source, skin)


def deleteUnregisteredSkins(scanResult: ScanResult):
    for skin in scanResult.toBeRemovedSkins:
        deleteSkinFromLocal(skin)

def updateAll(scanResult: ScanResult):
    if getConf("autoRemoveUnregisteredSkins"):
        deleteUnregisteredSkins(scanResult)
    updateRegisteredSkins(scanResult)

def updateSingleSkinFromRemote(source, remoteSkin):

    print(f"Downloading {remoteSkin[getSourceParam(source, "name")]}...")

    #download to temp the skin
    downloadedFiles = remoteService.downloadSkinToTempDir(source, remoteSkin)

    for file in downloadedFiles:
    
        #Move the file to the target directory and replace existing file if any
        final_path = localService.moveSkinFromPathToDestination(file, remoteSkin[getSourceParam(source, "aircraft")])

        print(f"Downloaded to {final_path}")

def deleteSkinFromLocal(localSkinInfo):
    localService.removeSkin(localSkinInfo)
    print(f"Deleted skin : {localSkinInfo["name"]}")