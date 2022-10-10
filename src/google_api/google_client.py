from multiprocessing import Lock
from queue import Queue
from typing import Any

from googleapiclient.discovery import HttpRequest


class QueuedRequest(HttpRequest):
    def __init__(self, request: HttpRequest) -> None:
        self.locker = Lock()
        self.locker.acquire()

        self.result: Any = None
        self.request = request

    def execute(self) -> Any:
        self.result = self.request.execute()
        self.locker.release()

        return self.result

    @property
    def uri(self) -> str:
        return self.request.uri


class GoogleClient:

    REQUESTS_QUEUE = Queue()

    requests_ans: dict[str, Any] = {}

    @classmethod
    def execute(cls, request: HttpRequest) -> None:
        cls.REQUESTS_QUEUE.put(request)

    @classmethod
    def execute_and_wait(cls, request: HttpRequest) -> Any:
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

            cls.requests_ans[request.uri] = request.execute()
            cls.REQUESTS_QUEUE.task_done()
