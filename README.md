# Pelecolas

Un proyecto para gestionar la cinefilia.

Hay una doble gestión.
El perfil de FilmAffinity y un Word con reseñas y su posible publicación en un blog.

## Índice

1. [Estructura](#Estructura)
    1. [Code](#Code)
    2. [Películas](#Películas)
        1. [Archivo Word](#Archivo-Word)
        2. [Archivos python](#Archivos-python)
2. [Archivo Word](#archivo-word-1)
3. [mains](#mains)
    1. [Readdata](#readdata)
    2. [Contar_criticas](#Contar_criticas)
    3. [Make_html](#Make_html)
        1. [Información automática](#Información-automática)
        2. [Scroll de títulos](#Scroll-de-títulos)
        3. [Quoter](#Quoter)
        4. [Etiquetas](#Etiquetas)
4. [Config](#Config)

## Estructura

La estructura debe ser:

```tree
Parent
    ├── Code
    |   └──...
    └── Películas
        ├── Películas.docx
        ├── read_data.py
        └──...
```

### Code

El repositorio de git se debe clonar en la carpeta Code.

### Películas

#### Archivo Word

Debe contener un archivo `.docx` con las reseñas.
El nombre de la carpeta puede cambiar, pero siempre debe tener el mismo nombre que el `.docx`.

El archivo debe iniciar con una linea con el nombre del archivo.
Después se añade un doble salto de línea.
A partir ahí comenzará una lista de reseñas.

Cada reseña empezará con el título de la película y `:` en negrita.
Si existen dos películas (reseñadas o no) con el mismo nombre, se escribirá entre paréntesis el año de la película.

Las reseñas deberán estar separadas entre sí por un doble salto de línea.

Se espera que cuando se cite literalmente una frase de la película, se haga en cursvia.

Cuando se mencione el título de otra película (reseñada o no) se haga entre comillas: “Otro título”.

La idea es que todas las reseñas estén contenidas en un mismo archivo Word.

Para comprobar qué consigue leer el código en nuestro documento de Word, se recomienda la ejecución de [`main_contar_criticas.py`](#Contar_criticas).

#### Archivos python

Los archivos `.py` sirven para ejecutar los archivos main del repositorio.
Con frecuencia queremos que el código utilice información de la carpeta Películas o bien que emita los resultados ahí.
Para indicar esta dirección usaremos siempre el mismo tipo de archivos `.py`.

```python
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CODE_DIR = SCRIPT_DIR.parent / 'Code'
sys.path.append(str(CODE_DIR))

# Modificar el archivo que se quiere importar
from main_read_data import main


if __name__ == "__main__":

    main(SCRIPT_DIR)
```

Si el `main` escogido no necesita la dirección, modificaremos la llamada.
Igualmente hay que incluir las líneas previas a la importación de la función `main`.

## mains

### Readdata

Dado un usuario de FilmAffinity, entra a su perfil y extrae en un documento Excel sus votaciones.
Para incluir a un usuario que no esté contemplado, se debe añadir en el json `Code\Readdata\usuarios.json`.

Al iniciar el programa se informará a qué usuario se va a exportar.
Con las flechas arriba y abajo se puede hacer scroll entre los usuarios recogidos en el json.
Si no se escribe nada, se exportará al usuario por defecto.
La elección del usuario quedará registrada para la próxima vez que se ejecute.

El archivo Excel generado se llamará `Sintaxis - usuario.xlsx`.

Del perfil de FilmAffinity se quieren extraer sólo las películas.
Por eso se hace un filtrado dado el título.
Si se encuentra un sufijo (_(TV)_, _(C)_,...), no se añade al excel.
Este criterio de filtrado se puede configurar.

### Contar_criticas

Recorre todo el archivo Word listando las críticas que encuentre.
Al terminar esta lectura, en la carpeta desde la que se llame generará un `.txt` con todas las películas encontradas.

### Make_html

Dado el título de una reseña incluída en el archivo Word, generará un documento html listo para ser publicado en un blog.

Las publicaciones siempre inician con un encabezado con el director, año de la película y duración.
El programa los pedirá al usuario.
Se deben introducir según los vaya pidiendo.

#### Información automática

Antes de empezar a pedir la información, el prgrama hará una búsqueda del título de la película en FilmAffinity.
Si encuentra la película lo avisará por pantalla.
Inmediatamente pedirá el nombre del director.
Basta con dejar este campo vacío.
Entonces el programa rellenará la reseña con los datos que haya leído en FilmAffinity.

Si el programa no ha encontrado la película en FilmAffinity, cuando nos pida el director, se puede introducir un enlace a la ficha de FilmAffinity.
El programa leerá la información y rellenará los datos necesarios.

#### Scroll de títulos

Si el título introducido por el usuario no se encuentra en el Word, el programa sugerirá los títulos más cercanos.
Si se introduce un título vacío (si se pulsa enter antes de escribir nada), el programa sugerirá una lista de todos los títulos del Word.
Una vez que esté emitida esta lista el usuario podrá escribir otro título o bien con las flechas de arriba y abajo, recorrer las sugerencias.

Es posible configurar un filtrado para que no aparezcan entre los títulos sugeridos aquellos que ya hayan sido publicados en el blog.

#### Quoter

Cuando detecta que en la reseña está citada otra película, busca si está publicada su reseña en el blog.
En caso de ser así, automáticamente se generará un link a esa reseña.
Para que esto se lleve a cabo, el prgrama ha tenido que leer el blog donde se quiere publicar.
El resultado de esta lectura se encuentra en un `.csv` en `Code\Make_html\bog_data.csv`.

Se utiliza un procesador de lenguaje natural para tratar de buscar referencias a otros directores.
Si en la reseña se menciona a un director con alguna de sus películas reseñada y publicada en nuestro blog, se generará un enlace a todas las reseñas de este director.
Como es inestable el procesado de lenguaje, antes de efectuar el enlace se nos pedirá confirmación.
Para contestar _Sí_ o _No_ basta con movernos con las flechas de arriba y abajo.

#### Etiquetas

Todas las reseñas tienen unas etiquetas fijas: siglo, década, año, director y país.
Dado que esta información se conoce, tras efectuar el html, se añade al portapapeles del equipo una cadena con las etiquetas lista para ser pegada en el blog.

## Config

La configuración de todo el proyecto se incluye en un archivo ini que se generará la primera vez que se ejecute cualquier main.
Para modificar la configuración acúdase al archivo `Code\General.ini`.

Al inicial cualquier main se da la posibilidad de entrar al menú de configuración.
Se exige para ello que el sistema operativo sea Windows.
Para abrir el menú de configuración presiónese la tecla control antes de inicial la ejecución del programa.
Se abrirá el menú de configuración antes de ejecutar el programa.
En el menú de configuración se tiene acceso a todos los parámetros de todas las secciones.
Se puede elegir la sección y el parámetro con las flechas de arriba y abajo.
Para salir de una sección simplemente púlsese enter sin escribir ningún parámetro.
