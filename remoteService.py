import requests
import re
import os
import hashlib

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
            "secondSkinFileName": "Skin1",
            "secondFileMd5": "HashDDS1"
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
                        print(f"Formatting error on line: {line}")

            # Add the skin information to the main dictionary
            skins[skin_id] = skin_info

        # return only the values (we do not need skins ids)
        return skins.values()

    else:
        raise Exception(f"Error downloading the file. Status code: {response.status_code}")


# Function to download a file from a URL and save it to a temporary directory
def downloadFile(url, temp_dir, expectedMD5):
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for HTTP errors
    temp_file_path = os.path.join(temp_dir, os.path.basename(url))

    with open(temp_file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):#TODO : check the chunk size is a good one
            f.write(chunk)
    
    if hashlib.md5(open(temp_file_path, "rb").read()).hexdigest() != expectedMD5:
        #TODO, retry
        raise Exception(f"Bad file download {temp_file_path}")
    
    return temp_file_path

def downloadSkinToTempDir(source, skinInfo, tempDir):

    #build skin URL
    url = getSourceInfo(source)["skinsURL"]
    url = url.replace("[aircraft]", skinInfo[getSourceParam(source, "aircraft")])
    url = url.replace("[skinFileName]", skinInfo[getSourceParam(source, "mainSkinFileName")])
    #TODO : manage two files skins
    # Download the file to the temporary folder
    return downloadFile(url=url, temp_dir=tempDir, expectedMD5=skinInfo[getSourceParam(source, "mainFileMd5")])