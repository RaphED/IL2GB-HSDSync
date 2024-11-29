import requests
import re
import os
import logging

from pythonServices.configurationService import getConf
from pythonServices.filesService import downloadFile

sourcesInfo = [
    {
        "source":"HSD",
        "catalogURL": "https://skins.combatbox.net/Info.txt",
        "skinsURL": "https://skins.combatbox.net/[aircraft]/[skinFileName]",
        "params":{
            "aircraft": "Plane",
            "name": "Title",
            "mainSkinFileName": "Skin0",
            "mainFileMd5": "HashDDS0",
            "mainFileSize":"Filesize0",
            "secondarySkinFileName": "Skin01",
            "secondaryFileMd5": "HashDDS01",
            "secondaryFileSize":"Filesize01",
        }
    }
]

def getSourceInfo(source):
    for sourceIter in sourcesInfo:
        if sourceIter["source"] == source:
            return sourceIter
    raise Exception(f"Caanot find source {source}!")

def getSourceParam(source, param):
    return getSourceInfo(source)["params"][param]

def getSkinsCatalogFromSource(source):

    # Download the content of the file
    sourceInfo = getSourceInfo(source)
    if sourcesInfo is None: 
        raise Exception("Unexpected source")
    response = requests.get(sourceInfo["catalogURL"])

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        file_content = response.text
        
        # Dictionary to store the skins
        skins = {}

        # Use regular expression to split the content into skin sections
        sections = re.split(r'\[Skin-\d+\]', file_content)[1:]  # Ignore the part before the first skin

        # For each section after the header
        for i, section in enumerate(sections):
            # Clean up the section
            section = section.strip()
            if not section:
                continue

            skin_id = i

            # Dictionary to store the skin information
            skin_info = {}

            # Loop through each line of the section
            for line in section.splitlines():
                # Ignore empty lines or comment lines (lines starting with #)
                if line.strip() and not line.startswith("#"):
                    try:
                        key, value = line.split('=', 1)  # Split at the first '='
                        skin_info[key.strip()] = value.strip()  # Store the key-value pair
                    except ValueError:
                        logging.error(f"Formatting error on line: {line}")

            # Add the skin information to the main dictionary
            skins[skin_id] = skin_info

        # return only the values (we do not need skins ids)
        return skins.values()

    else:
        raise Exception(f"Error downloading the file. Status code: {response.status_code}")

def getSpaceUsageOfRemoteSkinCatalog(source, remoteSkinList):
    totalDiskSpace = 0
    for skin in remoteSkinList:
        totalDiskSpace += int(skin[getSourceParam(source, "mainFileSize")])
        
        secondaryFileSpace = skin[getSourceParam(source, "secondaryFileSize")]
        if secondaryFileSpace is not None and secondaryFileSpace != "":
            totalDiskSpace += int(secondaryFileSpace)
    
    return totalDiskSpace

def downloadSkinToTempDir(source, skinInfo):

    #build skin URL
    url = getSourceInfo(source)["skinsURL"]
    url = url.replace("[aircraft]", skinInfo[getSourceParam(source, "aircraft")])
    urlMainSkin = url.replace("[skinFileName]", skinInfo[getSourceParam(source, "mainSkinFileName")])

    # Download the file(s) to the temporary folder
    downloadedFiles = []
    downloadedFiles.append(downloadFile(url=urlMainSkin, expectedMD5=skinInfo[getSourceParam(source, "mainFileMd5")]))
    
    #if there is a second skin file
    secondarySkinFileName = skinInfo.get(getSourceParam(source, "secondarySkinFileName"))
    if secondarySkinFileName is not None and secondarySkinFileName != "":
        #hack : works only for HSD, the #1 is replaced by %123 on the URL
        remoteFileName = skinInfo[getSourceParam(source, "secondarySkinFileName")].replace("#1", "%231")
        urlSecondarySkin = url.replace("[skinFileName]", remoteFileName)
        downloadFileName = downloadFile(url=urlSecondarySkin, expectedMD5=skinInfo[getSourceParam(source, "secondaryFileMd5")])
        properFileName = downloadFileName.replace("%231","#1")
        os.rename(downloadFileName, properFileName)
        downloadedFiles.append(properFileName)
    
    return downloadedFiles


customPhotosCatalogURL = "https://www.lesirreductibles.com/irreskins/IRRE/CustomPhotos/[mode]CustomPhotosManifest.json"
customPhotosFilesURL = "https://www.lesirreductibles.com/irreskins/IRRE/CustomPhotos/[mode]/[aircraft]/Textures/custom_photo.dds"


def getCockpitNotesModeInfo(mode):
    match mode:
        case "noSync":
            return {
                "catalogURL": None,
                "filesURL": None
            }
        case "originalPhotos" | "officialNumbers" | "technochatNumbers":
            return {
                "catalogURL": customPhotosCatalogURL.replace("[mode]", mode),
                "filesURL": customPhotosFilesURL.replace("[mode]", mode),
            }
        case _:
            raise Exception(f"Unexpected cockpitNotesModes {mode}")

def getCustomPhotosList():
    #hard coded remote address for the cockpitNotesCatalog
    catalogURL = getCockpitNotesModeInfo(getConf("cockpitNotesMode"))["catalogURL"]
    if catalogURL is None:
        return []

    response = requests.get(catalogURL)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        file_content = response.json()
        return file_content
    return []

def downloadCustomPhoto(cockpitNotesMode, cockpitNote):
    filesURL = getCockpitNotesModeInfo(cockpitNotesMode)["filesURL"]

    targetURL = filesURL.replace("[aircraft]", cockpitNote["aircraft"])
    return downloadFile(targetURL, cockpitNote["md5"])