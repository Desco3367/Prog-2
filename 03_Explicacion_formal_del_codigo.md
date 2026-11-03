# Explicación formal del funcionamiento del código

**Trabajo práctico grupal "Lector de datos tabulares" — Grupo G24 (Berruti, Liali, Vranjes)**
Programación 2 — Licenciatura en Ciencia de Datos, UNR

> **Alcance de este documento.** Se describe con registro técnico el comportamiento del código entregado (`modulo/funciones.py`, `modulo/clase.py` y `ejemplos.py`), siguiendo su estructura línea por línea o por bloques breves. Toda afirmación sobre el comportamiento fue contrastada con el código fuente y, cuando correspondía, con ejecuciones reales (Python 3.12.2, pandas 2.2.2, Windows 11). Los números de línea remiten a los archivos tal como fueron entregados. Las justificaciones de diseño son **defendibles**, pero no reproducen las razones efectivas del grupo, que no constan por escrito; cuando una decisión es débil, se lo indica junto con la mejor defensa disponible y una mejora posible.

---

## 0. Índice

1. [Introducción y alcance](#1-introducción-y-alcance)
2. [Arquitectura](#2-arquitectura)
3. [Modelo de datos y representaciones intermedias](#3-modelo-de-datos-y-representaciones-intermedias)
4. [Especificación de `modulo/funciones.py`](#4-especificación-de-modulofuncionespy)
5. [Especificación de `modulo/clase.py`](#5-especificación-de-moduloclasepy)
6. [Algoritmo de inferencia de tipos](#6-algoritmo-de-inferencia-de-tipos)
7. [Semántica formal de la combinación de opciones](#7-semántica-formal-de-la-combinación-de-opciones)
8. [Condiciones de error](#8-condiciones-de-error)
9. [Análisis de complejidad temporal y espacial](#9-análisis-de-complejidad-temporal-y-espacial)
10. [`ejemplos.py`: descripción y resultados esperados](#10-ejemplospy-descripción-y-resultados-esperados)
11. [Limitaciones y posibles extensiones](#11-limitaciones-y-posibles-extensiones)
12. [Glosario](#12-glosario)

**Convenciones de notación**

| Símbolo | Significado |
|---|---|
| `archivo.py:N` o "archivo.py, línea N" | Línea N del archivo indicado. `L40-41` abrevia "líneas 40 a 41" del archivo que se esté tratando. |
| *n* | Cantidad de filas de datos del archivo (sin contar el encabezado). |
| *k* | Cantidad de columnas (campos de la primera línea). |
| *f* | Cantidad de funciones de filtro registradas. |
| *t* | Cantidad de columnas con tipo forzado. |
| *c* | Cantidad de columnas seleccionadas (en §3.2 y §6, *c* denota además una columna individual; en §7.1 esa cantidad se escribe *m*). |
| *C* | Cantidad total de caracteres del archivo. |
| ⟨x₁, …, xₘ⟩ | Secuencia (lista) ordenada. |
| `T` | Uno de los tipos soportados: `bool`, `int`, `float`, `str`. |

Las firmas se presentan con **anotaciones de tipo descriptivas** (por ejemplo `-> list[str]`) para precisar la especificación; el código entregado **no** contiene anotaciones de tipo (verificado: `LectorCSV.leer.__annotations__ == {}`).

---

## 1. Introducción y alcance

### 1.1 Problema que resuelve

El código implementa un **lector de tablas almacenadas en archivos de texto plano delimitado** (CSV y variantes). Dada la ruta de un archivo cuya primera línea es, por defecto, un encabezado con los nombres de las columnas, el lector produce una **lista de diccionarios**: cada diccionario representa una fila, sus claves son los nombres de las columnas y sus valores son los datos convertidos al tipo que corresponde (`int`, `float`, `bool`, `str` o `None` para las celdas vacías).

Sobre esa funcionalidad básica, el lector permite:

| Requisito de la consigna | Mecanismo en el código |
|---|---|
| Leer CSV y otros separadores (punto y coma, tabulación, arbitrarios, incluso de varios caracteres) | Parámetro `delimitador` de `LectorCSV.__init__` (`clase.py:21`) y `str.split` en `separar_linea` (`funciones.py:3`). |
| Primera fila como encabezado; definir qué pasa con nombres vacíos o repetidos | `_procesar_lineas` (`clase.py:110-118`): ambos casos detienen la lectura con `ValueError`. |
| Archivos sin encabezado (opcional) | `encabezado=False` (`clase.py:119-122`): columnas `col_0`, `col_1`, … |
| Tipos `int`, `float`, `str`, `bool` y nulos | `inferir_tipo_columna` y `convertir_valor` (`funciones.py:36-117`). Celda vacía → `None`. |
| Inferencia automática documentada | Orden `bool → int → float → str` (`funciones.py:47-75`; comentario `clase.py:4-6`). |
| Tipo indicado por el usuario con prioridad, sin sustituirlo si falla | `forzar_tipo` (`clase.py:38-43`) y `clase.py:158-159`; error con fila y columna en `funciones.py:94-115`. |
| Cantidad de filas, rango, columnas, filtro por función | `establecer_limite`, `establecer_rango`, `seleccionar_columnas`, `agregar_filtro` (`clase.py:45-63`) y `_aplicar_filtros_y_rangos` (`clase.py:190-221`). |
| Documentar la combinación de opciones | Comentario de criterios `clase.py:7-9`. |
| Mensajes de error con fila y columna | Mensajes (mayormente f-strings) en `clase.py:103-139`, `clase.py:149`, `clase.py:195` y `funciones.py:94-115`. |
| pandas solo para mostrar | `import pandas as pd` únicamente en `ejemplos.py:1`. |

### 1.2 Restricciones de la consigna respetadas

- **Sin módulo `csv` ni lectores de pandas en el lector.** El análisis del texto se realiza exclusivamente con métodos de `str` (`split`, `strip`, `rstrip`, `lower`) y con las funciones de conversión `int()` y `float()`. El paquete `modulo/` importa únicamente objetos de sí mismo (`clase.py:11-17`); no importa ninguna biblioteca, ni siquiera de la biblioteca estándar.
- **pandas fuera del lector.** La conversión a `DataFrame` se realiza en el programa de demostración (`ejemplos.py:15, 31, 42`), tal como pide la sección 4 de la consigna, y además se muestra la lista de diccionarios original (`ejemplos.py:11-12, 29, 38-39`), porque pandas altera la representación de tipos y nulos (ver §10.1).
- **Política de errores.** La consigna admite detener la lectura ante un problema e informar un error que identifique qué ocurrió y, cuando corresponda, la fila y la columna. El código adopta esa política: **ante el primer problema detectado se lanza una excepción** y no se devuelve ningún resultado parcial.

### 1.3 Fuera de alcance (no soportado por diseño o por omisión)

Campos entre comillas con el delimitador o saltos de línea en su interior (formato RFC 4180), coma decimal, marcadores textuales de nulo (`NA`, `NULL`, `N/A`), booleanos distintos de `true`/`false`, codificaciones distintas de UTF-8 y detección automática del delimitador. Estos puntos se tratan en §11.

---

## 2. Arquitectura

### 2.1 Estructura de archivos

```text
G24_Berruti_Liali_Vranjes/            ← raíz del proyecto (directorio de trabajo esperado)
├── ejemplos.py                       ← script de demostración (52 líneas)
├── datos1.csv                        ← coma + espacio, CRLF, 6 filas, una celda vacía
├── datos2.txt                        ← punto y coma + espacio, 3 filas
├── derror.csv                        ← coma, valor 'veinte' en la línea 3
└── modulo/                           ← paquete (sin __init__.py)
    ├── funciones.py                  ← 8 funciones puras (133 líneas)
    └── clase.py                      ← clase LectorCSV (221 líneas)
```

Según la terminología de la cátedra, un **módulo** es un archivo `.py` con código reutilizable y un **paquete** es una colección de módulos organizada en una carpeta. En consecuencia, `modulo/` es un **paquete** (pese a su nombre) que contiene dos módulos: `funciones.py` y `clase.py`. `ejemplos.py` es un **script**: contiene código ejecutable a nivel superior para una tarea puntual (la demostración), mientras que los dos módulos contienen solo definiciones y no producen efectos al ser importados.

### 2.2 Grafo de dependencias

```text
ejemplos.py ──(import pandas as pd)──────────────► pandas   (biblioteca externa)
     │
     └──(from modulo.clase import LectorCSV)──► modulo/clase.py
                                                     │
                     (from modulo.funciones import    │
                      separar_linea, inferir_tipo_columna,
                      convertir_valor, cumple_todos_los_filtros,
                      recortar_diccionario)          ▼
                                               modulo/funciones.py   (sin importaciones)
```

Propiedades del grafo:

1. **Acíclico y en capas.** `funciones.py` no depende de nada; `clase.py` depende solo de `funciones.py`; `ejemplos.py` depende de `clase.py` y de pandas. Ningún módulo del paquete conoce a `ejemplos.py`.
2. **pandas confinado al script.** El paquete `modulo/` funciona con Python estándar, sin instalar nada. pandas se requiere únicamente para ejecutar `ejemplos.py`.
3. **Importaciones explícitas.** Se importan objetos puntuales (`from … import …`), nunca `import *`, práctica que la cátedra desaconseja porque oculta qué nombres ingresan al espacio de nombres. `clase.py` importa 5 de las 8 funciones: `es_booleano`, `es_entero` y `es_flotante` son auxiliares de `inferir_tipo_columna` y no se usan desde la clase.

### 2.3 Reparto de responsabilidades

| Componente | Paradigma | Estado | Responsabilidad |
|---|---|---|---|
| `funciones.py` | Funcional (funciones puras) | Ninguno | Operaciones elementales sobre texto y valores: separar una línea, reconocer un tipo, inferir el tipo de una columna, convertir un valor, evaluar filtros, proyectar columnas. |
| `clase.py` → `LectorCSV` | Orientado a objetos | Configuración del lector (7 atributos de instancia) | Acumular la configuración mediante la interfaz pública y orquestar el procesamiento en `leer()`. |
| `ejemplos.py` | Script imperativo | Variables globales del script | Construir lectores, invocar `leer()`, mostrar resultados (`print`, `pd.DataFrame`) y capturar errores. |

La consigna (sección 3.1) admite POO, programación funcional o una combinación. La solución combina ambos enfoques con un criterio defendible: **lo que no requiere estado se implementa como funciones puras** (fáciles de probar de forma aislada y de reutilizar) y **lo que se acumula en varios pasos —la configuración— se encapsula en un objeto**. El estado del objeto es exclusivamente configuración: los datos leídos no se almacenan como atributos sino que se devuelven (§5.6).

El método `leer()` actúa como **fachada** del procesamiento, que se organiza como una secuencia de cuatro etapas implementadas por **métodos protegidos** (prefijo `_`):

```text
leer(ruta)
  1. _leer_archivo(ruta)                         → lineas            : list[str]
  2. _procesar_lineas(lineas)                    → encabezados, filas_crudas
  3. _convertir_tipos(encabezados, filas_crudas) → filas_tipadas     : list[dict]
  4. _aplicar_filtros_y_rangos(encabezados, filas_tipadas) → resultado : list[dict]
```

### 2.4 Paquete sin `__init__.py` (namespace package)

La carpeta `modulo/` no contiene `__init__.py`. Desde Python 3.3 (PEP 420), una carpeta sin ese archivo que se encuentra en la ruta de búsqueda de módulos se importa como **paquete de espacio de nombres** (*namespace package*). Se verificó que `modulo.__file__` es `None` y que `modulo.__path__` existe y apunta a la carpeta, lo que coincide con la definición técnica de paquete que el apunte de la cátedra (Unidad 1, "Uso de código externo") cita del glosario de la documentación de Python (un módulo con atributo `__path__`). Los apuntes no tratan `__init__.py`; agregarlo vacío convertiría a `modulo/` en un paquete *regular* sin cambiar el comportamiento observable del TP.

Consecuencia sobre `__name__`: cuando se importa, la variable especial `__name__` del módulo `clase.py` vale `'modulo.clase'` (verificado), no `'clase'`.

### 2.5 Requisitos de ejecución

| Requisito | Detalle |
|---|---|
| Intérprete | Python 3 con f-strings (≥ 3.6) y orden de inserción garantizado en diccionarios (≥ 3.7); para paquetes sin `__init__.py`, ≥ 3.3. Se verificó con Python 3.12.2. |
| Dependencias | Ninguna para `modulo/`. pandas (verificado con 2.2.2) para `ejemplos.py`. No hay `requirements.txt`. |
| Directorio de trabajo | La **raíz del proyecto**. Motivo: las rutas de datos de `ejemplos.py` (`"datos1.csv"`, `"datos2.txt"`, `"derror.csv"`, en `ejemplos.py:8, 27, 35, 49`) son **relativas** y se resuelven contra el directorio de trabajo actual, no contra la carpeta del script. |
| Resolución de importaciones | Las importaciones `from modulo.clase …` (`ejemplos.py:2`) y `from modulo.funciones …` (`clase.py:11`) son **absolutas** y requieren que la raíz del proyecto esté en `sys.path`. |

Comportamiento verificado según la forma de ejecución:

| Comando | Resultado |
|---|---|
| `python ejemplos.py` desde la raíz | Funciona (salida en §10). |
| `python <ruta>/ejemplos.py` desde otra carpeta | Las importaciones funcionan (Python agrega la carpeta del script a `sys.path`), pero la lectura falla: `FileNotFoundError: No se encontró el archivo en la ruta: datos1.csv`. |
| `python modulo/clase.py` | `ModuleNotFoundError: No module named 'modulo'` (la carpeta agregada a `sys.path` es `modulo/`, no la raíz). |
| Consola interactiva abierta en la raíz: `from modulo.clase import LectorCSV` | Funciona; es el procedimiento indicado para leer en vivo un archivo nuevo. |

La cátedra recomienda, para rutas robustas, construirlas a partir de un directorio base bien definido con `pathlib.Path`. `leer()` acepta objetos `Path` porque `open()` los acepta (verificado), pero `ejemplos.py` no los usa (mejora en §11).

---

## 3. Modelo de datos y representaciones intermedias

### 3.1 Cadena de representaciones

El archivo atraviesa cuatro representaciones sucesivas. Cada una es producida por una etapa de `leer()` y consumida por la siguiente; todas son **listas** (arreglos dinámicos de referencias), porque el orden de las filas es significativo y las operaciones dominantes son agregar al final (`append`, costo constante amortizado) y acceder por posición (costo constante).

| # | Variable (en `leer`) | Tipo | Producida por | Contenido |
|---|---|---|---|---|
| R0 | archivo en disco | bytes UTF-8 | — | Texto plano delimitado. |
| R1 | `lineas` | `list[str]` | `_leer_archivo` (`clase.py:84-97`) | Una cadena por línea física, sin el terminador de línea. |
| R2 | `encabezados` | `list[str]` | `_procesar_lineas` (`clase.py:99-143`) | *k* nombres de columna. |
| R2 | `filas_crudas` | `list[list[str]]` | `_procesar_lineas` | *n* filas, cada una con *k* campos de texto ya recortados (`strip`). |
| R3 | `filas_tipadas` | `list[dict[str, int \| float \| bool \| str \| None]]` | `_convertir_tipos` (`clase.py:145-188`) | *n* diccionarios `{columna: valor tipado}`. |
| R4 | `filas_filtradas` (valor devuelto) | `list[dict[str, int \| float \| bool \| str \| None]]` | `_aplicar_filtros_y_rangos` (`clase.py:190-221`) | Subsecuencia de R3, eventualmente proyectada a las columnas seleccionadas. |

Ejemplo de la evolución de la primera fila de datos de `datos1.csv` (línea física `001, Cuaderno, 2500.5, 10, true` terminada en `\r\n`):

```python
# R1: elemento de `lineas` (el \r\n fue traducido a \n por el modo texto y luego eliminado)
'001, Cuaderno, 2500.5, 10, true'
# R2: elemento de `filas_crudas` (split por ',' y strip de cada campo)
['001', 'Cuaderno', '2500.5', '10', 'true']
# R3: elemento de `filas_tipadas` (con forzar_tipo("codigo", str), como en el ejemplo 1)
{'codigo': '001', 'nombre': 'Cuaderno', 'precio': 2500.5, 'cantidad': 10, 'disponible': True}
```

Además de las representaciones de filas, `_convertir_tipos` construye una estructura auxiliar `tipos_definidos: dict[str, type]` (`clase.py:152`) que asocia a cada columna el tipo con el que se convertirán sus valores. Los tipos se almacenan como **objetos clase** (`int`, `float`, `str`, `bool`), no como cadenas: en Python los tipos son clases y las clases son objetos que pueden guardarse como valores de un diccionario.

### 3.2 Invariantes

Se enuncian las propiedades que el código garantiza en cada representación cuando la etapa correspondiente termina sin lanzar excepciones.

**Sobre R1 (`lineas`)**

- **I1.1** `len(lineas) ≥ 1` (el caso de 0 líneas se rechaza en `clase.py:94-95`).
- **I1.2** Ningún elemento termina en `"\n"` ni en `"\r"` (`clase.py:90`).
- **I1.3** `lineas[j]` corresponde a la línea física *j* + 1 del archivo (correspondencia biyectiva: no se descarta ninguna línea).

**Sobre R2 (`encabezados`, `filas_crudas`)**

- **I2.1** `k = len(encabezados) ≥ 1`, donde *k* es la cantidad de campos de la primera línea.
- **I2.2** Con `encabezado=True`: todos los nombres son no vacíos y distintos dos a dos, con comparación sensible a mayúsculas (`clase.py:113-116`). Con `encabezado=False`: `encabezados == ["col_0", …, f"col_{k-1}"]` (`clase.py:120-121`), distintos por construcción.
- **I2.3** Para toda fila `r` de `filas_crudas`: `len(r) == k` (`clase.py:135-139`).
- **I2.4** Cada campo es una cadena sin espacios en blanco iniciales ni finales (`funciones.py:6`). Un campo vacío o compuesto solo por blancos queda representado por `""`.
- **I2.5** Ninguna línea de datos aceptada es "en blanco" (`linea.strip() != ""`, `clase.py:130-131`).
- **I2.6** `filas_crudas[i]` proviene de la línea física `i + 2` si `encabezado=True`, o `i + 1` si `encabezado=False` (consecuencia de I1.3 e I2.5: las líneas en blanco no se saltean, provocan error).

**Sobre R3 (`filas_tipadas`)**

- **I3.1** `len(filas_tipadas) == len(filas_crudas) == n`.
- **I3.2** Cada diccionario tiene exactamente las claves de `encabezados`, en ese orden de inserción.
- **I3.3** Para toda columna *c* con tipo `T_c = tipos_definidos[c]` y toda fila: el valor es `None` si y solo si el campo crudo era `""`; en caso contrario `type(valor) is T_c`. En particular, todos los valores no nulos de una columna son del mismo tipo (columnas homogéneas).
- **I3.4** El tipo de cada columna depende de **todas** las filas del archivo (inferencia) o de `forzar_tipo` (prioridad), y nunca del rango, los filtros, el límite ni la selección de columnas.

**Sobre R4 (resultado)**

- **I4.1** El resultado es una subsecuencia de R3 que preserva el orden del archivo.
- **I4.2** Sin selección de columnas, los diccionarios devueltos son **los mismos objetos** creados en `_convertir_tipos` (no copias); con selección, son diccionarios nuevos creados por `recortar_diccionario`, con las claves en el orden indicado por el usuario.
- **I4.3** Si hay límite *L* configurado, `len(resultado) ≤ ⌈L⌉` (para *L* entero, `≤ L`).

### 3.3 Representación de valores

| Texto del campo (después de `strip`) | Tipo de la columna | Valor en R3 |
|---|---|---|
| `""` | cualquiera | `None` |
| `"10"` | `int` | `10` |
| `"10"` | `float` | `10.0` |
| `"001"` | `int` (inferido) | `1` (se pierden los ceros iniciales) |
| `"001"` | `str` (forzado) | `"001"` |
| `"TRUE"`, `"True"`, `"true"` | `bool` | `True` |
| `"nan"` | `float` | `float('nan')` (no es `None`) |
| `"Buenos Aires"` | `str` | `"Buenos Aires"` (los espacios internos se conservan) |

El valor nulo se representa con `None`, en línea con el criterio de la cátedra: `None` denota ausencia de valor, mientras que `0` o `""` son valores concretos.

---

## 4. Especificación de `modulo/funciones.py`

El módulo define ocho funciones de nivel superior, sin estado compartido, sin importaciones y sin salida por consola. Todas son **funciones puras** en el sentido de la cátedra: el resultado depende exclusivamente de los argumentos y no producen efectos secundarios observables fuera de su ámbito local (las listas y diccionarios que mutan, como `campos_limpios` o `nuevo_diccionario`, se crean dentro de la función). La única salvedad es `cumple_todos_los_filtros`, cuya pureza depende de la de los filtros que recibe.

| Línea | Función | Usada por |
|---|---|---|
| 1 | `separar_linea` | `clase.py:105, 133` |
| 10 | `es_booleano` | `funciones.py:50` |
| 18 | `es_entero` | `funciones.py:59` |
| 27 | `es_flotante` | `funciones.py:68` |
| 36 | `inferir_tipo_columna` | `clase.py:164` |
| 78 | `convertir_valor` | `clase.py:182` |
| 120 | `cumple_todos_los_filtros` | `clase.py:210` |
| 128 | `recortar_diccionario` | `clase.py:217` |

### 4.1 `separar_linea` (`funciones.py:1-7`)

| Elemento | Especificación |
|---|---|
| Firma | `separar_linea(linea: str, delimitador: str) -> list[str]` |
| Parámetros | `linea`: una línea del archivo sin terminador. `delimitador`: separador de campos, de uno o más caracteres. |
| Retorno | Lista de los campos, en orden, cada uno sin blancos iniciales ni finales. |
| Precondiciones | `delimitador` es una cadena no vacía (garantizado por `clase.py:27-28` solo al construir el objeto). |
| Postcondiciones | `len(resultado) == linea.count(delimitador) + 1` (ocurrencias no solapadas); por lo tanto `len(resultado) ≥ 1`. Para todo campo `e`: `e == e.strip()`. |
| Excepciones | Ninguna bajo las precondiciones. Fuera de ellas: `ValueError: empty separator` si `delimitador == ""`; `TypeError: must be str or None, not int` si el delimitador no es cadena (ambas verificadas, lanzadas en L3). |
| Complejidad | Tiempo O(\|linea\|); espacio O(\|linea\|). |

Descripción línea a línea:

- **L1** Se define la función con dos parámetros posicionales.
- **L2** *Docstring* de una línea que describe la tarea.
- **L3** `partes = linea.split(delimitador)`: se particiona la línea en cada ocurrencia del delimitador. `str.split` acepta separadores de varios caracteres, lo que satisface la extensión opcional de la consigna sin recurrir a expresiones regulares (verificado: `separar_linea("a||b|| c", "||") == ['a', 'b', 'c']`). Un delimitador al final produce un último campo vacío (`"a,b,"` → `['a', 'b', '']`).
- **L4** Se inicializa la lista acumuladora `campos_limpios`.
- **L5-6** Se recorre `partes` y se agrega cada elemento recortado con `strip()`, que elimina todo espacio en blanco de los bordes (espacios, tabulaciones, espacio duro U+00A0) pero conserva los internos. Este paso es el que permite leer `datos1.csv`, donde cada coma va seguida de un espacio.
- **L7** Se devuelve la lista.

Observaciones:

- **Comillas.** La separación es puramente sintáctica: no reconoce campos entre comillas. `"Rosario, SF",2` produce tres campos, y `"hola"` se conserva con las comillas.
- **`delimitador=None`.** `str.split(None)` separa por secuencias de blancos y descarta los extremos (verificado: `separar_linea("a   b\tc", None) == ['a', 'b', 'c']`). `LectorCSV(delimitador=None)` no está prohibido y funciona por este motivo; es un comportamiento no documentado ni validado.
- **Equivalencia funcional.** El cuerpo equivale a la comprensión de listas `[e.strip() for e in linea.split(delimitador)]` o a `list(map(str.strip, linea.split(delimitador)))`; el grupo optó por el patrón explícito "lista vacía + `for` + `append`" de la Unidad 1.

### 4.2 `es_booleano` (`funciones.py:10-15`)

| Elemento | Especificación |
|---|---|
| Firma | `es_booleano(texto: str) -> bool` |
| Retorno | `True` si y solo si `texto.lower()` es `"true"` o `"false"`. |
| Precondiciones | `texto` es una cadena (en el uso real, ya recortada y no vacía). |
| Postcondiciones | Reconocimiento insensible a mayúsculas: `"TRUE"`, `"True"`, `"false"` → `True`; `"verdadero"`, `"1"`, `" true"` (con espacio) → `False`. |
| Excepciones | `AttributeError` si `texto` no tiene método `lower` (inalcanzable desde `LectorCSV`). |
| Complejidad | O(\|texto\|). |

- **L10-11** Definición y *docstring*.
- **L12** Se normaliza a minúsculas, porque la comparación de cadenas en Python distingue mayúsculas y minúsculas.
- **L13-14** Prueba de pertenencia a la colección fija `["true", "false"]` (búsqueda lineal sobre 2 elementos, costo constante). Si pertenece, se devuelve `True`.
- **L15** Caso contrario, `False` (estructura `if … return` seguida de `return` sin `else`).

Observación: la colección fija de valores válidos se escribe como lista; la cátedra recomienda una **tupla** para colecciones fijas de valores posibles. El comportamiento es idéntico; la tupla solo comunicaría mejor la inmutabilidad. La función completa equivale a `return texto.lower() in ("true", "false")`.

### 4.3 `es_entero` (`funciones.py:18-24`)

| Elemento | Especificación |
|---|---|
| Firma | `es_entero(texto: str) -> bool` |
| Retorno | `True` si `int(texto)` no lanza `ValueError`; `False` en caso contrario. |
| Precondiciones | `texto` es una cadena. |
| Postcondiciones | Acepta exactamente el lenguaje de `int()` en base 10: signo opcional (`"+5"`, `"-3"`), ceros iniciales (`"001"`), guiones bajos entre dígitos (`"1_000"`), blancos en los bordes y dígitos Unicode (`"٣"`). Rechaza `"1.0"`, `"1e3"`, `"nan"`, `"inf"`, `"1,5"`, `""`. (Todo verificado.) |
| Excepciones | Captura solo `ValueError`. Un argumento no cadena como `None` produce `TypeError`, que se propaga (inalcanzable desde `LectorCSV`). |
| Complejidad | O(\|texto\|) para longitudes usuales. |

- **L18-19** Definición y *docstring*.
- **L20-22** Bloque `try`: se intenta la conversión y, si no falla, se devuelve `True`. El valor convertido se **descarta**: la función solo responde si la conversión es posible.
- **L23-24** `except ValueError`: la excepción esperada se **traduce** a `False`. La captura es específica, como recomienda la cátedra (evitar `except:` sin tipo).

Justificación defendible: se delega en `int()` la definición de "entero válido" en lugar de reimplementarla (por ejemplo con `str.isdigit()`, que rechaza el signo: `"-5".isdigit()` es `False`). Durante la inferencia, que un valor no sea entero es un **resultado esperado** y no un error, por eso se devuelve un booleano en vez de propagar la excepción. Costo aceptado: el valor se convierte dos veces (aquí y luego en `convertir_valor`), un factor constante que no altera la complejidad asintótica.

Caso límite (Python 3.12): `int()` rechaza con `ValueError` cadenas de más de 4300 dígitos; `es_entero` devuelve entonces `False` y el valor termina inferido como `float` con valor `inf` (verificado con 5000 dígitos). Es un caso patológico, sin relevancia práctica.

### 4.4 `es_flotante` (`funciones.py:27-33`)

| Elemento | Especificación |
|---|---|
| Firma | `es_flotante(texto: str) -> bool` |
| Retorno | `True` si `float(texto)` no lanza `ValueError`; `False` en caso contrario. |
| Precondiciones | `texto` es una cadena. |
| Postcondiciones | Acepta el lenguaje de `float()`: decimales con punto (`".5"`, `"5."`), notación científica (`"1e3"`), `"nan"`, `"inf"`, `"Infinity"`, guiones bajos (`"1_000.5"`) y todo lo que acepta `int()`. Rechaza la coma decimal (`"1,5"`). Atención: `"1.000"` se acepta y vale `1.0` (el punto es separador decimal, no de miles). (Verificado.) |
| Excepciones | Igual que `es_entero`. |
| Complejidad | O(\|texto\|). |

- **L27-33** Estructura idéntica a `es_entero`, sustituyendo `int` por `float`.

Propiedad usada por la inferencia (§6): todo texto aceptado por `int()` es aceptado por `float()` (inclusión de lenguajes). El caso de más de 4300 dígitos mencionado en §4.3 no contradice la inclusión, porque allí es `int()` el que rechaza y `float()` el que acepta; su único efecto es que esa columna se infiere `float` en lugar de `int`.

### 4.5 `inferir_tipo_columna` (`funciones.py:36-75`)

| Elemento | Especificación |
|---|---|
| Firma | `inferir_tipo_columna(valores_columna: list[str]) -> type` |
| Parámetros | `valores_columna`: los *n* campos crudos de una columna, en orden de fila. |
| Retorno | Uno de los objetos clase `bool`, `int`, `float`, `str` (no una cadena con su nombre). |
| Precondiciones | Los valores son cadenas ya recortadas (I2.4): la única representación de una celda vacía es `""`. |
| Postcondiciones | Sea *V* el conjunto de valores no vacíos. Si `T` es el tipo devuelto, entonces para todo `v ∈ V`, `convertir_valor(v, T, …)` no lanza excepción. La definición formal está en §6. |
| Excepciones | Ninguna (las de `int()`/`float()` son capturadas por `es_entero`/`es_flotante`). |
| Complejidad | Tiempo O(*n*) (hasta cuatro recorridos de la columna, cada uno con corte temprano salvo el primero); espacio O(*n*) por la lista `no_vacios`. |

Descripción línea a línea:

- **L36-37** Definición y *docstring*, que documenta el orden de prueba.
- **L38-41** Se construye `no_vacios`, la sublista de valores distintos de `""` (patrón de filtrado con `for` + `if` + `append`). Las celdas vacías no participan de la decisión de tipo: un nulo es compatible con cualquier tipo.
- **L43-45** **Guarda de columna vacía.** Si no hay valores no vacíos (columna enteramente vacía, o archivo sin filas de datos), se devuelve `str`. Esta guarda es **imprescindible**: un "para todo" sobre un conjunto vacío es verdadero (igual que `all([])` es `True`), y como la bandera `todos_bool` arranca en `True`, sin la guarda una columna vacía se inferiría `bool` (verificado con una versión sin guarda).
- **L47-54** **Prueba de `bool`.** Se inicializa la bandera `todos_bool = True` y se busca un contraejemplo: al primer valor que no satisface `es_booleano` se baja la bandera y se interrumpe el recorrido con `break` (salida temprana). Si no hubo contraejemplo, se devuelve `bool`.
- **L56-63** **Prueba de `int`.** Mismo esquema con `es_entero`.
- **L65-72** **Prueba de `float`.** Mismo esquema con `es_flotante`. El comentario de L65 aclara que esta prueba también cubre las columnas que mezclan enteros y decimales (`"10"`, `"30.5"`), porque todo entero es aceptado por `float()`.
- **L74-75** **Caso por defecto.** Si ninguna prueba tuvo éxito, se devuelve `str`, el único tipo capaz de representar cualquier texto.

Equivalencia: cada bloque de bandera + `for` + `break` implementa un cuantificador universal con cortocircuito; es equivalente a `all(es_booleano(v) for v in no_vacios)` (y análogos), resultado verificado sobre los casos de la tabla de §6.3.

### 4.6 `convertir_valor` (`funciones.py:78-117`)

| Elemento | Especificación |
|---|---|
| Firma | `convertir_valor(texto: str, tipo_esperado: type, num_fila: int, nombre_col: str) -> int \| float \| bool \| str \| None` |
| Parámetros | `texto`: campo crudo recortado. `tipo_esperado`: clase destino. `num_fila`: número de **línea del archivo** (base 1) usado solo en el mensaje de error. `nombre_col`: nombre de la columna, usado solo en el mensaje. |
| Retorno | `None` si `texto == ""`; en otro caso, un valor `x` con `type(x) is tipo_esperado`. |
| Precondiciones | `tipo_esperado ∈ {int, float, str, bool}`. |
| Postcondiciones | Celda vacía → `None` **para cualquier tipo**, incluido `str`. `str` → texto sin modificar. `bool` → `True`/`False` según `texto.lower()`. `int`/`float` → resultado de `int(texto)`/`float(texto)`. |
| Excepciones | `ValueError` con mensaje `Error en fila {num_fila}, columna '{nombre_col}': el valor '{texto}' no se puede convertir a {bool\|int\|float}.`; `ValueError("Tipo de dato no soportado: …")` si el tipo no es uno de los cuatro. |
| Complejidad | O(\|texto\|). |

Descripción línea a línea:

- **L78-80** Definición y *docstring* de dos líneas que anticipa el contrato (vacío → `None`; error con fila y columna).
- **L81-82** **Cláusula de guarda del nulo.** Se evalúa **antes** que el tipo, de modo que el nulo es uniforme para todas las columnas: incluso con tipo `str`, una celda vacía da `None` y no `""` (verificado).
- **L84-85** Tipo `str`: el texto ya es el valor final.
- **L87-97** Tipo `bool`: se normaliza con `lower()` y se compara con `"true"` (→ `True`, L89-90) y `"false"` (→ `False`, L91-92) en una estructura `if/elif/else` de tres ramas; en la tercera se lanza `ValueError` (L93-97). No se usa `bool(texto)` porque cualquier cadena no vacía es verdadera: `bool("false")` devuelve `True` (verificado). Este `raise` **no** está dentro de un `except`, por lo que no produce encadenamiento de excepciones.
- **L99-106** Tipo `int`: `try: return int(texto)`; si `int()` lanza `ValueError`, se lanza un **nuevo** `ValueError` con el mensaje del grupo (L103-106). Como el `raise` está dentro del bloque `except`, Python registra la excepción original en el atributo `__context__` (**encadenamiento implícito**; verificado: `__context__` es `ValueError: invalid literal for int() with base 10: 'veinte'` y `__cause__` es `None`).
- **L108-115** Tipo `float`: idéntico al caso `int`.
- **L117** **Caso por defecto** para un tipo no soportado. Es inalcanzable a través de la interfaz pública: `forzar_tipo` rechaza tipos no válidos (`clase.py:40-41`) e `inferir_tipo_columna` solo devuelve los cuatro tipos. Solo podría alcanzarse modificando el atributo protegido `_tipos_columnas` desde afuera.

Observaciones:

- **Estilo de cláusulas de guarda.** Cada rama termina con `return` o `raise`, por lo que la secuencia de `if` independientes se comporta como una cadena `if/elif`: la primera condición verdadera determina el resultado.
- **Comparación de tipos con `==`.** `tipo_esperado == str` compara objetos clase; para clases, la igualdad coincide con la identidad (`is`).
- **Evaluación inmediata.** `num_fila` y `nombre_col` se calculan y se pasan en cada llamada aunque solo se usan si hay error (Python evalúa los argumentos antes de ejecutar la función). El *f-string* del mensaje, en cambio, solo se construye en la rama del `raise`.
- **Posible simplificación.** Las ramas `int` y `float` repiten el mismo patrón; podrían unificarse con `tipo_esperado(texto)` y `tipo_esperado.__name__` en el mensaje. `bool` requiere tratamiento propio por la razón expuesta en L87-97.

### 4.7 `cumple_todos_los_filtros` (`funciones.py:120-125`)

| Elemento | Especificación |
|---|---|
| Firma | `cumple_todos_los_filtros(fila_diccionario: dict, lista_funciones_filtro: list[Callable[[dict], object]]) -> bool` |
| Retorno | `True` si y solo si todos los filtros devuelven un valor **verdadero** (*truthy*) para la fila; `True` si la lista está vacía. |
| Precondiciones | Cada elemento es invocable con un argumento. Se espera (no se exige) que los filtros sean puros. |
| Postcondiciones | Conjunción con evaluación de izquierda a derecha y **cortocircuito**: si el filtro *j* devuelve un valor falso, los filtros *j*+1, … no se invocan. |
| Excepciones | Propaga cualquier excepción lanzada por un filtro (`KeyError` por columna mal escrita, `TypeError` por comparar `None`, etc.) y `TypeError: '…' object is not callable` si un elemento no es invocable. |
| Complejidad | O(*f*) invocaciones en el peor caso (más el costo de cada filtro); O(1) en el mejor caso. |

- **L120-121** Definición y *docstring*.
- **L122-124** Se recorre la lista; al primer filtro cuyo resultado sea falso (`if not funcion(fila_diccionario)`) se devuelve `False`. Se usa el **valor de verdad** del resultado, no se exige un `bool`: un filtro que devuelve `0`, `""` o `None` excluye la fila.
- **L125** Si ninguno falló, `True`.

Es una **función de orden superior** (recibe funciones como argumento y las invoca) y se apoya en el **duck typing**: no se verifica el tipo de los filtros, basta con que sean invocables (verificado con `lambda`, `def`, `functools.partial` y un objeto con `__call__`). Equivale a `all(f(fila_diccionario) for f in lista_funciones_filtro)`, incluido el cortocircuito; no equivale a `all([...])` con lista por comprensión, que evaluaría todos los filtros antes.

Advertencia de pureza: el filtro recibe el **diccionario real** de la fila, no una copia. Un filtro que modifica la fila altera el resultado devuelto (verificado: un filtro que asigna `fila['precio'] = 0` deja ese valor en la salida).

### 4.8 `recortar_diccionario` (`funciones.py:128-133`)

| Elemento | Especificación |
|---|---|
| Firma | `recortar_diccionario(fila_diccionario: dict, columnas_elegidas: Iterable[str]) -> dict` |
| Retorno | Un **diccionario nuevo** con las claves de `columnas_elegidas`, en ese orden, y los valores de la fila original. |
| Precondiciones | Toda columna elegida es clave de `fila_diccionario` (garantizado por la validación de `clase.py:192-195`). |
| Postcondiciones | El diccionario original no se modifica. El orden de claves es el de `columnas_elegidas` (verificado: `recortar_diccionario({'a':1,'b':2,'c':3}, ['c','a']) == {'c': 3, 'a': 1}`). Una columna repetida aparece una sola vez (la segunda asignación reemplaza el valor por el mismo). |
| Excepciones | `KeyError` si una columna no existe (inalcanzable desde `leer()` por la validación previa). |
| Complejidad | O(*c*) en promedio (acceso a diccionario de costo constante promedio). |

- **L128-129** Definición y *docstring* (contiene la errata "solp" por "solo").
- **L130** Diccionario vacío acumulador.
- **L131-132** Para cada columna elegida, se copia el par clave-valor. Al asignar en un diccionario, si la clave existe se reemplaza el valor y, si no, se agrega el par; desde Python 3.7 se conserva el orden de inserción, lo que explica que el resultado respete el orden pedido.
- **L133** Se devuelve el diccionario nuevo. Equivale a `{col: fila_diccionario[col] for col in columnas_elegidas}`.

---

## 5. Especificación de `modulo/clase.py`

### 5.1 Comentario de criterios (L1-9)

Las líneas 1 a 9 son un bloque de comentarios (`#`) que documenta las decisiones del grupo. Su contenido, contrastado con el código:

| Líneas | Criterio documentado | Implementación | Concordancia |
|---|---|---|---|
| L2-3 | Primera fila como encabezado; nombres vacíos o repetidos detienen la lectura con `ValueError`; con `encabezado=False`, nombres `col_0`, `col_1`, … | `clase.py:110-122` | Concuerda. No se aclara que la comparación de repetidos distingue mayúsculas. |
| L4 | Orden de inferencia `bool → int → float → str` | `funciones.py:47-75` | Concuerda. |
| L4-5 | Celdas vacías → `None`; columna completamente vacía → tipo `str` | `funciones.py:43-45, 81-82` | Concuerda. |
| L5-6 | Se reconocen `'true'` y `'false'` como booleanos | `funciones.py:12-13, 88-92` | El código es **más permisivo** que lo documentado: el reconocimiento es insensible a mayúsculas (`TRUE`, `False`). |
| L6 | Los tipos de `forzar_tipo()` tienen prioridad | `clase.py:158-159` | Concuerda. |
| L7 | 1) Rango de filas, numeradas desde 1, extremos incluidos | `clase.py:198-202` | Concuerda. No se aclara que la numeración es de **filas de datos** (sin el encabezado) mientras que los mensajes de error usan **líneas del archivo** (§7.4). |
| L8 | 2) Filtros, 3) Límite | `clase.py:205-211` | Concuerda; implica que el límite cuenta filas que **cumplen** los filtros. |
| L8-9 | 4) Selección de columnas al final; permite filtrar por columnas no incluidas en el resultado | `clase.py:192-195, 214-219` | Concuerda. |

Observación: al tratarse de comentarios y no de un *docstring*, esta documentación no es accesible con `help(LectorCSV)`; la clase no tiene *docstring* (verificado: `LectorCSV.__doc__ is None`). La cátedra (Unidad 2, Encapsulamiento) recomienda documentar la interfaz con *docstrings* consultables mediante `help()`. Mejora: trasladar este bloque al *docstring* de la clase (§11).

### 5.2 Importaciones (L11-17)

```python
from modulo.funciones import (
    separar_linea,
    inferir_tipo_columna,
    convertir_valor,
    cumple_todos_los_filtros,
    recortar_diccionario
)
```

- Importación **absoluta** desde el paquete `modulo`: requiere que la raíz del proyecto esté en `sys.path` (§2.5). Una alternativa que no depende de ello dentro del paquete sería la importación relativa `from .funciones import …`, no cubierta en los apuntes.
- Los paréntesis permiten listar los nombres en varias líneas.
- Se importan las cinco funciones que la clase invoca directamente.

### 5.3 Estado de `LectorCSV`

La clase se define en L20 sin superclase explícita, por lo que hereda implícitamente de `object` (verificado: `LectorCSV.__mro__ == (LectorCSV, object)`). El estado de cada instancia consiste en siete **atributos de instancia**, todos creados en `__init__`:

| Atributo | Línea | Visibilidad (convención) | Tipo esperado | Valor inicial | Modificado por | Invariante pretendido |
|---|---|---|---|---|---|---|
| `delimitador` | 30 | público | `str` | `","` | `__init__` | `delimitador != ""`. Solo se garantiza en la construcción: al ser público, una asignación posterior `lector.delimitador = ""` lo viola y `leer()` falla con `ValueError: empty separator` (verificado). |
| `encabezado` | 31 | público | `bool` | `True` | `__init__` | Se usa por su valor de verdad; no se valida (`encabezado="no"` se comporta como `True`, verificado). |
| `_tipos_columnas` | 32 | protegido | `dict[str, type]` | `{}` | `forzar_tipo` | Todo valor ∈ {`int`, `float`, `str`, `bool`}. Las claves no se validan hasta `leer()`. |
| `_filtros` | 33 | protegido | `list[Callable]` | `[]` | `agregar_filtro` | Solo crece (no hay método para quitar filtros). Los elementos no se validan. |
| `_limite_filas` | 34 | protegido | `int \| None` | `None` | `establecer_limite` | `None` o `≥ 0`. |
| `_rango_filas` | 35 | protegido | `tuple[int, int] \| None` | `None` | `establecer_rango` | `None` o `(inicio, fin)` con `1 ≤ inicio ≤ fin`. |
| `_columnas` | 36 | protegido | `list[str] \| None` | `None` | `seleccionar_columnas` | Ninguno al configurar; la existencia de las columnas se verifica en `leer()`. |

Notas de diseño:

- **Atributos protegidos.** Siguiendo la terminología de la cátedra, el prefijo de un guion bajo marca un atributo **protegido**: por convención no debe accederse ni modificarse desde fuera de la clase, aunque Python no lo impide. La protección es solo convencional: se verificó que `lector._limite_filas = -5` hace que `leer()` devuelva `[]` sin error, y que `lector._rango_filas = (0, 2)` también devuelve `[]` (el *slice* resultante es `filas[-1:2]`). Por eso la configuración se realiza mediante métodos que validan.
- **Atributos opcionales inicializados en `None`.** `_limite_filas`, `_rango_filas` y `_columnas` se crean en `__init__` con valor `None`, práctica que la cátedra recomienda para que todas las instancias tengan la misma estructura. `None` codifica "opción no configurada" y permite distinguir "sin límite" (`None`) de "límite 0" (resultado vacío).
- **Colecciones mutables creadas en el cuerpo.** El diccionario y la lista de L32-33 se crean dentro de `__init__` y no como valores por defecto de parámetros, por lo que cada instancia tiene sus propias colecciones.
- **Inconsistencia de visibilidad.** `delimitador` y `encabezado` son públicos mientras que el resto de la configuración es protegida; además, la regla "delimitador no vacío" puede violarse sin tocar ningún atributo protegido. Defensa: son los parámetros "básicos" del método de inicialización. Mejora alineada con la cátedra: convertir `delimitador` en una propiedad (`@property` con *setter* que valide).

### 5.4 Método de inicialización `__init__` (L21-36)

| Elemento | Especificación |
|---|---|
| Firma | `__init__(self, delimitador: str = ",", encabezado: bool = True) -> None` |
| Precondiciones | Ninguna exigida salvo `delimitador != ""`. |
| Postcondiciones | La instancia tiene los siete atributos de §5.3 con sus valores iniciales (verificado: `vars(LectorCSV())` devuelve exactamente esos siete pares). |
| Excepciones | `ValueError("El delimitador no puede ser vacío.")` (L28). |
| Complejidad | O(1). |

- **L21** Método de inicialización con **argumentos por defecto**: el caso más frecuente (CSV con coma y encabezado) se obtiene con `LectorCSV()`. Los valores por defecto son inmutables (`","` y `True`).
- **L22-26** *Docstring* con una breve lista de parámetros. Describe al delimitador como "caracter", aunque se admiten delimitadores de varios caracteres.
- **L27-28** **Validación previa a la asignación.** Si el delimitador es la cadena vacía, se lanza `ValueError`. Como la validación precede a toda asignación y la excepción se propaga fuera de la expresión de instanciación, ninguna variable del programa usuario queda ligada a un lector inválido. (La cátedra denomina a `__init__` *método de inicialización*: se ejecuta cada vez que se crea un objeto de la clase y define su estado inicial; la excepción interrumpe esa inicialización.) Solo se valida el caso `""`: un delimitador no cadena (por ejemplo `44`) se acepta y falla recién al leer con `TypeError` (verificado).
- **L30-31** Se guardan los parámetros como atributos públicos.
- **L32-36** Se inicializan los cinco atributos protegidos (comentarios en línea describen cada uno).
- El método no tiene `return` (un `__init__` devuelve implícitamente `None`).

### 5.5 Métodos públicos de configuración (L38-63)

Los cinco métodos de configuración tienen la misma forma: reciben uno o dos argumentos (dos en `forzar_tipo` y `establecer_rango`), opcionalmente los validan y los almacenan en un atributo protegido. Funcionan como los **setters** descritos por la cátedra, con una diferencia favorable: ante un valor inválido **lanzan** `ValueError` en lugar de imprimir un mensaje, criterio que la unidad de Excepciones presenta como preferible. Ninguno tiene `return`, por lo que todos devuelven `None`; en consecuencia, **no admiten encadenamiento de métodos** (verificado: `LectorCSV().forzar_tipo("codigo", str).establecer_limite(2)` lanza `AttributeError: 'NoneType' object has no attribute 'establecer_limite'`). No existen *getters*.

| Método | Líneas | Valida | Excepción y mensaje exacto | No valida |
|---|---|---|---|---|
| `forzar_tipo(columna, tipo_dato)` | 38-43 | `tipo_dato ∈ [int, float, str, bool]` | `ValueError("Tipo no válido. Use int, float, str o bool.")` | Existencia de `columna` (se verifica en `leer`, `clase.py:147-149`). |
| `agregar_filtro(funcion_filtro)` | 45-47 | — | — | Que sea invocable (un `5` se acepta y falla en `leer()` con `TypeError: 'int' object is not callable`). |
| `establecer_limite(limite)` | 49-53 | `limite ≥ 0` | `ValueError("El limite de filas no puede ser negativo")` | Tipo: `"3"` → `TypeError` crudo en L51; `None` → `TypeError` (no permite quitar el límite); `2.5` se acepta (límite efectivo 3); `True` se acepta (límite 1). |
| `establecer_rango(inicio, fin)` | 55-59 | `inicio ≥ 1` y `fin ≥ inicio` | `ValueError("Rango invalido: 'inicio' debe ser >= 1 y 'fin' >= 'inicio'")` | Tipo: `("1", 3)` → `TypeError` crudo en L57; `(1, 3.0)` se acepta y falla en `leer()` (L200) con `TypeError: slice indices must be integers…`. |
| `seleccionar_columnas(lista_columnas)` | 61-63 | — | — | Tipo y existencia. `None` desactiva la selección; una cadena se recorre carácter por carácter; `[]` produce diccionarios vacíos; se guarda la **misma** lista (alias). |

Especificación formal de los cinco métodos. Precondiciones: ninguna exigida al invocante; las condiciones de la columna "Valida" se comprueban dentro del método y su incumplimiento lanza la excepción indicada. Todos devuelven `None`.

| Método | Firma | Postcondición (si no se lanza excepción) | Complejidad |
|---|---|---|---|
| `forzar_tipo` | `forzar_tipo(self, columna: str, tipo_dato: type) -> None` | `self._tipos_columnas[columna] is tipo_dato` (reemplaza un valor previo para la misma columna). | O(1) promedio (prueba en una lista de 4 elementos y asignación en diccionario). |
| `agregar_filtro` | `agregar_filtro(self, funcion_filtro: Callable[[dict], object]) -> None` | `self._filtros[-1] is funcion_filtro`; la longitud de `_filtros` aumenta en 1. | O(1) amortizado (`append`). |
| `establecer_limite` | `establecer_limite(self, limite: int) -> None` | `self._limite_filas == limite`. | O(1). |
| `establecer_rango` | `establecer_rango(self, inicio: int, fin: int) -> None` | `self._rango_filas == (inicio, fin)`. | O(1). |
| `seleccionar_columnas` | `seleccionar_columnas(self, lista_columnas: list[str]) -> None` | `self._columnas is lista_columnas` (misma referencia, sin copia). | O(1). |

**`forzar_tipo` (L38-43)**

- **L38** Recibe el nombre de la columna y la **clase** destino (por ejemplo `str`, no `"str"`).
- **L39** *Docstring*. Contiene la ligadura tipográfica "ﬁ" (U+FB01) en "Deﬁne", probablemente copiada de un PDF; no afecta la ejecución.
- **L40-41** Prueba de pertenencia de la clase a la colección fija `[int, float, str, bool]` (comparación por igualdad, que en clases coincide con la identidad). Un valor no válido —incluida la cadena `"int"`— produce `ValueError`. Según el criterio de la cátedra, un argumento de **tipo** incorrecto (una cadena en lugar de una clase) correspondería a `TypeError`; el grupo unifica ambos casos en `ValueError`. La línea 41 tiene un espacio sobrante al final.
- **L43** Asignación en el diccionario: si la columna ya tenía tipo forzado, el valor se **reemplaza** (gana la última llamada; verificado).
- Justificación de la validación diferida de la columna: al configurar todavía no se conoce el encabezado del archivo; además, el mismo lector puede usarse con distintos archivos.

**`agregar_filtro` (L45-47)**

- **L45-46** Definición y *docstring*.
- **L47** Agrega la función al final de `_filtros`. Las funciones son objetos de primera clase y pueden almacenarse en una lista. Los filtros **se acumulan** entre lecturas sucesivas con el mismo lector (verificado: con un segundo filtro, la siguiente lectura aplica ambos) y no hay forma de quitarlos salvo crear otro lector.

**`establecer_limite` (L49-53)**

- **L49-50** Definición y *docstring*.
- **L51-52** Rechaza valores negativos. El límite 0 es válido y produce `[]`.
- **L53** Asigna el atributo protegido.

**`establecer_rango` (L55-59)**

- **L55-56** Definición y *docstring*, que aclara que la numeración comienza en 1.
- **L57** La condición `inicio < 1 or fin < inicio` usa el operador `or`, que evalúa en cortocircuito (si `inicio < 1`, no se evalúa la segunda comparación). Por la tabla de prioridades, las comparaciones se resuelven antes que `or`, por lo que no se requieren paréntesis.
- **L58** Mensaje de error (sin tilde en "invalido").
- **L59** Se almacena una **tupla** `(inicio, fin)`: un par fijo que no se modifica, uso de tupla que coincide con la recomendación de la cátedra para registros inmutables.

**`seleccionar_columnas` (L61-63)**

- **L61-62** Definición y *docstring*.
- **L63** Asigna la referencia recibida. No se copia la lista: si el programa usuario modifica luego su lista (`cols.append("precio")`), la configuración del lector cambia sin pasar por ningún método (verificado: `lector._columnas is cols` es `True`). Es una fuga de encapsulamiento; se corrige con `self._columnas = list(lista_columnas)` o `tuple(lista_columnas)`.

### 5.6 Método `leer` (L65-82)

| Elemento | Especificación |
|---|---|
| Firma | `leer(self, ruta_archivo: str \| os.PathLike) -> list[dict[str, int \| float \| bool \| str \| None]]` |
| Parámetros | `ruta_archivo`: ruta absoluta o relativa al directorio de trabajo. Se acepta también un `pathlib.Path` (verificado). |
| Retorno | El resultado R4 descrito en §3 y definido formalmente en §7. |
| Precondiciones | Archivo existente, legible, codificado en UTF-8. |
| Postcondiciones | **No modifica el estado del objeto** (verificado: `vars(lector)` es igual antes y después), por lo que el mismo lector puede leer varios archivos con la misma configuración. |
| Excepciones | Las condiciones E5 a E17 de §8.2 y las no capturadas de §8.3 que se manifiestan durante la lectura (N1-N5 y N8-N10); ninguna se captura en este método. E1-E4, N6 y N7 se producen antes, al configurar. |
| Complejidad | O(*n·k*) en tiempo y espacio (§9). |

- **L65** Único método público que produce datos.
- **L66-69** *Docstring* que enumera las responsabilidades.
- **L70, L73, L76, L79** Comentarios que numeran las cuatro etapas.
- **L71** Etapa 1: lectura del archivo (R1).
- **L74** Etapa 2: separación de encabezado y filas, con **desempaquetado** de la tupla devuelta por `_procesar_lineas` (`return encabezados, filas_crudas`, L143).
- **L77** Etapa 3: determinación de tipos y conversión (R3).
- **L80** Etapa 4: rango, filtros, límite y proyección (R4).
- **L82** Se devuelve el resultado.

`leer()` es la **interfaz pública** del procesamiento y los cuatro métodos que invoca forman el **interior** de la clase. Desde el exterior solo importa qué recibe y qué devuelve `leer()`; la implementación de cada etapa puede cambiar sin afectar a `ejemplos.py`. `leer()` no es una función pura (su resultado depende del contenido del archivo y de la configuración almacenada en `self`), pero tampoco tiene efectos secundarios sobre el objeto. El procesamiento es de **evaluación inmediata**: cada etapa produce la lista completa antes de pasar a la siguiente.

### 5.7 Método protegido `_leer_archivo` (L84-97)

| Elemento | Especificación |
|---|---|
| Firma | `_leer_archivo(self, ruta_archivo) -> list[str]` |
| Retorno | Lista de líneas sin terminador (R1). |
| Precondiciones | Ninguna verificada antes de abrir; para obtener un resultado, la ruta debe designar un archivo existente, legible y codificado en UTF-8. |
| Postcondiciones | I1.1, I1.2, I1.3. El archivo queda cerrado al salir del bloque `with`, haya o no excepción. |
| Excepciones | `FileNotFoundError` propio (L92, encadenado); `ValueError` de archivo vacío (L95); `UnicodeDecodeError` y `PermissionError` sin capturar (§8). |
| Complejidad | Tiempo y espacio O(*C*). |

- **L84-85** Definición y *docstring*.
- **L86** Bloque `try` que delimita la región donde se captura `FileNotFoundError`.
- **L87** `with open(ruta_archivo, "r", encoding="utf-8") as archivo:`
  - Modo `"r"`: lectura de texto (es el modo por defecto; se explicita para dejar claro que no se escribe).
  - `encoding="utf-8"` explícito, como recomienda la cátedra: en Windows la codificación por defecto es cp1252, y sin este argumento un archivo UTF-8 con "Córdoba" se lee como "CÃ³rdoba" sin ningún error (corrupción silenciosa, verificado).
  - La sentencia `with` (gestor de contexto) garantiza el cierre del archivo incluso si ocurre una excepción durante la lectura; por eso no hay `close()` ni `finally`.
- **L88** Lista acumuladora.
- **L89** `for linea in archivo`: el objeto archivo es un **iterador** que entrega una línea por vez (verificado: `iter(archivo) is archivo`). En modo texto rige la traducción de saltos de línea universales: `\r\n` y `\r` aislado se entregan como `\n` (verificado: archivos CRLF y archivos con solo CR se leen correctamente). La decodificación UTF-8 ocurre durante esta iteración; un byte inválido lanza `UnicodeDecodeError` desde esta línea (verificado en el *traceback*).
- **L90** `linea.rstrip("\n\r")` elimina únicamente los caracteres de fin de línea del extremo derecho. No se usa `strip()` ni `rstrip()` sin argumentos porque borrarían también tabulaciones finales: con delimitador `"\t"` y último campo vacío, `"1\t2\t\n".strip().split("\t")` da `['1', '2']` (se pierde una columna), mientras que con `rstrip("\n\r")` se obtiene `['1', '2', '']` (correcto). La inclusión de `"\r"` es defensiva: con la traducción del modo texto ya no quedan `\r`, pero eliminarlo no tiene costo y cubre una apertura con `newline=""`.
- **L91-92** Se captura `FileNotFoundError` y se lanza un **nuevo** `FileNotFoundError` con mensaje en castellano que incluye la ruta. Se conserva el tipo (quien llama puede seguir capturando `FileNotFoundError`), pero: (a) al lanzarse dentro del `except`, se produce encadenamiento implícito y el *traceback* muestra "During handling of the above exception, another exception occurred"; (b) la nueva excepción pierde los atributos `errno` y `filename` (quedan en `None`; la original tenía `errno=2`). Ambos hechos verificados. Alternativas de la cátedra: `raise … from error` (causa explícita), `raise … from None` (oculta la original) o `raise` sin argumentos (relanza la original intacta).
- **L94-95** Si no se leyó ninguna línea (archivo de 0 bytes), `ValueError` con la ruta. Un archivo cuyo contenido es solo `"\n"` tiene **una** línea vacía y no entra en este caso, sino en el de L102-103.
- **L97** Se devuelve la lista. A partir de aquí, todo el procesamiento ocurre con el archivo ya cerrado y las líneas en memoria.

Comportamiento con el salto de línea final: un único `\n` al final del archivo no genera una línea adicional; dos saltos finales sí generan una línea vacía, que `_procesar_lineas` rechaza como fila vacía (verificado).

### 5.8 Método protegido `_procesar_lineas` (L99-143)

| Elemento | Especificación |
|---|---|
| Firma | `_procesar_lineas(self, lineas: list[str]) -> tuple[list[str], list[list[str]]]` |
| Precondiciones | `len(lineas) ≥ 1` (garantizado por `_leer_archivo`). |
| Retorno | Tupla `(encabezados, filas_crudas)` (R2). |
| Postcondiciones | I2.1 a I2.6. |
| Excepciones | Cinco condiciones de `ValueError` (primera línea vacía, nombre vacío, nombre repetido, fila vacía, cantidad de campos), ver §8. Además, un delimitador inválido asignado después de la inicialización o no cadena (N9, N10) se manifiesta aquí, en la primera llamada a `separar_linea` (L105). |
| Complejidad | Tiempo O(*C* + *k*²); espacio O(*C*). |

**Bloque A — primera línea (L101-106)**

- **L99-100** Definición y *docstring*.
- **L101** Se toma la primera línea (índice 0; Python indexa desde cero).
- **L102-103** Si la primera línea está en blanco (vacía o solo con espacios o tabulaciones), `ValueError("Error en fila 1: La primera línea del archivo está vacía.")`. Se aplica tanto con encabezado como sin él.
- **L105** Se separa la primera línea con el delimitador configurado.
- **L106** `cant_columnas` (*k*) queda determinado por la **primera línea**: define el esquema contra el cual se validan todas las demás.

**Bloque B — encabezado (L109-122)**

- **L109** Lista de nombres de columna.
- **L110** Rama según el valor de verdad de `self.encabezado`.
- **L111-117** Con encabezado, para cada posición `i` (base 0):
  - **L112** Se obtiene el nombre.
  - **L113-114** Nombre vacío → `ValueError` que informa la columna en **base 1** (`{i + 1}`): `"Error en fila 1, columna 2: El nombre de la columna está vacío."` para `a,,c`. Un delimitador final (`a,b,`) produce un nombre vacío en la última posición.
  - **L115-116** Nombre ya presente → `ValueError` con el nombre repetido. La prueba `nombre in encabezados` es una **búsqueda lineal** sobre la lista, sensible a mayúsculas (`Nombre` y `nombre` son distintos, verificado). Dentro del `for`, constituye un bucle anidado implícito de costo O(*k*²).
  - **L117** Se agrega el nombre.
  - Los controles se aplican por posición, de izquierda a derecha: para `a,a,` se informa primero la repetición en la columna 2 y no el vacío de la columna 3 (verificado).
  - Justificación del error por repetidos: las claves de un diccionario son únicas; con nombres repetidos, la segunda columna sobrescribiría a la primera y se perderían datos sin aviso (`dict(zip(["a","b","a"], [1,2,3]))` da `{'a': 3, 'b': 2}`, verificado). Se prefiere detener la lectura antes que renombrar automáticamente.
- **L118** Los datos comienzan en el índice 1 de `lineas`.
- **L119-122** Sin encabezado: nombres generados `col_0`, …, `col_{k-1}` (base 0) y los datos comienzan en el índice 0, de modo que la primera línea es a la vez fuente del esquema y primera fila de datos.

**Bloque C — filas de datos (L125-141)**

- **L125** Lista de filas crudas.
- **L126** Se recorre `range(indice_inicio_datos, len(lineas))`, que omite el encabezado cuando corresponde.
- **L127** `num_fila_archivo = i + 1`: conversión del índice base 0 de `lineas` al número de **línea física** base 1 (exacto por I1.3).
- **L128** Línea actual.
- **L130-131** Línea en blanco → `ValueError("Error en fila {N}: Se encontró una fila vacía.")`. Las líneas en blanco **no se saltean**: se consideran un error de formato. Este control se aplica sobre la línea completa y **antes** de separarla, con dos consecuencias verificadas: (a) una línea `,,` (solo delimitadores) no está en blanco y se acepta como fila de nulos, mientras que la fila equivalente con tabulador (`\t\t`) o espacio está en blanco y es error; (b) en un archivo de una sola columna, una celda vacía es una línea vacía y, por lo tanto, siempre produce error: en ese caso no es posible representar un nulo.
- **L133** Se separa la línea.
- **L135-139** Si la cantidad de campos difiere de *k*, `ValueError` con lo esperado y lo encontrado. Detecta tanto campos de más como de menos. Sin soporte de comillas, un campo como `"Rosario, SF"` también dispara este error.
- **L141** Se agrega la fila validada.
- **L143** Se devuelven ambos resultados como una tupla (devolución de múltiples valores), producidos en una sola pasada.

Observación menor: con `encabezado=False`, la primera línea se separa dos veces (L105 y, en la primera iteración, L133), y las validaciones de L130 y L135 se superan trivialmente para ella (ya fue controlada en L102 y es la que define *k*). Es un costo constante sin efecto observable.

### 5.9 Método protegido `_convertir_tipos` (L145-188)

| Elemento | Especificación |
|---|---|
| Firma | `_convertir_tipos(self, encabezados: list[str], filas_crudas: list[list[str]]) -> list[dict]` |
| Precondiciones | I2.1 a I2.6. |
| Retorno | `filas_tipadas` (R3). |
| Postcondiciones | I3.1 a I3.4. |
| Excepciones | `ValueError` por columna forzada inexistente (L149) y `ValueError` de conversión propagado desde `convertir_valor` (solo posible en columnas con tipo forzado). |
| Complejidad | Tiempo O(*t·k* + *n·k*); espacio O(*n·k*). |

**Bloque A — validación de tipos forzados (L147-149)**

- **L145-146** Definición y *docstring*.
- **L147** Se recorre el diccionario `_tipos_columnas`; recorrer un diccionario entrega sus **claves**.
- **L148-149** Si una columna forzada no figura en el encabezado, `ValueError("La columna '{col}' indicada en forzar_tipo no existe en la tabla.")`. Esta validación ocurre **después** de leer y separar todo el archivo, porque recién entonces se conoce el encabezado. Un archivo con BOM (marca de orden de bytes, típica de Excel) deja el primer nombre como `'﻿a'`, y `forzar_tipo('a', …)` falla aquí (verificado).

**Bloque B — determinación del tipo de cada columna (L151-164)**

- **L151-152** Se obtiene *k* y se crea `tipos_definidos`.
- **L155** Se recorre cada posición de columna `col_i`.
- **L156** Nombre de la columna en esa posición.
- **L158-159** **Prioridad del tipo forzado**: si la columna tiene tipo indicado por el usuario, se usa ese tipo y **no se ejecuta la inferencia**. La prueba `nombre_col in self._tipos_columnas` sobre un diccionario tiene costo constante en promedio.
- **L160-164** En caso contrario, se construye la lista `valores_columna` con el campo `col_i` de **todas** las filas (L161-163, equivalente a un `map` de cada fila a `fila[col_i]`) y se infiere el tipo (L164). La inferencia usa la columna completa, de modo que el tipo no depende del rango, los filtros ni el límite (I3.4).

**Bloque C — construcción de los diccionarios (L167-186)**

- **L167** Lista resultado.
- **L168** Se recorre cada índice de fila `fila_i` (base 0).
- **L169** Fila cruda correspondiente.
- **L171-174** Número de línea del archivo para los mensajes: `fila_i + 2` con encabezado (base 1 más la línea del encabezado) y `fila_i + 1` sin encabezado. Es exacto por I2.6. (Podría escribirse como expresión condicional: `fila_i + 2 if self.encabezado else fila_i + 1`.)
- **L176** Diccionario de la fila.
- **L177-180** Para cada columna se obtienen el nombre, el texto y el tipo (acceso en paralelo por índice a `encabezados` y `elementos_fila`; el paralelismo queda encapsulado en este método y desaparece al construir el diccionario).
- **L182-184** Se convierte el valor y se asigna con el nombre de columna como clave. Los argumentos se pasan por posición; su orden es significativo (si se invirtieran `num_fila_archivo` y `nombre_col`, el mensaje de error quedaría cruzado).
- **L186** Se agrega el diccionario a la lista.
- **L188** Se devuelve la lista.

Propiedades derivadas:

- **Orden de detección de errores de conversión.** La conversión recorre las celdas en orden fila por fila y, dentro de cada fila, de izquierda a derecha; el primer valor no convertible detiene la lectura (verificado: con `a` y `b` forzadas a `int` y celdas inválidas en `(línea 2, b)` y `(línea 3, a)`, se informa la de la línea 2, columna `b`).
- **Errores fuera del rango.** Como se convierte todo el archivo antes de aplicar el rango, un valor no convertible en una fila que no pertenece al rango igualmente detiene la lectura (verificado: con `establecer_rango(1, 1)` y un valor inválido en la línea 4, el error es `Error en fila 4, columna 'b': …`).
- **Columnas inferidas nunca fallan.** Por la postcondición de `inferir_tipo_columna`, `convertir_valor` solo puede lanzar excepción en columnas con tipo forzado. Esto implementa la regla de la consigna: si un valor no puede convertirse al tipo indicado, no se sustituye el tipo solicitado por otro inferido.

### 5.10 Método protegido `_aplicar_filtros_y_rangos` (L190-221)

| Elemento | Especificación |
|---|---|
| Firma | `_aplicar_filtros_y_rangos(self, encabezados: list[str], filas_tipadas: list[dict]) -> list[dict]` |
| Retorno | R4, definido formalmente en §7. |
| Precondiciones | `filas_tipadas` satisface I3.1 a I3.4 y `encabezados` satisface I2.2. |
| Postcondiciones | I4.1 a I4.3. El método no modifica `filas_tipadas` ni sus diccionarios (salvo que lo haga un filtro, §4.7) ni el estado del objeto. |
| Excepciones | `ValueError` por columna seleccionada inexistente (L195); excepciones de los filtros, sin capturar (propagadas desde `funciones.py:123`); `TypeError` en L200 si el rango contiene valores no enteros. |
| Complejidad | Tiempo O(*c·k* + *r* + *s·f* + *p·c*), donde *r* es la cantidad de filas del rango, *s* ≤ *r* la cantidad de filas examinadas antes del corte y *p* la cantidad de filas devueltas. |

**Bloque A — validación de la selección (L192-195)**

- **L190-191** Definición y *docstring*.
- **L192-195** Si hay selección de columnas, se verifica que cada una exista en el encabezado (búsqueda lineal, O(*c·k*)); si no, `ValueError("La columna seleccionada '{col}' no existe en la tabla.")`. La validación ocurre después de leer y convertir todo el archivo. Si se pasó una cadena en lugar de una lista, el `for` la recorre carácter por carácter (`seleccionar_columnas("nombre")` → `La columna seleccionada 'n' no existe en la tabla.`, verificado).

**Bloque B — etapa 1: rango (L198-202)**

- **L199** Desempaquetado de la tupla.
- **L200** `filas_tipadas[inicio - 1 : fin]`: conversión de la numeración del usuario (base 1, extremos incluidos) a un *slice* de Python (base 0, extremo superior excluido). Se resta 1 al inicio; al fin no, porque el *slice* lo excluye: la fila *fin* (base 1) tiene índice *fin − 1*, y el *slice* hasta *fin* la incluye. Ejemplo verificado: `(2, 3)` → índices 1 y 2 → Lapicera y Carpeta. El *slicing* no falla con índices fuera de rango: `(3, 100)` devuelve desde la fila 3 hasta el final y `(50, 60)` devuelve `[]`, sin error ni advertencia. El *slice* crea una lista nueva (copia de referencias).
- **L201-202** Sin rango, se usa la misma lista (sin copia).

**Bloque C — etapas 2 y 3: filtros y límite, fusionadas (L205-211)**

- **L205** Lista de filas aceptadas.
- **L206** Se recorren las filas del rango en orden.
- **L207-208** **Antes** de evaluar los filtros sobre la fila actual, si hay límite y ya se alcanzó, se interrumpe el recorrido con `break`. La condición `self._limite_filas is not None and len(filas_filtradas) >= self._limite_filas` depende del **cortocircuito** del `and`: si no hay límite, la comparación no se evalúa (invertir el orden de los operandos produciría `TypeError` al comparar `int` con `None`, verificado). Como el control precede a la evaluación de los filtros, estos se invocan el mínimo indispensable (verificado: con límite 2 y un filtro que acepta todo, el filtro se invoca exactamente 2 veces; con límite 0, ninguna).
- **L210-211** Si la fila satisface todos los filtros, se agrega. Con la lista de filtros vacía, toda fila se acepta.
- Consecuencia: el límite cuenta filas que **cumplen** los filtros. El lector sigue examinando filas hasta reunir *L* filas válidas o agotar el rango; no se limita a examinar las primeras *L* filas (es una de las dos opciones que plantea la consigna en 3.4).

**Bloque D — etapa 4: proyección de columnas (L214-219)**

- **L214-219** Si hay selección, se construye una lista nueva con un diccionario recortado por fila (`recortar_diccionario`). Al ejecutarse al final, los filtros reciben la fila completa y tipada: se puede filtrar por una columna que no se incluye en el resultado.
- **L221** Sin selección, se devuelve `filas_filtradas`, cuyos diccionarios son los mismos objetos creados en `_convertir_tipos`.

---

## 6. Algoritmo de inferencia de tipos

### 6.1 Definición formal

Sea una columna *c* cuyos campos crudos (ya recortados) son ⟨w₁, …, wₙ⟩. Se definen:

- **Conjunto de valores no vacíos:** *V* = { wᵢ : wᵢ ≠ `""` }.
- **Lenguajes aceptados** (conjuntos de cadenas que cada predicado reconoce):
  - *D*(bool) = { v : `v.lower()` ∈ {`"true"`, `"false"`} } — predicado `es_booleano`.
  - *D*(int) = { v : `int(v)` no lanza `ValueError` } — predicado `es_entero`.
  - *D*(float) = { v : `float(v)` no lanza `ValueError` } — predicado `es_flotante`.
  - *D*(str) = todas las cadenas.

Si la columna tiene tipo forzado *T*_f (`c ∈ _tipos_columnas`), entonces **tipo(c) = T_f** y no se evalúa lo que sigue (`clase.py:158-159`). En caso contrario, `inferir_tipo_columna` calcula:

```text
            ⎧ str     si V = ∅
            ⎪ bool    si V ≠ ∅  y  ∀v ∈ V: v ∈ D(bool)
  tipo(c) = ⎨ int     si V ≠ ∅  y  ∀v ∈ V: v ∈ D(int)     y no se cumple lo anterior
            ⎪ float   si V ≠ ∅  y  ∀v ∈ V: v ∈ D(float)   y no se cumple lo anterior
            ⎩ str     en cualquier otro caso
```

Las cláusulas se evalúan en el orden escrito y se adopta la primera que se cumple (`funciones.py:44-75`).

### 6.2 Propiedades

1. **Relaciones entre lenguajes.**
   - *D*(bool) ∩ *D*(int) = ∅ y *D*(bool) ∩ *D*(float) = ∅: ningún `"true"`/`"false"` es numérico.
   - *D*(int) ⊆ *D*(float) ⊆ *D*(str): todo texto que acepta `int()` lo acepta `float()` (verificado con signos, ceros iniciales, guiones bajos y dígitos Unicode). El caso de más de 4300 dígitos (§4.3) no es una excepción a la inclusión: `int()` lo rechaza y `float()` lo acepta.
2. **Consecuencias para el orden.** Por la disyunción, el orden relativo entre `bool` e `int` no altera el resultado. En cambio, **`int` debe probarse antes que `float`**: como *D*(int) ⊆ *D*(float), si se probara `float` primero ninguna columna se inferiría `int`. El orden implementado elige, entre los tipos numéricos, **el más específico que representa todos los valores**; esto responde la pregunta de la consigna sobre `10`, `20` y `30.5` (resultado: `float`).
3. **Mezclas.** `bool` e `int` no tienen otro tipo común que `str`; por eso `["true", "1"]` se infiere `str`. Una mezcla de números y texto también da `str` (inferencia "todo o nada": un solo valor no numérico vuelve `str` a toda la columna).
4. **Corrección de la conversión.** Si tipo(c) fue inferido, para todo `v ∈ V` se cumple `v ∈ D(tipo(c))`, y por lo tanto `convertir_valor(v, tipo(c), …)` no lanza excepción: `bool` usa la misma normalización `lower()` en ambas funciones, e `int`/`float` usan la misma función de conversión (`int()` o `float()`).
5. **Nulos.** Los campos vacíos no intervienen en la decisión y se convierten a `None` cualquiera sea el tipo. Una columna sin valores no vacíos es `str` con todos sus valores `None`.
6. **Independencia de la selección.** *V* se calcula sobre las *n* filas del archivo, no sobre las del rango ni las que pasan los filtros (I3.4).
7. **Equivalencia.** El algoritmo coincide con la versión que usa `all(pred(v) for v in V)` para cada tipo (verificado sobre los 22 casos de la tabla siguiente).
8. **Costo.** Un recorrido para copiar la columna (`clase.py:161-163`), uno para construir *V* (`funciones.py:38-41`) y hasta tres recorridos de *V* con corte temprano: O(*n*) por columna. El peor caso es una columna cuyos valores parecen numéricos salvo el último.

### 6.3 Tabla de casos (verificados)

Cada fila muestra los valores de la columna, el tipo inferido y los valores convertidos que produce `convertir_valor` con ese tipo.

| # | Valores de la columna | Tipo inferido | Valores convertidos | Comentario |
|---|---|---|---|---|
| 1 | `"1"`, `"0"` | `int` | `1`, `0` | `"1"`/`"0"` no son booleanos. |
| 2 | `"true"`, `"1"` | `str` | `"true"`, `"1"` | Mezcla bool/int: solo `str` los contiene. |
| 3 | `"TRUE"`, `"False"`, `""` | `bool` | `True`, `False`, `None` | Insensible a mayúsculas; vacío ignorado. |
| 4 | `"10"`, `"20"`, `"30.5"` | `float` | `10.0`, `20.0`, `30.5` | Caso de la consigna. |
| 5 | `"10"`, `"20.0"` | `float` | `10.0`, `20.0` | `int("20.0")` falla. |
| 6 | `"10"`, `""`, `"30"` | `int` | `10`, `None`, `30` | Nulo dentro de columna entera. |
| 7 | `"10"`, `"NA"` | `str` | `"10"`, `"NA"` | `NA` no es marcador de nulo. |
| 8 | `"10"`, `"nan"` | `float` | `10.0`, `nan` | `float("nan")` es válido; `nan` no es `None`. |
| 9 | `"1e3"`, `"2"` | `float` | `1000.0`, `2.0` | Notación científica. |
| 10 | `"inf"`, `"1"` | `float` | `inf`, `1.0` | Infinito aceptado por `float()`. |
| 11 | `"1.000"` | `float` | `1.0` | El punto es decimal, no separador de miles. |
| 12 | `"1,5"`, `"2"` | `str` | `"1,5"`, `"2"` | Coma decimal no soportada. |
| 13 | `"001"`, `"002"` | `int` | `1`, `2` | Se pierden ceros iniciales (usar `forzar_tipo(…, str)`). |
| 14 | `"+5"`, `"-3"` | `int` | `5`, `-3` | Signos aceptados. |
| 15 | `"-0"`, `"7"` | `int` | `0`, `7` | |
| 16 | `"1_000"`, `"2"` | `int` | `1000`, `2` | `int()` acepta guiones bajos. |
| 17 | `"0x1A"` | `str` | `"0x1A"` | Sin base explícita, `int()` no acepta hexadecimal. |
| 18 | `"true"`, `"false"`, `"maybe"` | `str` | sin cambios | Un valor ajeno vuelve `str` la columna. |
| 19 | `"VERDADERO"`, `"FALSO"` | `str` | sin cambios | Booleanos de Excel en castellano no reconocidos. |
| 20 | `"yes"`, `"no"` | `str` | sin cambios | Solo `true`/`false`. |
| 21 | `""`, `""` | `str` | `None`, `None` | Columna completamente vacía. |
| 22 | (sin filas) | `str` | — | Archivo con solo encabezado: `leer()` devuelve `[]`. |

Ejemplo sobre los datos entregados (`datos1.csv` sin forzar tipos): `codigo` → `int` (`"001"` → `1`), `nombre` → `str`, `precio` → `float` (mezcla `"800"` y `"2500.5"`), `cantidad` → `int` con un `None`, `disponible` → `bool` (verificado). En `derror.csv`, sin forzar tipos, `cantidad` contiene `"veinte"` y se infiere `str` (`'10'`, `'veinte'`, `'8'`) sin error; con `forzar_tipo("cantidad", int)` la lectura se detiene (ejemplo 4, §10.4).

---

## 7. Semántica formal de la combinación de opciones

### 7.1 Datos de entrada de la etapa de selección

Sea **F** = ⟨φ₁, φ₂, …, φₙ⟩ la secuencia de filas tipadas (R3) en el orden del archivo, donde φᵢ es la *i*-ésima **fila de datos** (*i* = 1 es la primera fila después del encabezado, o la primera línea si `encabezado=False`). **F** se calcula siempre a partir del archivo completo, con independencia de la configuración de selección.

La configuración relevante es:

- **R** = `_rango_filas` ∈ {⊥} ∪ {(a, b) : 1 ≤ a ≤ b}, donde ⊥ denota "no configurado" (`None`).
- **P** = `_filtros` = ⟨g₁, …, g_f⟩, con *f* ≥ 0.
- **L** = `_limite_filas` ∈ {⊥} ∪ ℕ₀.
- **K** = `_columnas` ∈ {⊥} ∪ ⟨c₁, …, c_m⟩.

### 7.2 Definición como composición de etapas

El resultado de `leer()` se define como

```text
  resultado = proy_K ( lim_L ( filt_P ( rango_R ( F ) ) ) )
```

con las siguientes funciones sobre secuencias:

1. **Rango** (`clase.py:198-202`):
   - rango_⊥(**F**) = **F**.
   - rango_(a,b)(**F**) = ⟨φₐ, φₐ₊₁, …, φ_min(b, n)⟩, y la secuencia vacía ⟨⟩ si a > n. Implementación: `F[a-1 : b]`.
2. **Filtro** (`clase.py:205-211`, `funciones.py:120-125`): sea el predicado
   P(φ) ≡ truthy(g₁(φ)) ∧ truthy(g₂(φ)) ∧ … ∧ truthy(g_f(φ)),
   evaluado de izquierda a derecha con cortocircuito, y con P ≡ verdadero si *f* = 0. Entonces filt_P(**S**) es la subsecuencia de **S** formada por los elementos que satisfacen P, **en el mismo orden**.
3. **Límite** (`clase.py:207-208`):
   - lim_⊥(**S**) = **S**.
   - lim_L(**S**) = ⟨s₁, …, s_min(L, |S|)⟩ (prefijo de longitud *L*). Para *L* no entero, el código produce el prefijo de longitud ⌈L⌉ (verificado con 2.5 → 3 filas), dado que compara `len(...) >= L`.
4. **Proyección** (`clase.py:214-219`, `funciones.py:128-133`):
   - proy_⊥(**S**) = **S** (mismos objetos diccionario).
   - proy_⟨c₁…c_m⟩(**S**) = ⟨π(s) : s ∈ **S**⟩, con π(s) = {c₁: s[c₁], …, c_m: s[c_m]} (diccionario nuevo, claves en el orden de *K*; repeticiones colapsan en una clave).

**Precondición de la proyección** (`clase.py:192-195`): {c₁, …, c_m} ⊆ encabezados; si no se cumple, `ValueError` **antes** de aplicar el rango.

### 7.3 Semántica operacional: fusión de filtro y límite

La implementación no materializa filt_P(rango_R(**F**)) y luego toma un prefijo: ambas etapas se **fusionan** en un único bucle que se interrumpe con `break` al alcanzar el límite (`clase.py:206-211`). Sea **S** = rango_R(**F**) = ⟨s₁, …, s_r⟩. El bucle evalúa P sobre s₁, s₂, … y se detiene en la primera posición *j* en la que ya se reunieron *L* filas aceptadas; la fila s_j no llega a evaluarse.

- **Equivalencia.** Si los filtros son puros y no lanzan excepciones, el resultado coincide exactamente con la composición de §7.2.
- **Diferencia observable.** P solo se evalúa sobre el **prefijo mínimo** de **S** necesario para obtener *L* filas. En consecuencia: (a) un filtro que lanzaría una excepción en una fila posterior al corte no la lanza; (b) un filtro que lanzaría excepción en una fila fuera del rango tampoco. Verificado con un filtro `f['cantidad'] > 3` sobre un archivo cuya cuarta fila tiene `cantidad` vacía: sin configuración lanza `TypeError`; con `establecer_rango(1, 3)` o con `establecer_limite(1)` devuelve resultado sin error. Esta dependencia contrasta con los errores de **conversión**, que se detectan sobre todo el archivo antes de aplicar cualquier opción.

### 7.4 Las dos numeraciones de filas

| Concepto | Símbolo | Base | Incluye el encabezado | Dónde se usa |
|---|---|---|---|---|
| Fila de datos | *i* | 1 | No | `establecer_rango(inicio, fin)` (`clase.py:55-59, 200`) |
| Línea física del archivo | ℓ | 1 | Sí | Todos los mensajes `Error en fila …` (`clase.py:103, 114, 116, 131, 137`; `funciones.py:95, 104, 113`) |
| Índice de Python en `lineas` | `i` (variable) | 0 | Sí | `clase.py:126-127` (ℓ = `i` + 1) |
| Índice de Python en `filas_crudas` / `filas_tipadas` | `fila_i` | 0 | No | `clase.py:168-174` y `clase.py:200` |

Relación: **ℓ = *i* + 1 si `encabezado=True`**, y **ℓ = *i* si `encabezado=False`** (en este último caso ambas numeraciones coinciden; verificado: con `encabezado=False`, `establecer_rango(2, 2)` devuelve la segunda línea del archivo). Ejemplo con encabezado: en `derror.csv`, el valor `veinte` está en la **fila de datos 2** (la que seleccionaría `establecer_rango(2, 2)`) y el mensaje informa **"fila 3"** (línea física 3). La correspondencia es exacta porque ninguna línea se descarta (I1.3, I2.6).

Numeración de columnas: el error de nombre vacío informa la **posición en base 1** (`columna {i + 1}`, `clase.py:114`); los errores de conversión informan el **nombre** de la columna; los nombres generados sin encabezado usan **base 0** (`col_0`, `clase.py:121`). Es una inconsistencia menor de convenciones.

### 7.5 Ejemplos verificados sobre `datos1.csv`

Filas de datos: 1 Cuaderno (cantidad 10, precio 2500.5), 2 Lapicera (25, 800.0), 3 Carpeta (8, 3200.0), 4 Regla (`None`, 500.0), 5 Mochila (3, 15000.0), 6 Goma (50, 300.5). Filtro *q*: `cantidad is not None and cantidad < 15`.

| Configuración | rango_R | filt_P | lim_L | Resultado (nombres) |
|---|---|---|---|---|
| Rango (2, 3) | 2, 3 | — | — | Lapicera, Carpeta |
| Rango (3, 100) | 3…6 | — | — | Carpeta, Regla, Mochila, Goma |
| Rango (50, 60) | ⟨⟩ | — | — | `[]` |
| Límite 2 | 1…6 | — | 1, 2 | Cuaderno, Lapicera |
| Límite 0 | 1…6 | — | ⟨⟩ | `[]` (si hubiera filtros, no se invocarían: verificado con un filtro contador) |
| Filtro `precio < 1000` + límite 2 | 1…6 | 2, 4, 6 | 2, 4 | Lapicera, Regla |
| Filtros *q* y `precio > 3000` (conjunción) | 1…6 | 3, 5 | — | Carpeta, Mochila |
| Filtro *q* + columnas `["nombre"]` | 1…6 | 1, 3, 5 | — | Cuaderno, Carpeta, Mochila (solo clave `nombre`; se filtró por `cantidad`, que no se devuelve) |
| Rango (4, 6) + filtro *q* | 4, 5, 6 | 5 | — | Mochila |
| **Ejemplo 2**: rango (1, 5) + *q* + límite 2 + columnas `["nombre", "precio"]` | 1…5 | 1, 3, 5 | 1, 3 | `[{'nombre': 'Cuaderno', 'precio': 2500.5}, {'nombre': 'Carpeta', 'precio': 3200.0}]` |

La fila "Filtro `precio < 1000` + límite 2" muestra que el límite cuenta filas que **cumplen** el filtro: se examinan las filas 1 a 4 y se devuelven la 2 y la 4, no las dos primeras del archivo.

---

## 8. Condiciones de error

### 8.1 Política general

- **Detención ante el primer error.** Ninguna etapa acumula errores ni devuelve resultados parciales: el primer problema detectado lanza una excepción que se **propaga** sin ser capturada por los métodos de la clase hasta el programa usuario (en `ejemplos.py:48-52`, un `try/except ValueError`).
- **Excepciones en lugar de `print`.** El paquete no imprime nada (no hay ningún `print` en `clase.py` ni en `funciones.py`). Comunicar el problema mediante una excepción permite que el programa usuario decida cómo reaccionar, criterio central de la unidad de Excepciones.
- **Tipos de excepción.** Se usa `ValueError` para valores inválidos (configuración, formato del archivo, conversión) y `FileNotFoundError` para la ruta inexistente. No se definen excepciones propias.
- **Capturas específicas.** Las únicas capturas del paquete son `except ValueError` (`funciones.py:23, 32, 102, 111`) y `except FileNotFoundError` (`clase.py:91`); no hay `except:` sin tipo ni `except Exception`.
- **Orden de detección.** Los errores se detectan por **etapa**, en este orden: configuración (al invocar el método) → `_leer_archivo` → `_procesar_lineas` (encabezado de izquierda a derecha, luego filas en orden) → `_convertir_tipos` (columnas forzadas, luego celdas fila por fila) → `_aplicar_filtros_y_rangos` (columnas seleccionadas, luego filtros). Por eso el primer error informado no es necesariamente el primero del archivo: con `forzar_tipo('b', int)` sobre `a,b / 1,x / 2,3,4`, se informa la cantidad de campos de la línea 3 y no el valor `x` de la línea 2 (verificado).

### 8.2 Errores lanzados por el código del grupo

Los mensajes se transcriben exactamente; `{…}` indica un valor interpolado.

| # | Condición | Etapa / método | Línea | Excepción | Mensaje exacto | Numeración |
|---|---|---|---|---|---|---|
| E1 | `delimitador == ""` | Configuración / `__init__` | `clase.py:28` | `ValueError` | `El delimitador no puede ser vacío.` | — |
| E2 | `tipo_dato` ∉ {int, float, str, bool} | Configuración / `forzar_tipo` | `clase.py:41` | `ValueError` | `Tipo no válido. Use int, float, str o bool.` | — |
| E3 | `limite < 0` | Configuración / `establecer_limite` | `clase.py:52` | `ValueError` | `El limite de filas no puede ser negativo` | — |
| E4 | `inicio < 1` o `fin < inicio` | Configuración / `establecer_rango` | `clase.py:58` | `ValueError` | `Rango invalido: 'inicio' debe ser >= 1 y 'fin' >= 'inicio'` | — |
| E5 | La ruta no existe | `_leer_archivo` | `clase.py:92` | `FileNotFoundError` (encadenada) | `No se encontró el archivo en la ruta: {ruta_archivo}` | — |
| E6 | Archivo de 0 líneas (0 bytes) | `_leer_archivo` | `clase.py:95` | `ValueError` | `El archivo '{ruta_archivo}' está vacío.` | — |
| E7 | Primera línea en blanco | `_procesar_lineas` | `clase.py:103` | `ValueError` | `Error en fila 1: La primera línea del archivo está vacía.` | Línea física |
| E8 | Nombre de columna vacío (solo con encabezado) | `_procesar_lineas` | `clase.py:114` | `ValueError` | `Error en fila 1, columna {i + 1}: El nombre de la columna está vacío.` | Línea física; columna por posición base 1 |
| E9 | Nombre de columna repetido (solo con encabezado; sensible a mayúsculas) | `_procesar_lineas` | `clase.py:116` | `ValueError` | `Error en fila 1: El nombre de columna '{nombre}' está repetido.` | Línea física |
| E10 | Línea de datos en blanco (incluye una línea vacía al final por doble salto) | `_procesar_lineas` | `clase.py:131` | `ValueError` | `Error en fila {num_fila_archivo}: Se encontró una fila vacía.` | Línea física |
| E11 | Cantidad de campos ≠ *k* | `_procesar_lineas` | `clase.py:136-139` | `ValueError` | `Error en fila {num_fila_archivo}: Cantidad incorrecta de elementos. Se esperaban {cant_columnas} columnas, pero se encontraron {len(elementos)}.` | Línea física |
| E12 | Columna de `forzar_tipo` inexistente | `_convertir_tipos` | `clase.py:149` | `ValueError` | `La columna '{col_forzada}' indicada en forzar_tipo no existe en la tabla.` | — |
| E13 | Valor no convertible a `bool` (columna forzada) | `_convertir_tipos` → `convertir_valor` | `funciones.py:94-97` | `ValueError` (sin encadenamiento) | `Error en fila {num_fila}, columna '{nombre_col}': el valor '{texto}' no se puede convertir a bool.` | Línea física; columna por nombre |
| E14 | Valor no convertible a `int` (columna forzada) | ídem | `funciones.py:103-106` | `ValueError` (encadenada) | `Error en fila {num_fila}, columna '{nombre_col}': el valor '{texto}' no se puede convertir a int.` | ídem |
| E15 | Valor no convertible a `float` (columna forzada) | ídem | `funciones.py:112-115` | `ValueError` (encadenada) | `Error en fila {num_fila}, columna '{nombre_col}': el valor '{texto}' no se puede convertir a float.` | ídem |
| E16 | Tipo no soportado en `convertir_valor` | ídem | `funciones.py:117` | `ValueError` | `Tipo de dato no soportado: {tipo_esperado}` | Inalcanzable por la interfaz pública |
| E17 | Columna seleccionada inexistente | `_aplicar_filtros_y_rangos` | `clase.py:195` | `ValueError` | `La columna seleccionada '{col}' no existe en la tabla.` | — |

Ejemplos de mensajes reales: E8 con `a,,c` → `Error en fila 1, columna 2: El nombre de la columna está vacío.`; E10 con una línea vacía en la línea 3 → `Error en fila 3: Se encontró una fila vacía.`; E11 → `Error en fila 3: Cantidad incorrecta de elementos. Se esperaban 2 columnas, pero se encontraron 3.`; E14 con `derror.csv` → `Error en fila 3, columna 'cantidad': el valor 'veinte' no se puede convertir a int.` (todos verificados).

### 8.3 Excepciones no capturadas por el lector

Estas excepciones no provienen de un `raise` del grupo, sino de Python o del código del usuario, y se propagan sin mensaje propio.

| # | Condición | Origen (línea donde se manifiesta) | Excepción y mensaje de Python | ¿La captura `except ValueError` de `ejemplos.py`? |
|---|---|---|---|---|
| N1 | Archivo no UTF-8 (latin-1/cp1252 con acentos, UTF-16) | Decodificación durante `for linea in archivo` (`clase.py:89`) | `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf3 …` | **Sí** (`UnicodeDecodeError` es subclase de `ValueError`), pero con el mensaje técnico de Python. |
| N2 | La ruta es una carpeta | `open` (`clase.py:87`) | En Windows: `PermissionError: [Errno 13] Permission denied: …` (en sistemas POSIX sería `IsADirectoryError`) | No. |
| N3 | Filtro que accede a una columna inexistente | Dentro del filtro, invocado en `funciones.py:123` | `KeyError: 'cantidd'` | No. No indica la fila. |
| N4 | Filtro que compara `None` (celda vacía) con un número | ídem | `TypeError: '<' not supported between instances of 'NoneType' and 'int'` | No. No indica la fila. |
| N5 | Filtro no invocable (`agregar_filtro(5)`) | `funciones.py:123` | `TypeError: 'int' object is not callable` | No. |
| N6 | `establecer_limite("3")` o `establecer_limite(None)` | `clase.py:51` (al configurar) | `TypeError: '<' not supported between instances of 'str' and 'int'` (o `'NoneType' and 'int'`) | No. |
| N7 | `establecer_rango("1", 3)` | `clase.py:57` (al configurar) | `TypeError: '<' not supported between instances of 'str' and 'int'` | No. |
| N8 | `establecer_rango(1, 3.0)` o `(1.5, 3)` | `clase.py:200` (al leer) | `TypeError: slice indices must be integers or None or have an __index__ method` | No. |
| N9 | Delimitador no cadena (`LectorCSV(delimitador=44)`) | `funciones.py:3` (al leer) | `TypeError: must be str or None, not int` | No. |
| N10 | `lector.delimitador = ""` después de construir | `funciones.py:3` (al leer) | `ValueError: empty separator` | Sí, con mensaje técnico. |

Casos que **no** producen excepción pero pueden sorprender: rango que excede el archivo (devuelve menos filas o `[]`), filtro sin `return` (devuelve `None`, se interpreta como falso y el resultado es `[]`), delimitador equivocado (una única columna con la línea entera), archivo sin encabezado leído con `encabezado=True` (la primera fila de datos se toma como encabezado).

### 8.4 Encadenamiento de excepciones

Cuando una excepción se lanza **dentro** de un bloque `except`, Python guarda la excepción que se estaba manejando en el atributo `__context__` de la nueva (encadenamiento implícito). Al no capturarse, el *traceback* muestra ambas, separadas por *"During handling of the above exception, another exception occurred"*.

| Sitio | ¿Encadena? | `__context__` (verificado) |
|---|---|---|
| E5 `clase.py:92` | Sí | `FileNotFoundError: [Errno 2] No such file or directory: '…'` (originada en `clase.py:87`). La nueva excepción tiene `errno=None` y `filename=None`. |
| E14 `funciones.py:103` | Sí | `ValueError: invalid literal for int() with base 10: 'veinte'` (originada en `funciones.py:101`). |
| E15 `funciones.py:112` | Sí | `ValueError` de `float()` (originada en `funciones.py:110`). |
| E13 `funciones.py:94` | No | `raise` fuera de un `except`. |
| Resto (E1-E4, E6-E12, E16, E17) | No | — |

*Traceback* verificado del caso `derror.csv` sin capturar, leído de abajo hacia arriba como recomienda la cátedra: la excepción final se lanza en `convertir_valor` (`funciones.py:103`), llamada desde `_convertir_tipos` (`clase.py:182`), llamada desde `leer` (`clase.py:77`), llamada desde el programa principal; por encima aparece la excepción original de `int('veinte')` en `funciones.py:101`.

Alternativas de la cátedra: `raise NuevaExcepcion(...) from error` hace explícita la relación de causa (*"The above exception was the direct cause of the following exception"*); `raise ... from None` suprime el contexto y muestra solo el mensaje del grupo, a usar con cuidado porque elimina información de diagnóstico. En `ejemplos.py` el efecto no se percibe porque solo se imprime `str(error)`.

---

## 9. Análisis de complejidad temporal y espacial

### 9.1 Supuestos y parámetros

Se usa la notación Big O en el **peor caso**, como en la cátedra. Parámetros: *n* filas de datos, *k* columnas, *f* filtros, *t* columnas con tipo forzado, *c* columnas seleccionadas, *r* filas del rango (*r* ≤ *n*), *s* filas examinadas por el bucle de filtrado antes del corte (*s* ≤ *r*), *p* filas devueltas (*p* ≤ *s*), *C* caracteres del archivo. Se supone que la longitud de cada campo está acotada por una constante (entonces *C* = Θ(*n·k*)), que cada filtro tiene costo O(1) y que las operaciones sobre diccionarios cuestan O(1) en promedio. Sobre listas: lectura por índice O(1) y `append` al final O(1) amortizado (arreglo dinámico); la prueba `x in lista` es búsqueda lineal O(longitud).

### 9.2 Complejidad temporal por etapa

| Etapa | Operaciones dominantes | Tiempo |
|---|---|---|
| Configuración | Asignaciones y validaciones de tamaño fijo | O(1) por llamada |
| `_leer_archivo` | Decodificar y recorrer el archivo; `rstrip` por línea | O(*C*) |
| `_procesar_lineas`: encabezado | *k* búsquedas lineales `nombre in encabezados` sobre una lista que crece: 0 + 1 + … + (*k* − 1) = *k*(*k* − 1)/2 comparaciones | O(*k*²) |
| `_procesar_lineas`: filas | `split` + `strip` por línea | O(*C*) = O(*n·k*) |
| `_convertir_tipos`: validación | *t* búsquedas lineales en `encabezados` | O(*t·k*) |
| `_convertir_tipos`: inferencia | Por columna no forzada: copiar la columna, filtrar vacíos y hasta 3 pasadas con corte temprano | O(*n*) por columna; O(*n·k*) total |
| `_convertir_tipos`: conversión | Una llamada a `convertir_valor` por celda | O(*n·k*) |
| `_aplicar_filtros_y_rangos`: validación | *c* búsquedas lineales en `encabezados` | O(*c·k*) |
| Rango | *Slice* que copia *r* referencias | O(*r*) |
| Filtros + límite | *s* iteraciones con hasta *f* invocaciones cada una | O(*s·f*) |
| Proyección | *p* diccionarios de *c* claves | O(*p·c*) |
| **Total** | | **O(*n·k* + *k*² + *t·k* + *c·k* + *s·f* + *p·c*)** |

Con *k*, *t*, *c* y *f* pequeños frente a *n* (el caso usual), el total es **O(*n·k*)**: lineal en el tamaño del archivo. No puede mejorarse asintóticamente mientras haya que inferir tipos, porque la inferencia exige examinar cada celda al menos una vez. Las varias pasadas de la inferencia multiplican el trabajo por una constante, que Big O descarta: por columna hay a lo sumo cinco recorridos (copia de la columna, filtrado de vacíos y tres pruebas de tipo), y O(5*n*) = O(*n*).

**Término cuadrático en *k*.** El control de nombres repetidos es un bucle anidado implícito (el `for` de `clase.py:111` y la búsqueda lineal de `clase.py:115`), el mismo patrón que la cátedra analiza al buscar duplicados con dos bucles anidados. La idea de la solución lineal también es la misma, registrar en una estructura auxiliar los valores ya vistos, aunque la implementación difiere: el apunte usa un arreglo auxiliar indexado por valor, posible porque los valores son enteros de un rango conocido (0 a 10); para nombres de columna, que son cadenas arbitrarias, la estructura adecuada es un `set` de nombres ya vistos (búsqueda de costo constante promedio), conservando la lista para el orden. Con las pocas columnas de un CSV habitual la diferencia no es observable.

### 9.3 El límite no reduce el trabajo de lectura ni de conversión

Las etapas 1 a 3 de `leer()` (`clase.py:71-77`) procesan siempre el archivo completo; el límite solo interviene en el bucle de `clase.py:206-208`, reduciendo *s* y, por lo tanto, el término O(*s·f*). Formalmente, el costo es

```text
  T(n, k, L) = Θ(n·k) + O(min(s_L, r) · f)
```

donde *s_L* es la cantidad de filas que hay que examinar para reunir *L* aceptadas: el primer sumando no depende de *L*. Medición propia (archivo de 100.000 filas y 4 columnas, tras una lectura de calentamiento, tres repeticiones): ≈ 0,30-0,32 s **con** `establecer_limite(1)` y ≈ 0,30-0,31 s **sin** límite. Las diferencias están dentro de la variación entre repeticiones.

El motivo de diseño es la inferencia: el tipo de una columna depende de todos sus valores, de modo que no puede convertirse ninguna celda antes de haber visto la columna completa. Una consecuencia coherente con esto es que un error de conversión fuera del rango o posterior al límite igualmente detiene la lectura (§5.9).

### 9.4 Complejidad espacial

| Estructura | Vida | Espacio |
|---|---|---|
| `lineas` (R1) | Variable local de `leer()` hasta su retorno | O(*C*) |
| `filas_crudas` (R2) | ídem | O(*n·k*) referencias + O(*C*) caracteres |
| `filas_tipadas` (R3) | ídem | O(*n·k*) |
| `valores_columna`, `no_vacios` | Transitorias, una columna por vez | O(*n*) |
| `tipos_definidos` | `_convertir_tipos` | O(*k*) |
| `filas_en_rango` | Copia solo si hay rango | O(*r*) |
| `filas_filtradas`, `resultado_final` | Hasta el retorno | O(*p*) referencias; O(*p·c*) si hay proyección |

Las tres representaciones del archivo coexisten mientras se ejecuta `leer()`, porque son variables locales de ese método: el pico de memoria es **O(*C* + *n·k*)**, aproximadamente tres copias del contenido del archivo en distintas formas. Para los archivos del TP es irrelevante. Para archivos muy grandes, la alternativa de la Unidad 3 sería procesar por *streaming* con **generadores** (evaluación perezosa); sin embargo, como la inferencia requiere la columna completa y un generador es de un solo uso, habría que **leer el archivo dos veces** (una pasada para inferir y otra para convertir) o restringir el *streaming* al caso en que todos los tipos estén forzados.

---

## 10. `ejemplos.py`: descripción y resultados esperados

`ejemplos.py` es el script de demostración. Se ejecuta desde la raíz del proyecto con `python ejemplos.py`. Contiene código a nivel superior, sin funciones ni la guarda `if __name__ == "__main__":`, de modo que importarlo ejecuta los cuatro ejemplos. Cada ejemplo crea un **lector independiente** (cuatro instancias), por lo que las configuraciones no interfieren entre sí.

- **L1** `import pandas as pd`: único uso de pandas en el proyecto, con el alias convencional.
- **L2** `from modulo.clase import LectorCSV`: importación de la interfaz pública.

### 10.1 Ejemplo 1 — Inferencia y tipo forzado (L5-16)

**Entrada.** `datos1.csv`: delimitador coma seguido de espacio, finales de línea CRLF, sin salto de línea final, 6 filas de datos; la fila de Regla tiene `cantidad` vacía y la fila de Lapicera tiene precio `800` (sin decimales).

**Configuración.** `LectorCSV(delimitador=",")` (L6; el argumento repite el valor por defecto, de forma explícita) y `forzar_tipo("codigo", str)` (L7), para conservar los ceros iniciales, que es exactamente el caso `00123` que plantea la consigna. La lectura se invoca en L8; L5 imprime el título del ejemplo.

**Procesamiento esperado.** `codigo` → `str` (forzado); `nombre` → `str`; `precio` → `float` (mezcla de `"800"` y `"2500.5"`); `cantidad` → `int` con un `None`; `disponible` → `bool`.

**Salida real (L10-12):**

```text
{'codigo': '001', 'nombre': 'Cuaderno', 'precio': 2500.5, 'cantidad': 10, 'disponible': True}
{'codigo': '002', 'nombre': 'Lapicera', 'precio': 800.0, 'cantidad': 25, 'disponible': True}
{'codigo': '003', 'nombre': 'Carpeta', 'precio': 3200.0, 'cantidad': 8, 'disponible': True}
{'codigo': '004', 'nombre': 'Regla', 'precio': 500.0, 'cantidad': None, 'disponible': False}
{'codigo': '005', 'nombre': 'Mochila', 'precio': 15000.0, 'cantidad': 3, 'disponible': True}
{'codigo': '006', 'nombre': 'Goma', 'precio': 300.5, 'cantidad': 50, 'disponible': True}
```

**Salida real como `DataFrame` (L14-16):**

```text
  codigo    nombre   precio  cantidad  disponible
0    001  Cuaderno   2500.5      10.0        True
1    002  Lapicera    800.0      25.0        True
2    003   Carpeta   3200.0       8.0        True
3    004     Regla    500.0       NaN       False
4    005   Mochila  15000.0       3.0        True
5    006      Goma    300.5      50.0        True
```

Observación: en el `DataFrame`, `cantidad` aparece como `10.0`, `25.0`, …, `NaN`. pandas convierte la columna a `float64` porque su tipo entero `int64` no admite valores faltantes, y representa `None` como `NaN`. La lista de diccionarios conserva los `int` y el `None`. Esto ilustra por qué la consigna exige mostrar también la lista original.

### 10.2 Ejemplo 2 — Combinación de opciones (L20-31)

**Configuración.** `establecer_rango(1, 5)` (L22); `agregar_filtro(lambda fila: fila["cantidad"] is not None and fila["cantidad"] < 15)` (L23); `establecer_limite(2)` (L24); `seleccionar_columnas(["nombre", "precio"])` (L25). El lector se crea en L21 y la lectura se invoca en L27.

**Derivación** (según §7.2):

1. rango_(1,5): Cuaderno, Lapicera, Carpeta, Regla, Mochila.
2. filt_P: Cuaderno (10), Carpeta (8), Mochila (3). Lapicera (25) no cumple; Regla (`None`) no cumple y, gracias al **cortocircuito** del `and`, no se evaluaría `None < 15`, que lanzaría `TypeError`. Se usa `is not None` porque `None` es un objeto único y se compara por identidad.
3. lim_2: Cuaderno, Carpeta. Operacionalmente (§7.3), el bucle se interrumpe al llegar a **Regla**, cuarta fila del rango, antes de evaluar el filtro sobre ella: el filtro se invoca solo sobre Cuaderno, Lapicera y Carpeta, y Mochila no llega a examinarse (verificado). En consecuencia, en esta configuración concreta la guarda `is not None` no llega a ejecutarse sobre `None` (el mismo ejemplo sin la guarda devuelve el mismo resultado, verificado); es necesaria para cualquier configuración que examine la fila de Regla, por ejemplo sin límite, donde la versión sin guarda lanza `TypeError` (verificado).
4. proy_⟨nombre, precio⟩: se filtró por `cantidad`, que no se incluye en el resultado.

**Salida real (L28-31):**

```text
[{'nombre': 'Cuaderno', 'precio': 2500.5}, {'nombre': 'Carpeta', 'precio': 3200.0}]

     nombre  precio
0  Cuaderno  2500.5
1   Carpeta  3200.0
```

El filtro es una **función anónima** (`lambda`), el uso que la cátedra asigna a estas funciones: una condición breve, de un solo uso, pasada como argumento a otra función.

### 10.3 Ejemplo 3 — Otro delimitador (L33-42)

**Entrada.** `datos2.txt`: delimitador punto y coma seguido de espacio, 3 filas.

**Configuración.** `LectorCSV(delimitador=";")` (L34), sin otras opciones; la lectura se invoca en L35.

**Salida real (L37-42):**

```text
{'id_envio': 101, 'destino': 'Rosario', 'costo': 4500.0, 'entregado': True}
{'id_envio': 102, 'destino': 'Cordoba', 'costo': 6200.5, 'entregado': False}
{'id_envio': 103, 'destino': 'Buenos Aires', 'costo': 5100.0, 'entregado': True}

   id_envio       destino   costo  entregado
0       101       Rosario  4500.0       True
1       102       Cordoba  6200.5      False
2       103  Buenos Aires  5100.0       True
```

Se observa que `costo` se infiere `float` por la mezcla de `"5100"` con decimales, y que `"Buenos Aires"` conserva el espacio interno (`strip` solo actúa en los bordes).

### 10.4 Ejemplo 4 — Manejo de errores (L44-52)

**Entrada.** `derror.csv`: la línea física 3 (`Lapicera, 800.0, veinte`) contiene un valor no numérico en `cantidad`.

**Configuración.** `LectorCSV(delimitador=",")` (L45) y `forzar_tipo("cantidad", int)` (L46); la lectura se invoca dentro del bloque `try`, en L49.

**Procesamiento.** Las etapas 1 y 2 terminan sin error. En la etapa 3, al convertir la fila de datos 2 (línea física 3), `int("veinte")` falla y `convertir_valor` lanza el `ValueError` del grupo (E14). La excepción se propaga a través de `_convertir_tipos` y `leer` hasta el bloque `try/except ValueError as error` de L48-52, que imprime el mensaje.

**Salida real:**

```text
El lector detectó el problema y detuvo la lectura:
Error en fila 3, columna 'cantidad': el valor 'veinte' no se puede convertir a int.
```

Contraste: sin `forzar_tipo`, la columna `cantidad` se infiere `str` (`'10'`, `'veinte'`, `'8'`) y la lectura termina sin error (verificado). El ejemplo muestra que el tipo forzado tiene prioridad y que, ante un valor no convertible, el lector **no sustituye** el tipo solicitado por otro inferido.

### 10.5 Cobertura de los ejemplos respecto de la consigna

La consigna (3.6) pide archivos pequeños y ejemplos de uso **con sus resultados esperados**, que contemplen la lectura habitual, la combinación de opciones y las situaciones problemáticas.

| Situación | ¿Cubierta por `ejemplos.py`? |
|---|---|
| Lectura habitual con inferencia | Sí (ejemplos 1 y 3) |
| Tipo forzado | Sí (ejemplos 1 y 4) |
| Otro delimitador | Sí (`;`, ejemplo 3) |
| Combinación de rango, filtro, límite y columnas | Sí (ejemplo 2) |
| Valor no convertible | Sí (ejemplo 4) |
| Archivo vacío, fila vacía, cantidad de campos distinta | No |
| Encabezado vacío o repetido | No |
| `encabezado=False`, tabulador, delimitador de varios caracteres | No |
| Resultados esperados escritos en el código o en comentarios | No (solo se imprimen) |

La cobertura es parcial. Todos los casos faltantes están implementados en el lector y fueron verificados en este documento (§8.2), por lo que la mejora consiste solo en agregar archivos y ejemplos.

---

## 11. Limitaciones y posibles extensiones

### 11.1 Limitaciones del formato de entrada

| Limitación | Efecto observado (verificado) | Extensión posible |
|---|---|---|
| Sin soporte de comillas (RFC 4180) | `"Rosario, SF",2` → E11 (cantidad de campos). Las comillas quedan en los valores y en los nombres de columna (`'"precio"'`). Una celda con salto de línea interno parte el registro en dos líneas físicas: si la celda es la última de la fila, la primera parte tiene *k* campos y el error E11 se informa en la línea siguiente; si está en una posición intermedia, se informa en la propia línea donde comienza el registro (ambos casos verificados). | Analizador carácter por carácter con estado "dentro/fuera de comillas" (o una expresión regular, que la consigna permite). |
| Coma decimal y separadores de miles | `"1,5"`, `"1500,50"` → columna `str`; forzar `float` → error. `"1.000"` → `1.0`. | Parámetro `separador_decimal` que normalice el texto antes de convertir. |
| Booleanos solo `true`/`false` | `VERDADERO`/`FALSO`, `yes`/`no`, `si`/`no`, `1`/`0` no se reconocen. | Parámetros con los conjuntos de literales verdaderos y falsos. |
| Solo la celda vacía es nulo | `NA`, `NULL`, `N/A`, `-` vuelven `str` la columna; `"nan"` es `float('nan')`, distinto de `None` (un filtro `is not None` lo deja pasar). | Parámetro con marcadores de nulo configurables. |
| Codificación fija UTF-8 | latin-1 o UTF-16 → `UnicodeDecodeError` (N1). Un BOM queda pegado al primer nombre (`'﻿codigo'`) o al primer valor. | `encoding="utf-8-sig"` (elimina el BOM) o parámetro `encoding`. |
| Sin detección del delimitador | Con el delimitador equivocado se obtiene una única columna, sin error. | Detección heurística sobre la primera línea, o advertencia si *k* = 1. |
| Líneas en blanco siempre son error | No se pueden representar nulos en archivos de una columna; `,,` es fila de nulos pero `\t\t` es error. | Política configurable (omitir o rechazar líneas en blanco) y control posterior a la separación. |
| Inferencia "todo o nada" | Un único valor atípico (`'1 500'`, `'−5'` con signo menos Unicode) vuelve `str` toda la columna. | Advertencia (`warnings.warn`) que indique la primera celda que impidió el tipo numérico. |
| Encabezado no validado contra los datos | Un archivo sin encabezado leído con `encabezado=True` pierde la primera fila y usa valores como claves. | Documentarlo; no es detectable en general. |

### 11.2 Limitaciones de la interfaz y del diseño

| Limitación | Defensa | Mejora |
|---|---|---|
| Validación de valor pero no de tipo en la configuración (N6-N9) | Se cubren los errores de valor más probables. | Validar con `isinstance` y lanzar `TypeError` para tipos incorrectos y `ValueError` para valores, como el ejemplo de validación de la cátedra. |
| `agregar_filtro` no verifica que el argumento sea invocable | Duck typing: se acepta cualquier invocable. | `if not callable(funcion_filtro): raise TypeError(...)`. |
| Los filtros se acumulan; el límite y el rango no pueden quitarse | El caso de uso previsto es un lector por consulta. | Métodos `quitar_filtros()` y aceptar `None` en `establecer_limite`/`establecer_rango`. |
| `seleccionar_columnas` guarda un alias de la lista del usuario | Costo O(1). | Copiar: `list(...)` o `tuple(...)`; o usar `*columnas`. |
| Atributo público `delimitador` sin protección posterior a `__init__` | Parámetro básico del método de inicialización. | `@property` con *setter* que valide. |
| Métodos de configuración devuelven `None` (sin encadenamiento) | Estilo de una llamada por línea, igual de claro. | `return self` (encadenamiento de métodos). |
| Errores de filtro sin fila ni contexto (N3, N4) | Son errores del código del usuario. | Capturar en `cumple_todos_los_filtros` y relanzar con `raise … from error` indicando la fila. |
| Sin excepciones propias | `ValueError` describe bien los casos y la consigna solo exige mensajes claros. | `class LectorCSVError(ValueError)` y subclases (formato, conversión), que siguen siendo capturadas por `except ValueError` y permiten distinguir los errores del lector de otros `ValueError` (por ejemplo `UnicodeDecodeError`). |
| Encadenamiento implícito en E5, E14, E15 | El mensaje propio es más claro para el usuario. | `raise … from error` o `from None`, según se quiera conservar u ocultar la causa. |
| Documentación en comentarios, sin *docstring* de clase ni anotaciones de tipo | Los nombres son descriptivos y cada método tiene *docstring* breve. | *Docstring* de clase con los criterios de L1-9 y secciones de parámetros, retorno y excepciones; anotaciones de tipo. |
| `__repr__` no definido | No era requerido. | `__repr__` que muestre la configuración, útil para depurar. |
| Colecciones fijas como listas (`clase.py:40`, `funciones.py:13`) | Comportamiento idéntico. | Tuplas, o constantes de clase (`TIPOS_VALIDOS = (int, float, str, bool)`). |
| `nombre in encabezados` sobre lista: O(*k*²) | *k* es pequeño en la práctica. | `set` auxiliar de nombres vistos: O(*k*). |
| Lectura completa en memoria; el límite no ahorra trabajo | La inferencia requiere la columna completa. | Generadores con dos pasadas, o *streaming* cuando todos los tipos estén forzados. |
| Doble conversión (detección y conversión) | Separación de responsabilidades; factor constante. | Inferencia que devuelva también los valores convertidos. |
| Rango fuera del archivo devuelve `[]` sin aviso | Comportamiento natural del *slicing*. | `warnings.warn(..., UserWarning)`. |

### 11.3 Limitaciones del entorno de ejecución y de la demostración

| Limitación | Mejora |
|---|---|
| Rutas de datos relativas al directorio de trabajo (§2.5) | Construirlas con `pathlib.Path(__file__).parent / "datos1.csv"`. |
| `ejemplos.py` sin `if __name__ == "__main__":` | Encerrar la demostración en la guarda, para que el archivo sea importable sin efectos. |
| Sin interfaz de línea de comandos para leer archivos nuevos | Script con `argparse` (ruta, `--delimitador`, `--sin-encabezado`). |
| Sin `requirements.txt` ni `__init__.py` | Agregar `requirements.txt` con `pandas` y un `__init__.py` vacío. |
| Ejemplos sin casos problemáticos ni resultados esperados escritos (§10.5) | Agregar archivos y ejemplos para cada condición de §8.2, con el resultado esperado documentado. |

---

## 12. Glosario

| Término | Definición en el contexto del TP |
|---|---|
| **Alias (referencia compartida)** | Dos nombres que refieren al mismo objeto mutable; modificar uno se observa desde el otro (`_columnas` y la lista del usuario). |
| **Atributo de instancia** | Variable asociada a un objeto que representa su estado (`self.delimitador`, `self._filtros`, …). |
| **Atributo / método protegido** | Nombre con un guion bajo inicial; por convención no debe usarse desde fuera de la clase. Python no lo impide. |
| **Búsqueda lineal** | Recorrido elemento por elemento para encontrar un valor; es lo que hace `in` sobre una lista. Costo O(longitud). |
| **Cláusula de guarda** | `if` inicial que resuelve un caso especial con `return` o `raise` y evita anidar el resto (`funciones.py:81-82`). |
| **Cortocircuito (evaluación no estricta)** | `and`/`or` no evalúan el segundo operando si el resultado ya está determinado (`clase.py:207`, `ejemplos.py:23`). |
| **Desempaquetado (*unpacking*)** | Asignación de los elementos de una tupla a varias variables (`clase.py:74, 199`). |
| **Duck typing** | Usar un objeto por lo que puede hacer y no por su clase: cualquier invocable sirve como filtro. |
| **Efecto secundario** | Cambio de estado observable fuera del ámbito local de una función (modificar un objeto externo, imprimir, escribir un archivo). |
| **Encadenamiento implícito** | Registro automático de la excepción en curso en `__context__` cuando se lanza otra dentro de un `except`. |
| **Encapsulamiento** | Reunir datos y operaciones ocultando los detalles internos y exponiendo una interfaz pública. |
| **Evaluación inmediata (*eager*)** | Los argumentos y cada etapa se calculan completos antes de usarse; el procesamiento de `leer()` es inmediato. |
| **Evaluación perezosa (*lazy*)** | Postergar el cálculo hasta que se necesita (generadores, `map`, `filter`). En el lector solo interviene al recorrer el objeto archivo, que es un iterador (`clase.py:89`); como todas las líneas se acumulan en una lista, el procesamiento global es inmediato. |
| **Fila de datos / línea física** | Numeraciones de §7.4: la primera excluye el encabezado (rango); la segunda cuenta líneas del archivo (mensajes de error). |
| **Función de orden superior** | Función que recibe o devuelve funciones (`cumple_todos_los_filtros`). |
| **Función pura** | Función cuyo resultado depende solo de sus argumentos y que no produce efectos secundarios (las de `funciones.py`; la pureza de `cumple_todos_los_filtros` depende de la de los filtros que recibe, §4). |
| **Gestor de contexto** | Objeto usado con `with` que adquiere y libera un recurso de forma segura (el archivo en `clase.py:87`). |
| **Inferencia de tipos** | Determinación automática del tipo de una columna a partir de sus valores (§6). |
| **Interfaz pública** | Métodos destinados al usuario: `__init__`, `forzar_tipo`, `agregar_filtro`, `establecer_limite`, `establecer_rango`, `seleccionar_columnas`, `leer`. |
| **Invariante** | Propiedad que se mantiene verdadera en un punto del programa (§3.2). Término no usado en los apuntes, que hablan de "mantener la coherencia del objeto". |
| **Namespace package** | Paquete sin `__init__.py`, admitido desde Python 3.3 (PEP 420). |
| **Paquete / módulo / script** | Carpeta de módulos / archivo `.py` con código reutilizable / archivo `.py` con código ejecutable para una tarea. |
| **Precondición / postcondición** | Condición que debe cumplirse al invocar una función / que la función garantiza al terminar. |
| **Propagación** | Ascenso de una excepción no capturada por la pila de llamadas hasta encontrar un `except` compatible. |
| ***Setter*** | Método que valida un valor antes de asignarlo a un atributo protegido (`establecer_limite`, `establecer_rango`, `forzar_tipo`). |
| ***Slicing*** | Extracción de una sublista `lista[inicio:fin]`, con `fin` excluido y sin error ante índices fuera de rango. |
| **Truthiness (valor de verdad)** | Interpretación de cualquier objeto como verdadero o falso en una condición; los filtros se evalúan así. |

