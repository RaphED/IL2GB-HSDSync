import os
from pythonServices.localService import getAndGenerateCustomPhotosCatalogFromPath

#(temporary?) tool used for preparing the custom photos folders :
#   - prepare the manifest files
#   - fix key sensitives issues

print("Start preparing custom photo folders")

mainPath = "D:\\Perso\\IRRE\\tech data cards"
folders = ["originalPhotos", "officialNumbers", "technochatNumbers", "MetalheadNumbers"]


#get subfolders and fix the caps naming issues
for folder in os.listdir(mainPath):
    if folder in folders:
        #ok we have one, lets fix some caps issus
        subFolderPath = os.path.join(mainPath, folder)

        print(f"-Folders {subFolderPath}")

        print(f"\t-Fixing names")
        #at first, lets rename the aircraft folders
        for aircraftFolder in os.listdir(subFolderPath):
            
            #aircraft folder renaming
            if aircraftFolder == "il2m42":
                os.rename(os.path.join(subFolderPath, aircraftFolder), os.path.join(subFolderPath, "IL2M42"))
            elif aircraftFolder == "il2m43":
                os.rename(os.path.join(subFolderPath, aircraftFolder), os.path.join(subFolderPath, "IL2m43"))
            elif aircraftFolder == "ju88C6":
                os.rename(os.path.join(subFolderPath, aircraftFolder), os.path.join(subFolderPath, "Ju88C6"))

        #rename "textures" folders to "Textures"
        for aircraftFolder in os.listdir(subFolderPath):
            for subAircraftFolder in os.listdir(os.path.join(subFolderPath, aircraftFolder)):
                if subAircraftFolder == "textures":
                    os.rename(os.path.join(subFolderPath, aircraftFolder, subAircraftFolder), os.path.join(subFolderPath, aircraftFolder, "Textures"))

        print(f"\t-Generating manifest")
        #then generate the manifest files
        getAndGenerateCustomPhotosCatalogFromPath(mainPath, folder)

print("DONE")