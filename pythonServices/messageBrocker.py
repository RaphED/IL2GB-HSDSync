import time

class Message:
    def __init__(self, text: str, object: object = None):
        self.timeStamp = time.time()
        self.text = text
        self.object = object

class MessageBrocker:

    def __init__(self):
        self.messageHooks = list()

    #SINGLETON MANAGEMENT
    _instance = None

    @staticmethod
    def getSingletonInstance():
        if MessageBrocker._instance is None:
            MessageBrocker._instance = MessageBrocker()
        return MessageBrocker._instance

    #BUS EXTERNAL INTERRACTIONS
    @staticmethod
    def emitMessage(messageText: str, enclosedObject : object = None) -> None:
        #register the message in the bus
        newMessage = Message(messageText, enclosedObject)
        
        #and send it to the registered message hooks
        brocker_instance = MessageBrocker.getSingletonInstance()
        for hook in brocker_instance.messageHooks:
            hook(messageText)

    @staticmethod
    def registerHook(callback):
        brocker_instance = MessageBrocker.getSingletonInstance()
        brocker_instance.messageHooks.append(callback)
