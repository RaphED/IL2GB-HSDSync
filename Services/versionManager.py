import requests
from packaging.version import Version


#This is THE reference for the current version
#Change version here when preparing a new release
currentVersion = 3

GITHUB_REPO_URL = "https://api.github.com/repos/RaphED/IL2GB-HSDSync"

def getCurrentVersion():
    return currentVersion

def getReleases():
    response = requests.get(f"{GITHUB_REPO_URL}/releases")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception ("Cannot get current version information")
    
def getLastRelease(draft = False, prerelease = False):
    lastRelease = None
    for release in getReleases():
        if release["draft"] and not draft:
            continue
        if release["prerelease"] and not prerelease:
            continue
        if lastRelease is None:
            lastRelease = release
        else:
            if Version(release["tag_name"]) > Version(lastRelease["tag_name"]):
                lastRelease = release

    return lastRelease
    
def isCurrentVersionUpToDate(draft = False, prerelease = False):
    release_info = getLastRelease(draft, prerelease)
    #special case where there is no current released version
    if release_info is None:
        return True
    latest_version = release_info["tag_name"]
    current_version = Version(f"{getCurrentVersion()}")
    remote_version = Version(latest_version)
    return remote_version <= current_version

#Direct access to provide the current version when calling directly that file (used for the build script)
if __name__ == "__main__":
    print(getCurrentVersion())