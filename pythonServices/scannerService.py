from pythonServices.configurationService import getConf, customPhotoSyncIsActive, checkIL2InstallPath, cockpitNotesModes
import pythonServices.localService as localService
import pythonServices.remoteService as remoteService
from pythonServices.subscriptionsService import getAllSubcriptions
from pythonServices.messageBrocker import MessageBrocker

import logging

class ScanResult:
    def __init__(self):
        self.subscribedSkins = list[remoteService.RemoteSkin]()
        self.missingSkins = list[remoteService.RemoteSkin]()
        self.toBeUpdatedSkins = list[remoteService.RemoteSkin]()
        self.toBeRemovedSkins= list()
        self.previouslyInstalledSkins = list()
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
            returnString += f"<chocolate>{skin['name']}</chocolate>\n"
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
    logging.info("START SCAN")
    scanResult = ScanResult()

    #get the local skins list in memory
    scanResult.previouslyInstalledSkins = localService.getSkinsList()
    
    #load all subscriptions and merge all skins in one list
    subscribedCollectionList = getAllSubcriptions()
    skins_ids = []
    for collection in subscribedCollectionList:
        if not collection.active:
            logging.info(f"Unactive subscribed collection : {collection.name}")
            continue    
        
        logging.info(f"Subscribed collection : {collection.name}")
        for skin in collection.skins:
            #do not load the same skin twice
            if skin.id() not in skins_ids:
                scanResult.subscribedSkins.append(skin)
                skins_ids.append(skin.id())
    
    #then check if we can find the remote skin matching with the local skin
    
    #initialise result collections
    scanResult.missingSkins = list()
    scanResult.toBeUpdatedSkins = list()

    for remoteSkin in scanResult.subscribedSkins:
        foundLocalSkin = None
        for localSkin in scanResult.previouslyInstalledSkins:
            #not the same A/C, no match
            if remoteSkin.object_type() != localSkin["aircraft"]:
                continue
            
            #not the same skin name, no match
            if remoteSkin.name() != localSkin["name"]:
                continue
            
            #there is a match !
            foundLocalSkin = localSkin
                            
            #the skins is already there. Up to date ? 
            skinAsToBeUpdated = False

            #check main file md5
            if remoteSkin.mainFileMd5() != localSkin["mainFileMd5"]:
                skinAsToBeUpdated = True
            else:
                #the main file is the same, but we have to look at the secondary file if any
                secondarySkinFileName = remoteSkin.secondaryFileName()
                
                #if there is a secondary file declared on the remote
                if secondarySkinFileName is not None and secondarySkinFileName != "":
                    
                    #check if we can find the secondary on the local
                    if localSkin.get("secondaryFileName") is None:
                        skinAsToBeUpdated = True
                    #check the md5 is the proper one
                    elif remoteSkin.secondaryFileMd5() != localSkin["secondaryFileMd5"]:
                        skinAsToBeUpdated = True
            
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
            if remoteSkin.object_type() == localSkin["aircraft"]: #prefiltering to optimize search
                #TODO: Manage orphans skins
                if remoteSkin.name() == localSkin["name"]:
                    foundRemoteSkin = remoteSkin
                    break

        #the skin cannot be found
        if foundRemoteSkin is None:
            scanResult.toBeRemovedSkins.append(localSkin)

    logging.info("END SCAN")
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