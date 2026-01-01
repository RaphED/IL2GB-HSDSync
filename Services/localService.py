import os
import hashlib
import json

import Services.loggingService as loggingService
from Services.configurationService import getConf
from Services.filesService import moveFile, deleteFile
from Services.messageBrocker import MessageBrocker


def getSkinDirectory():
    return os.path.join(getConf("IL2GBGameDirectory"), "data\\graphics\\skins")

def getCustomPhotosDirectory():
    return os.path.join(getConf("IL2GBGameDirectory"), "data\\graphics\\planes")

class ddsFile:
    def __init__(self, fileName: str, fileSize: int, fileMd5: str):
        self.fileName = fileName
        self.fileSize = fileSize
        self.fileMd5 = fileMd5

class LocalSkin:
    def __init__(self, game_asset_code: str, name: str, dds_files: list[ddsFile]):
        self.game_asset_code = game_asset_code
        self.name = name
        self.dds_files = dds_files


def getSkinsList() -> list[LocalSkin]:
    skinList: list[LocalSkin] = []
    skinsDirectory = getSkinDirectory()
    
    _progress = 0.1
    _estimated_total_progress = 0.8
    MessageBrocker.emitProgress(_progress) #TEMP PROGRESS
    
    _progress_step = (_estimated_total_progress - _progress) / len(list(os.walk(skinsDirectory)))

    for root, dirs, files in os.walk(skinsDirectory):
        _progress += _progress_step #TEMP PROGRESS
        MessageBrocker.emitProgress(_progress) #TEMP PROGRESS

        #continue if no files
        if len(files) == 0:
            continue

        #get only dds files
        ddsfiles = [f for f in files if f.lower().endswith('.dds')]

        if len(ddsfiles) == 0:
            continue

        parentDir = os.path.dirname(root)
        
        #only manage 1 level skins (otherwise these are lost skins)
        if parentDir != skinsDirectory:
            loggingService.warning(f"Unexpected skin(s) {ddsfiles} placement at {root}. Not managed")
            continue
        
        game_asset_code =  os.path.basename(os.path.normpath(root))

        #parse only main skin files
        for ddsFileName in [file for file in ddsfiles if not file.endswith("#1.dds")]:
            fileFullPath = os.path.join(root,ddsFileName)
            filestats = os.stat(fileFullPath)

            skin_name = ddsFileName[:-4] #remove extention to get the name
            #case of dual skins files, remove the &1
            if skin_name.endswith("&1"):
                skin_name = skin_name[:-2]
            
            skinList.append(LocalSkin(
                game_asset_code=game_asset_code,
                name=skin_name,
                dds_files=[
                    ddsFile(
                        fileName=ddsFileName,
                        fileSize=filestats.st_size,
                        fileMd5=manage_file_md5(fileFullPath)
                    )
                ]
            ))

        #then if there are secondary files, attach them to the same skin entry
        for ddsSecondaryFileName in [file for file in ddsfiles if file.endswith("#1.dds")]:
            fileFullPath = os.path.join(root,ddsSecondaryFileName)
            filestats = os.stat(fileFullPath)

            for index, skin in enumerate(skinList):
                #check if the secondary file matches the main file
                if skin.dds_files[0].fileName[:-4] == ddsSecondaryFileName[:-6]:
                    skinList[index].dds_files.append(
                        ddsFile(
                            fileName=ddsSecondaryFileName,
                            fileSize=filestats.st_size,
                            fileMd5=manage_file_md5(fileFullPath)
                        )
                    )
                    #stop the loop when found
                    break
    return skinList

def moveSkinFromPathToDestination(src_path, aircraft):
    return moveFile(src_path, os.path.join(getSkinDirectory(), aircraft))

def removeSkin(localSkinInfo: LocalSkin):
    
    for file in localSkinInfo.dds_files:
        filePath = os.path.join(getSkinDirectory(), localSkinInfo.game_asset_code, file.fileName)
        deleteFile(filePath)

