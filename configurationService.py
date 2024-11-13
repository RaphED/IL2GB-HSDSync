import json
import os

# Path to the configuration file
config_file = 'config.json'

# Default values for the configuration file
default_config = {
    "IL2GBGameDirectory": "D:\\IL-2 Sturmovik Battle of Stalingrad",
    "autoRemoveUnregisteredSkins": False
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


def checkConfParamIsValid(param):
    match param:
        case "IL2GBGameDirectory":
            #skin directory is a good one if we can find the IL2.exe
            return os.path.exists(os.path.join(getConf(param), "bin\\game\\Il-2.exe"))
        
        case _:
            raise Exception(f"Unexpected param : {param}")