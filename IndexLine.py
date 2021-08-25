class IndexLine():
    # Esta clase debería ser capaz de dar cualquier orden a las películas
    def __init__(self, totales):
        self.m_totales = totales
        # Hay que inicializarlo para que no escriba en los encabezados
        self.m_current = 2

    def get_current_line(self):
        # Actualizo el valor
        self.m_current += 1
        # Devuelvo el valor antes de haberlo actualizado
        return self.m_current - 1

    def __int__(self):
        return self.m_current