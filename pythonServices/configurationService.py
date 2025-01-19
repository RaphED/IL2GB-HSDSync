import json
import os
import string

# Path to the configuration file
config_file = 'ISS-config.json'

# Default values for the configuration file
default_config = {
    "IL2GBGameDirectory": "D:\\IL-2 Sturmovik Battle of Stalingrad",
    "autoRemoveUnregisteredSkins": False,
    "cockpitNotesMode": "noSync",
    "applyCensorship": False
}

cockpitNotesModes = {
    "noSync": "No synchronization, keep current images",
    "originalPhotos": "Original IL2 game photos",
    "officialNumbers": "Cockpit notes from IL2 specifications (C6_lefuneste)",
    "technochatNumbers": "Cockpit notes from technochat measurements (C6_lefuneste)",
    "MetalheadNumbers": "Cockpit notes from Metalhead measurements"
}


# Global variable to hold the configuration in memory
current_config = None

def configurationFileExists():
    return os.path.exists(config_file)

# Function to load or create the configuration file
def load_config():
    # Check if the configuration file exists
    if not configurationFileExists():
        # If the file doesn't exist, create it with the default values
        raise Exception(f"The configuration file {config_file} does not exist")
    else:
        # If the file exists, load it
        with open(config_file, 'r') as f:
            try:
                global current_config
                current_config = json.load(f)
                return current_config
            except json.JSONDecodeError as e:
                raise Exception(
                    f"Cannot read configuration file {config_file}.\n"
                    f"Check json format, and especially '\\' caracters in the paths that must be written '\\\\'\n"
                    f"ERROR detail -> {e}"
                    )
            except Exception as e:
                raise e

def getConf(param):
    global current_config
    if current_config is None:
        current_config = load_config()
    
    value = current_config.get(param)
    #if the value cannot be found, try to initialise it with the default value
    if value is None:
        value = default_config.get(param)
    
    #the value is not even in the default one which means it is not a proper one
    if value is None:
        raise Exception(f"Internal error : unexpected param {param}")
    
    return value

def update_config_param(param, newValue):
    """ Update the in-memory configuration with new values and save it to the file. """
    global current_config
    if current_config is None:
        current_config = load_config()
    current_config[param] = newValue

    with open(config_file, 'w') as f:
        json.dump(current_config, f, indent=4)

def generateConfFile():
    with open(config_file, 'w') as f:
        json.dump(default_config, f, indent=4)
    return default_config

def checkIL2InstallPath():
    return os.path.exists(os.path.join(getConf("IL2GBGameDirectory"), "bin\\game\\Il-2.exe"))

def tryToFindIL2Path(exe_name='Il-2.exe'):
    # Get the list of available drives (e.g., C:, D:, etc.)
    drives = [drive + ':\\' for drive in string.ascii_uppercase if os.path.exists(drive + ':')]

    for drive in drives:
        # Traverse each drive looking for the IL2.exe file
        for root, dirs, files in os.walk(drive, followlinks=True):
            try:
                if exe_name in files:
                    # Return the parent directory of the found file
                    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.join(root, exe_name))))
            except PermissionError:
                # Ignore permission errors and continue with the next directories
                continue
    
    return None  # Return None if the file was not found

def customPhotoSyncIsActive():
    return getConf("cockpitNotesMode") != "noSync"