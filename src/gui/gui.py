
from queue import Queue
from threading import Thread, current_thread
from src.gui.console_event import ConsoleEvent


class GUI:
    # Todos los hilos (distintos de main) que quieren acceder a la interfaz
    THREADS_QUEUE = Queue()
    # Cola con todos los eventos de consola
    INTERFACE_QUEUE: dict[Thread, Queue] = {}

    @classmethod
    def add_event(cls, current_thread: Thread, event: ConsoleEvent):
        # Si el hilo introducido ya tiene más eventos encolados, añado uno más
        if current_thread in cls.INTERFACE_QUEUE:
            queue = cls.INTERFACE_QUEUE[current_thread]
        else:
            # El hilo actual no tiene eventos introducidos.
            # Añado el hilo al diccionario
            queue: Queue = cls.INTERFACE_QUEUE.setdefault(
                current_thread, Queue())
            # Añado el hilo a la cola de hilos
            cls.THREADS_QUEUE.put(current_thread)

        # Añado el evento a la cola correspondiente al hilo introducido
        queue.put(event)

    @classmethod
    def run_queue(cls, event_queue: Queue):
        while True:
            event: ConsoleEvent = event_queue.get()
            if event is None:
                return

            # Ejecuto la request y la guardo en el historial
            event.execute()
            # Indico que he acabado con la última request sacada de la cola
            event_queue.task_done()

    @classmethod
    def run(cls):
        while True:
            # Obtengo un hilo para agotar todos sus eventos
            thread = cls.THREADS_QUEUE.get()
            if thread is None:
                return
            # Accedo a su cola de eventos
            events_queue = cls.INTERFACE_QUEUE[thread]
            cls.run_queue(events_queue)

            cls.THREADS_QUEUE.task_done()

    @classmethod
    def close_suite(cls):
        GUI.add_event(current_thread(), None)

