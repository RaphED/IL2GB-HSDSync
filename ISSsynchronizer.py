from requests.exceptions import HTTPError

import pythonServices.localService as localService
import pythonServices.remoteService as remoteService
from pythonServices.messageBrocker import MessageBrocker
from pythonServices.configurationService import getConf, customPhotoSyncIsActive

from ISSScanner import ScanResult

import logging

def updateRegisteredSkins(scanResult: ScanResult) -> tuple[int, int]:

    _progress = 0.2
    _estimated_total_progress = 1
    successUpdates = 0
    MessageBrocker.emitProgress(_progress) #TEMP PROGRESS
    totalUpdates = sum([len(lst) for lst in scanResult.missingSkins.values()]) + sum([len(lst) for lst in scanResult.toBeUpdatedSkins.values()])
    _progress_step = (_estimated_total_progress - _progress)
    if totalUpdates != 0:
        _progress_step = _progress_step / totalUpdates
    
    for source in scanResult.getUsedSources():
        
        #import all missings skins
        for skin in scanResult.missingSkins[source]:
            try:
                updateSingleSkinFromRemote(source, skin)
                successUpdates = successUpdates+1
            except Exception as e:
                MessageBrocker.emitConsoleMessage(f"<red>Technical error : cannot sync {skin.getValue("name")}</red>")
                logging.error(e)

            _progress += _progress_step #TEMP PROGRESS
            MessageBrocker.emitProgress(_progress) #TEMP PROGRESS
            

        #import all to be updated skins
        for skin in scanResult.toBeUpdatedSkins[source]:
            try:
                updateSingleSkinFromRemote(source, skin)
                successUpdates = successUpdates+1
            except Exception as e:
                MessageBrocker.emitConsoleMessage(f"<red>Technical error : cannot sync {skin.getValue("name")}</red>")
                logging.error(e)

            _progress += _progress_step #TEMP PROGRESS
            MessageBrocker.emitProgress(_progress) #TEMP PROGRESS

    return totalUpdates, successUpdates


def deleteUnregisteredSkins(scanResult: ScanResult):
    for skin in scanResult.toBeRemovedSkins:
        deleteSkinFromLocal(skin)

def updateSingleSkinFromRemote(source, remoteSkin: remoteService.RemoteSkin):

    MessageBrocker.emitConsoleMessage(f"<blue>Downloading {remoteSkin.getValue("name")}...</blue>")

    #download to temp the skin
    downloadedFiles = remoteService.downloadSkinToTempDir(source, remoteSkin)

    for file in downloadedFiles:
    
        #Move the file to the target directory and replace existing file if any
        final_path = localService.moveSkinFromPathToDestination(file, remoteSkin.getValue("aircraft"))

        MessageBrocker.emitConsoleMessage(f"Downloaded to {final_path}")

def deleteSkinFromLocal(localSkinInfo):
    localService.removeSkin(localSkinInfo)
    MessageBrocker.emitConsoleMessage(f"<chocolate>Deleted skin : {localSkinInfo["name"]}</chocolate>")


def updateCustomPhotos(toBeUpdatedPhotos):
    cockpitMode = getConf("cockpitNotesMode")
    _progress = 0
    _estimated_total_progress = 0.2
    MessageBrocker.emitProgress(_progress) #TEMP PROGRESS
    totalUpdates = len(toBeUpdatedPhotos)
    if totalUpdates == 0:
        totalUpdates = 1
    _progress_step = (_estimated_total_progress - _progress) / totalUpdates

    for customPhoto in toBeUpdatedPhotos:
        
        try:
            downloadedFile = remoteService.downloadCustomPhoto(cockpitMode, customPhoto)
            
            #Move the file to the target directory and replace existing file if any
            localService.moveCustomPhotoFromPathToDestination(downloadedFile, customPhoto["aircraft"])
            MessageBrocker.emitConsoleMessage(f"Custom photo {customPhoto["aircraft"]} updated")
        
        except HTTPError as httpError:
            MessageBrocker.emitConsoleMessage(f"Custom photo {customPhoto["aircraft"]} download ERROR {httpError.args} ")

        _progress += _progress_step #TEMP PROGRESS
        MessageBrocker.emitProgress(_progress) #TEMP PROGRESS

def updateAll(scanResult: ScanResult):
    MessageBrocker.emitConsoleMessage("\nSYNCHRONIZATION BEGINS...\n")
    MessageBrocker.emitProgress(0) #TEMP PROGRESS
    logging.info("START SYNC")

    if customPhotoSyncIsActive():
        updateCustomPhotos(scanResult.toBeUpdatedCockpitNotes)
    MessageBrocker.emitProgress(0.2) #TEMP PROGRESS
    if getConf("autoRemoveUnregisteredSkins"):
        deleteUnregisteredSkins(scanResult)
    
    totalUpdates, successUpdates = updateRegisteredSkins(scanResult)

    logging.info("END SYNC")
    MessageBrocker.emitProgress(1) #TEMP PROGRESS
    MessageBrocker.emitConsoleMessage("\n<green><bold>SYNCHRONIZATION FINISHED</bold></green>\n")
    
    if totalUpdates == successUpdates:
        MessageBrocker.emitConsoleMessage("<green>Yours skins are now up to date</green>")
    else:
        MessageBrocker.emitConsoleMessage(f"<red>Could not sync all skins ({successUpdates} on {totalUpdates}) </red>")
