import requests
import json

from Services.configurationService import getConf, cockpitNotesModes
from Services.filesService import downloadFile
from Services.messageBrocker import MessageBrocker

main_api_URL = "https://hsd-online.net/api"
collections_catalog_URL = f"{main_api_URL}/skinsCollections"
collection_brownser_URL = "https://hsd-online.net/collections/[collection_id]"
skins_download_URL = f"{main_api_URL}/skins/files/[path]"

class RemoteSkin:
    def __init__(self, json_raw_data: json) -> None:
        self._json_raw_data = json_raw_data

    #Translation of parameters from json
    def id(self):
        return self._json_raw_data["id"]
    def name(self):
        return self._json_raw_data["title"]
    def game_asset_code(self):
        return self._json_raw_data["game_asset"]["code_name"]
    
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

    class remoteDDSFileInfo:
        def __init__(self, destination_name: str, path: str, md5: str):
            self.destination_name = destination_name
            self.md5 = md5
            self.path = path
    
    def dds_files(self) -> list[remoteDDSFileInfo]:
        variant = self.get_variant_regarding_censorship_configuration()
        dds_files_info = []
        for file in variant.get("dds_files", []):
            dds_file = self.remoteDDSFileInfo(
                destination_name=file["destination_name"],
                path=file["path"],
                md5=file["MD5"]
            )
            dds_files_info.append(dds_file)
        
        return dds_files_info
    
    def size_in_b(self) -> int:
        if getConf("applyCensorship"):
            return self._json_raw_data["size_in_b_restricted_only"]
        else:
            return self._json_raw_data["size_in_b_unrestricted"]

class RemoteCollection:
    def __init__(self, json_raw_data: json) -> None:
        self._json_raw_data = json_raw_data

    #Translation of parameters from json
    def id(self):
        return self._json_raw_data["id"]
    def name(self):
        return self._json_raw_data["name"]
    def description(self):
        return self._json_raw_data["description"]
    def creator(self):
        return self._json_raw_data["creator"]
    def skin_count(self) -> int:
        return self._json_raw_data["skins_count"]
    def size_in_b_unrestricted(self) -> int:
        return self._json_raw_data["size_in_b_unrestricted"]
    def size_in_b_restricted_only(self) -> int:
        return self._json_raw_data["size_in_b_restricted_only"]
    def browser_URL(self) -> str:
        return collection_brownser_URL.replace("[collection_id]", str(self.id()))
    def api_URL(self) -> str:
        return f"{main_api_URL}/skinsCollections/{self.id()}"
    
def getRemoteCollectionsCatalog() -> list[RemoteCollection]:
    try:
        response = requests.get(collections_catalog_URL)

         # Check if the request was successful (status code 200)
        if response.status_code == 200:
            file_content = response.json()
            remote_collections = []
            for collection_json in file_content:
                remote_collections.append(RemoteCollection(collection_json))
            return remote_collections
        else:
            raise Exception(f"Cannot retrieve collections catalog due to server response :{response.status_code}")
    except requests.ConnectionError as e:
        MessageBrocker.emitConsoleMessage("Cannot join server to retrieve collections catalog.")
        raise e
    except Exception as e:
        raise e


def downloadSkinToTempDir(skinInfo: RemoteSkin):

    downloadedFiles = []

    #download all dds files
    for file in skinInfo.dds_files():

        downloadedFiles.append(
            downloadFile(
                url=skins_download_URL.replace("[path]", file.path), 
                destination_file_name=file.destination_name, 
                expectedMD5=file.md5
            )
        )
    
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