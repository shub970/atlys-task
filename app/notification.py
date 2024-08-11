from abc import ABC, abstractmethod


class NotificationHandler(ABC):
    @abstractmethod
    def notify(self):
        pass

# using Factory pattern here for extendibility
def NotificationHandlerFactory(medium='console'):
    notifiers = {
        "console": ConsoleNotifier
    }
    return notifiers[medium]()

class ConsoleNotifier(NotificationHandler):

    def __init__(self) -> None:
        super().__init__()
        
    def notify(self, message: str):
        print("Notification: ", message)
