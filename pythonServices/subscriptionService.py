import os
import json
import re
import logging
import shutil

from pythonServices.remoteService import getSourceInfo, RemoteSkin
from pythonServices.filesService import downloadFile

subscriptionPath = os.path.join(os.getcwd(),"Subscriptions")

class SubscribedCollection:
    def __init__(self, subcriptionName, source, criteria):
        
        self.subcriptionName = subcriptionName
        #default source is HSD
        sourceName = "HSD"
        if source is not None:
            sourceName = source
        self.source = getSourceInfo(sourceName)["source"]
        
        self.criteria: dict[str,str]= criteria
        

    def match(self, remoteSkinInfo: RemoteSkin, applyCensorship = False) -> bool:
        
        #cannot take a skin if we want to apply censorship and there is not uncensored version
        if applyCensorship and not remoteSkinInfo.hasAnCensoredVersion():
            return False
        
        for criterion in self.criteria.keys():
            if remoteSkinInfo.infos.get(criterion) is None:
                logging.warning(f"Unexpected criteron '{criterion}' for skin source '{remoteSkinInfo.source}' and collection '{self.subcriptionName}'")
                return False
            #transform * in .*
            matchingRegExp =self.criteria[criterion].replace("*", ".*") 
            if not re.match(matchingRegExp,remoteSkinInfo.infos[criterion]):
                return False
        return True
    
    def toString(self):
        return f"{self.subcriptionName} - source is {self.source} - {self.criteria}" 

def getSubscribedCollectionFromFile(subscriptionFilePath):
    
    subscribedCollectionlist = []
    try:
        file = open(subscriptionFilePath, "r")
        rawJsonData = json.load(file)

        #raw data should be a list
        for rawSubscription in rawJsonData:
            proxyFile = rawSubscription.get("ProxyISS")
            if proxyFile is None:   #OPTION 1 : this is a normal collection
                subscribedCollectionlist.append(
                    SubscribedCollection(
                        subcriptionName=os.path.basename(subscriptionFilePath).replace(".iss", ""),
                        source=rawSubscription.get("source"),
                        criteria=rawSubscription["criteria"]
                    )
                )
            else:   #OPTION 2 : this is a link to remote iss file
                downloadedFile = downloadFile(proxyFile, prefix_with_uuid=True)
                subscribedCollectionlist += getSubscribedCollectionFromFile(downloadedFile)

        
        return subscribedCollectionlist
                
    except Exception as e:
        logging.error(f"Error at loading subscription file {subscriptionFilePath}. Error detail : {e}")
        return []
    
def getSubscribeCollectionFromRawJson(rawJson,name):
    cooked=json.loads(rawJson)
    subscribedCollectionlist = []
    for rawSubscription in cooked:
            subscribedCollectionlist.append(
                SubscribedCollection(
                    subcriptionName=os.path.basename(name),
                    source=rawSubscription.get("source"),
                    criteria=rawSubscription["criteria"]
                )
            )
    return subscribedCollectionlist
        
def getAllSubscribedCollection() -> list[SubscribedCollection]:

    returnedCollections = []
    subscriptionDictionary = getAllSubscribedCollectionByFileName()
    for fileName in subscriptionDictionary.keys():
        returnedCollections += subscriptionDictionary[fileName]
        
    return returnedCollections

def getAllSubscribedCollectionByFileName(getDisabledFiles = False) -> dict[str, list[SubscribedCollection]]:
    returnedCollections = dict[str, list[SubscribedCollection]]()
    #create subsciption path of not exists
    if not os.path.exists(subscriptionPath):
        os.makedirs(subscriptionPath)
    
    for root, dirs, files in os.walk(subscriptionPath):
        for file in files:
            if file.endswith(".iss"): #We only consider files with iss extension
                returnedCollections[file] = getSubscribedCollectionFromFile(os.path.join(root,file))
            if getDisabledFiles and file.endswith(".iss.disabled"):
                returnedCollections[file] = getSubscribedCollectionFromFile(os.path.join(root,file))
    
    return returnedCollections

def isSubcriptionFolderEmpty():
    for root, dirs, files in os.walk(subscriptionPath):
        for file in files:
            if file.endswith(".iss"): #We only consider files with iss extension
                return False
    
    return True

def getSubcriptionNameFromFileName(fileNameWithExtension):
    if fileNameWithExtension.endswith(".iss"):
        return fileNameWithExtension[:-4]
    elif fileNameWithExtension.endswith(".iss.disabled"):
        return fileNameWithExtension[:-13]
    else:
        raise Exception(f"Unexpected subscription file name {fileNameWithExtension}")

def activateSubscription(fileNameWithExtension):
    filePath = os.path.join(subscriptionPath, fileNameWithExtension)
    if not os.path.exists(filePath) or not fileNameWithExtension.endswith(".iss.disabled"):
        raise Exception(f"Unexpected subscription to activate {fileNameWithExtension}")
    else:
        newFileName = fileNameWithExtension[:-9]
        newFilePath = os.path.join(subscriptionPath, newFileName)
        os.rename(filePath,newFilePath)
        return newFileName

def desactivateSubscription(fileNameWithExtension):
    filePath = os.path.join(subscriptionPath, fileNameWithExtension)
    if not os.path.exists(filePath) or not fileNameWithExtension.endswith(".iss"):
        raise Exception(f"Unexpected subscription to activate {fileNameWithExtension}")
    else:
        newFileName = fileNameWithExtension + ".disabled"
        newFilePath = os.path.join(subscriptionPath, newFileName)
        os.rename(filePath,newFilePath)
        return newFileName

def deleteSubscriptionFile(fileNameWithExtension):
    filePath = os.path.join(subscriptionPath, fileNameWithExtension)
    if not os.path.exists(filePath):
        raise Exception(f"Unexpected subscription to delete {fileNameWithExtension}")
    else:
        os.remove(filePath)

def importSubcriptionFile(file_path):
    # Copy the selected file to the 'Subscriptions' folder
    file_name = os.path.basename(file_path)  # Extract the file name
    destination_path = os.path.join(subscriptionPath, file_name)
    shutil.copy(file_path, destination_path)
    return destination_path