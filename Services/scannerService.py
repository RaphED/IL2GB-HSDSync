import Services.loggingService as loggingService
from Services.configurationService import getConf, customPhotoSyncIsActive, checkIL2InstallPath, cockpitNotesModes
import Services.localService as localService
import Services.remoteService as remoteService
from Services.subscriptionsService import getAllSubcriptions
from Services.messageBrocker import MessageBrocker

class ScanResult:
    def __init__(self):
        self.subscribedSkins = list[remoteService.RemoteSkin]()
        self.missingSkins = list[remoteService.RemoteSkin]()
        self.toBeUpdatedSkins = list[remoteService.RemoteSkin]()
        self.toBeRemovedSkins= list[localService.LocalSkin]()
        self.previouslyInstalledSkins = list[localService.LocalSkin]()
        self.toBeUpdatedCockpitNotes = list()
        
    def getDiskUsageStats(self):
        return {
            "subscribedSkinsSpace":sum([skin.size_in_b() for skin in self.subscribedSkins]),
            "missingSkinsSpace": sum([skin.size_in_b() for skin in self.missingSkins]),
            "toBeUpdatedSkinsSpace": sum([skin.size_in_b() for skin in self.toBeUpdatedSkins]),
            "toBeRemovedSkinsSpace": localService.getSpaceUsageOfLocalSkinCatalog(self.toBeRemovedSkins),
            "previouslyInstalledSkinsSpace": localService.getSpaceUsageOfLocalSkinCatalog(self.previouslyInstalledSkins),
            "toBeUpdatedCustomPhotos": remoteService.getSpaceUsageOfCustomPhotoCatalog(self.toBeUpdatedCockpitNotes)
        }
    
    def toString(self):
        returnString = ""

        diskSpaceStats = self.getDiskUsageStats()


        if customPhotoSyncIsActive():
            returnString += f"\n************ Cockpit notes ************\n"
            returnString += f"Selected images : {cockpitNotesModes[getConf("cockpitNotesMode")]}\n\n"
            if len(self.toBeUpdatedCockpitNotes) == 0:
                returnString += "<bold>All custom photos are up to date</bold>\n"
            else:
                returnString += f"<bold>{len(self.toBeUpdatedCockpitNotes)} custom photos are to be updated ({bytesToString(diskSpaceStats["toBeUpdatedCustomPhotos"])})</bold>\n"

        returnString += f"\nMissing skins ({bytesToString(diskSpaceStats["missingSkinsSpace"])}) :\n"
        for skin in self.missingSkins:
            returnString += f"<blue>{skin.name()}</blue>\n"
        if len(self.missingSkins) == 0:
            returnString +="- None -\n"

        returnString += f"\nTo be updated skins ({bytesToString(diskSpaceStats["toBeUpdatedSkinsSpace"])}) :\n"
        for skin in self.toBeUpdatedSkins:
            returnString += f"<blue>{skin.name()}</blue>\n"
        if len(self.toBeUpdatedSkins) == 0:
            returnString +="- None -\n"

        afterUpdateDiskSpace = diskSpaceStats["subscribedSkinsSpace"]

        returnString += f"\n********** Unregistered skins ********** ({bytesToString(diskSpaceStats["toBeRemovedSkinsSpace"])})"

        returnString += "\n"
        
        for skin in self.toBeRemovedSkins:
            returnString += f"<chocolate>{skin.name}</chocolate>\n"
        if len(self.toBeRemovedSkins) == 0:
            returnString +="- None -\n"

        returnString += "\n*********** Disk space analysis ***********\n\n"
        
        beforeUpdateDiskSpace = diskSpaceStats["previouslyInstalledSkinsSpace"]

        toBeDownloaded = diskSpaceStats["toBeUpdatedSkinsSpace"] + diskSpaceStats["missingSkinsSpace"] + diskSpaceStats["toBeUpdatedCustomPhotos"]

        #if unregistered skins are not deleted, count them it the final space
        unregistered_remove_message = "will be removed"
        if not getConf("autoRemoveUnregisteredSkins"):
            unregistered_remove_message = "won't be removed"
            afterUpdateDiskSpace += diskSpaceStats["toBeRemovedSkinsSpace"]

        spaceDelta = afterUpdateDiskSpace - beforeUpdateDiskSpace
        

        if self.IsSyncUpToDate():
            returnString += f"Disk space used by your skins : {bytesToString(beforeUpdateDiskSpace)}\n"
            returnString += f"Disk space used by your unregistered skins : {bytesToString(diskSpaceStats["toBeRemovedSkinsSpace"])}"
        else:
            returnString += f"Disk space used by your skins (before update) : {bytesToString(beforeUpdateDiskSpace)}\n"
            returnString += f"Disk space used by your unregistered skins ({unregistered_remove_message}): {bytesToString(diskSpaceStats["toBeRemovedSkinsSpace"])}\n"
            returnString += f"Disk space used by your skins (after update) : {bytesToString(afterUpdateDiskSpace)} ({bytesToString(spaceDelta, forceSign=True)})"
        
        
        returnString += "\n\n<bold>*************** Scan result ***************</bold>\n\n"
        if self.IsSyncUpToDate():
            returnString += "<green><bold>Skins are up to date.</bold></green>\n"
        else:
            returnString += "<red><bold>Synchronisation required!</bold></red>\n"
            returnString += f"<bold>To be downloaded : {bytesToString(toBeDownloaded)}</bold>\n"

        return returnString 
    
    def IsSyncUpToDate(self):
        if len(self.missingSkins) != 0:
            return False
        if len(self.toBeUpdatedSkins) != 0:
            return False
        if getConf("autoRemoveUnregisteredSkins") and len(self.toBeRemovedSkins) != 0:
            return False
        if len(self.toBeUpdatedCockpitNotes) > 0:
            return False
        return True

