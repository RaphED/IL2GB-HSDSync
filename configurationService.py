import json
import os

# Path to the configuration file
config_file = 'config.json'

# Default values for the configuration file
default_config = {
    "skinsDirectory": "D:\SteamLibrary\steamapps\common\IL-2 Sturmovik Battle of Stalingrad\data\graphics\skins",
}

# Global variable to hold the configuration in memory
current_config = None

# Function to load or create the configuration file
def load_config():
    # Check if the configuration file exists
    if not os.path.exists(config_file):
        # If the file doesn't exist, create it with the default values
        print(f"The file {config_file} does not exist, creating it with default values...")
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config
    else:
        # If the file exists, load it
        print(f"Loading the configuration file {config_file}...")
        with open(config_file, 'r') as f:
            return json.load(f)

def getConf(param):
    global current_config
    if current_config is None:
        current_config = load_config()
    
    value = current_config.get(param)
    if value is None:
        raise Exception(f"Internal error : unexpected param {param}")
    
    return value

def update_config_param(param, newValue):
    """ Update the in-memory configuration with new values and save it to the file. """
    global current_config
    current_config[param] = newValue

    with open(config_file, 'w') as f:
        json.dump(current_config, f, indent=4)
    print("Configuration updated successfully.")