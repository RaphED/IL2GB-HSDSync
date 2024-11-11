import os
import json
import re
from remoteService import getSourceInfo 

class SubscribedCollection:
    def __init__(self, source, criteria):
        
        #default source is HSD
        sourceName = "HSD"
        if source is not None:
            sourceName = source
        self.source = getSourceInfo(sourceName)["source"]
        
        self.criteria: dict[str,str]= criteria
        

    def match(self, remoteSkinInfo):
        for criterion in self.criteria.keys():
            #transform * in .*
            matchingRegExp =self.criteria[criterion].replace("*", ".*") 
            if not re.match(matchingRegExp,remoteSkinInfo[criterion]):
                return False
        return True

def getSubscribedCollectionFromFile(subscriptionFilePath):
    file = open(subscriptionFilePath, "r")
    rawJsonData: list = json.load(file)

    subscribedCollectionlist = []
    #raw data should be a list
    for rawSubscription in rawJsonData:
        subscribedCollectionlist.append(
            SubscribedCollection(
                source=rawSubscription.get("source"),
                criteria=rawSubscription["criteria"]
            )
        )
    
    return subscribedCollectionlist

def getAllSubscribedCollection() -> list[SubscribedCollection]:

    returnedCollections = []
    subscriptionPath = os.path.join(os.getcwd(),"Subscriptions")
    #create subsciption path of not exists
    if not os.path.exists(subscriptionPath):
        os.makedirs(subscriptionPath)
    
    for root, dirs, files in os.walk(subscriptionPath):
        for file in files:
            if file.endswith(".is3"): #We only consider files with is3 extension
                returnedCollections += getSubscribedCollectionFromFile(os.path.join(root,file))
    
    return returnedCollections