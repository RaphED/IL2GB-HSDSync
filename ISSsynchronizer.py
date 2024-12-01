from requests.exceptions import HTTPError

import pythonServices.localService as localService
import pythonServices.remoteService as remoteService
from pythonServices.messageBrocker import MessageBrocker
from pythonServices.configurationService import getConf, customPhotoSyncIsActive

from ISSScanner import ScanResult

import logging



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

    for customPhoto in toBeUpdatedPhotos:
        
        try:
            downloadedFile = remoteService.downloadCustomPhoto(cockpitMode, customPhoto)
            
            #Move the file to the target directory and replace existing file if any
            localService.moveCustomPhotoFromPathToDestination(downloadedFile, customPhoto["aircraft"])
            MessageBrocker.emitConsoleMessage(f"Custom photo {customPhoto["aircraft"]} updated")
        
        except HTTPError as httpError:
            MessageBrocker.emitConsoleMessage(f"Custom photo {customPhoto["aircraft"]} download ERROR {httpError.args} ")





async def updateAll(scanResult: ScanResult):
    MessageBrocker.emitConsoleMessage("SYNCHRONIZATION BEGINS")
    
    if customPhotoSyncIsActive():
        updateCustomPhotos(scanResult.toBeUpdatedCockpitNotes)
    
    if getConf("autoRemoveUnregisteredSkins"):
        deleteUnregisteredSkins(scanResult)
    
    updateRegisteredSkins(scanResult)

    MessageBrocker.emitConsoleMessage("SYNCHRONIZATION FINISHED")
