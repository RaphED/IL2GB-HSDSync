import requests
import json

from Services.configurationService import getConf
from Services.filesService import downloadFile
from Services.messageBrocker import MessageBrocker

main_api_URL = "https://hsd-online.net/api"
collections_catalog_URL = f"{main_api_URL}/skinsCollections"
collection_brownser_URL = "https://hsd-online.net/collections/[collection_id]"
skins_download_URL = f"{main_api_URL}/skins/files/[path]"
cockpit_notes_packs_URL = f"{main_api_URL}/cockpitNotesPacks"
cockpit_notes_download_URL = f"{main_api_URL}/cockpitNotesPacks/notes/[path]"
cockpit_notes_pack_browser_URL = "https://hsd-online.net/cockpit-notes/[pack_id]"

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
    def game(self):
        #skins of servers older than the multi-games support are IL-2 Great Battles ones
        return self._json_raw_data["game_asset"].get("game") or "IL2GB"
    
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
    def creator_name(self):
        return self._json_raw_data["creator_name"]
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
            for collection_json in file_content["collections"]:
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


# COCKPIT NOTES

# File installed by the game in data/graphics/planes/<aircraft code>/Textures/
COCKPIT_NOTE_FILE_NAME = "custom_photo.dds"

class RemoteCockpitNote:
    def __init__(self, json_raw_data: json) -> None:
        self._json_raw_data = json_raw_data

    def aircraft_code(self):
        return self._json_raw_data["game_asset"]["code_name"]
    def aircraft_name(self):
        return self._json_raw_data["game_asset"]["display_name"]
    def game(self):
        return self._json_raw_data["game_asset"]["game"]
    def md5(self):
        return self._json_raw_data["MD5"]
    def size_in_b(self) -> int:
        return self._json_raw_data["size_in_b"]
    def download_URL(self):
        return cockpit_notes_download_URL.replace("[path]", self._json_raw_data["path"])

class RemoteCockpitNotesPack:
    def __init__(self, json_raw_data: json) -> None:
        self._json_raw_data = json_raw_data

    def id(self):
        return self._json_raw_data["id"]
    def title(self):
        return self._json_raw_data["title"]
    def description(self):
        return self._json_raw_data["description"]
    def creator_name(self):
        return self._json_raw_data["creator"]
    def game(self):
        return self._json_raw_data["game"]
    def notes_count(self) -> int:
        return self._json_raw_data["notes_count"]
    def size_in_b(self) -> int:
        return self._json_raw_data["size_in_b"]
    def is_online(self) -> bool:
        return self._json_raw_data["state"] == "Approved"
    def browser_URL(self) -> str:
        return cockpit_notes_pack_browser_URL.replace("[pack_id]", str(self.id()))
    def notes(self) -> list[RemoteCockpitNote]:
        #only loaded with a single pack, not in the catalog
        return [RemoteCockpitNote(note_json) for note_json in self._json_raw_data.get("notes", [])]

def getRemoteCockpitNotesPacksCatalog() -> list[RemoteCockpitNotesPack]:
    """Online (approved) packs, without their notes"""
    try:
        response = requests.get(cockpit_notes_packs_URL)
        if response.status_code == 200:
            return [RemoteCockpitNotesPack(pack_json) for pack_json in response.json()["packs"]]
        else:
            raise Exception(f"Cannot retrieve cockpit notes packs catalog due to server response :{response.status_code}")
    except requests.ConnectionError as e:
        MessageBrocker.emitConsoleMessage("Cannot join server to retrieve cockpit notes packs catalog.")
        raise e

def getRemoteCockpitNotesPack(pack_id: int) -> RemoteCockpitNotesPack | None:
    """The pack with its notes, None if it does not exist (anymore)"""
    try:
        response = requests.get(f"{cockpit_notes_packs_URL}/{pack_id}")
        if response.status_code == 200:
            return RemoteCockpitNotesPack(response.json())
        elif response.status_code == 404:
            return None
        else:
            raise Exception(f"Cannot retrieve cockpit notes pack {pack_id} due to server response :{response.status_code}")
    except requests.ConnectionError as e:
        MessageBrocker.emitConsoleMessage("Cannot join server to retrieve cockpit notes. Consider deactivating its synchronization.")
        raise e

def downloadCockpitNote(note: RemoteCockpitNote):
    return downloadFile(note.download_URL(), expectedMD5=note.md5(), destination_file_name=COCKPIT_NOTE_FILE_NAME)
