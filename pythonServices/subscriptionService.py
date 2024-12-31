import os
import json
import re
import logging

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
                downloadedFile = downloadFile(proxyFile)
                subscribedCollectionlist += getSubscribedCollectionFromFile(downloadedFile)

        
        return subscribedCollectionlist
                
    except Exception as e:
        logging.error(f"Error at loading subscription file {subscriptionFilePath}. Error detail : {e}")
        return []
    
def getSubscribeCollectionFromRawJson(rawJson,name):
    subscribedCollectionlist = []
    for rawSubscription in rawJson:
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

def getAllSubscribedCollectionByFileName() -> dict[str, list[SubscribedCollection]]:
    returnedCollections = dict[str, list[SubscribedCollection]]()
    #create subsciption path of not exists
    if not os.path.exists(subscriptionPath):
        os.makedirs(subscriptionPath)
    
    for root, dirs, files in os.walk(subscriptionPath):
        for file in files:
            if file.endswith(".iss"): #We only consider files with iss extension
                returnedCollections[file[:-4]] = getSubscribedCollectionFromFile(os.path.join(root,file))
    
    return returnedCollections

def isSubcriptionFolderEmpty():
    for root, dirs, files in os.walk(subscriptionPath):
        for file in files:
            if file.endswith(".iss"): #We only consider files with iss extension
                return False
    
    return True