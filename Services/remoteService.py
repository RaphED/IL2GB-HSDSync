import requests
import json

from Services.configurationService import getConf, cockpitNotesModes
from Services.filesService import downloadFile
from Services.messageBrocker import MessageBrocker

skins_download_URL ="https://skins.combatbox.net/[aircraft]/[skinFileName]"

class RemoteSkin:
    def __init__(self, json_raw_data: json) -> None:
        self._json_raw_data = json_raw_data

    #Translation of parameters from json
    def id(self):
        return self._json_raw_data["id"]
    def name(self):
        return self._json_raw_data["title"]
    def object_type(self):
        return self._json_raw_data["plane"]
    
    #get variant sub json data
    def unrestricted_variant_content(self) -> json:
        restricted_variant = self._json_raw_data.get("Restricted_Symbols")
        if restricted_variant is not None:
            return restricted_variant
        return self.restricted_variant_content()
    def restricted_variant_content(self) -> json:
        return self._json_raw_data.get("No_Restricted_Symbols")
    def get_variant_regarding_censorship_configuration(self) -> json:
        if getConf("applyCensorship"):
            return self.restricted_variant_content()
        else:
            return self.unrestricted_variant_content()

    def mainFileName(self):
        return self.get_variant_regarding_censorship_configuration()["main_file_name"]    
    def mainFileMd5(self):
        return self.get_variant_regarding_censorship_configuration()["main_file_MD5"]
    def secondaryFileName(self):
        return self.get_variant_regarding_censorship_configuration().get("secondary_file_name", None)
    def secondaryFileMd5(self):
        return self.get_variant_regarding_censorship_configuration().get("secondary_file_MD5", None)
    
    def size_in_b(self) -> int:
        if getConf("applyCensorship"):
            return self._json_raw_data["size_in_b_restricted_only"]
        else:
            return self._json_raw_data["size_in_b_unrestricted"]

def downloadSkinToTempDir(skinInfo: RemoteSkin):

    #build skin URL
    url = skins_download_URL.replace("[aircraft]", skinInfo.object_type())
    urlMainSkin = url.replace("[skinFileName]", skinInfo.mainFileName())

    downloadedFiles = []
    
    #check what is this is a single or dual file skin
    secondarySkinFileName = skinInfo.secondaryFileName()

    if secondarySkinFileName is not None and secondarySkinFileName != "":
        #it is a dual file
        first_dds_file_name = skinInfo.name() + "&1.dds"
        second_dds_file_name = skinInfo.name() + "&1#1.dds"

        #hack : works only for HSD, the #1 is replaced by %123 on the URL
        remoteFileName = secondarySkinFileName.replace("#1", "%231")
        urlSecondarySkin = url.replace("[skinFileName]", remoteFileName)

        downloadedFiles.append(downloadFile(url=urlMainSkin, destination_file_name=first_dds_file_name, expectedMD5=skinInfo.mainFileMd5()))    
        downloadedFiles.append(downloadFile(url=urlSecondarySkin, destination_file_name=second_dds_file_name, expectedMD5=skinInfo.secondaryFileMd5()))
        
    else:
        dds_file_name = skinInfo.name() + ".dds"
        downloadedFiles.append(downloadFile(url=urlMainSkin, destination_file_name=dds_file_name, expectedMD5=skinInfo.mainFileMd5()))    
    
    return downloadedFiles


customPhotosCatalogURL = "https://www.lesirreductibles.com/irreskins/IRRE/CustomPhotos/[mode]CustomPhotosManifest.json"
customPhotosFilesURL = "https://www.lesirreductibles.com/irreskins/IRRE/CustomPhotos/[mode]/[aircraft]/Textures/custom_photo.dds"


def getCockpitNotesModeInfo(mode):
    if mode not in cockpitNotesModes.keys():
        raise Exception(f"Unexpected cockpitNotesModes {mode}")
    
    if mode == "noSync":
        return {
            "catalogURL": None,
            "filesURL": None
        }
    else:
        return {
            "catalogURL": customPhotosCatalogURL.replace("[mode]", mode),
            "filesURL": customPhotosFilesURL.replace("[mode]", mode),
        }
            

def getCustomPhotosList():
    #hard coded remote address for the cockpitNotesCatalog
    catalogURL = getCockpitNotesModeInfo(getConf("cockpitNotesMode"))["catalogURL"]
    if catalogURL is None:
        return []

    try:
        response = requests.get(catalogURL)

         # Check if the request was successful (status code 200)
        if response.status_code == 200:
            file_content = response.json()
            return file_content
        else:
            raise Exception(f"Cannot retrieve cockpit notes catalog due to server response :{response.status_code}")
    except requests.ConnectionError as e:
        MessageBrocker.emitConsoleMessage("Cannot join server to retrieve cockpit notes. Consider deactivating its synchronization.")
        raise e
    except Exception as e:
        raise e

def getSpaceUsageOfCustomPhotoCatalog(customPhotosList):
    totalDiskSpace = 0
    for skin in customPhotosList:
        #This is soooo bad. custom photos are about 1 400 000 bites
        #TODO : addd the file size in the manifests
        totalDiskSpace += 1400000
    
    return totalDiskSpace

def downloadCustomPhoto(cockpitNotesMode, cockpitNote):
    filesURL = getCockpitNotesModeInfo(cockpitNotesMode)["filesURL"]

    targetURL = filesURL.replace("[aircraft]", cockpitNote["aircraft"])
    return downloadFile(targetURL, cockpitNote["md5"])