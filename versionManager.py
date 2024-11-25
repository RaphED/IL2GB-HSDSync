import requests
from packaging.version import Version


#This is THE reference for the current ISS version
#Change version here when preparing a new release
currentVersion = 0

GITHUB_REPO_URL = "https://api.github.com/repos/RaphED/IL2GB-inter-squadrons-skins-synchronizer"

def getCurrentVersion():
    return currentVersion

def get_latest_release_info():
    response = requests.get(f"{GITHUB_REPO_URL}/releases/latest")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception ("Cannot get current version information")
    
def isCurrentVersionUpToDate():
    release_info = get_latest_release_info()
    latest_version = release_info["tag_name"]
    current_version = Version(f"{getCurrentVersion()}")
    remote_version = Version(latest_version)
    return remote_version <= current_version


#Direct access to provide the current version when calling directly that file (used for the build script)
if __name__ == "__main__":
    print(getCurrentVersion())