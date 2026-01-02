import json
import os
import string
import winreg
from pathlib import Path

# Path to the configuration file
config_file = 'HSDSync-config.json'

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

def _check_steam_registry():
    """Check Windows registry for Steam installation path."""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam")
        steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
        winreg.CloseKey(key)
        return steam_path
    except:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam")
            steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
            winreg.CloseKey(key)
            return steam_path
        except:
            return None

def _get_steam_library_folders(steam_path):
    """Get all Steam library folders from libraryfolders.vdf."""
    libraries = [steam_path]
    vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
    
    try:
        if os.path.exists(vdf_path):
            with open(vdf_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Parse the VDF file to find library paths
                import re
                paths = re.findall(r'"path"\s+"([^"]+)"', content)
                libraries.extend(paths)
    except:
        pass
    
    return libraries

def _search_in_directory(directory, exe_name='Il-2.exe', max_depth=4):
    """Search for IL-2 executable in a specific directory with limited depth."""
    try:
        for root, dirs, files in os.walk(directory):
            # Limit search depth
            depth = root[len(directory):].count(os.sep)
            if depth > max_depth:
                dirs[:] = []  # Don't go deeper
                continue
            
            if exe_name in files:
                # Return the parent directory of bin/game/Il-2.exe
                return os.path.dirname(os.path.dirname(os.path.dirname(os.path.join(root, exe_name))))
    except (PermissionError, OSError):
        pass
    return None

def tryToFindIL2Path(exe_name='Il-2.exe'):
    """
    Try to find IL-2 Sturmovik installation path using optimized search:
    1. Check Steam registry and known Steam libraries
    2. Check common installation directories
    3. As last resort, search all drives (limited depth)
    """
    
    # Priority 1: Check Steam registry and libraries
    steam_path = _check_steam_registry()
    if steam_path:
        steam_libraries = _get_steam_library_folders(steam_path)
        for library in steam_libraries:
            # Check in steamapps/common folder
            common_path = os.path.join(library, "steamapps", "common")
            if os.path.exists(common_path):
                result = _search_in_directory(common_path, exe_name, max_depth=3)
                if result:
                    return os.path.normpath(result)
    
    # Priority 2: Check common installation directories
    drives = [drive + ':\\' for drive in string.ascii_uppercase if os.path.exists(drive + ':')]
    common_dirs = [
        "Program Files (x86)\\Steam\\steamapps\\common",
        "Program Files\\Steam\\steamapps\\common",
        "Steam\\steamapps\\common",
        "Games",
        "SteamLibrary\\steamapps\\common"
    ]
    
    for drive in drives:
        for common_dir in common_dirs:
            full_path = os.path.join(drive, common_dir)
            if os.path.exists(full_path):
                result = _search_in_directory(full_path, exe_name, max_depth=3)
                if result:
                    return os.path.normpath(result)
    
    # Priority 3: Search root of each drive (limited depth as last resort)
    for drive in drives:
        # Only search at limited depth to avoid scanning entire system
        result = _search_in_directory(drive, exe_name, max_depth=2)
        if result:
            return os.path.normpath(result)
    
    return None  # Return None if the file was not found

def customPhotoSyncIsActive():
    return getConf("cockpitNotesMode") != "noSync"