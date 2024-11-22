import requests
import os
import subprocess
import sys
import time
from packaging.version import Version

SAVE_PATH="ISSS.exe"
API_URL = f"https://github.com/RaphED/IL2GB-inter-squadrons-skins-synchronizer"

def get_latest_release_info():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch release information.")
        return None


def update_application(download_url):
    try:
        # Send a GET request to download the file in streaming mode
        response = requests.get(download_url, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes (4xx, 5xx)
        
        # Open the target file in binary write mode and write chunks to it
        with open(SAVE_PATH, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):  # Download in chunks
                if chunk:  # Only write non-empty chunks
                    file.write(chunk)

        print(f"Executable saved successfully to: {SAVE_PATH}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the file: {e}")
    except IOError as e:
        print(f"Error saving the file: {e}")
    
    print("Application updated successfully.")


if __name__ == "__main__":
   
    release_info = get_latest_release_info()
    if release_info:
        # Assuming the first asset is what we want
        assets = release_info.get("assets", [])
        if assets:
            download_url = assets[0]["browser_download_url"]
            update_application(download_url) 
            
            # Restart new updated application
            time.sleep(5)
            try:
                    # Start the updater with the specified arguments
                    subprocess.Popen(
                        [SAVE_PATH],  # Arguments to the updater
                        shell=False,            # Don't use a shell to avoid unnecessary dependencies
                        close_fds=True,         # Close file descriptors to detach from the parent process
                        creationflags=subprocess.DETACHED_PROCESS if sys.platform == "win32" else 0  # Detach process on Windows
                    )
                    print("Updater launched successfully. Closing main application...")
                    sys.exit()  # Close the main application
            except Exception as e:
                print(f"Failed to launch updater: {e}")
                sys.exit(1)  # Exit with an error code              
