import localService
import remoteService
import subscriptionService

class ScanResult:
    def __init__(self):
        self.missingSkins = dict[str, list]()
        self.toBeUpdatedSkins = dict[str, list]()
        self.toBeRemovedSkins= list()

    def appendMissingSkin(self, source, remoteSkinInfo):
        self.missingSkins[source].append(remoteSkinInfo)

    def appendToBeUpdateSkin(self, source, remoteSkinInfo):
        self.toBeUpdatedSkins[source].append(remoteSkinInfo)

    def appendToBeRemovedSkin(self, localSkinInfo):
        self.toBeRemovedSkins.append(localSkinInfo)

    def toString(self):
        returnString = ""
        
        allSources = self.missingSkins.keys() | self.toBeUpdatedSkins.keys()
        
        for source in allSources:
            returnString += f"*********** {source} ***********\n"
            returnString += "Missing skins:\n"
            for skin in self.missingSkins[source]:
                returnString += f"\t- {skin['Skin0']}\n"

            returnString += "To be updated skins:\n"
            for skin in self.toBeUpdatedSkins[source]:
                returnString += f"\t- {skin['Skin0']}\n"

        returnString += "To be removed skins:\n"
        for skin in self.toBeRemovedSkins:
            returnString += f"\t- {skin['ddsFileName']}\n"

        return returnString


def scanSkins():
    
    #get the local skins list in memory
    localSkinsCollection = localService.getSkinsList()

    #load all subscriptions
    subscribedCollectionList = subscriptionService.getAllSubscribedCollection()

    #identify the used sources
    usedSource = []
    for collection in subscribedCollectionList:
        if collection.source not in usedSource:
            usedSource.append(collection.source)
    
    subscribedSkins = dict[str,list]()
    #  and get all the skins from each source matching with the subscriptions
    for source in usedSource:
        subscribedSkins[source] = list()
        for skin in remoteService.getSkinsCatalogFromSource(source):
            #check if the skin matches with a subcription
            for collection in subscribedCollectionList:
                if collection.source == source and collection.match(skin):
                    subscribedSkins[source].append(skin)
                    break #to avoid to add multiple times the same skin
    
        
    scanResult = ScanResult()
    
    #then, for each source, check if we can find the remote skin matching with the local skin
    for source in usedSource:
        
        #initialise result collections
        scanResult.missingSkins[source] = list()
        scanResult.toBeUpdatedSkins[source] = list()

        for remoteSkin in subscribedSkins[source]:
            foundLocalSkin = None
            for localSkin in localSkinsCollection:
                if remoteSkin["Plane"] == localSkin["aircraft"]: #prefiltering to optimize search
                    if remoteSkin["Skin0"] == localSkin["ddsFileName"]: #TODO : manage 2 files skins
                        #the skins is already there. Up to date ? 
                        if remoteSkin["HashDDS0"] != localSkin["md5"]:
                            scanResult.appendToBeUpdateSkin(source, remoteSkin)
                        
                        foundLocalSkin = localSkin
                        #and then no need to pursue the research
                        break
            
            if not foundLocalSkin:
                scanResult.appendMissingSkin(source, remoteSkin)

    #Then list all local skins not present in the remote skins
    for localSkin in localSkinsCollection:
        foundRemoteSkin = None
        #check in all sources
        for source in usedSource:
            for remoteSkin in subscribedSkins[source]:
                if remoteSkin["Plane"] == localSkin["aircraft"]: #prefiltering to optimize search
                    if remoteSkin["Skin0"] == localSkin["ddsFileName"]: #TODO : manage 2 files skins
                        foundRemoteSkin = remoteSkin
                        break
            if foundRemoteSkin is not None:
                break
        #the skin cannot be found in any source
        if foundRemoteSkin is None:
            scanResult.appendToBeRemovedSkin(localSkin)

    return scanResult


