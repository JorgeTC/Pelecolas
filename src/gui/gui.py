from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from multiprocessing import Lock
from queue import Queue
from threading import current_thread, main_thread


class ConsoleEvent(metaclass=ABCMeta):

    def __init__(self) -> None:
        # Bloqueo el locker hasta haber completado la tarea
        self.locker = Lock()
        self.locker.acquire()

    @abstractmethod
    def execute(self):
        pass

    def execute_if_main_thread(self):
        curr_thread = current_thread()

        # Si estoy en el hilo principal, lo ejecuto
        if curr_thread is main_thread():
            self.execute()
        else:
            # Si no, me encolo junto a los otros eventos de consola que tenga que ejecutar mi hilo
            GUI.add_event(curr_thread.name, self)


class DummyConsoleEvent(ConsoleEvent):
    # Objeto para ser usado como Sentinel.

    def __init__(self):
        # Como esperamos que los objetos Sentinel se definan en el ámbito global, no esperamos que haya colisión de id
        # En cualquier caso este objeto está pensado para ser comparado con objetos de la clase padre.
        # Es decir, este id solo sirve para el remoto caso en que se definieran varias instancias
        self._id = id(self)

    def execute(self):
        # Definimos un método que no esperamos llamar para cumplir con la metaclase
        raise NotImplementedError

    def __eq__(self, other):
        # Esperamos que el objeto con el que comparamos sea de la clase padre,
        # por lo tanto no debería tener este atributo definido.
        try:
            # Si tiene el atributo definido y usamos la clase como un singleton, esta comparación siempre devolverá True
            return self._id == other._id
        except AttributeError:
            return False


# Último evento que se debe añadir a la cola de un hilo.
# Este evento no realiza nada, se utiliza como sentinel para indicar a la iteración que ese hilo ha liberado la gui
CLOSING_EVENT = DummyConsoleEvent()

# String que se añadirá junto a los nombre de otros hilos.
# No se espera que exista ningún hilo con este nombre, se añadirá a la cola de hilos indicando a la gui que ha terminado
CLOSING_THREAD = "_Closing_thread"


@contextmanager
def pop_from_dict[K, T](dictionary: dict[K, T], key: K):
    try:
        # Extraer el valor asociado con la clave
        value = dictionary[key]
        # Devolvemos la variable antes de eliminarla del diccionario
        yield value
    finally:
        # Asegurarse de que la clave se elimina
        dictionary.pop(key, None)


class GUI:
    # Todos los hilos (distintos de main) que quieren acceder a la interfaz
    THREADS_QUEUE: Queue[str] = Queue()
    # Cola con todos los eventos de consola
    INTERFACE_QUEUE: dict[str, Queue[ConsoleEvent]] = {}

    @classmethod
    def add_event(cls, thread_name: str, event: ConsoleEvent):
        # Si el hilo introducido ya tiene más eventos encolados, añado uno más
        if thread_name in cls.INTERFACE_QUEUE:
            queue = cls.INTERFACE_QUEUE[thread_name]
        else:
            # El hilo actual no tiene eventos introducidos.
            # Añado el hilo al diccionario
            queue = cls.INTERFACE_QUEUE.setdefault(thread_name,
                                                   Queue())
            # Añado el hilo a la cola de hilos
            cls.THREADS_QUEUE.put(thread_name)

        # Añado el evento a la cola correspondiente al hilo introducido
        queue.put(event)

    @classmethod
    def run(cls):
        # Itero los hilo para agotar todos sus eventos
        while (thread_name := cls.THREADS_QUEUE.get()) is not CLOSING_THREAD:
            # Accedo a su cola de eventos y los ejecuto todos.
            # Elimino el hilo después de haber ejecutado todos sus eventos.
            # No puedo eliminarlo antes porque ee hilo puede añadir más eventos a su cola.
            # Eliminando el hilo del diccionario me aseguro de que si un hilo con el mismo nombre
            # me añade más eventos, tenga una cola nueva para él.
            with pop_from_dict(cls.INTERFACE_QUEUE, thread_name) as events_queue:
                run_queue(events_queue)

            cls.THREADS_QUEUE.task_done()

    @classmethod
    def close_suite(cls):
        # Método que se debe llamar desde un hilo no principal.
        # Indica que ya no va a pedir más eventos de consola y permite
        # al siguiente hilo encolado que tome el control de la consola.
        thread_name = current_thread().name
        # Compruebo que este hilo me haya añadido eventos.
        # Si no lo ha hecho no tiene sentido añadir un evento de cierre
        if thread_name in cls.INTERFACE_QUEUE:
            GUI.add_event(thread_name, CLOSING_EVENT)

    @classmethod
    def close_gui(cls):
        # Añade un nombre de un hilo que se espera que no exista
        # Esto indica al ejecutor que ha terminado de ejecutar eventos
        GUI.add_event(CLOSING_THREAD, CLOSING_EVENT)


def run_queue(event_queue: Queue[ConsoleEvent]):
    while (event := event_queue.get()) != CLOSING_EVENT:
        # Ejecuto la request y la guardo en el historial
        event.execute()
        # Indico que he acabado con la última request sacada de la cola
        event_queue.task_done()
