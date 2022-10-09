from queue import Queue
from typing import Any
from googleapiclient.discovery import HttpRequest


class GoogleClient:

    REQUESTS_QUEUE = Queue()

    requests_ans: dict[str, Any] = {}

    @classmethod
    def execute(cls, request: HttpRequest) -> None:
        cls.REQUESTS_QUEUE.put(request)

    @classmethod
    def execute_and_wait(cls, request: HttpRequest) -> Any:
        cls.REQUESTS_QUEUE.put(request)
        # Espero a que se añada la respuesta
        while True:
            if request.uri in cls.requests_ans:
                return cls.requests_ans[request.uri]

    @classmethod
    def run_queue(cls):
        while True:
            request: HttpRequest = cls.REQUESTS_QUEUE.get()
            if request is None:
                return

            cls.requests_ans[request.uri] = request.execute()
            cls.REQUESTS_QUEUE.task_done()