def bytesToString(bytesSize: int, forceSign: bool = False):
    
    file_size_bytes = abs(bytesSize)
    sign = "" 
    if bytesSize < 0:
        sign = "-"
    elif bytesSize > 0 and forceSign:
        sign = "+"

    file_size_kb = file_size_bytes / 1024

    if file_size_kb < 1:
        return f"{sign}{file_size_bytes} B"

    file_size_mb = file_size_kb / 1024

    if file_size_mb < 1:
        return f"{sign}{file_size_kb:.2f} KB"
    
    file_size_gb = file_size_mb / 1024

    if file_size_gb < 1:
        return f"{sign}{file_size_mb:.2f} MB"
    
    return f"{sign}{file_size_gb:.2f} GB"

def scanSkins():
    loggingService.info("START SCAN")
    scanResult = ScanResult()

    #get the local skins list in memory
    scanResult.previouslyInstalledSkins = localService.getSkinsList()
    
    #load all subscriptions and merge all skins in one list
    subscribedCollectionList = getAllSubcriptions()
    skins_ids = []
    for collection in subscribedCollectionList:
        if not collection.active:
            loggingService.info(f"Unactive subscribed collection : {collection.name}")
            continue    
        
        loggingService.info(f"Subscribed collection : {collection.name}")
        for skin in collection.skins:
            #do not load the same skin twice
            if skin.id() not in skins_ids:
                scanResult.subscribedSkins.append(skin)
                skins_ids.append(skin.id())
    
    #then check if we can find the remote skin matching with the local skin
    
    #initialise result collections
    scanResult.missingSkins = list[remoteService.RemoteSkin]()
    scanResult.toBeUpdatedSkins = list[remoteService.RemoteSkin]()

    for remoteSkin in scanResult.subscribedSkins:
        foundLocalSkin = None
        for localSkin in scanResult.previouslyInstalledSkins:
            #not the same A/C, no match
            if remoteSkin.game_asset_code() != localSkin.game_asset_code:
                continue
            
            #not the same skin name, no match
            if remoteSkin.name() != localSkin.name:
                continue
            
            #there is a match !
            foundLocalSkin = localSkin
                            
            #the skins is already there. Up to date ? 
            skinAsToBeUpdated = False

            for dds_file in remoteSkin.dds_files():
                #search the corresponding local file and if any difference is identified, then mark the skin as to be updated
                matching_local_file = None
                for local_dds_file in localSkin.dds_files:
                    if local_dds_file.fileName == dds_file.destination_name:
                        matching_local_file = local_dds_file
                        break
                
                if matching_local_file is None:
                    skinAsToBeUpdated = True
                    break
                
                if matching_local_file.fileMd5 != dds_file.md5:
                    skinAsToBeUpdated = True
                    break
            
            #if any modification has to be made, put the skin in the list to be updated
            if skinAsToBeUpdated:
                scanResult.toBeUpdatedSkins.append(remoteSkin)

            #and then no need to pursue the research as if we are there, we have found a match
            break
        
        if not foundLocalSkin:
            scanResult.missingSkins.append(remoteSkin)

    #Then list all local skins not present in the remote skins
    for localSkin in scanResult.previouslyInstalledSkins:
        foundRemoteSkin = None

        for remoteSkin in scanResult.subscribedSkins:
            if remoteSkin.game_asset_code() == localSkin.game_asset_code: #prefiltering to optimize search
                #TODO: Manage orphans skins
                if remoteSkin.name() == localSkin.name:
                    foundRemoteSkin = remoteSkin
                    break

        #the skin cannot be found
        if foundRemoteSkin is None:
            scanResult.toBeRemovedSkins.append(localSkin)

    loggingService.info("END SCAN")
    return scanResult


def scanCustomPhotos():
    
    localCustomPhotos = localService.getCustomPhotosList()
    remoteCustomPhotos = remoteService.getCustomPhotosList()

    toBeUpdatedPhotos = []

    for remotePhoto in remoteCustomPhotos:
        match = False
        for localPhoto in localCustomPhotos:
            if remotePhoto["aircraft"].lower() == localPhoto["aircraft"].lower():
                #we have a match
                if remotePhoto["md5"] != localPhoto["md5"]:
                    #photo has to be updated
                    toBeUpdatedPhotos.append(remotePhoto)
                match = True
                break
        
        if not match:
            toBeUpdatedPhotos.append(remotePhoto)

    return toBeUpdatedPhotos

def scanAll():
    #check conf is proper
    if not checkIL2InstallPath():
        MessageBrocker.emitConsoleMessage("!!! INVALID IL2 path !!!\nPlease modify the path from the parameters panel")
        MessageBrocker.emitConsoleMessage("SCAN Cancelled")
        return None


    MessageBrocker.emitConsoleMessage("SCAN BEGINS...")
    MessageBrocker.emitProgress(0) #TEMP PROGRESS
    
    scanResult = scanSkins()
    if customPhotoSyncIsActive():
        scanResult.toBeUpdatedCockpitNotes = scanCustomPhotos()
    MessageBrocker.emitProgress(1.0) #TEMP PROGRESS
    MessageBrocker.emitConsoleMessage("SCAN FINISHED")
    return scanResult