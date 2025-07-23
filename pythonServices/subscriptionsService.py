import json
import requests

from pythonServices.filesService import fileExists
from pythonServices.remoteService import RemoteSkin

# Path to the subscription file
subscription_file = 'HSDSync-subscription.json'

# Function to load or create the subsscription file
def load_subscription_file():
    # Check if the file exists
    if not fileExists(subscription_file):
        # If the file doesn't exist, create it with the default values
        save_subscription_file()
    else:
        # If the file exists, load it
        with open(subscription_file, 'r') as f:
            try:
                global subscription_list
                subscription_list = json.load(f)
                return subscription_list
            except Exception as e:
                raise e
            
def save_subscription_file():
    with open(subscription_file, 'w') as f:
        json.dump(subscription_list, f, indent=4)            

class SubscribedCollection:
    def __init__(self, collectionURL: str, active: bool = True):
        self.collectionURL = collectionURL
        self.active = active

        self.id = None
        self.name = None
        self.descrption = None
        self.artist = None
        self.skins: list[RemoteSkin] = []

        #Automatically load data from URL on object creation
        self.loadDataFromURL()

    def loadDataFromURL(self):
        response = requests.get(self.collectionURL)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception (f"Cannot get collection data from URL {self.collectionURL}")


subscription_list:list [SubscribedCollection] = []

def getCollection(collection_id: int):
    for collection in subscription_list:
        if collection.id == collection_id:
            return collection
    return None

def importNewCollection(collectionURL: str):
    #Load the new collection
    new_collection = SubscribedCollection(collectionURL)
    #save it in the cache list
    global subscription_list
    #check collection is not already in the list
    if getCollection(new_collection.id) is not None:
        Warning(f"Cannot add the same collection twice (id ={new_collection.id})")
    else:
        subscription_list.append(new_collection)
        #save the file
        save_subscription_file()
    return new_collection

def removeCollection(collection_id):
    if getCollection(collection_id) is not None:
        Exception(f"Cannot remove non existing collection with id {collection_id}")
    global subscription_list
    subscription_list = [sub for sub in subscription_list if sub.id != collection_id]
    save_subscription_file()