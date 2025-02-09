from enum import Enum, auto
from queue import Queue
from threading import Event
from typing import Any

from googleapiclient.discovery import HttpRequest


class QueuedRequest:
    def __init__(self, request: HttpRequest):
        # La request que ejecutaré
        self.request = request

        # Creo una variable en la que guardar el resultado de la request
        self.result = None

        # Genero un evento que marcaré como set cuando haya guardado la respuesta de la request
        self.event = Event()

    def execute(self):
        # Ejecuto la request, guardo el resultado
        self.result = self.request.execute()
        # y marco el evento como completado.
        self.event.set()

    def wait_result(self) -> Any:
        # Espero a que se ejecute el evento y se marque como completado
        self.event.wait()
        # Puedo entonces devolver el resultado
        return self.result


class RequestsQueue(Enum):
    DONE = auto()


class GoogleClient:

    # Cola de requests por ejecutar
    REQUESTS_QUEUE: Queue[QueuedRequest | RequestsQueue] = Queue()

    @classmethod
    def execute(cls, request: HttpRequest) -> None:
        # Añado la request a la cola
        cls.REQUESTS_QUEUE.put(QueuedRequest(request))

    @classmethod
    def execute_and_wait(cls, request: HttpRequest) -> Any:
        # Creo un objeto que es capaz de decirme cuándo ha sido ejecutada la request
        queued_request = QueuedRequest(request)
        # Le paso la request al ejecutor
        cls.REQUESTS_QUEUE.put(queued_request)

        # Pido al objeto que espere hasta que tenga la respuesta de la request
        return queued_request.wait_result()

    @classmethod
    def run_queue(cls):
        while (request := cls.REQUESTS_QUEUE.get()) is not RequestsQueue.DONE:
            # Ejecuto la request
            request.execute()
            # Indico que he acabado con la última request sacada de la cola
            cls.REQUESTS_QUEUE.task_done()

    @classmethod
    def close_queue(cls):
        cls.REQUESTS_QUEUE.put(RequestsQueue.DONE)
