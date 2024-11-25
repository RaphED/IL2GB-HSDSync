import os
import shutil
import requests
import hashlib

temporaryFolder = "temp"

def getTempFolderFullPath():
    return os.path.join(os.curdir, temporaryFolder)

def temporaryFolderExists():
    return os.path.exists(getTempFolderFullPath())

def cleanTemporaryFolder():
    if temporaryFolderExists():
        for root, dirs, files in os.walk(getTempFolderFullPath()):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

# Function to download a file from a URL and save it to a temporary directory
def downloadFile(url, expectedMD5 = None):
    
    tempDir = getTempFolderFullPath()
    #create the temp directory if not exist
    if not os.path.exists(tempDir):
        os.makedirs(tempDir)
    
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for HTTP errors
    temp_file_path = os.path.join(tempDir, os.path.basename(url))

    with open(temp_file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):#TODO : check the chunk size is a good one
            f.write(chunk)
    
    if expectedMD5 is not None and hashlib.md5(open(temp_file_path, "rb").read()).hexdigest() != expectedMD5:
        #TODO, retry
        raise Exception(f"Bad file download {temp_file_path}")
    
    return temp_file_path


# Function to move the file and replace if necessary
def moveFile(src_path, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    dest_path = os.path.join(dest_dir, os.path.basename(src_path))
    
    # Remove the destination file if it exists
    if os.path.exists(dest_path):
        os.remove(dest_path)

    # Move the file
    shutil.move(src_path, dest_path)
    return dest_path
