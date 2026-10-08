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
    "IL2KoreaGameDirectory": "",
    "autoRemoveUnregisteredSkins": False,
    "cockpitNotesMode": "noSync",
    "applyCensorship": False,
    "displayCollectionsIcons": False
}

# Supported games, keyed by the game code used by HSD (game_asset.game)
# - configKey: configuration parameter holding the game root folder (empty = game not installed)
# - exeName: executable in <root>\bin\game, used to check and auto-detect the root folder
# - launcherSubFolder: sub folder holding the game root, when the launcher folder is selected instead
GAMES = {
    "IL2GB": {
        "label": "IL-2 Great Battles",
        "configKey": "IL2GBGameDirectory",
        "exeName": "Il-2.exe",
        "launcherSubFolder": None,
    },
    "IL2Korea": {
        "label": "IL-2 Korea",
        "configKey": "IL2KoreaGameDirectory",
        "exeName": "IL2Series.exe",
        "launcherSubFolder": "game",
    },
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

def getGameDirectory(game):
    return getConf(GAMES[game]["configKey"])

def isValidGamePath(game, path):
    if not path:
        return False
    return os.path.exists(os.path.join(path, "bin\\game", GAMES[game]["exeName"]))

def checkGameInstallPath(game):
    return isValidGamePath(game, getGameDirectory(game))

def isGameConfigured(game):
    return getGameDirectory(game) != ""

def getInstalledGames():
    return [game for game in GAMES.keys() if checkGameInstallPath(game)]

def normalizeGamePath(game, path):
    """Return the game root folder for a selected folder (the launcher folder is accepted for games that have one)"""
    subFolder = GAMES[game]["launcherSubFolder"]
    if subFolder and not isValidGamePath(game, path) and isValidGamePath(game, os.path.join(path, subFolder)):
        return os.path.normpath(os.path.join(path, subFolder))
    return path

def setGameDirectory(game, path):
    update_config_param(GAMES[game]["configKey"], normalizeGamePath(game, os.path.normpath(path)))

def detectPathsOfNewGames():
    """Once per game added after the configuration file was generated: try to auto-detect its path.
    The parameter is stored even when not found (empty), so that the search is not done at each launch."""
    global current_config
    if current_config is None:
        current_config = load_config()
    for game, game_info in GAMES.items():
        if game_info["configKey"] in current_config:
            continue
        foundGamePath = tryToFindGamePath(game)
        if foundGamePath:
            setGameDirectory(game, foundGamePath)
        else:
            update_config_param(game_info["configKey"], "")

def _get_uninstall_locations():
    """Install locations of the IL-2 games registered in Windows (standalone installers and Steam)."""
    locations = []
    uninstall_keys = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    for hive, key_path in uninstall_keys:
        try:
            key = winreg.OpenKey(hive, key_path)
        except OSError:
            continue
        for index in range(winreg.QueryInfoKey(key)[0]):
            try:
                sub_key = winreg.OpenKey(key, winreg.EnumKey(key, index))
                display_name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                if "IL-2" in display_name or "IL2" in display_name:
                    locations.append(winreg.QueryValueEx(sub_key, "InstallLocation")[0])
                winreg.CloseKey(sub_key)
            except OSError:
                continue
        winreg.CloseKey(key)
    return [location for location in locations if location and os.path.exists(location)]

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

def tryToFindGamePath(game):
    return tryToFindIL2Path(GAMES[game]["exeName"])

def tryToFindIL2Path(exe_name='Il-2.exe'):
    """
    Try to find IL-2 Sturmovik installation path using optimized search:
    0. Check the install locations registered in Windows
    1. Check Steam registry and known Steam libraries
    2. Check common installation directories
    3. As last resort, search all drives (limited depth)
    """

    # Priority 0: Check registered install locations (e.g. IL-2 Korea standalone installer)
    for location in _get_uninstall_locations():
        result = _search_in_directory(location, exe_name, max_depth=3)
        if result:
            return os.path.normpath(result)

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
    #cockpit notes only exist for IL-2 Great Battles
    return getConf("cockpitNotesMode") != "noSync" and checkGameInstallPath("IL2GB")