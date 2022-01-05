def split_title_year(title: str):
    '''
    Dado un título de los escritos en el word,
    quiero extraer el posible año que tenga entre paréntesis
    '''
    # Busco paréntesis en el título introducido
    año_primera_pos = title.rfind("(")
    año_ultima_pos = title.rfind(')')

    # Compruebo si he encontrado paréntesis
    if año_primera_pos < 0 or año_ultima_pos < 0:
        return "", title

    # Extraigo el posible año
    año = title[año_primera_pos + 1:año_ultima_pos]
    # Compruebo que sean 4 dígitos
    if not año.isnumeric() or len(año) != 4:
        return "", title

    # En caso contrario efectivamente existe un año
    title = title[:año_primera_pos]
    # Quito los espacios que hayan podido quedar
    title = title.strip()

    return año, title
