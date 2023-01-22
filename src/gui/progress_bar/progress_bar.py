from typing import Optional

from .progress_bar_done import ProgressBarDone
from .progress_bar_iterations import ProgressBarIterations

# Interfaz para barra de progreso.
# Si introduzco la cantidad de iteraciones avanzará lo correspondiente con cada `update`.
# De lo contrario hay que introducir la proporción de progreso completado.
class ProgressBar:
    def __init__(self, iterations: int = None):
        self.instance = ProgressBarDone(
        ) if iterations is None else ProgressBarIterations(iterations)

    def update(self, done: Optional[float] = None):
        if done is not None:
            self.instance.update(done)
        else:
            self.instance.update()
