from typing import Callable, Any

class MessageBrocker:

    def __init__(self):
        self.consoleMessageHooks = list[Callable[[str], Any]]()
        self.progressHooks = list[Callable[[float], Any]]()

    #SINGLETON MANAGEMENT
    _instance = None

    @staticmethod
    def getSingletonInstance():
        if MessageBrocker._instance is None:
            MessageBrocker._instance = MessageBrocker()
        return MessageBrocker._instance

    #EXTERNAL INTERRACTIONS
    # --- CONSOLE MESSAGES
    @staticmethod
    def emitConsoleMessage(consoleText: str) -> None:
       brocker_instance = MessageBrocker.getSingletonInstance()
       for hook in brocker_instance.consoleMessageHooks:
           hook(consoleText)

    @staticmethod
    def registerConsoleHook(callback: Callable[[str], Any]):
        brocker_instance = MessageBrocker.getSingletonInstance()
        brocker_instance.consoleMessageHooks.append(callback)

    # --- PROGRESS MESSAGES
    @staticmethod
    def emitProgress(percentage: float) -> None:
       brocker_instance = MessageBrocker.getSingletonInstance()
       for hook in brocker_instance.progressHooks:
           hook(percentage)

    @staticmethod
    def registerProgressHook(callback: Callable[[float], Any]):
        brocker_instance = MessageBrocker.getSingletonInstance()
        brocker_instance.progressHooks.append(callback)
