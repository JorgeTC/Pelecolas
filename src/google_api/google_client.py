from multiprocessing import Lock
from queue import Queue
from typing import Any

from googleapiclient.discovery import HttpRequest


class QueuedRequest(HttpRequest):
    def __init__(self, request: HttpRequest) -> None:
        self.request = request

        # Creo un locker que liberaré cuando tenga la respuesta
        self.locker = Lock()
        self.locker.acquire()

        # Variable para la respuesta de la request
        self.result: Any = None

    def execute(self) -> Any:
        # Ejecuto la request
        self.result = HttpRequest.execute(self)
        # Libero el locker para indicar que ya está el resultado
        self.locker.release()

        # Devuelvo lo que me ha dado el método execute de la clase base
        return self.result

    def __getattr__(self, attr):
        # Cuando quiera acceder a un atributo de la clase base,
        # lo saco de la instancia que tengo guardada.
        return getattr(self.request, attr)


class GoogleClient:

    # Cola de requests por ejecutar
    REQUESTS_QUEUE = Queue()

    # Historial de todas las request
    requests_ans: dict[str, Any] = {}

    @classmethod
    def execute(cls, request: HttpRequest) -> None:
        # Añado la request a la cola
        cls.REQUESTS_QUEUE.put(request)

    @classmethod
    def execute_and_wait(cls, request: HttpRequest) -> Any:
        # Añado la request a la cola
        enrich_request = QueuedRequest(request)
        cls.REQUESTS_QUEUE.put(enrich_request)

        # Espero a que se obtenga la respuesta
        with enrich_request.locker:
            return enrich_request.result

    @classmethod
    def run_queue(cls):
        while True:
            request: HttpRequest = cls.REQUESTS_QUEUE.get()
            if request is None:
                return

            # Ejecuto la request y la guardo en el historial
            cls.requests_ans[request.uri] = request.execute()
            # Indico que he acabado con la última request sacada de la cola
            cls.REQUESTS_QUEUE.task_done()
