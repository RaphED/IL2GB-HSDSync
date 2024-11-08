import localService
import remoteService

class registeredCollection:
    def __init__():
        squadron = "IRRE"


class ScanResult:
    def __init__(self):
        self.missingSkins = []
        self.toBeUpdatedSkins = []
        self.toBeRemovedSkins= []

    def appendMissingSkin(self, remoteSkinInfo):
        self.missingSkins.append(remoteSkinInfo)

    def appendToBeUpdateSkin(self, remoteSkinInfo):
        self.toBeUpdatedSkins.append(remoteSkinInfo)

    def appendToBeRemovedSkin(self, localSkinInfo):
        self.toBeRemovedSkins.append(localSkinInfo)

    def toString(self):
        returnString = ""
        returnString += "Missing skins:\n"
        for skin in self.missingSkins:
            returnString += f"\t- {skin['Skin0']}\n"

        returnString += "To be updated skins:\n"
        for skin in self.toBeUpdatedSkins:
            returnString += f"\t- {skin['Skin0']}\n"

        returnString += "To be removed skins:\n"
        for skin in self.toBeRemovedSkins:
            returnString += f"\t- {skin['ddsFileName']}\n"

        return returnString
        


def scanSkins():
    
    #get the full collection list in memory
    remoteSkinsCollection = remoteService.getSkinsList()

    #get the local skins list in memory
    localSkinsCollection = localService.getSkinsList()

    #TODO : get the registered skins
    registeredCollectionList = []
    #TEMP
    #registeredCollectionList.append(registeredCollection())

    scanResult = ScanResult()
    
    #TODO: identify missing skins
    #temp, only squadron == il2 group
    registeredRemoteSkins = [skin for skin in remoteSkinsCollection.values() if skin["IL2Group"] == "IRRE"]
    
    for remoteSkin in registeredRemoteSkins:

        foundLocalSkin = None
        for localSkin in localSkinsCollection:
            if remoteSkin["Plane"] == localSkin["aircraft"]: #prefiltering to optimize search
                if remoteSkin["Skin0"] == localSkin["ddsFileName"]: #TODO : manage 2 files skins
                    #the skins is already there. Up to date ? 
                    if remoteSkin["HashDDS0"] != localSkin["md5"]:
                        scanResult.appendToBeUpdateSkin(remoteSkin)
                    
                    foundLocalSkin = localSkin
                    
                    #and then no need to pursue the research
                    break
        
        if not foundLocalSkin:
            scanResult.appendMissingSkin(remoteSkin)

    #TODO: identify to be removed skins
    for localSkin in localSkinsCollection:
        foundRemoteSkin = None
        for remoteSkin in registeredRemoteSkins:
            if remoteSkin["Plane"] == localSkin["aircraft"]: #prefiltering to optimize search
                if remoteSkin["Skin0"] == localSkin["ddsFileName"]: #TODO : manage 2 files skins
                    foundRemoteSkin = remoteSkin
                    break
        if foundRemoteSkin is None:
            scanResult.appendToBeRemovedSkin(localSkin)

    return scanResult