def getSpaceUsageOfLocalSkinCatalog(skinList: list[LocalSkin]):
    totalDiskSpace = 0
    for skin in skinList:
        for file in skin.dds_files:
            totalDiskSpace += file.fileSize
    
    return totalDiskSpace



def getCustomPhotosList():
    return getCustomPhotosListFromPath(getCustomPhotosDirectory())

def getCustomPhotosListFromPath(path):
    notesList = []
    
    for root, dirs, files in os.walk(path):
        
        #continue if no files
        if len(files) == 0:
            continue

        #get only custom photos files
        customPhotosfiles = [f for f in files if f == 'custom_photo.dds']

        if len(customPhotosfiles) != 1:
            continue
        currentPhotoFile = customPhotosfiles[0]

        #parent dir should be "textures"
        if os.path.basename(os.path.normpath(root)) != "Textures":
            loggingService.warning(f"Found unexpected custom photo at {root}")
            continue

        aircraft =  os.path.basename(os.path.normpath(os.path.dirname(root)))

        notesList.append({
            "aircraft": aircraft,
            "md5": manage_file_md5(os.path.join(root,currentPhotoFile))
        })
        
    return notesList

def getAndGenerateCustomPhotosCatalogFromPath(parentPath, catalogName):
    catalogPath = os.path.join(parentPath, catalogName)
    cockpitNotesList = getCustomPhotosListFromPath(catalogPath)
    generateCockpitNotesCatalogFileName = f"{catalogName}CustomPhotosManifest.json"
    fullFilePath = os.path.join(parentPath, generateCockpitNotesCatalogFileName)
    with open(fullFilePath, 'w') as f:
        json.dump(cockpitNotesList, f, indent=4)

    return cockpitNotesList

def moveCustomPhotoFromPathToDestination(src_path, aircraft):
    destinationPath = os.path.join(getCustomPhotosDirectory(), aircraft, "Textures")
    return moveFile(src_path, destinationPath)

def calculate_metadata_hash(file_path):
    """Calculate a hash based on file metadata."""
    stat = os.stat(file_path)
    metadata = {
        'size': stat.st_size,
        'mtime': stat.st_mtime,
        'ctime': stat.st_ctime,
        'mode': stat.st_mode
    }
    # Create a consistent string representation of metadata
    metadata_str = f"{metadata['size']}_{metadata['mtime']}_{metadata['ctime']}_{metadata['mode']}"
    return hashlib.md5(metadata_str.encode()).hexdigest()

def calculate_full_md5(file_path):
    """Calculate the full MD5 of the entire file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

file_hashes_name = "HSDSync-hashes.json"

def manage_file_md5(file_path, json_file=file_hashes_name):
    """
    Manage file hashes using metadata as a quick check before full MD5 calculation.
    Returns the full MD5 hash of the file.
    """
    # Load the JSON file into memory if it hasn't been done already
    if not hasattr(manage_file_md5, "json_data"):
        try:
            with open(json_file, 'r') as f:
                manage_file_md5.json_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            manage_file_md5.json_data = {}
    
    # Calculate metadata hash
    metadata_hash = calculate_metadata_hash(file_path)
    
    # Check if the file exists in cache and metadata matches
    if file_path in manage_file_md5.json_data:
        stored_data = manage_file_md5.json_data[file_path]
        
        if stored_data['metadata_hash'] == metadata_hash:
            # Si les métadonnées correspondent, on retourne le MD5 stocké
            return stored_data['full_md5']
    
    # Si le fichier n'existe pas dans le cache ou si les métadonnées sont différentes
    full_md5 = calculate_full_md5(file_path)
    
    # Mettre à jour le cache
    manage_file_md5.json_data[file_path] = {
        'metadata_hash': metadata_hash,
        'full_md5': full_md5
    }
    
    # Sauvegarder dans le fichier JSON
    with open(json_file, 'w') as f:
        json.dump(manage_file_md5.json_data, f, indent=4)
    
    return full_md5