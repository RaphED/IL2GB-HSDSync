from requests.exceptions import HTTPError

import Services.localService as localService
import Services.remoteService as remoteService
from Services.messageBrocker import MessageBrocker
from Services.configurationService import getConf, customPhotoSyncIsActive
from Services.scannerService import ScanResult, CockpitNoteUpdate
import Services.loggingService as loggingService

def updateRegisteredSkins(scanResult: ScanResult) -> tuple[int, int]:

    _progress = 0.2
    _estimated_total_progress = 1
    successUpdates = 0
    MessageBrocker.emitProgress(_progress) #TEMP PROGRESS
    totalUpdates = len(scanResult.missingSkins) + len(scanResult.toBeUpdatedSkins)
    _progress_step = (_estimated_total_progress - _progress)
    if totalUpdates != 0:
        _progress_step = _progress_step / totalUpdates
           
    #import all missings skins
    for skin in scanResult.missingSkins:
        try:
            updateSingleSkinFromRemote(skin)
            successUpdates = successUpdates+1
        except Exception as e:
            MessageBrocker.emitConsoleMessage(f"<red>Technical error : cannot sync {skin.name()}</red>")
            loggingService.error(e)

        _progress += _progress_step #TEMP PROGRESS
        MessageBrocker.emitProgress(_progress) #TEMP PROGRESS
        

    #import all to be updated skins
    for skin in scanResult.toBeUpdatedSkins:
        try:
            updateSingleSkinFromRemote(skin)
            successUpdates = successUpdates+1
        except Exception as e:
            MessageBrocker.emitConsoleMessage(f"<red>Technical error : cannot sync {skin.name()}</red>")
            loggingService.error(e)

        _progress += _progress_step #TEMP PROGRESS
        MessageBrocker.emitProgress(_progress) #TEMP PROGRESS

    return totalUpdates, successUpdates


def deleteUnregisteredSkins(scanResult: ScanResult):
    for skin in scanResult.toBeRemovedSkins:
        deleteSkinFromLocal(skin)

def updateSingleSkinFromRemote(remoteSkin: remoteService.RemoteSkin):

    MessageBrocker.emitConsoleMessage(f"<blue>Downloading {remoteSkin.name()}...</blue>")

    #download to temp the skin
    downloadedFiles = remoteService.downloadSkinToTempDir(remoteSkin)

    for file in downloadedFiles:
    
        #Move the file to the target directory and replace existing file if any
        final_path = localService.moveSkinFromPathToDestination(file, remoteSkin.game(), remoteSkin.game_asset_code())

        MessageBrocker.emitConsoleMessage(f"Downloaded to {final_path}")

def deleteSkinFromLocal(localSkinInfo: localService.LocalSkin):
    localService.removeSkin(localSkinInfo)
    MessageBrocker.emitConsoleMessage(f"<chocolate>Deleted skin : {localSkinInfo.name}</chocolate>")


def updateCustomPhotos(toBeUpdatedPhotos: list[CockpitNoteUpdate]):
    _progress = 0
    _estimated_total_progress = 0.2
    MessageBrocker.emitProgress(_progress) #TEMP PROGRESS
    totalUpdates = len(toBeUpdatedPhotos)
    if totalUpdates == 0:
        totalUpdates = 1
    _progress_step = (_estimated_total_progress - _progress) / totalUpdates

    for update in toBeUpdatedPhotos:
        aircraftName = update.note.aircraft_name()
        try:
            downloadedFile = remoteService.downloadCockpitNote(update.note)

            #Move the file to the target directory and replace existing file if any
            localService.moveCustomPhotoFromPathToDestination(downloadedFile, update.note.game(), update.aircraftFolder)
            MessageBrocker.emitConsoleMessage(f"Cockpit note {aircraftName} updated ({update.pack.title()})")

        except HTTPError as httpError:
            MessageBrocker.emitConsoleMessage(f"<red>Cockpit note {aircraftName} download ERROR {httpError.args}</red>")
        except Exception as e:
            MessageBrocker.emitConsoleMessage(f"<red>Technical error : cannot sync the cockpit note {aircraftName}</red>")
            loggingService.error(e)

        _progress += _progress_step #TEMP PROGRESS
        MessageBrocker.emitProgress(_progress) #TEMP PROGRESS

def updateAll(scanResult: ScanResult):
    MessageBrocker.emitConsoleMessage("\nSYNCHRONIZATION BEGINS...\n")
    MessageBrocker.emitProgress(0) #TEMP PROGRESS
    loggingService.info("START SYNC")

    if customPhotoSyncIsActive():
        updateCustomPhotos(scanResult.toBeUpdatedCockpitNotes)
    MessageBrocker.emitProgress(0.2) #TEMP PROGRESS
    if getConf("autoRemoveUnregisteredSkins"):
        deleteUnregisteredSkins(scanResult)
    
    totalUpdates, successUpdates = updateRegisteredSkins(scanResult)

    loggingService.info("END SYNC")
    MessageBrocker.emitProgress(1) #TEMP PROGRESS
    MessageBrocker.emitConsoleMessage("\n<green><bold>SYNCHRONIZATION FINISHED</bold></green>\n")
    
    if totalUpdates == successUpdates:
        MessageBrocker.emitConsoleMessage("<green>Yours skins are now up to date</green>")
    else:
        MessageBrocker.emitConsoleMessage(f"<red>Could not sync all skins ({successUpdates} on {totalUpdates}) </red>")
