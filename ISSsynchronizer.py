from requests.exceptions import HTTPError

import pythonServices.localService as localService
import pythonServices.remoteService as remoteService
from pythonServices.messageBrocker import MessageBrocker
from pythonServices.configurationService import getConf, customPhotoSyncIsActive

from ISSScanner import ScanResult

import logging



def updateRegisteredSkins(scanResult: ScanResult):

    _progress = 0.2
    _estimated_total_progress = 1
    MessageBrocker.emitProgress(_progress) #TEMP PROGRESS
    totalUpdates = sum([len(lst) for lst in scanResult.missingSkins.values()]) + sum([len(lst) for lst in scanResult.toBeUpdatedSkins.values()])
    if totalUpdates == 0:
        totalUpdates = 1
    _progress_step = (_estimated_total_progress - _progress) / totalUpdates
    
    for source in scanResult.getUsedSources():
        
        #import all missings skins
        for skin in scanResult.missingSkins[source]:
            updateSingleSkinFromRemote(source, skin)

            _progress += _progress_step #TEMP PROGRESS
            MessageBrocker.emitProgress(_progress) #TEMP PROGRESS
            

        #import all to be updated skins
        for skin in scanResult.toBeUpdatedSkins[source]:
            updateSingleSkinFromRemote(source, skin)

            _progress += _progress_step #TEMP PROGRESS
            MessageBrocker.emitProgress(_progress) #TEMP PROGRESS


def deleteUnregisteredSkins(scanResult: ScanResult):
    for skin in scanResult.toBeRemovedSkins:
        deleteSkinFromLocal(skin)

def updateSingleSkinFromRemote(source, remoteSkin: remoteService.RemoteSkin):

    MessageBrocker.emitConsoleMessage(f"Downloading {remoteSkin.getValue("name")}...")

    #download to temp the skin
    downloadedFiles = remoteService.downloadSkinToTempDir(source, remoteSkin)

    for file in downloadedFiles:
    
        #Move the file to the target directory and replace existing file if any
        final_path = localService.moveSkinFromPathToDestination(file, remoteSkin.getValue("aircraft"))

        MessageBrocker.emitConsoleMessage(f"Downloaded to {final_path}")

def deleteSkinFromLocal(localSkinInfo):
    localService.removeSkin(localSkinInfo)
    MessageBrocker.emitConsoleMessage(f"Deleted skin : {localSkinInfo["name"]}")


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

async def updateAll(scanResult: ScanResult):
    MessageBrocker.emitConsoleMessage("SYNCHRONIZATION BEGINS...")
    MessageBrocker.emitProgress(0) #TEMP PROGRESS

    if customPhotoSyncIsActive():
        updateCustomPhotos(scanResult.toBeUpdatedCockpitNotes)
    MessageBrocker.emitProgress(0.2) #TEMP PROGRESS
    if getConf("autoRemoveUnregisteredSkins"):
        deleteUnregisteredSkins(scanResult)
    
    updateRegisteredSkins(scanResult)

    MessageBrocker.emitProgress(1) #TEMP PROGRESS
    MessageBrocker.emitConsoleMessage("SYNCHRONIZATION FINISHED")
