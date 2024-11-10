import os
import json
import re

class SubscribedCollection:
    def __init__(self, source, criteria):
        #todo : check source is an existing one
        self.source = source
        #todo ? check criteria is a dictionary
        self.criteria: dict[str,str]= criteria
        

    def isInCollection(self, remoteSkinInfo):
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
                source=rawSubscription["source"],
                criteria=rawSubscription["criteria"]
            )
        )
    
    return subscribedCollectionlist

def getAllSubscribedCollection():


    returnedCollections = []
    subscriptionPath = os.path.join(os.getcwd(),"Subscriptions")
    #TODO : manage if folder does not exist
    for root, dirs, files in os.walk(subscriptionPath):
        for file in files:
            if file.endswith(".is3"):
                returnedCollections += getSubscribedCollectionFromFile(os.path.join(root,file))
    
    return returnedCollections