# Pelecolas

Un proyecto para gestionar la cinefilia.

Hay una doble gestión.
El perfil de FilmAffinity y un Word con reseñas y su posible publicación en un blog.

## Índice

1. [Estructura](#Estructura)
    1. [Code](#Code)
    2. [Películas](#Películas)
        1. [Archivos Word](#Archivos-Word)
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
    4. [Publish_post](#Publish-post)
    5. [Make_and_publish](#Make-and-publish)
4. [Config](#Config)
5. [Agradecimientos](#Agradecimientos)

## Estructura

La estructura debe ser:

```tree
Parent
    ├── Code
    |   ├── mains
    |   ├── res
    |   └── src
    └── Películas
        ├── Word
        |   ├── Películas - 2017.docx
        |   ├── Películas - 2018.docx
        |   └──...
        ├── read_data.py
        └──...
```

### Code

El repositorio de git se debe clonar en la carpeta Code.

### Películas

#### Archivos Word

En una carpeta se deben guardar todos los archivos Word.
El nombre de la carpeta se puede configurar en el ini.
El nombre de los archivos debe ser todos iguales.
A este nombre se le añade ` - ` seguido del año de ese documento.

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
from mains.main_read_data import main


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
Se usa como plantilla el archivo excel `Code\res\Readdata\Plantilla.xlsx`.

Del perfil de FilmAffinity se quieren extraer sólo las películas.
Por eso se hace un filtrado dado el título.
Si se encuentra un sufijo (_(TV)_, _(C)_,...), no se añade al excel.
Este criterio de filtrado se puede configurar.

### Contar_criticas

Recorre todo el archivo Word listando las críticas que encuentre.
Al terminar esta lectura, en la carpeta desde la que se llame generará un `.txt` con todas las películas encontradas.

En el archivo ini se puede configurar si se quiere añadir el índice del título a su izquierda.
También se puede añadir un separador por años.
Los años son los que lee del nombre del Word cuyos títulos está listando.

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
Si esta opción está activa, tampoco se mostrarán los títulos que estén programados.

#### Quoter

Cuando detecta que en la reseña está citada otra película, busca si está publicada su reseña en el blog.
En caso de ser así, automáticamente se generará un link a esa reseña.
Para que esto se lleve a cabo, el programa ha tenido que leer el blog donde se quiere publicar.
El resultado de esta lectura se encuentra en un `.csv` en `Code\res\Make_html\bog_data.csv`.
El archivo csv se actualiza si se ha publicado alguna entrada entre la última fecha de creación del archivo y la fecha actual.

Se utiliza un procesador de lenguaje natural para tratar de buscar referencias a otros directores.
Si en la reseña se menciona a un director con alguna de sus películas reseñada y publicada en nuestro blog, se generará un enlace a todas las reseñas de este director.
Como es inestable el procesado de lenguaje, antes de efectuar el enlace se nos pedirá confirmación.
Para contestar _Sí_ o _No_ basta con movernos con las flechas de arriba y abajo.

#### Etiquetas

Todas las reseñas tienen unas etiquetas fijas: siglo, década, año, director y país.
Dado que esta información se conoce, tras efectuar el html, se añade como comentario al final del html.

### Publish post

Se publicará en el blog un html que se enceuntren en la carpeta _Películas_.
Los html deben tener como nombre `Reseña _titulo_.html`.

Para que sea posible la publicación la carpeta _Películas_ debe tener los permisos pertinentes para acceder al blog.
Son un archivo `blogger.dat` y `client_secrets.json`.
El archivo `client_secrets.json` se guarda en la carpeta `res\blog_credentials`.
El otro archivo lo generará el código automáticamente.
El blog elegido será el que tiene el id especificado en el ini.

En el archivo de configuración se puede elegir fecha, hora y si la publicación se hará en borrador o no.
La hora debe estar explícita `hh:mm`.
La fecha puede escribirse con formato `dd/mm/aaaa` o bien puede escribirse la palabra `auto`.
En este último caso el programa buscará en el blog cuál es el próximo viernes disponible.
Se avisará al usuario por consola de cuál es la fecha elegida.

Como las [etiquetas](#Etiquetas) de la reseña están escritas en la última línea del html, se leerá este contenido y se escribirá como etiquetas de la publicación.

### Make and publish

Crea y publica un html.
Tiene todas las prestaciones de las secciones [Make_html](#Make-html) y [Publish_post](#Publish-post).
Tras publicar el html, elimina el archivo.

## Config

La configuración de todo el proyecto se incluye en un archivo ini que se generará la primera vez que se ejecute cualquier main.
Para modificar la configuración acúdase al archivo `Code\res\General.ini`.

Al inicial cualquier main se da la posibilidad de entrar al menú de configuración.
Se exige para ello que el sistema operativo sea Windows.
Para abrir el menú de configuración presiónese la tecla control antes de inicial la ejecución del programa.
Se abrirá el menú de configuración antes de ejecutar el programa.
En el menú de configuración se tiene acceso a todos los parámetros de todas las secciones.
Se puede elegir la sección y el parámetro con las flechas de arriba y abajo.
Para salir de una sección simplemente púlsese enter sin escribir ningún parámetro.

## Agradecimientos

Por corregirme los imports,
por pisotear y escupir sobre cada linea de código que escribía,
por ser la primera en escuchar cada idea antes de escribirla;
por ser la primera en oír cómo la idea fracasaba...
Por enseñarme qué es un csv, un dataframe y por enseñarme a leer un html.
Por enseñarme markdown y permitir que estas mismas líneas existan.
Por enseñarme a componer rutas.
Por hacerme evitar los espaghettis.
Por ser la única responsable de que este proyecto sea más de un único archivo.
Por soportar los nombres de archivos con espacios, mi enorme dependencia del ratón,
mi alergia a la consola y mis dobles clicks.
Por responder incondicionalmente a mis llamadas de Skype.

Por recordarme que hay que dormir.
Por contestar a mis preguntas en circunstancias y a horas intempestivas.
Por sacarme de paseo incluso cuando me he portado mal.
Por ser el más fuerte motivo que me separa del código.

También por ver a mi lado las películas que bien merecidamente nadie ha visto.
Por convertir por primera vez aquel docx a pdf y leérselo aquella primera vez.
Por aquella captura de pantalla de la segunda crítica que escribí en mi vida.

Por seguir entrando al blog y por ser mi única editora.

Y por seguir ahí a pesar de todo.
Este proyecto no sería posible sin [Sasha](https://github.com/sashiyalala)
