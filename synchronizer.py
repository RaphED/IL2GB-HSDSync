import localService
import remoteService

class registeredCollection:
    def __init__():
        squadron = "IRRE"



def scanSkins():
    
    #get the full collection list in memory
    remoteSkinsCollection = remoteService.getSkinsList()

    #get the local skins list in memory
    localSkinsCollection = localService.getSkinsList()

    #TODO : get the registered skins
    registeredCollectionList = []
    #TEMP
    #registeredCollectionList.append(registeredCollection())

    missingSkins = []
    toBeUpdatedSkins = []
    toBeRemovedSkins= []
    
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
                        toBeUpdatedSkins.append(remoteSkin)
                    
                    foundLocalSkin = localSkin
                    
                    #and then no need to pursue the research
                    break
        
        if not foundLocalSkin:
            missingSkins.append(remoteSkin)

    #TODO: identify to be removed skins
    for localSkin in localSkinsCollection:
        foundRemoteSkin = None
        for remoteSkin in registeredRemoteSkins:
            if remoteSkin["Plane"] == localSkin["aircraft"]: #prefiltering to optimize search
                if remoteSkin["Skin0"] == localSkin["ddsFileName"]: #TODO : manage 2 files skins
                    foundRemoteSkin = remoteSkin
                    break
        if foundRemoteSkin is None:
            toBeRemovedSkins.append(localSkin)

    return {
        "missingSkins": missingSkins,
        "toBeUpdatedSkins": toBeUpdatedSkins,
        "toBeRemovedSkins": toBeRemovedSkins
    }