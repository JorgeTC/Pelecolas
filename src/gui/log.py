from src.gui.console_event import ConsoleEvent, Priority

def Log(message: str):
    CLog(message)

class CLog(ConsoleEvent):
    def __init__(self, message: str, priority: Priority = Priority.LOW) -> None:
        ConsoleEvent.__init__(self, priority)

        self.message = message

        ConsoleEvent.execute_if_main_thread(self)

    def execute(self) -> None:
        print(self.message)
