# Cómo funciona el código, explicado en criollo, línea por línea

**TP "Lector de datos tabulares" — Grupo G24 (Berruti, Liali, Vranjes) — Programación 2, Lic. en Ciencia de Datos (UNR)**

> **Para quién es esto:** para cualquiera del grupo que tenga que pararse frente a los docentes y explicar el código, aunque se haya perdido clases. La idea es que leas cada renglón del código y entiendas *qué hace* y *por qué está ahí*.
>
> **Qué tan confiable es:** todo lo que se dice acá sobre el comportamiento del código se comprobó corriendo el código real (Python 3.12, pandas 2.2). Las salidas que aparecen son las que imprime de verdad. Los números de línea son los de los archivos tal cual están en la entrega: `modulo/funciones.py` (133 líneas), `modulo/clase.py` (221 líneas) y `ejemplos.py` (52 líneas).

**Cómo leer este documento**

- `clase.py:105` quiere decir "archivo `clase.py`, línea 105".
- Cada bloque tiene el código copiado tal cual y abajo la explicación en criollo.
- Las líneas en blanco se mencionan agrupadas (no hacen nada, solo separan).
- **Ojo con dos palabras que parecen lo mismo y no lo son:**
  - **"línea del archivo"**: el renglón del CSV contando el encabezado como línea 1. Es lo que usan los **mensajes de error**.
  - **"fila de datos"**: contando desde la primera fila *después* del encabezado. Es lo que usa **`establecer_rango`**.
- Cuando aparece una palabra "de la cátedra" (por ejemplo *atributo protegido*, *función pura*, *cortocircuito*, *context manager*), es para que en la defensa uses el mismo vocabulario que los apuntes.

---

## 0. Índice

1. La película completa en 1 minuto
2. `funciones.py` línea por línea
   - 2.1 `separar_linea` (L1-7)
   - 2.2 `es_booleano` (L10-15)
   - 2.3 `es_entero` y `es_flotante` (L18-33)
   - 2.4 `inferir_tipo_columna` (L36-75)
   - 2.5 `convertir_valor` (L78-117)
   - 2.6 `cumple_todos_los_filtros` (L120-125)
   - 2.7 `recortar_diccionario` (L128-133)
3. `clase.py` línea por línea
   - 3.1 Comentario de criterios (L1-9)
   - 3.2 Imports (L11-17)
   - 3.3 La clase y `__init__` (L20-36)
   - 3.4 Métodos de configuración (L38-63)
   - 3.5 `leer`, el director de orquesta (L65-82)
   - 3.6 `_leer_archivo` (L84-97)
   - 3.7 `_procesar_lineas` (L99-143)
   - 3.8 `_convertir_tipos` (L145-188)
   - 3.9 `_aplicar_filtros_y_rangos` (L190-221)
4. `ejemplos.py` línea por línea (y qué imprime cada ejemplo)
5. Sigamos un dato de punta a punta (el Ejemplo 2, variable por variable)
6. Lo que tenés que tener clarísimo antes de la defensa

---

## 1. La película completa en 1 minuto

### Los personajes

El lector en sí está repartido en dos archivos dentro de la carpeta `modulo/` (que, en el vocabulario de la cátedra, es un **paquete**: una carpeta con varios módulos). Afuera de esa carpeta hay un tercer archivo, `ejemplos.py`, que es el que lo usa:

| Archivo | Qué tiene | Analogía |
|---|---|---|
| `modulo/funciones.py` | 8 funciones chiquitas que hacen **una sola cosa** cada una (cortar una línea, ver si un texto es un número, convertir un valor, etc.). No guardan nada entre una llamada y otra: son **funciones puras**. | Las herramientas de la caja: un destornillador no se acuerda de qué tornillo atornilló antes. |
| `modulo/clase.py` | La clase `LectorCSV`. Guarda la **configuración** (qué delimitador, qué tipos forzar, qué filtros, cuántas filas, qué columnas) y, cuando le pedís `leer(...)`, pasa el archivo por una línea de montaje de 4 estaciones usando las herramientas de `funciones.py`. | El operario que tiene anotado en una libreta lo que le pediste y usa las herramientas en orden. |
| `ejemplos.py` | El **script** de demostración: crea lectores, los configura, lee y muestra el resultado (con `print` y con pandas). | El cliente que hace el pedido. |

### Cómo se usa (siempre en 3 pasos)

```python
lector = LectorCSV(delimitador=",")          # 1) crear el lector (con su configuración básica)
lector.forzar_tipo("codigo", str)           # 2) configurar (opcional, todo lo que quieras)
datos = lector.leer("datos1.csv")           # 3) leer: devuelve una lista de diccionarios
```

### El recorrido de los datos (el dibujito)

Con `datos1.csv` y la configuración del Ejemplo 2 (rango 1 a 5, filtro "cantidad menor a 15", límite 2, columnas nombre y precio):

```text
 datos1.csv  (texto plano en el disco)
 ┌──────────────────────────────────────────────┐
 │codigo, nombre, precio, cantidad, disponible  │
 │001, Cuaderno, 2500.5, 10, true               │
 │...                                           │
 └──────────────────────────────────────────────┘
        │
        │  ESTACIÓN 1: _leer_archivo  (clase.py:84-97)
        │  abre el archivo, lo recorre renglón por renglón y le saca el "enter" del final
        ▼
 lineas = ['codigo, nombre, precio, cantidad, disponible',
           '001, Cuaderno, 2500.5, 10, true', ...]                 ← lista de str (7 renglones)
        │
        │  ESTACIÓN 2: _procesar_lineas  (clase.py:99-143)   usa separar_linea
        │  corta cada renglón por el delimitador, limpia espacios, valida el encabezado
        │  y que todas las filas tengan la misma cantidad de campos
        ▼
 encabezados  = ['codigo', 'nombre', 'precio', 'cantidad', 'disponible']
 filas_crudas = [['001', 'Cuaderno', '2500.5', '10', 'true'], ...]  ← lista de listas de str
        │
        │  ESTACIÓN 3: _convertir_tipos  (clase.py:145-188)   usa inferir_tipo_columna y convertir_valor
        │  decide el tipo de cada columna (o usa el forzado) y convierte cada celda
        ▼
 filas_tipadas = [{'codigo': 1, 'nombre': 'Cuaderno', 'precio': 2500.5,
                   'cantidad': 10, 'disponible': True}, ...]       ← lista de diccionarios con tipos
        │
        │  ESTACIÓN 4: _aplicar_filtros_y_rangos  (clase.py:190-221)
        │  usa cumple_todos_los_filtros y recortar_diccionario, en este orden:
        │    (1) rango  →  (2) filtros  →  (3) límite  →  (4) selección de columnas
        ▼
 resultado = [{'nombre': 'Cuaderno', 'precio': 2500.5},
              {'nombre': 'Carpeta',  'precio': 3200.0}]            ← lo que devuelve leer()
```

En una frase: **texto del archivo → renglones → listas de pedacitos de texto → diccionarios con tipos → filtrado y recorte → resultado**.

### Tres ideas que atraviesan todo el código

1. **Todo empieza siendo texto.** Del archivo solo salen strings. `'2500.5'` recién se convierte en el número `2500.5` en la estación 3.
2. **El tipo se decide por columna entera, no celda por celda.** Si en una columna hay `'10'`, `'20'` y `'30.5'`, la columna entera es `float` (y el `'10'` pasa a `10.0`).
3. **Ante un problema, el lector frena y avisa con una excepción** (`ValueError` casi siempre), con un mensaje que dice qué pasó y en qué fila/columna. El lector **nunca imprime** nada: los `print` están todos en `ejemplos.py`.

---

## 2. `funciones.py` línea por línea

Antes de arrancar, fijate en algo general: **ninguna de estas 8 funciones sabe que existe una clase `LectorCSV`**. Reciben todo lo que necesitan por parámetro y devuelven un resultado (o lanzan una excepción). No imprimen, no leen archivos, no tocan variables de afuera. Eso es lo que la cátedra llama **función pura**: con las mismas entradas, siempre la misma salida. Por eso se pueden probar sueltas en la consola, por ejemplo `es_entero("001")`, sin armar ningún lector.

### 2.1 `separar_linea` — cortar un renglón en campos

#### Líneas 1-2

```python
def separar_linea(linea, delimitador):
    """Corta un renglon por el delimitador y quita los espacios sobrantes"""
```

- `def` define una función llamada `separar_linea` que recibe dos cosas:
  - `linea`: un string con **un renglón** del archivo (ya sin el "enter" del final, eso lo saca `clase.py:90`).
  - `delimitador`: el string que separa los campos, por ejemplo `","`, `";"` o `"\t"`.
- La línea 2 es el **docstring**: un texto entre comillas triples justo debajo del `def` que documenta qué hace la función. No ejecuta nada; lo ves si hacés `help(separar_linea)`.

#### Línea 3

```python
    partes = linea.split(delimitador)
```

`split` corta el string cada vez que encuentra el delimitador y devuelve una **lista** con los pedazos. O sea:

```python
"001, Cuaderno, 2500.5".split(",")   # → ['001', ' Cuaderno', ' 2500.5']
```

Fijate en el espacio adelante de `' Cuaderno'` y `' 2500.5'`: es el espacio que hay después de cada coma en `datos1.csv`. `split` no lo saca: corta y listo. De eso se encarga la línea 6.

- **Dato a favor:** `split` acepta delimitadores de **más de un carácter** (`"||"`, `" | "`), así que el lector soporta un delimitador arbitrario, incluso de varios caracteres, sin usar expresiones regulares. Ojo con cómo lo decís: la consigna **valora** explícitamente aceptar otros separadores (punto y coma, tab); el delimitador arbitrario de más de un carácter lo propone como **ampliación opcional**.
- **Ojo con esto:** si el renglón termina con el delimitador, por ejemplo `"a,b,"`, el último pedazo es un string vacío `''`. Eso después se va a convertir en un campo vacío (o en un error de "nombre vacío" si es el encabezado).

#### Línea 4

```python
    campos_limpios = []
```

Una lista vacía donde vamos a ir guardando los campos ya limpios. Es el patrón de la U1: **lista vacía + `for` + `append`**.

#### Líneas 5-6

```python
    for elemento in partes:
        campos_limpios.append(elemento.strip())
```

Recorre cada pedazo y le aplica `strip()`, que saca los espacios (y tabs y otros "blancos") **de los bordes**, no del medio. Después lo agrega al final de `campos_limpios` con `append`.

```python
" Cuaderno".strip()        # → 'Cuaderno'
"  Buenos Aires ".strip()  # → 'Buenos Aires'   (el espacio del medio queda, por suerte)
```

#### Línea 7

```python
    return campos_limpios
```

Devuelve la lista limpia. Ejemplos reales:

```python
separar_linea("001, Cuaderno, 2500.5", ",")        # → ['001', 'Cuaderno', '2500.5']
separar_linea("004, Regla, 500, , false", ",")     # → ['004', 'Regla', '500', '', 'false']
separar_linea("103; Buenos Aires; 5100; true", ";")# → ['103', 'Buenos Aires', '5100', 'true']
```

En el segundo, mirá la celda de cantidad de la Regla: queda como `''` (string vacío). Más adelante (`funciones.py:81-82`) ese `''` se va a convertir en `None`.

> **Para la defensa:**
> - Es una función pura: el `append` modifica una lista **local** (creada adentro), así que no es un efecto secundario.
> - Versión más corta con lo de la U3: `[e.strip() for e in linea.split(delimitador)]` (da exactamente lo mismo).
> - **Limitación:** no entiende comillas. `"Rosario, SF",2` se corta en tres pedazos y después da error de cantidad de campos.

#### Líneas 8-9

En blanco. Dos líneas vacías entre funciones es pura convención de estilo; no hacen nada.

---

### 2.2 `es_booleano` — ¿este texto es "true" o "false"?

#### Líneas 10-11

```python
def es_booleano(texto):
    """Devuelve True si el texto es true o false"""
```

Recibe un string y responde `True` o `False`. Ojo con la pregunta que contesta: **"¿este texto representa un booleano?"**, no "¿es verdadero?". Por eso `es_booleano("false")` da `True`: `"false"` *es* un booleano válido.

#### Línea 12

```python
    texto_min = texto.lower()
```

Pasa el texto a minúsculas. ¿Por qué? Porque comparar strings distingue mayúsculas: `"TRUE" == "true"` da `False`. Pasando todo a minúsculas, `"TRUE"`, `"True"` y `"true"` quedan iguales (`"TrUe".lower()` → `'true'`). Esto es importante porque Excel exporta `TRUE`/`FALSE` en mayúsculas.

#### Líneas 13-15

```python
    if texto_min in ["true", "false"]:
        return True
    return False
```

- `in` pregunta si el valor está en la lista.
- Si está, `return True` y la función **termina ahí** (un `return` corta la ejecución).
- Si no está, no entra al `if`, sigue de largo y llega a `return False`. Por eso no hace falta `else`.

```python
es_booleano("TRUE")   # → True
es_booleano("False")  # → True
es_booleano("si")     # → False
es_booleano("1")      # → False   ← "1" y "0" NO son booleanos para el lector
```

> **Para la defensa:**
> - **Qué se reconoce como booleano:** solo `true` y `false`, sin importar mayúsculas. `VERDADERO/FALSO` (Excel en castellano), `si/no`, `yes/no`, `1/0` **no**. Es una decisión documentada (comentario de `clase.py:5-6`).
> - Mejora chiquita: `["true", "false"]` es una colección fija, y la cátedra recomienda **tupla** para eso: `("true", "false")`. Funciona igual; es estilo.
> - Versión de una línea: `return texto.lower() in ("true", "false")`.

#### Líneas 16-17

En blanco.

---

### 2.3 `es_entero` y `es_flotante` — "probá, y si explota, atajalo"

#### Líneas 18-19

```python
def es_entero(texto):
    """Devuelve True si el texto puede convertirse a entero"""
```

Responde si el texto se puede convertir a `int`.

#### Líneas 20-24

```python
    try:
        int(texto)
        return True
    except ValueError:
        return False
```

Esto es como probarte un pantalón en el probador: lo intentás, y si no entra, no pasa nada grave.

- `try:` → "intentá esto".
- `int(texto)` intenta convertir. Fijate que **el resultado no se guarda en ninguna variable**: no nos importa el número, solo saber si se pudo.
- Si se pudo, sigue a `return True`.
- Si `int` no puede, lanza un `ValueError`; el `except ValueError:` lo **ataja** y devuelve `False`.

```python
es_entero("001")     # → True   (int("001") da 1)
es_entero("-5")      # → True
es_entero("2500.5")  # → False  (int no acepta el punto decimal)
es_entero("veinte")  # → False
es_entero("1_000")   # → True   (curiosidad: int acepta guiones bajos)
```

> **Para la defensa:**
> - **¿Por qué no `isdigit()`?** Porque `"-5".isdigit()` da `False`, y `-5` es un entero. Dejamos que `int()` sea el que decide qué es un entero válido.
> - Se ataja **solo** `ValueError`, la excepción específica que esperamos. No hay `except:` "a lo bruto", que la cátedra marca como algo a evitar.
> - En la inferencia, que un valor "no sea entero" **no es un error**: es una respuesta normal (se prueba el siguiente tipo). Por eso se traduce la excepción a `False` en vez de dejarla propagar.

#### Líneas 25-26

En blanco.

#### Líneas 27-33

```python
def es_flotante(texto):
    """Devuelve True si el texto puede convertirse a flotante"""
    try:
        float(texto)
        return True
    except ValueError:
        return False
```

Idéntica a `es_entero`, pero probando con `float`.

```python
es_flotante("2500.5")  # → True
es_flotante("800")     # → True   ← todo entero también es un float válido
es_flotante("1,5")     # → False  ← coma decimal: NO se reconoce
es_flotante("1e3")     # → True   (notación científica = 1000.0)
es_flotante("nan")     # → True   (float acepta "nan" e "inf")
```

> **Ojo con esto:** la **coma decimal** (`1500,50`, típico de Excel en castellano) no se reconoce como número. Además, como el delimitador por defecto es la coma, `1500,50` se partiría en dos campos.

#### Líneas 34-35

En blanco.

### 2.4 `inferir_tipo_columna` — decidir el tipo de una columna entera

Esta es una de las funciones más importantes. La idea es la de un control de admisión: a la columna le preguntamos "¿todos tus valores son booleanos?"; si sí, es `bool`. Si no, "¿todos son enteros?"; si sí, es `int`. Si no, "¿todos son float?". Y si tampoco, queda como `str`, que es el tipo que acepta cualquier cosa.

#### Líneas 36-37

```python
def inferir_tipo_columna(valores_columna):
    """Deduce el tipo de dato de una columna probando en orden: bool, int, float y str."""
```

- Recibe `valores_columna`: una lista con **todos los valores de UNA columna**, como strings ya limpios. Por ejemplo, la columna cantidad de `datos1.csv`: `['10', '25', '8', '', '3', '50']`.
- **Devuelve una clase** (`bool`, `int`, `float` o `str`), no el texto `"int"`. En Python los tipos son clases y las clases también son objetos, así que se pueden devolver, guardar en un diccionario y comparar.

#### Líneas 38-41

```python
    no_vacios = []
    for valor in valores_columna:
        if valor != "":
            no_vacios.append(valor)
```

Arma una lista nueva **sin las celdas vacías**. ¿Por qué? Porque una celda vacía es un nulo (después va a ser `None`) y no tiene que "votar" el tipo de la columna. Si no las sacáramos, el `''` haría fallar todas las pruebas y la columna cantidad quedaría `str` por culpa de la Regla.

```python
# columna cantidad de datos1.csv
['10', '25', '8', '', '3', '50']   →   no_vacios = ['10', '25', '8', '3', '50']
```

#### Línea 42

En blanco.

#### Líneas 43-45

```python
    # Si todas las celdas están vacías, la columna queda como str
    if len(no_vacios) == 0:
        return str
```

Si la columna está **toda vacía**, devuelve `str` (y después todos sus valores serán `None`).

**Ojo con esto, porque es fino:** esta guarda no es decorativa, es imprescindible. Mirá la línea 48: la bandera `todos_bool` arranca en `True`. Si la lista está vacía, el `for` no da ninguna vuelta, nadie baja la bandera, y la función diría que la columna es `bool`. Es lo mismo que pasa con `all([])`, que da `True`: "todos los elementos de un conjunto vacío cumplen" es verdadero. La guarda evita esa trampa.

```python
inferir_tipo_columna(['', ''])  # → <class 'str'>
inferir_tipo_columna([])        # → <class 'str'>
```

#### Línea 46

En blanco.

#### Líneas 47-54

```python
    # 1. Probamos si todos son booleanos
    todos_bool = True
    for valor in no_vacios:
        if not es_booleano(valor):
            todos_bool = False
            break
    if todos_bool:
        return bool
```

El patrón **bandera + `break`**:

1. `todos_bool = True`: "suponemos que sí, hasta que alguien demuestre lo contrario".
2. Recorremos los valores. Si **uno solo** no es booleano (`not es_booleano(valor)`), bajamos la bandera y cortamos con `break`. No tiene sentido seguir mirando: con un solo valor que no encaja, la columna ya no puede ser `bool`.
3. Si terminamos y la bandera sigue en `True`, la columna es `bool` y la función termina con `return bool`.

```python
inferir_tipo_columna(['true', 'true', 'true', 'false', 'true', 'true'])  # → bool  (columna disponible)
inferir_tipo_columna(['TRUE', 'False', ''])                             # → bool
```

En la columna precio (`'2500.5'` es el primer valor), el bucle da **una sola vuelta**: `'2500.5'` no es booleano → bandera abajo → `break`.

#### Línea 55

En blanco.

#### Líneas 56-63

```python
    # 2. Probamos si todos son enteros
    todos_int = True
    for valor in no_vacios:
        if not es_entero(valor):
            todos_int = False
            break
    if todos_int:
        return int
```

Mismo patrón, ahora con `es_entero`.

```python
inferir_tipo_columna(['10', '25', '8', '', '3', '50'])  # → int   (columna cantidad)
inferir_tipo_columna(['001', '002'])                   # → int   (por eso hay que forzar str en codigo)
inferir_tipo_columna(['1', '0'])                       # → int   (no bool: '1' no es 'true')
```

#### Línea 64

En blanco.

#### Líneas 65-72

```python
    # 3. Probamos si todos son flotantes (incluye mezcla de int y float)
    todos_float = True
    for valor in no_vacios:
        if not es_flotante(valor):
            todos_float = False
            break
    if todos_float:
        return float
```

Mismo patrón con `es_flotante`. El comentario lo dice: acá caen las columnas que **mezclan** enteros y decimales, porque `float('10')` funciona.

```python
inferir_tipo_columna(['10', '20', '30.5'])  # → float   (el ejemplo exacto de la consigna)
# columna precio de datos1.csv: ['2500.5', '800', '3200.0', '500', '15000.0', '300.5'] → float
```

Con precio pasa esto: la prueba de `bool` corta en `'2500.5'`, la de `int` también corta en `'2500.5'`, y la de `float` recorre los 6 valores y aprueba. Resultado: `float`, y por eso `'800'` termina siendo `800.0`.

#### Línea 73

En blanco.

#### Líneas 74-75

```python
    # 4. Si hay mezcla de números y texto, queda como str
    return str
```

Si no pasó ninguna prueba, la columna es texto. `str` es el "tipo comodín": cualquier cosa se puede guardar como texto.

```python
inferir_tipo_columna(['10', 'veinte', '8'])  # → str
inferir_tipo_columna(['10', 'NA'])           # → str   ← un solo 'NA' arrastra a toda la columna
inferir_tipo_columna(['Cuaderno', 'Lapicera'])  # → str
```

#### Resumen de la inferencia en una tabla

| Valores de la columna | Resultado | Por qué |
|---|---|---|
| `['true', 'false', '']` | `bool` | todos los no vacíos son true/false |
| `['10', '25', '', '3']` | `int` | el vacío no vota; el resto son enteros |
| `['1', '0']` | `int` | `'1'` no es `'true'`, así que no es bool |
| `['10', '20', '30.5']` | `float` | `'30.5'` no es int, pero todos son float |
| `['10', 'veinte', '8']` | `str` | hay texto mezclado |
| `['10', 'NA']` | `str` | `'NA'` no es un nulo para el lector, es texto |
| `['', '']` o `[]` | `str` | columna toda vacía (guarda de L44-45) |

> **Para la defensa — ¿por qué el orden bool → int → float → str?**
> Va **del más exigente al más permisivo**. `int` tiene que ir antes que `float` porque todo entero se puede leer como float, pero no al revés: `float("10")` funciona y `int("10.0")` falla. Si probáramos `float` primero, **todas** las columnas de enteros quedarían como float. Y `str` va al final porque acepta todo.
>
> **Otras cosas que te pueden preguntar:**
> - Los tres bucles con bandera son "`all` escrito a mano": `all(es_entero(v) for v in no_vacios)` haría lo mismo.
> - En el peor caso la función recorre la columna 4 veces (no_vacios, bool, int, float), pero eso es una constante: sigue siendo O(N). Y en general corta antes por el `break`.
> - La variable `valor` se reutiliza en los cuatro `for`. No es un bug porque son bucles uno detrás del otro y ninguno usa lo que dejó el anterior. Lo que dicen los apuntes (U1, ejecución repetitiva) es que la variable de iteración **pisa** cualquier valor que ya tuviera ese nombre, y por eso recomiendan no usar para iterar el nombre de otra variable del programa. Acá esa pisada es inofensiva; si te lo marcan, nombres distintos lo dejarían más prolijo.

#### Líneas 76-77

En blanco.

---

### 2.5 `convertir_valor` — de texto al tipo que corresponde

Ya sabemos el tipo de la columna. Ahora hay que convertir **cada celda**, de a una. Esta función recibe una celda (texto) y el tipo que le toca, y devuelve el valor convertido, o lanza un error con fila y columna si no se puede.

#### Líneas 78-80

```python
def convertir_valor(texto, tipo_esperado, num_fila, nombre_col):
    """Convierte el texto al tipo de dato que corresponde. Si está vacía devuelve None,
     y si falla la conversión, avisa con un error indicando la fila y la columna."""
```

Cuatro parámetros:

| Parámetro | Qué es | Ejemplo |
|---|---|---|
| `texto` | el contenido de la celda, ya limpio | `'2500.5'` |
| `tipo_esperado` | la clase a la que hay que convertir | `float` |
| `num_fila` | número de **línea del archivo** (solo para el mensaje de error) | `2` |
| `nombre_col` | nombre de la columna (solo para el mensaje de error) | `'precio'` |

Fijate que `num_fila` y `nombre_col` **no se usan para convertir**: solo están para armar un mensaje de error útil. La consigna exige que el error diga en qué fila y columna está el problema, y como la función es pura (no sabe nada del archivo), hay que pasárselos.

#### Líneas 81-82

```python
    if texto == "":
        return None
```

**Celda vacía → `None`, siempre**, antes de mirar el tipo. Incluso si la columna es `str`.

```python
convertir_valor("", int, 5, "cantidad")  # → None   (la cantidad de la Regla)
convertir_valor("", str, 5, "nombre")    # → None   (no '')
```

¿Por qué `None` y no `0` o `""`? Porque para la cátedra `None` representa **ausencia de valor**, y `0` o `""` son valores concretos. Una cantidad vacía no es "cero unidades", es "no sabemos". Como el texto ya viene con `strip()`, una celda que tenía solo espacios también llega como `''` y queda `None`.

#### Línea 83

En blanco.

#### Líneas 84-85

```python
    if tipo_esperado == str:
        return texto
```

Si la columna es de texto, no hay nada que convertir: el valor ya es un string. **Así es como `forzar_tipo("codigo", str)` conserva los ceros de `'001'`**: el texto pasa tal cual.

```python
convertir_valor("001", str, 2, "codigo")  # → '001'
```

#### Línea 86

En blanco.

#### Líneas 87-97

```python
    if tipo_esperado == bool:
        texto_min = texto.lower()
        if texto_min == "true":
            return True
        elif texto_min == "false":
            return False
        else:
            raise ValueError(
                f"Error en fila {num_fila}, columna '{nombre_col}': "
                f"el valor '{texto}' no se puede convertir a bool."
            )
```

Rama para booleanos. **¿Por qué no hacer simplemente `bool(texto)`?** Porque en Python cualquier string que no esté vacío es "verdadero": `bool("false")` da `True`. Sería un desastre. Entonces se compara a mano:

- pasa a minúsculas (L88),
- si es `"true"` → `True` (L89-90),
- si es `"false"` → `False` (L91-92),
- si es otra cosa → lanza `ValueError` (L93-97). Acá hay tres salidas posibles, por eso se usa `if / elif / else`.

```python
convertir_valor("TRUE", bool, 2, "disponible")  # → True
convertir_valor("si", bool, 2, "disponible")
# ValueError: Error en fila 2, columna 'disponible': el valor 'si' no se puede convertir a bool.
```

**Sobre el mensaje (L95-96):** son dos **f-strings** (strings con `f` adelante, donde lo que va entre llaves se reemplaza por el valor de la variable) escritos uno abajo del otro dentro del paréntesis. Python **los pega solos** en un único string. Es solo para que la línea no quede larguísima.

#### Línea 98

En blanco.

#### Líneas 99-106

```python
    if tipo_esperado == int:
        try:
            return int(texto)
        except ValueError:
            raise ValueError(
                f"Error en fila {num_fila}, columna '{nombre_col}': "
                f"el valor '{texto}' no se puede convertir a int."
            )
```

Rama para enteros: intenta `int(texto)`; si funciona, lo devuelve. Si `int` lanza su `ValueError` (con un mensaje en inglés poco claro), lo atajamos y lanzamos **otro** `ValueError` con nuestro mensaje en castellano, con fila, columna y valor.

```python
convertir_valor("10", int, 2, "cantidad")      # → 10
convertir_valor("veinte", int, 3, "cantidad")
# ValueError: Error en fila 3, columna 'cantidad': el valor 'veinte' no se puede convertir a int.
convertir_valor("10.0", int, 3, "cantidad")
# ValueError: ... el valor '10.0' no se puede convertir a int.   ← int no acepta decimales
```

> **Detalle técnico que pueden preguntar (encadenamiento de excepciones):** como el `raise` nuevo está **adentro** del `except`, si nadie lo captura, el traceback muestra los dos errores unidos por *"During handling of the above exception, another exception occurred"*. Es encadenamiento **implícito**. La cátedra muestra dos alternativas: `raise ValueError(...) from error` (deja explícito que el original fue la causa) o `raise ValueError(...) from None` (oculta el original). En `ejemplos.py` no se nota porque se captura y se imprime solo nuestro mensaje.

#### Línea 107

En blanco.

#### Líneas 108-115

```python
    if tipo_esperado == float:
        try:
            return float(texto)
        except ValueError:
            raise ValueError(
                f"Error en fila {num_fila}, columna '{nombre_col}': "
                f"el valor '{texto}' no se puede convertir a float."
            )
```

Igual que la de `int`, con `float`.

```python
convertir_valor("800", float, 3, "precio")  # → 800.0
convertir_valor("abc", float, 3, "precio")
# ValueError: Error en fila 3, columna 'precio': el valor 'abc' no se puede convertir a float.
```

#### Línea 116

En blanco.

#### Línea 117

```python
    raise ValueError(f"Tipo de dato no soportado: {tipo_esperado}")
```

**Red de seguridad.** Si llegamos acá es porque el tipo no era ninguno de los cuatro. En el uso normal **nunca pasa**: `forzar_tipo` ya rechaza otros tipos (`clase.py:40-41`) y la inferencia solo devuelve esos cuatro. Pero si alguien llama a la función a mano con otra cosa, en vez de devolver `None` en silencio, avisa:

```python
convertir_valor("x", list, 3, "col")
# ValueError: Tipo de dato no soportado: <class 'list'>
```

#### Cosas para entender de `convertir_valor` como un todo

- **Son `if` sueltos, no `elif`, y funciona igual.** Cada rama termina en `return` o `raise`, así que si entraste a una, no seguís a la siguiente. Este estilo se llama "cláusulas de guarda": primero los casos especiales (vacío, str) y después el resto, sin anidar.
- **Ojo con esto, que es clave:** si el tipo de la columna fue **inferido**, la conversión **nunca falla**, porque la inferencia ya probó todos los valores con las mismas funciones (`int()`, `float()`, `true/false`). Los errores de conversión aparecen **solo cuando el tipo fue forzado** con `forzar_tipo`. Por eso en el Ejemplo 4 hay error (cantidad forzada a `int` con un `'veinte'`), pero si no se forzara, la columna se inferiría `str` y no habría error.
- La consigna dice que si un valor no se puede convertir al tipo pedido **no se puede reemplazar el tipo por otro**. El código cumple: no "cae" a `str`, lanza un error.
- **¿Por qué no `return tipo_esperado(texto)` para todo?** Funcionaría para `int`, `float` y `str`, pero no para `bool` (`bool("false")` es `True`). Para `int` y `float` se podría unificar usando `tipo_esperado.__name__` en el mensaje; hoy esas dos ramas repiten el mismo patrón.

#### Líneas 118-119

En blanco.

### 2.6 `cumple_todos_los_filtros` — el patovica de la puerta

Pensalo como el patovica de un boliche con una lista de condiciones: si fallás **una**, no entrás. Y apenas fallás una, ni siquiera mira las demás.

#### Líneas 120-121

```python
def cumple_todos_los_filtros(fila_diccionario, lista_funciones_filtro):
    """Evalua las funciones de filtro y devuelve True si la fila cumple todas"""
```

Recibe:
- `fila_diccionario`: **una fila** ya convertida, por ejemplo `{'codigo': 4, 'nombre': 'Regla', 'precio': 500.0, 'cantidad': None, 'disponible': False}`.
- `lista_funciones_filtro`: una **lista de funciones** (los filtros que el usuario agregó con `agregar_filtro`).

Que una función reciba otras funciones como argumento es lo que la cátedra llama **función de orden superior**. Y que podamos guardar funciones en una lista es porque en Python las funciones son **ciudadanos de primera clase**: objetos como cualquier otro.

#### Líneas 122-124

```python
    for funcion in lista_funciones_filtro:
        if not funcion(fila_diccionario):
            return False
```

- Recorre los filtros de a uno.
- `funcion(fila_diccionario)` **llama** al filtro pasándole la fila. El filtro devuelve `True` (la fila se queda) o `False` (la fila se va).
- Si el resultado es falso (`not ...`), devuelve `False` **inmediatamente**: los filtros que quedaban ni se llaman. Es una "salida temprana", igual que el cortocircuito de un `and`.

#### Línea 125

```python
    return True
```

Si la fila sobrevivió a todos los filtros, pasa. Ejemplos con la fila de la Regla de arriba:

```python
f1 = lambda f: f["precio"] > 100
f2 = lambda f: f["cantidad"] is not None

cumple_todos_los_filtros(fila_regla, [])        # → True   (sin filtros, pasan todas)
cumple_todos_los_filtros(fila_regla, [f1])      # → True   (500.0 > 100)
cumple_todos_los_filtros(fila_regla, [f1, f2])  # → False  (cantidad es None)
```

> **Para la defensa:**
> - **Varios filtros = AND.** La fila tiene que cumplir todos.
> - **Lista vacía → `True`**: si el usuario no puso filtros, no se descarta nada. Es lo mismo que da `all([])`.
> - Equivale a `return all(f(fila_diccionario) for f in lista_funciones_filtro)`, incluso en lo de cortar en el primer `False`. Se escribió con `for` porque es el estilo de la U1.
> - **Duck typing:** no se chequea qué es `funcion`; solo se la llama. Sirve una `lambda`, una función con `def` o un objeto con `__call__`. Si alguien agrega algo que no se puede llamar (por ejemplo `5`), recién explota acá con `TypeError: 'int' object is not callable`.
> - **"Truthiness":** como dice `if not funcion(...)`, se usa el valor de verdad de lo que devuelva el filtro. **Ojo:** un filtro escrito con `def` que se olvida el `return` devuelve `None`, que cuenta como falso, y descarta **todas** las filas sin ningún error.
> - **Ojo 2:** el filtro recibe el diccionario **real**, no una copia. Si un filtro hiciera `fila["precio"] = 0`, cambiaría el resultado. Por eso los filtros deberían ser funciones puras.

#### Líneas 126-127

En blanco.

---

### 2.7 `recortar_diccionario` — quedarse solo con las columnas pedidas

#### Líneas 128-129

```python
def recortar_diccionario(fila_diccionario, columnas_elegidas):
    """Arma un nuevo diccionario solp con las columnas seleccionadas"""
```

Recibe una fila completa y la lista de columnas que pidió el usuario. (El "solp" del docstring es un typo de "solo"; si lo ven, reconocelo y listo.)

#### Línea 130

```python
    nuevo_diccionario = {}
```

Un diccionario **nuevo**, vacío. No se toca el original.

#### Líneas 131-132

```python
    for col in columnas_elegidas:
        nuevo_diccionario[col] = fila_diccionario[col]
```

Para cada columna pedida, copia el par `columna: valor` al diccionario nuevo. Asignar a una clave que no existe la **agrega**.

#### Línea 133

```python
    return nuevo_diccionario
```

```python
fila = {"codigo": 1, "nombre": "Cuaderno", "precio": 2500.5}
recortar_diccionario(fila, ["precio", "nombre"])   # → {'precio': 2500.5, 'nombre': 'Cuaderno'}
```

Fijate que el resultado sale **en el orden que pidió el usuario** (`precio` antes que `nombre`), no en el del archivo. Eso pasa porque los diccionarios de Python (desde la 3.7) recuerdan el orden en que se insertaron las claves.

> **Para la defensa:**
> - Si una columna no existiera, `fila_diccionario[col]` daría `KeyError`. **Pero eso no puede pasar**, porque `clase.py:192-195` valida antes que todas las columnas pedidas existan, y si no, lanza un `ValueError` con un mensaje claro.
> - Versión con *dict comprehension* (U3): `{col: fila_diccionario[col] for col in columnas_elegidas}`.

---

## 3. `clase.py` línea por línea

Acá vive `LectorCSV`. Tené en mente la analogía de la cátedra: la **clase es el molde** y cada **objeto** (o **instancia**) es un budín hecho con ese molde. En `ejemplos.py` se hacen cuatro "budines" distintos (`lector1`, `lector2`, `lector3`, `lector_error`), cada uno con su propia configuración.

### 3.1 El comentario de criterios (líneas 1-9)

#### Línea 1

```python
# Criterios definidos por el grupo:
```

Todo lo que empieza con `#` es un **comentario**: Python lo ignora. Este bloque es la **documentación de las decisiones** que pide la consigna (qué pasa con los encabezados, cómo se infieren los tipos, cómo se combinan las opciones).

#### Líneas 2-3

```python
# - Encabezados: se usa la primera fila por defecto. Si hay nombres de columnas vacíos
#   o repetidos se detiene la lectura con ValueError. Si encabezado=False, se nombran col_0, col_1...
```

Criterio de **encabezados**:
- Por defecto, la primera línea son los nombres de las columnas.
- Nombre vacío o repetido → error (`ValueError`) y se corta la lectura. Lo hacen `clase.py:113-116`.
- Si el archivo no tiene encabezado, se crea el lector con `encabezado=False` y las columnas se llaman `col_0`, `col_1`, ... (lo hace `clase.py:120-121`). **Ojo:** arrancan en 0.

#### Líneas 4-6

```python
# - Tipos de datos: orden de inferencia bool -> int -> float -> str. Celdas vacías se guardan
#   como None (si toda una columna está vacía queda como tipo str). Se reconoce 'true' y 'false'
#   como booleanos. Los tipos indicados con forzar_tipo() tienen prioridad.
```

Criterio de **tipos**, que es exactamente lo que implementan `inferir_tipo_columna` y `convertir_valor`:
- orden bool → int → float → str (`funciones.py:47-75`),
- vacío → `None` (`funciones.py:81-82`),
- columna toda vacía → `str` (`funciones.py:44-45`),
- booleanos: solo `'true'` y `'false'` (sin importar mayúsculas),
- lo que fuerza el usuario gana sobre la inferencia (`clase.py:158-159`).

#### Líneas 7-9

```python
# - Combinación de opciones: 1) Rango de filas (numeradas desde 1, incluye inicio y fin),
#   2) Filtros, 3) Límite de cantidad de filas y 4) Selección de columnas al final (permite
#   filtrar por columnas que no se incluyen en el resultado).
```

Criterio de **combinación de opciones**, que es lo que la consigna pide documentar explícitamente:
1. primero el **rango** (filas de datos numeradas desde 1, con los dos extremos incluidos),
2. después los **filtros**,
3. después el **límite** (que cuenta filas que *pasaron* el filtro),
4. al final la **selección de columnas**, para que se pueda filtrar por una columna que no vas a devolver.

> **Para la defensa:** `help(LectorCSV)` **no muestra** este bloque, porque los comentarios con `#` no son docstrings (y la clase no tiene docstring propio: `LectorCSV.__doc__` es `None`). Mejora obvia: pasar este texto a un docstring de la clase.

#### Línea 10

En blanco.

---

### 3.2 Los imports (líneas 11-17)

```python
from modulo.funciones import (
    separar_linea,
    inferir_tipo_columna,
    convertir_valor,
    cumple_todos_los_filtros,
    recortar_diccionario
)
```

- Trae **5 funciones puntuales** del módulo `funciones.py`, que está adentro de la carpeta (paquete) `modulo`. Los paréntesis permiten escribir la lista en varias líneas.
- **No usa `import *`**, que la cátedra desaconseja (no sabés qué nombres entran ni con cuáles chocan).
- **¿Por qué no importa `es_booleano`, `es_entero` ni `es_flotante`?** Porque la clase no las usa directamente: las usa `inferir_tipo_columna`, adentro de `funciones.py`.
- Es un import **absoluto** (`modulo.funciones`), así que funciona cuando el programa se ejecuta desde la carpeta del proyecto (la que contiene a `modulo/`). Por eso:
  - `python ejemplos.py` parado en la carpeta del proyecto → funciona.
  - `python modulo/clase.py` → `ModuleNotFoundError: No module named 'modulo'` (igual no tendría sentido: `clase.py` es un módulo, solo tiene definiciones, no es un script).
- **No hay `__init__.py` en `modulo/`** y aun así funciona: desde Python 3.3, una carpeta sin `__init__.py` se puede importar igual (se llama *namespace package*). Los apuntes no hablan de `__init__.py`.

#### Líneas 18-19

En blanco.

---

### 3.3 La clase y el método de inicialización (líneas 20-36)

#### Línea 20

```python
class LectorCSV:
```

Define la clase (el molde). No hereda explícitamente de nadie, así que hereda implícitamente de `object`, como toda clase en Python 3. No hay herencia ni jerarquías en el TP: hay un único tipo de lector y las variantes (coma, punto y coma, tab) son **datos** (el delimitador), no comportamientos distintos.

#### Línea 21

```python
    def __init__(self, delimitador=",", encabezado=True):
```

`__init__` es el **método de inicialización**: Python lo ejecuta automáticamente cada vez que creás un objeto con `LectorCSV(...)`. Ojo con el detalle de la cátedra: `__init__` **no crea** el objeto (eso lo hace Python antes); lo **inicializa**, o sea, le carga el estado inicial.

- `self` es **el objeto que se está inicializando**. Nunca se pasa a mano: cuando escribís `LectorCSV(delimitador=";")`, Python pone `self` solo.
- `delimitador=","` y `encabezado=True` son **argumentos con valor por defecto**: si no los pasás, valen eso. Por eso `LectorCSV()` sin nada ya sirve para el caso más común (CSV con coma y con encabezado).

#### Líneas 22-26

```python
        """
        Guarda configuracion predeterminada del lector
        - delimitador: caracter que separa los valores en el archivo
        - encabezado: si la primera fila es el encabezado o no
        """
```

Docstring de `__init__`, con una mini lista de los parámetros. (Dice "caracter", pero el delimitador puede ser de varios caracteres: `" | "` funciona.)

#### Líneas 27-28

```python
        if delimitador == "":
            raise ValueError("El delimitador no puede ser vacío.")
```

**Validación temprana.** Si alguien pide un delimitador vacío, frenamos acá, al crear el lector, con un mensaje claro. ¿Por qué es necesario? Porque más adelante `split("")` explotaría con un mensaje críptico de Python (`ValueError: empty separator`). Mejor "fallar temprano y claro".

```python
LectorCSV(delimitador="")   # ValueError: El delimitador no puede ser vacío.
```

Como el error ocurre durante la inicialización, la variable nunca llega a recibir el objeto: nadie se queda con un lector inválido.

#### Línea 29

En blanco.

#### Líneas 30-31

```python
        self.delimitador = delimitador
        self.encabezado = encabezado
```

Guarda los dos parámetros como **atributos de instancia** (variables que pertenecen a ese objeto: cada lector tiene los suyos). Estos dos **no** llevan guion bajo: son **públicos**.

> **Ojo con esto (inconsistencia que te pueden marcar):** como `delimitador` es público, alguien puede hacer después `lector.delimitador = ""` y saltearse la validación de L27-28. En ese caso `leer()` falla con el `ValueError: empty separator` de Python, no con el mensaje del grupo. La solución "de la cátedra" sería una `@property` con setter que valide.

#### Líneas 32-36

```python
        self._tipos_columnas = {}       # Diccionario para {columna: tipo}
        self._filtros = []              # Lista de funciones para filtrar
        self._limite_filas = None       # Cantidad máxima de filas a leer
        self._rango_filas = None        # Tupla (inicio, fin) para rango de filas
        self._columnas = None           # Lista de columnas a conservar
```

Los otros cinco atributos, todos con **un guion bajo adelante**. En la terminología de la cátedra son **atributos protegidos**: por convención, "esto es interno, no lo toques desde afuera". (Python no lo impide; es un acuerdo entre programadores.)

| Atributo | Valor inicial | Qué va a guardar |
|---|---|---|
| `_tipos_columnas` | `{}` | diccionario `{nombre_columna: clase}`, por ejemplo `{'codigo': str}` |
| `_filtros` | `[]` | lista de funciones filtro |
| `_limite_filas` | `None` | un entero (cuántas filas como máximo) |
| `_rango_filas` | `None` | una tupla `(inicio, fin)` |
| `_columnas` | `None` | lista de nombres de columnas a devolver |

¿Por qué inicializar todo acá, aunque esté vacío?

- Es la recomendación de la cátedra sobre **atributos opcionales**: definirlos en `__init__` con un valor por defecto (en general `None`), así **todos los lectores tienen siempre los mismos atributos** y no hay `AttributeError` por preguntar algo que no existe.
- `None` significa **"no configurado"**. Eso permite distinguir "sin límite" (`None`) de "límite 0" (que es válido y devuelve `[]`). Más adelante se pregunta con `is not None` (L192, 198, 207, 214).
- Las colecciones mutables (`{}` y `[]`) se crean **adentro** del cuerpo y no como valor por defecto de un parámetro: así cada lector tiene su propia lista y su propio diccionario.

Recién creado, un lector se ve así por dentro (`vars(LectorCSV())`):

```python
{'delimitador': ',', 'encabezado': True, '_tipos_columnas': {}, '_filtros': [],
 '_limite_filas': None, '_rango_filas': None, '_columnas': None}
```

> **Para la defensa — ¿qué es el "estado" del lector?** Solo la **configuración**. Los datos leídos **no** se guardan como atributo: `leer()` los devuelve. Por eso el mismo lector puede leer varios archivos, y dos lectores no se pisan entre sí.

#### Línea 37

En blanco.

### 3.4 Los métodos de configuración (líneas 38-63)

Estos cinco métodos son la "libreta de pedidos": **no leen nada**, solo anotan en los atributos protegidos lo que querés que pase cuando llames a `leer()`. Funcionan como los **setters** de la cátedra: validan el dato (cuando pueden) y recién después lo guardan. A diferencia del ejemplo de los apuntes, que hace `print` ante un valor inválido, acá se **lanza `ValueError`**, que es lo que recomienda la unidad de Excepciones.

Ninguno tiene `return`, así que **devuelven `None`**. Consecuencia: no se pueden encadenar (`lector.forzar_tipo(...).establecer_limite(2)` da `AttributeError: 'NoneType' object has no attribute 'establecer_limite'`). Para encadenar habría que terminar cada uno con `return self`.

#### Línea 38

```python
    def forzar_tipo(self, columna, tipo_dato):
```

Permite decir "esta columna es de tal tipo, no la adivines". Recibe el **nombre** de la columna (str) y la **clase** del tipo (`int`, `float`, `str` o `bool`, sin comillas).

#### Línea 39

```python
        """Deﬁne manualmente qué tipo de dato va a tener una columna."""
```

Docstring. (Curiosidad: "Deﬁne" tiene la ligadura tipográfica "ﬁ", un solo carácter Unicode, señal de que se copió de un PDF. No afecta en nada.)

#### Líneas 40-41

```python
        if tipo_dato not in [int, float, str, bool]:
            raise ValueError("Tipo no válido. Use int, float, str o bool.") 
```

Valida que el tipo sea uno de los cuatro soportados. Fijate que la lista tiene **las clases**, no strings:

```python
lector.forzar_tipo("a", list)    # ValueError: Tipo no válido. Use int, float, str o bool.
lector.forzar_tipo("a", "int")   # también ValueError: el string "int" no es la clase int
```

(Por el criterio de la cátedra, pasar un string en vez de una clase sería más bien un `TypeError`; es un detalle para reconocer si lo preguntan. Y `[int, float, str, bool]` es una colección fija: una tupla sería más fiel a los apuntes.)

#### Línea 42

En blanco.

#### Línea 43

```python
        self._tipos_columnas[columna] = tipo_dato
```

Anota en el diccionario. Después de `forzar_tipo("codigo", str)` queda `{'codigo': str}`.

- Si forzás dos veces la misma columna, **gana la última** (asignar a una clave existente reemplaza el valor).
- **No se fija si la columna existe.** No puede: todavía no se leyó el archivo, así que no conoce el encabezado. Esa validación se hace al leer, en `clase.py:147-149`.

#### Línea 44

En blanco.

#### Líneas 45-47

```python
    def agregar_filtro(self, funcion_filtro):
        """Agrega una condición para filtrar las filas que queremos mantener."""
        self._filtros.append(funcion_filtro)
```

Agrega una función filtro a la lista. La función tiene que recibir una fila (diccionario) y devolver `True` si la fila se queda.

- Podés llamar varias veces: los filtros se **acumulan** y se combinan con AND.
- **No valida** que lo que pasás sea una función. Si pasás `5`, recién explota al leer.
- **No hay forma de sacar un filtro.** Si querés "empezar de cero", creás otro `LectorCSV`.

#### Línea 48

En blanco.

#### Líneas 49-53

```python
    def establecer_limite(self, limite):
        """Define la cantidad maxima de filas a leer"""
        if limite < 0:
            raise ValueError("El limite de filas no puede ser negativo")
        self._limite_filas = limite
```

Fija la cantidad máxima de filas del resultado.

- Negativo → error. `0` está permitido y devuelve `[]` (lista vacía).
- Valida el **valor**, no el **tipo**: `establecer_limite(2.5)` se acepta, y `establecer_limite("3")` da un `TypeError` "crudo" de Python (`'<' not supported between instances of 'str' and 'int'`) en vez de un mensaje propio.
- Lo importante de entender: **el límite cuenta filas que cumplen el filtro**, no "las primeras N del archivo". Eso se ve en `clase.py:206-211`.

#### Línea 54

En blanco.

#### Líneas 55-59

```python
    def establecer_rango(self, inicio, fin):
        """Elige desde qué número de fila hasta cuál queremos procesar (arrancando a contar desde 1)."""
        if inicio < 1 or fin < inicio:
            raise ValueError("Rango invalido: 'inicio' debe ser >= 1 y 'fin' >= 'inicio'")
        self._rango_filas = (inicio, fin)
```

Fija un rango de **filas de datos**, contando desde 1 (la 1 es la primera fila después del encabezado), **con los dos extremos incluidos**.

- `inicio < 1 or fin < inicio` rechaza cosas como `(0, 3)` o `(3, 2)`.
- Se guarda como **tupla** `(inicio, fin)`: es un par fijo que no se modifica, justo el caso en que la cátedra recomienda tupla.
- Si `fin` se pasa del total de filas **no hay error**: `(3, 100)` devuelve desde la 3 hasta la última, y `(50, 60)` devuelve `[]`. Eso es porque después se aplica con *slicing*, que no se queja si te pasás del final.

```python
lector.establecer_rango(0, 3)   # ValueError: Rango invalido: 'inicio' debe ser >= 1 y 'fin' >= 'inicio'
lector.establecer_rango(3, 2)   # ValueError: (el mismo)
```

#### Línea 60

En blanco.

#### Líneas 61-63

```python
    def seleccionar_columnas(self, lista_columnas):
        """Define las columnas que se quieren obtener en el resultado"""
        self._columnas = lista_columnas
```

Anota qué columnas querés en el resultado (y en qué orden).

- No valida nada acá (otra vez: no conoce el encabezado). Se valida en `clase.py:192-195`.
- **Ojo 1:** guarda **la misma lista** que le pasaste, no una copia. Si después de llamarlo modificás tu lista (`cols.append("precio")`), el lector "se entera" y cambia el resultado. Se arreglaría con `self._columnas = list(lista_columnas)` (cuidando aparte el caso `None` del último punto, porque `list(None)` da `TypeError`).
- **Ojo 2:** si pasás un string en vez de una lista, `seleccionar_columnas("nombre")`, después se recorre **letra por letra** y falla con `La columna seleccionada 'n' no existe en la tabla.`
- `seleccionar_columnas(None)` vuelve a "todas las columnas" (es el único de estos métodos que se puede "deshacer" así).

#### Línea 64

En blanco.

---

### 3.5 `leer`: el director de orquesta (líneas 65-82)

Este es el único método que "hace el trabajo" desde el punto de vista del usuario. Pero en realidad no hace casi nada él mismo: **llama a cuatro métodos protegidos en orden** y va pasando el resultado de uno al siguiente, como una posta.

#### Líneas 65-69

```python
    def leer(self, ruta_archivo):
        """
        Funcion principal: abre el archivo, separa los datos, les asigna 
        los tipos correctos y aplica los filtros, rangos y columnas
        """
```

Recibe la ruta del archivo (un string como `"datos1.csv"`; también acepta un `Path` de `pathlib`, porque `open()` lo acepta). El docstring resume el pipeline.

#### Líneas 70-71

```python
        # 1. Lectura del archivo
        lineas = self._leer_archivo(ruta_archivo)
```

Estación 1. `self._leer_archivo(...)` llama a otro método **del mismo objeto** (por eso el `self.`). Devuelve la lista de renglones.

#### Línea 72

En blanco.

#### Líneas 73-74

```python
        # 2. Separamos el encabezado y los datos, controlando errores
        encabezados, filas_crudas = self._procesar_lineas(lineas)
```

Estación 2. `_procesar_lineas` devuelve **dos cosas** (en realidad una tupla de dos elementos) y acá se "desarman" en dos variables. Eso se llama **desempaquetado** (*unpacking*): es lo mismo que `cuadrado, cubo = potencias(8)` de los apuntes.

#### Línea 75

En blanco.

#### Líneas 76-77

```python
        # 3. Asignamos los tipos (automaticos o los que pidio el usuario)
        filas_tipadas = self._convertir_tipos(encabezados, filas_crudas)
```

Estación 3. Devuelve la lista de diccionarios con los valores ya convertidos.

#### Línea 78

En blanco.

#### Líneas 79-80

```python
        # 4. Aplicamos rango, filtros, limite y recorte de columnas
        filas_filtradas = self._aplicar_filtros_y_rangos(encabezados, filas_tipadas)
```

Estación 4. Aplica las opciones que configuraste.

#### Línea 81

En blanco.

#### Línea 82

```python
        return filas_filtradas
```

Devuelve el resultado final: una **lista de diccionarios**, como pide la consigna.

> **Para la defensa:**
> - **Interfaz pública vs. interior:** el usuario solo conoce `__init__`, los cinco métodos de configuración y `leer`. Los cuatro métodos con `_` son el "motor" (la analogía del auto del apunte de encapsulamiento: usás los pedales y la palanca de cambios sin saber cómo funcionan por dentro los frenos o la caja de cambios). Si mañana se cambia cómo se convierte, `ejemplos.py` no se entera. `help(LectorCSV)` ni siquiera muestra los métodos con `_`.
> - **`leer` no modifica `self`**: el estado del objeto queda igual antes y después de leer. Por eso se puede llamar dos veces y da lo mismo.
> - **Si algo falla en cualquier estación**, la excepción **se propaga**: sale de ese método, sale de `leer` y llega a quien llamó a `leer` (en el Ejemplo 4, al `try/except` de `ejemplos.py`). Ningún método interno la ataja para frenarla: las dos únicas capturas internas (`FileNotFoundError` en `_leer_archivo` y el `ValueError` de `int`/`float` en `convertir_valor`) vuelven a lanzar el error, ahora con mensaje en castellano.

#### Línea 83

En blanco.

### 3.6 `_leer_archivo` — Estación 1: del disco a una lista de renglones (líneas 84-97)

#### Líneas 84-85

```python
    def _leer_archivo(self, ruta_archivo):
        """Abre el archivo de texto plano y devuelve sus lineas limpias"""
```

**Método protegido** (guion bajo): es interno, no está pensado para que lo llame el usuario.

#### Línea 86

```python
        try:
```

Abre un bloque "intentá esto" porque abrir un archivo puede fallar (por ejemplo, si la ruta está mal escrita).

#### Línea 87

```python
            with open(ruta_archivo, "r", encoding="utf-8") as archivo:
```

Acá pasan tres cosas:

- `open(...)` abre el archivo. `"r"` = modo lectura de texto (es el modo por defecto, pero ponerlo deja claro que no se escribe nada).
- `encoding="utf-8"` le dice cómo traducir los bytes del archivo a letras. **Es importante en Windows**, donde el encoding por defecto no es UTF-8: sin esto, un "Córdoba" escrito en UTF-8 se leería como "CÃ³rdoba" **sin ningún error** (datos corruptos en silencio). La cátedra recomienda ponerlo siempre.
- `with ... as archivo:` usa el archivo abierto como **context manager**: garantiza que el archivo **se cierra solo** al salir del bloque, incluso si hay un error en el medio. Por eso no hay ningún `archivo.close()`.

#### Línea 88

```python
                lineas = []
```

Lista vacía donde van los renglones.

#### Líneas 89-90

```python
                for linea in archivo:
                    lineas.append(linea.rstrip("\n\r"))
```

- `for linea in archivo` recorre el archivo **renglón por renglón**. Cada renglón viene con el salto de línea pegado al final: `'001, Cuaderno, 2500.5, 10, true\n'`. (Menos el último de `datos1.csv`, porque el archivo no termina con un "enter": a ese el `rstrip` no le saca nada.)
- `rstrip("\n\r")` saca **solo** los caracteres `\n` y `\r` del lado derecho:

```python
'001, Cuaderno, 2500.5, 10, true\n'.rstrip("\n\r")   # → '001, Cuaderno, 2500.5, 10, true'
```

> **¿Por qué `rstrip("\n\r")` y no `strip()`?** Porque `strip()` sin argumentos borra **todos** los blancos, tabs incluidos. Si el delimitador fuera tab y el último campo estuviera vacío (`"1\t2\t\n"`), `strip()` se comería el último tab y se perdería una columna. Con `rstrip("\n\r")` queda `"1\t2\t"`, que da tres campos (el último vacío → `None`). Los espacios alrededor de cada campo se limpian después, campo por campo, en `separar_linea`.
>
> **¿Y el `\r`?** `datos1.csv` tiene finales de línea de Windows (`\r\n`). En modo texto Python ya los convierte en `\n` solo, pero sacar también el `\r` no cuesta nada y cubre casos raros.

#### Líneas 91-92

```python
        except FileNotFoundError:
            raise FileNotFoundError(f"No se encontró el archivo en la ruta: {ruta_archivo}")
```

Si el archivo no existe, `open` lanza `FileNotFoundError` con un mensaje en inglés. Lo atajamos y lanzamos **otro del mismo tipo** con un mensaje en castellano que incluye la ruta. Mantener el tipo sirve para que quien use el lector pueda seguir haciendo `except FileNotFoundError`.

```python
LectorCSV().leer("no_existe.csv")
# FileNotFoundError: No se encontró el archivo en la ruta: no_existe.csv
```

> **Ojo con esto:**
> - Igual que en `convertir_valor`, como se lanza dentro del `except`, el traceback muestra los dos errores encadenados ("During handling of the above exception...").
> - Las rutas relativas (`"datos1.csv"`) se buscan desde **la carpeta donde estás parado en la terminal**, no desde donde está el código. Si corrés `ejemplos.py` desde otra carpeta, salta este error.
> - `ejemplos.py` solo captura `ValueError`, y `FileNotFoundError` **no** es un `ValueError`: una ruta mal escrita cortaría el programa.
> - Otros problemas el lector no los captura: un archivo en otra codificación (latin-1 con tildes) da `UnicodeDecodeError`, y una carpeta en vez de archivo da `PermissionError` en Windows. Detalle fino: `UnicodeDecodeError` es una subclase de `ValueError`, así que el `except ValueError` de `ejemplos.py` **sí** lo atajaría (con el mensaje en inglés de Python); el `PermissionError` no.

#### Línea 93

En blanco.

#### Líneas 94-95

```python
        if len(lineas) == 0:
            raise ValueError(f"El archivo '{ruta_archivo}' está vacío.")
```

Si el archivo no tenía **nada** (0 bytes), la lista queda vacía y se avisa. Fijate que `lineas` se creó adentro del `with` (que está adentro del `try`) y se puede usar acá afuera sin problema: en Python las variables viven en toda la función, no solo en el bloque donde nacen.

Detalle: un archivo que tiene solo un "enter" **no** cae acá (da `lineas = ['']`, con un elemento). Ese caso lo agarra la línea 102.

#### Línea 96

En blanco.

#### Línea 97

```python
        return lineas
```

Con `datos1.csv` devuelve estos 7 strings:

```python
['codigo, nombre, precio, cantidad, disponible',
 '001, Cuaderno, 2500.5, 10, true',
 '002, Lapicera, 800, 25, true',
 '003, Carpeta, 3200.0, 8, true',
 '004, Regla, 500, , false',
 '005, Mochila, 15000.0, 3, true',
 '006, Goma, 300.5, 50, true']
```

#### Línea 98

En blanco.

---

### 3.7 `_procesar_lineas` — Estación 2: de renglones a listas de campos (líneas 99-143)

Esta estación hace de "control de calidad estructural": separa los campos, arma los nombres de columna y verifica que el archivo tenga una forma de tabla razonable.

#### Líneas 99-100

```python
    def _procesar_lineas(self, lineas):
        """Separa las lineas usando el delimitador configurado"""
```

Recibe la lista de renglones. Va a devolver **dos** cosas: los nombres de columna y las filas separadas.

#### Línea 101

```python
        primera_linea = lineas[0]
```

Toma el primer renglón (índice 0, porque Python cuenta desde 0). Es seguro hacerlo: `_leer_archivo` ya garantizó que hay al menos una línea.

#### Líneas 102-103

```python
        if primera_linea.strip() == "":
            raise ValueError("Error en fila 1: La primera línea del archivo está vacía.")
```

Si el primer renglón está en blanco (o solo tiene espacios), error. Ese renglón define cuántas columnas hay, así que sin él no se puede hacer nada.

#### Línea 104

En blanco.

#### Línea 105

```python
        primeros_elementos = separar_linea(primera_linea, self.delimitador)
```

Corta el primer renglón con el delimitador que configuraste (`self.delimitador`). Con `datos1.csv`:

```python
'codigo, nombre, precio, cantidad, disponible'.split(",")
# → ['codigo', ' nombre', ' precio', ' cantidad', ' disponible']   (split solo)
primeros_elementos
# → ['codigo', 'nombre', 'precio', 'cantidad', 'disponible']        (después del strip)
```

Si no hubiera `strip`, las claves serían `' nombre'` con espacio adelante, y `fila["nombre"]` daría `KeyError`.

#### Línea 106

```python
        cant_columnas = len(primeros_elementos)
```

**La primera línea manda**: define cuántas columnas tiene la tabla (5 en `datos1.csv`). Todas las demás filas tienen que tener esa misma cantidad. Esto vale tanto con encabezado como sin encabezado.

#### Línea 107

En blanco.

#### Líneas 108-110

```python
        # Procesamiento del encabezado
        encabezados = []
        if self.encabezado:
```

Lista vacía para los nombres de columna. Y la bifurcación: ¿el archivo tiene encabezado? (`if self.encabezado:` usa directamente el valor de verdad del atributo.)

#### Líneas 111-112

```python
            for i in range(cant_columnas):
                nombre = primeros_elementos[i]
```

Recorre las posiciones `0, 1, ..., cant_columnas - 1` y toma el nombre de cada una. (`range(n)` va de 0 a n-1.) Se usa el índice `i` porque hace falta para el mensaje de error de la línea 114.

#### Líneas 113-114

```python
                if nombre == "":
                    raise ValueError(f"Error en fila 1, columna {i + 1}: El nombre de la columna está vacío.")
```

Nombre vacío → error. Fijate el `{i + 1}`: adentro de un f-string se puede poner una cuenta. Se suma 1 para que el mensaje cuente columnas **desde 1**, como cuenta una persona.

```text
encabezado "a,,c"  →  Error en fila 1, columna 2: El nombre de la columna está vacío.
encabezado "a,b,"  →  error en la columna 3 (la coma final genera un nombre vacío)
```

#### Líneas 115-116

```python
                if nombre in encabezados:
                    raise ValueError(f"Error en fila 1: El nombre de columna '{nombre}' está repetido.")
```

Nombre repetido → error. Pregunta "¿este nombre ya lo había aceptado antes?" buscando en la lista que se va armando.

- **¿Por qué es error y no se renombra?** Porque cada fila va a ser un diccionario, y en un diccionario las claves son únicas: con dos columnas `a`, la segunda **pisaría** a la primera y se perderían datos sin aviso. Mejor frenar con un mensaje claro.
- Distingue mayúsculas: `Nombre` y `nombre` **no** son repetidos.

```text
encabezado "a,b,a"  →  Error en fila 1: El nombre de columna 'a' está repetido.
```

> **Para la defensa (complejidad):** `nombre in encabezados` es una **búsqueda lineal** en una lista. Adentro de un `for` sobre las K columnas, el total es del orden de K² comparaciones: un "bucle anidado escondido". Con 5 columnas no importa nada; con un `set` auxiliar quedaría lineal.

#### Línea 117

```python
                encabezados.append(nombre)
```

Si pasó los dos controles, se agrega a la lista.

#### Línea 118

```python
            indice_inicio_datos = 1
```

Con encabezado, los datos empiezan en `lineas[1]` (el `lineas[0]` era el encabezado).

#### Líneas 119-122

```python
        else:
            for i in range(cant_columnas):
                encabezados.append(f"col_{i}")
            indice_inicio_datos = 0
```

Sin encabezado (`encabezado=False`): se inventan nombres `col_0`, `col_1`, ... y los datos empiezan en `lineas[0]` (la primera línea también es una fila de datos).

```python
# archivo: "Yerba,1500,10\nAzucar,980,0\n"
LectorCSV(encabezado=False).leer(ruta)
# → [{'col_0': 'Yerba', 'col_1': 1500, 'col_2': 10}, {'col_0': 'Azucar', 'col_1': 980, 'col_2': 0}]
```

> **Ojo con esto:** si el docente te da un archivo **sin** encabezado y te olvidás de `encabezado=False`, en general el lector **no da error**: usa la primera fila de datos como nombres de columna y la pierde (por ejemplo, `Yerba,1500,10` pasa a ser el encabezado). Solo da error por casualidad, si en esa primera fila hay dos valores iguales ("nombre de columna repetido") o una celda vacía. Y al revés, un archivo **con** encabezado leído con `encabezado=False` mete los nombres como si fueran datos, y las columnas numéricas terminan siendo `str` (porque `'precio'` no es un número).

#### Línea 123

En blanco.

#### Líneas 124-125

```python
        # Procesamiento de las filas de datos
        filas_crudas = []
```

Lista donde van las filas separadas (una **lista de listas** de strings).

#### Línea 126

```python
        for i in range(indice_inicio_datos, len(lineas)):
```

Recorre los índices desde donde empiezan los datos (1 o 0) hasta el último renglón. Con `datos1.csv` y encabezado: `i` va de 1 a 6.

#### Línea 127

```python
            num_fila_archivo = i + 1
```

Convierte el índice de la lista (que empieza en 0) en **número de línea del archivo** (que empieza en 1). Así, si hay un error en `lineas[2]`, el mensaje dice "fila 3", que es el renglón 3 que verías en un editor de texto.

#### Línea 128

```python
            linea_actual = lineas[i]
```

El renglón que toca procesar en esta vuelta.

#### Línea 129

En blanco.

#### Líneas 130-131

```python
            if linea_actual.strip() == "":
                raise ValueError(f"Error en fila {num_fila_archivo}: Se encontró una fila vacía.")
```

**Decisión del grupo: una fila vacía es un error**, no se saltea en silencio.

```text
"a,b\n1,2\n\n3,4\n"  →  Error en fila 3: Se encontró una fila vacía.
```

> **Ojo con esto:**
> - Un único "enter" al final del archivo está bien (no genera una línea extra). **Dos** "enter" al final sí generan una línea vacía y dan este error.
> - Gracias a que las filas vacías dan error (no se saltean), el número de índice y el número de línea del archivo **siempre coinciden**. Si se salteara alguna, los números de fila de los mensajes quedarían corridos.
> - Una fila `,,` (solo comas) **no** es vacía para este chequeo: pasa y queda como una fila con todos `None`. En cambio, con delimitador tab, una fila `\t\t` sí cuenta como vacía (porque `strip()` borra tabs). Es una pequeña inconsistencia.

#### Línea 132

En blanco.

#### Línea 133

```python
            elementos = separar_linea(linea_actual, self.delimitador)
```

Corta el renglón en campos limpios. Por ejemplo, para la Regla: `['004', 'Regla', '500', '', 'false']`.

#### Línea 134

En blanco.

#### Líneas 135-139

```python
            if len(elementos) != cant_columnas:
                raise ValueError(
                    f"Error en fila {num_fila_archivo}: Cantidad incorrecta de elementos. "
                    f"Se esperaban {cant_columnas} columnas, pero se encontraron {len(elementos)}."
                )
```

Si la fila tiene **más o menos** campos que la primera línea, error con el número de línea y las dos cantidades.

```text
"a,b\n1,2\n3,4,5\n"  →  Error en fila 3: Cantidad incorrecta de elementos. Se esperaban 2 columnas, pero se encontraron 3.
```

Esto también es lo que salta cuando el **delimitador está mal elegido** de una forma que cambia la cantidad de campos, o cuando un texto tiene comas adentro entre comillas (que el lector no soporta).

#### Línea 140

En blanco.

#### Línea 141

```python
            filas_crudas.append(elementos)
```

La fila pasó los controles: se guarda.

#### Línea 142

En blanco.

#### Línea 143

```python
        return encabezados, filas_crudas
```

Devuelve **dos valores separados por coma**: Python los empaqueta en una tupla, y `leer` (L74) los desempaqueta. Con `datos1.csv`:

```python
encabezados  = ['codigo', 'nombre', 'precio', 'cantidad', 'disponible']
filas_crudas = [['001', 'Cuaderno', '2500.5', '10', 'true'],
                ['002', 'Lapicera', '800', '25', 'true'],
                ['003', 'Carpeta', '3200.0', '8', 'true'],
                ['004', 'Regla', '500', '', 'false'],
                ['005', 'Mochila', '15000.0', '3', 'true'],
                ['006', 'Goma', '300.5', '50', 'true']]
```

Fijate que **todo sigue siendo texto** (`'2500.5'`, `'true'`). Los tipos recién aparecen en la próxima estación.

> **Para la defensa:** la variable `i` se usa en dos bucles distintos de este método (L111 o L120, y L126). No es un bug porque son bucles consecutivos: el segundo `for` pisa el valor que dejó el primero, que es justo lo que los apuntes advierten que hace una variable de iteración con un nombre ya usado, pero acá ese valor viejo ya no se necesita. Igual, `i_col` e `i_linea` serían más claros.

#### Línea 144

En blanco.

### 3.8 `_convertir_tipos` — Estación 3: de texto a valores con tipo (líneas 145-188)

Esta estación trabaja en **dos pasadas**, como quien primero clasifica la ropa por color y después la lava:

- **Parte A (L154-164):** decide el tipo de cada **columna**.
- **Parte B (L166-186):** convierte cada **celda** y arma los diccionarios.

#### Líneas 145-146

```python
    def _convertir_tipos(self, encabezados, filas_crudas):
        """Infiere o aplica tipos de datos (int, float, bool, str, None)"""
```

Recibe los nombres de columna y las filas como listas de strings.

#### Líneas 147-149

```python
        for col_forzada in self._tipos_columnas:
            if col_forzada not in encabezados:
                raise ValueError(f"La columna '{col_forzada}' indicada en forzar_tipo no existe en la tabla.")
```

Primero, un control: **¿las columnas que forzaste existen?** Recién ahora se puede verificar, porque recién ahora conocemos el encabezado.

- Recorrer un diccionario con `for` entrega sus **claves** (los nombres de columna), sin necesidad de `.keys()`.

```python
lector.forzar_tipo("zz", int)
lector.leer("datos1.csv")
# ValueError: La columna 'zz' indicada en forzar_tipo no existe en la tabla.
```

#### Línea 150

En blanco.

#### Líneas 151-152

```python
        cant_columnas = len(encabezados)
        tipos_definidos = {}
```

`cant_columnas` = cuántas columnas hay (5). `tipos_definidos` va a ser un diccionario `{nombre_columna: clase}` con el tipo final de **cada** columna (forzado o inferido).

#### Línea 153

En blanco.

#### Líneas 154-156

```python
        # A. Determinamos el tipo de cada columna
        for col_i in range(cant_columnas):
            nombre_col = encabezados[col_i]
```

Recorre las columnas por posición (`col_i` = 0, 1, 2, ...) y toma su nombre.

#### Línea 157

En blanco.

#### Líneas 158-159

```python
            if nombre_col in self._tipos_columnas:
                tipos_definidos[nombre_col] = self._tipos_columnas[nombre_col]
```

**Si el usuario forzó el tipo de esta columna, se usa ese y no se infiere nada.** Esta es la "prioridad del tipo forzado" que pide la consigna. (Acá `in` sobre un diccionario pregunta por las **claves**.)

#### Líneas 160-164

```python
            else:
                valores_columna = []
                for fila in filas_crudas:
                    valores_columna.append(fila[col_i])
                tipos_definidos[nombre_col] = inferir_tipo_columna(valores_columna)
```

Si no está forzada, se arma la **columna** juntando el elemento `col_i` de cada fila, y se le pide a `inferir_tipo_columna` que decida. O sea, se "da vuelta" la tabla: de filas a columnas.

```python
# col_i = 3 (cantidad) en datos1.csv
valores_columna = ['10', '25', '8', '', '3', '50']   →   int
```

Con `datos1.csv` **sin forzar nada** (como en el Ejemplo 2), queda:

```python
tipos_definidos = {'codigo': int, 'nombre': str, 'precio': float, 'cantidad': int, 'disponible': bool}
```

Y con `forzar_tipo("codigo", str)` (Ejemplo 1), lo único que cambia es `'codigo': str`.

> **Ojo con esto:** la inferencia mira **todas las filas del archivo**, no solo las del rango que pediste ni las que pasan el filtro. Por eso el tipo de una columna no depende de qué filas pidas.

#### Línea 165

En blanco.

#### Líneas 166-167

```python
        # B. Armamos la lista de diccionarios convirtiendo cada valor
        lista_diccionarios = []
```

Empieza la parte B. Esta lista va a ser el resultado de la estación.

#### Líneas 168-169

```python
        for fila_i in range(len(filas_crudas)):
            elementos_fila = filas_crudas[fila_i]
```

Recorre las filas por posición (`fila_i` = 0, 1, ..., 5) y toma la fila cruda.

#### Línea 170

En blanco.

#### Líneas 171-174

```python
            if self.encabezado:
                num_fila_archivo = fila_i + 2
            else:
                num_fila_archivo = fila_i + 1
```

Calcula en qué **línea del archivo** está esta fila, para los mensajes de error:

- `+1` porque `fila_i` cuenta desde 0 y las personas desde 1.
- `+1` más si hay encabezado, porque el encabezado ocupa la línea 1.

O sea, con encabezado, la fila de datos `fila_i = 0` está en la línea 2 del archivo. En `derror.csv`, `'veinte'` está en `fila_i = 1` → **línea 3**. Por eso el error del Ejemplo 4 dice "fila 3".

(Con una expresión condicional de la U3 quedaría en una línea: `num_fila_archivo = fila_i + 2 if self.encabezado else fila_i + 1`.)

#### Línea 175

En blanco.

#### Línea 176

```python
            diccionario_fila = {}
```

Un diccionario vacío para esta fila.

#### Líneas 177-180

```python
            for col_i in range(cant_columnas):
                nombre_col = encabezados[col_i]
                valor_texto = elementos_fila[col_i]
                tipo_col = tipos_definidos[nombre_col]
```

Para cada columna de la fila junta tres datos: el **nombre** (de `encabezados`), el **texto** de la celda (de la fila cruda, en la misma posición) y el **tipo** que le toca (de `tipos_definidos`). Fijate que `encabezados[col_i]` y `elementos_fila[col_i]` se recorren "en paralelo" por la misma posición; esto queda encerrado acá adentro y, una vez armado el diccionario, ya no hace falta acordarse de posiciones.

#### Línea 181

En blanco.

#### Líneas 182-184

```python
                diccionario_fila[nombre_col] = convertir_valor(
                    valor_texto, tipo_col, num_fila_archivo, nombre_col
                )
```

Convierte la celda con `convertir_valor` y la guarda en el diccionario bajo el nombre de la columna. Si la conversión falla, el `ValueError` sale de `convertir_valor`, atraviesa este método y `leer`, y llega a quien llamó (se **propaga**).

```python
# primera fila de datos1.csv, columna precio
convertir_valor('2500.5', float, 2, 'precio')   # → 2500.5
```

Los argumentos se pasan **por posición**, así que el orden importa: si se invirtieran `num_fila_archivo` y `nombre_col`, el mensaje de error saldría cruzado.

#### Línea 185

En blanco.

#### Línea 186

```python
            lista_diccionarios.append(diccionario_fila)
```

Fila terminada → a la lista.

#### Línea 187

En blanco.

#### Línea 188

```python
        return lista_diccionarios
```

Con `datos1.csv` sin forzar tipos devuelve:

```python
[{'codigo': 1, 'nombre': 'Cuaderno', 'precio': 2500.5, 'cantidad': 10, 'disponible': True},
 {'codigo': 2, 'nombre': 'Lapicera', 'precio': 800.0, 'cantidad': 25, 'disponible': True},
 {'codigo': 3, 'nombre': 'Carpeta', 'precio': 3200.0, 'cantidad': 8, 'disponible': True},
 {'codigo': 4, 'nombre': 'Regla', 'precio': 500.0, 'cantidad': None, 'disponible': False},
 {'codigo': 5, 'nombre': 'Mochila', 'precio': 15000.0, 'cantidad': 3, 'disponible': True},
 {'codigo': 6, 'nombre': 'Goma', 'precio': 300.5, 'cantidad': 50, 'disponible': True}]
```

> **Ojo con esto (dos consecuencias del diseño "todo el archivo primero"):**
> - **Se convierte el archivo entero, aunque hayas pedido un rango o un límite.** Si hay un valor inconvertible en una fila que ni siquiera ibas a devolver, igual se corta la lectura.
> - **El límite no ahorra trabajo de lectura:** siempre se lee, separa y convierte todo; el límite recién actúa en la estación 4.

#### Línea 189

En blanco.

---

### 3.9 `_aplicar_filtros_y_rangos` — Estación 4: elegir qué filas y qué columnas (líneas 190-221)

Acá se aplican las cuatro opciones **en este orden**: rango → filtros → límite → columnas. Es exactamente el orden documentado en `clase.py:7-9`.

#### Líneas 190-191

```python
    def _aplicar_filtros_y_rangos(self, encabezados, filas_tipadas):
        """Filtra y recorta los datos aplicando todas las reglas que definió el usuario"""
```

Recibe los nombres de columna (para validar la selección) y las filas ya convertidas.

#### Líneas 192-195

```python
        if self._columnas is not None:
            for col in self._columnas:
                if col not in encabezados:
                    raise ValueError(f"La columna seleccionada '{col}' no existe en la tabla.")
```

Si el usuario eligió columnas (`is not None` = "si configuró algo"), verifica que todas existan. Se hace **antes** de filtrar, pero **después** de haber leído y convertido todo el archivo (este método es la última estación).

```python
lector.seleccionar_columnas(["zz"])
lector.leer("datos1.csv")
# ValueError: La columna seleccionada 'zz' no existe en la tabla.
```

Se usa `is not None` (y no `!= None`) porque `None` es un objeto único y se compara por **identidad**.

#### Línea 196

En blanco.

#### Líneas 197-200

```python
        # 1er Rango de filas
        if self._rango_filas is not None:
            inicio, fin = self._rango_filas
            filas_en_rango = filas_tipadas[inicio - 1 : fin]
```

**Paso 1: el rango.** Si hay rango configurado, desempaqueta la tupla y corta la lista con **slicing**.

La cuenta `[inicio - 1 : fin]` es la que más preguntan, así que despacio:

- El usuario cuenta filas **desde 1** y con **los dos extremos incluidos**.
- Python indexa **desde 0** y el slice `[a:b]` incluye `a` pero **excluye** `b`.
- Al `inicio` se le resta 1 para pasarlo a base 0.
- Al `fin` **no** se le resta nada: en base 0 sería `fin - 1`, pero como el slice excluye el final, hay que sumarle 1 → queda `fin`. Se cancelan.

| Rango pedido | Slice | Qué filas de datos devuelve |
|---|---|---|
| `(1, 5)` | `[0:5]` | 1, 2, 3, 4, 5 |
| `(2, 3)` | `[1:3]` | 2 y 3 |
| `(3, 100)` | `[2:100]` | de la 3 hasta la última, sin error |
| `(50, 60)` | `[49:60]` | ninguna: `[]`, sin error |

El slicing **no se queja** si te pasás del final: por eso un rango "grande" no da error.

#### Líneas 201-202

```python
        else:
            filas_en_rango = filas_tipadas
```

Sin rango, se usan todas las filas. (Es la misma lista, no una copia; no hay problema porque es una variable local.)

#### Línea 203

En blanco.

#### Líneas 204-205

```python
        # 2do Filtros y 3er Límite de cantidad
        filas_filtradas = []
```

**Pasos 2 y 3 juntos**, en un solo bucle. Lista vacía para las filas que pasan.

#### Línea 206

```python
        for fila in filas_en_rango:
```

Recorre las filas que quedaron después del rango, en orden.

#### Líneas 207-208

```python
            if self._limite_filas is not None and len(filas_filtradas) >= self._limite_filas:
                break
```

**El límite, chequeado al principio de cada vuelta.** "Si hay límite y ya junté esa cantidad de filas buenas, corto el bucle."

Dos cosas finas:

1. **Cortocircuito del `and`** (la cátedra lo llama evaluación no estricta): si `self._limite_filas` es `None`, la primera parte da `False` y Python **ni evalúa** la segunda. Y está bien que no la evalúe, porque `len(...) >= None` lanzaría `TypeError`. Por eso el orden de los dos lados no es indistinto.
2. **El límite cuenta filas que pasaron el filtro.** O sea, el lector sigue leyendo hasta juntar N filas que **cumplan**; no se queda con "las primeras N filas y después filtra". La consigna pedía decidir esto, y este es el comportamiento elegido. Además, como se chequea **antes** de llamar al filtro, no se evalúan filtros de más.

Con límite `0`: en la primera vuelta `0 >= 0` → `break` → resultado `[]`.

#### Línea 209

En blanco.

#### Líneas 210-211

```python
            if cumple_todos_los_filtros(fila, self._filtros):
                filas_filtradas.append(fila)
```

**Los filtros.** Si la fila pasa todos los filtros (o si no hay filtros: lista vacía → `True`), se guarda. Fijate que el filtro recibe la **fila completa** y ya tipada: por eso se puede filtrar por `cantidad` aunque después solo devuelvas `nombre` y `precio`.

#### Línea 212

En blanco.

#### Líneas 213-219

```python
        # 4to Selección de columnas
        if self._columnas is not None:
            resultado_final = []
            for fila in filas_filtradas:
                fila_recortada = recortar_diccionario(fila, self._columnas)
                resultado_final.append(fila_recortada)
            return resultado_final
```

**Paso 4: las columnas, al final de todo.** Si el usuario eligió columnas, arma una lista nueva con cada fila recortada (diccionarios nuevos, en el orden de columnas que pidió el usuario) y la devuelve. Ese `return` termina el método acá.

#### Línea 220

En blanco.

#### Línea 221

```python
        return filas_filtradas
```

Si **no** se eligieron columnas, nunca se entró al `if` anterior y se devuelven las filas filtradas completas. (El método tiene dos `return`; según el caso sale por uno o por el otro.)

> **Para la defensa — resumen de la estación 4:**
> - Orden: **rango → filtros → límite → columnas**.
> - El rango usa numeración de **filas de datos desde 1**, extremos incluidos.
> - El límite cuenta filas que **cumplen** el filtro, y corta apenas las junta.
> - Se puede filtrar por una columna que no se devuelve.
> - Si un filtro explota (por ejemplo, compara `None < 15`, o usa un nombre de columna mal escrito), el error **no se captura** y no dice en qué fila pasó. Y un filtro "roto" puede funcionar o explotar según el rango y el límite, porque solo se evalúa sobre las filas que llegan a este bucle.

---

## 4. `ejemplos.py` línea por línea

`ejemplos.py` es el **script** de demostración (código para ejecutar), mientras que `funciones.py` y `clase.py` son **módulos** (código para importar). Es el único archivo que imprime cosas y el único que usa pandas, como pide la consigna.

**Cómo correrlo:** abrí la terminal **parada en la carpeta del proyecto** (la que tiene `ejemplos.py`, `modulo/` y los CSV) y ejecutá `python ejemplos.py`. Tiene que ser desde ahí por dos razones: el `from modulo...` y las rutas `"datos1.csv"` son relativas a esa carpeta.

### Las importaciones

#### Línea 1

```python
import pandas as pd
```

Importa pandas con el alias `pd` (la convención de siempre, como `np` para numpy). Se usa **solo para mostrar** los resultados como tabla. El lector en sí no usa pandas (la consigna lo prohíbe para leer). pandas tiene que estar instalado (`python -m pip install pandas`).

#### Línea 2

```python
from modulo.clase import LectorCSV
```

Trae la clase `LectorCSV` del módulo `clase.py`, que está dentro del paquete `modulo`. Al importar, Python ejecuta `clase.py` de arriba a abajo, que solo tiene definiciones (y el import de `funciones.py`), así que no imprime nada.

#### Líneas 3-4

En blanco.

---

### Ejemplo 1: lectura normal con un tipo forzado (líneas 5-16)

#### Línea 5

```python
print("EJEMPLO 1: Lectura de datos1.csv (Inferencia y tipo forzado)")
```

Un título en pantalla.

#### Línea 6

```python
lector1 = LectorCSV(delimitador=",")
```

Crea el primer lector (primera instancia). Pasar `delimitador=","` es redundante (ya es el valor por defecto), pero deja explícito qué separador se espera. Se pasa **por nombre** (`delimitador=`), lo que hace la llamada autoexplicativa.

#### Línea 7

```python
lector1.forzar_tipo("codigo", str)
```

"La columna codigo es texto, no la adivines." Sin esto, `'001'` se inferiría como `int` y quedaría `1` (se pierden los ceros, que es justamente el ejemplo `00123` de la consigna). Por dentro, deja `lector1._tipos_columnas = {'codigo': str}`.

#### Línea 8

```python
datos_productos = lector1.leer("datos1.csv")
```

Lee el archivo pasando por las cuatro estaciones. Como no hay rango, filtros, límite ni columnas, la estación 4 devuelve todo. `datos_productos` queda con una lista de 6 diccionarios.

#### Línea 9

En blanco.

#### Línea 10

```python
print("\nDatos leídos del archivo:")
```

El `\n` al principio imprime una línea en blanco antes del texto.

#### Líneas 11-12

```python
for fila in datos_productos:
    print(fila)
```

Imprime cada diccionario en su propio renglón. **Salida real:**

```text
{'codigo': '001', 'nombre': 'Cuaderno', 'precio': 2500.5, 'cantidad': 10, 'disponible': True}
{'codigo': '002', 'nombre': 'Lapicera', 'precio': 800.0, 'cantidad': 25, 'disponible': True}
{'codigo': '003', 'nombre': 'Carpeta', 'precio': 3200.0, 'cantidad': 8, 'disponible': True}
{'codigo': '004', 'nombre': 'Regla', 'precio': 500.0, 'cantidad': None, 'disponible': False}
{'codigo': '005', 'nombre': 'Mochila', 'precio': 15000.0, 'cantidad': 3, 'disponible': True}
{'codigo': '006', 'nombre': 'Goma', 'precio': 300.5, 'cantidad': 50, 'disponible': True}
```

Cómo explicar cada columna:

| Columna | Valores en el archivo | Tipo final | Por qué |
|---|---|---|---|
| `codigo` | `001`, `002`, ... | `str` | **forzado** (L7); conserva los ceros |
| `nombre` | `Cuaderno`, ... | `str` | inferido: no son bool, ni int, ni float |
| `precio` | `2500.5`, `800`, `3200.0`, ... | `float` | inferido: hay decimales, y `'800'` pasa a `800.0` |
| `cantidad` | `10`, `25`, `8`, *(vacío)*, `3`, `50` | `int` | inferido: el vacío no vota; la Regla queda `None` |
| `disponible` | `true`, ..., `false`, ... | `bool` | inferido: todos son true/false |

#### Línea 13

En blanco.

#### Línea 14

```python
print("\nVisualización como DataFrame de pandas:")
```

Otro título.

#### Línea 15

```python
tabla_productos = pd.DataFrame(datos_productos)
```

Convierte la lista de diccionarios en un `DataFrame` de pandas: cada diccionario es una fila y las claves son las columnas. Esto se hace **acá**, fuera del lector, como pide la consigna.

#### Línea 16

```python
print(tabla_productos)
```

**Salida real:**

```text
  codigo    nombre   precio  cantidad  disponible
0    001  Cuaderno   2500.5      10.0        True
1    002  Lapicera    800.0      25.0        True
2    003   Carpeta   3200.0       8.0        True
3    004     Regla    500.0       NaN       False
4    005   Mochila  15000.0       3.0        True
5    006      Goma    300.5      50.0        True
```

> **Ojo con esto (pregunta casi segura):** en el DataFrame la cantidad aparece como `10.0`, `25.0`, ... y la de la Regla como `NaN`. **No es culpa del lector**: pandas necesita un solo tipo por columna y el tipo entero que usa por defecto (`int64`) no admite huecos, así que pasa la columna entera a `float64` y cambia el `None` por `NaN`. En la lista de diccionarios (la salida de arriba) los valores son `10` (int) y `None`. Por eso la consigna pide mostrar **también** la lista original.

#### Líneas 17-19

En blanco. No imprimen nada: por eso, en la salida, "EJEMPLO 2" aparece pegado a la tabla anterior.

---

### Ejemplo 2: combinando rango, filtro, límite y columnas (líneas 20-31)

#### Línea 20

```python
print("EJEMPLO 2: Selección sobre datos1.csv (Rango, Filtro, Límite y Columnas)")
```

Título.

#### Línea 21

```python
lector2 = LectorCSV(delimitador=",")
```

Un lector **nuevo**, independiente de `lector1`. Ojo: este **no** fuerza `codigo` a `str`, así que en este lector `codigo` se infiere `int` (no se nota porque al final no se devuelve esa columna).

#### Línea 22

```python
lector2.establecer_rango(1, 5)
```

Filas de datos 1 a 5, incluidas: Cuaderno, Lapicera, Carpeta, Regla, Mochila. (La Goma, fila 6, queda afuera.)

#### Línea 23

```python
lector2.agregar_filtro(lambda fila: fila["cantidad"] is not None and fila["cantidad"] < 15)
```

Agrega un filtro escrito como **función anónima** (`lambda`): recibe una fila y devuelve `True` si la cantidad **no es nula y es menor a 15**. Es el uso típico de `lambda` según la cátedra: una función cortita y de un solo uso que se pasa como argumento.

**¿Por qué el `is not None and`?** Porque la Regla tiene `cantidad = None`, y `None < 15` lanza `TypeError`. Gracias al **cortocircuito** del `and`, si la primera parte da `False` (la cantidad es `None`), la segunda ni se evalúa y la fila simplemente no pasa.

> **Detalle fino (comprobado corriéndolo, y te puede servir si te repreguntan):** con la configuración *exacta* de este ejemplo, el filtro **nunca llega a evaluarse sobre la Regla**: el límite de 2 corta el bucle justo antes de esa fila (lo ves vuelta por vuelta en la sección 5). El filtro se llama solo 3 veces: Cuaderno, Lapicera y Carpeta. O sea que acá la guarda no llega a "trabajar". Pero si sacás el límite, o lo subís a 3, un filtro **sin** la guarda (`fila["cantidad"] < 15`) explota con `TypeError: '<' not supported between instances of 'NoneType' and 'int'` al llegar a la Regla. La guarda hace que el filtro sea correcto **para cualquier configuración**, no solo para esta.

#### Línea 24

```python
lector2.establecer_limite(2)
```

Como máximo 2 filas **que cumplan el filtro**.

#### Línea 25

```python
lector2.seleccionar_columnas(["nombre", "precio"])
```

Del resultado, solo `nombre` y `precio`. Fijate que el filtro usa `cantidad`, que no se devuelve: se puede porque las columnas se recortan al final.

#### Línea 26

En blanco.

#### Línea 27

```python
datos_filtrados = lector2.leer("datos1.csv")
```

Lee aplicando todo lo anterior. (En la sección 5 está este mismo paso, variable por variable.)

#### Líneas 28-29

```python
print("\nLista de diccionarios filtrada y recortada:")
print(datos_filtrados)
```

Imprime la lista entera en un solo renglón. **Salida real:**

```text
[{'nombre': 'Cuaderno', 'precio': 2500.5}, {'nombre': 'Carpeta', 'precio': 3200.0}]
```

¿Por qué esas dos? Del rango 1-5, cumplirían el filtro Cuaderno (10), Carpeta (8) y Mochila (3); Lapicera (25) no cumple y Regla (`None`) tampoco. Pero el límite es 2: después de juntar Cuaderno y Carpeta, al empezar la vuelta siguiente el bucle corta. **Ni la Regla ni la Mochila llegan a pasar por el filtro.**

#### Líneas 30-31

```python
print("\nDataFrame de pandas:")
print(pd.DataFrame(datos_filtrados))
```

Lo mismo como tabla. **Salida real:**

```text
     nombre  precio
0  Cuaderno  2500.5
1   Carpeta  3200.0
```

Las columnas salen en el orden que se pidió en `seleccionar_columnas`.

#### Línea 32

En blanco.

---

### Ejemplo 3: otro delimitador (líneas 33-42)

#### Línea 33

```python
print("EJEMPLO 3: Lectura de datos2.txt con separador punto y coma (;)")
```

Título.

#### Línea 34

```python
lector3 = LectorCSV(delimitador=";")
```

Un lector que separa por punto y coma. Es la única diferencia: todo lo demás funciona igual, porque el delimitador es un **dato** que se le pasa a `split`. (La extensión `.txt` no importa: el lector no mira la extensión, mira el contenido.)

#### Línea 35

```python
datos_envios = lector3.leer("datos2.txt")
```

`datos2.txt` tiene: `id_envio; destino; costo; entregado` y tres filas.

#### Línea 36

En blanco.

#### Líneas 37-39

```python
print("\nDatos leídos del archivo:")
for fila in datos_envios:
    print(fila)
```

**Salida real:**

```text
{'id_envio': 101, 'destino': 'Rosario', 'costo': 4500.0, 'entregado': True}
{'id_envio': 102, 'destino': 'Cordoba', 'costo': 6200.5, 'entregado': False}
{'id_envio': 103, 'destino': 'Buenos Aires', 'costo': 5100.0, 'entregado': True}
```

Para explicar: `id_envio` → `int`; `destino` → `str` (y `'Buenos Aires'` conserva el espacio del medio, porque `strip` solo limpia bordes); `costo` → `float` (`'5100'` pasa a `5100.0` porque la columna tiene decimales); `entregado` → `bool`.

#### Línea 40

En blanco.

#### Líneas 41-42

```python
print("\nDataFrame de pandas:")
print(pd.DataFrame(datos_envios))
```

**Salida real:**

```text
   id_envio       destino   costo  entregado
0       101       Rosario  4500.0       True
1       102       Cordoba  6200.5      False
2       103  Buenos Aires  5100.0       True
```

#### Línea 43

En blanco.

---

### Ejemplo 4: manejo de errores (líneas 44-52)

#### Línea 44

```python
print("EJEMPLO 4: Manejo de errores leyendo derror.csv")
```

Título.

#### Línea 45

```python
lector_error = LectorCSV(delimitador=",")
```

Otro lector nuevo.

#### Línea 46

```python
lector_error.forzar_tipo("cantidad", int)
```

"La cantidad **tiene** que ser entera." `derror.csv` tiene en la fila de la Lapicera `veinte` en vez de un número.

> **Ojo con esto:** si **no** se forzara el tipo, no habría error: la columna `cantidad` (`'10'`, `'veinte'`, `'8'`) se inferiría como `str` y el lector devolvería `'10'`, `'veinte'`, `'8'` como textos. El error aparece **porque** el usuario exigió `int` y la consigna prohíbe cambiarle el tipo pedido por otro.

#### Línea 47

En blanco.

#### Líneas 48-49

```python
try:
    lector_error.leer("derror.csv")
```

Intenta leer. Fijate que el resultado **no se guarda** en ninguna variable: se espera que falle. Lo que pasa adentro: la estación 3 llega a la Lapicera (`fila_i = 1` → línea 3 del archivo), `convertir_valor('veinte', int, 3, 'cantidad')` lanza `ValueError`, y como nadie lo captura en el camino, sube por `_convertir_tipos` → `leer` → hasta acá.

#### Líneas 50-52

```python
except ValueError as error:
    print("El lector detectó el problema y detuvo la lectura:")
    print(error)
```

`except ValueError as error` **ataja** el error y lo guarda en la variable `error`. `print(error)` muestra su mensaje. **Salida real:**

```text
El lector detectó el problema y detuvo la lectura:
Error en fila 3, columna 'cantidad': el valor 'veinte' no se puede convertir a int.
```

"Fila 3" porque es la **línea 3 del archivo** (la 1 es el encabezado, la 2 es Cuaderno, la 3 es Lapicera).

> **Para la defensa:**
> - Esto muestra la división de tareas: **el lector lanza** el error, **el programa que lo usa decide** qué hacer (acá, imprimirlo). Si el lector hiciera `print` adentro, el programa no se enteraría.
> - Se captura **solo** `ValueError` (específico), no un `except:` genérico.
> - Si sacaras el `try/except`, el programa terminaría y mostraría el *traceback*. Se empieza a leer por abajo: la última línea es nuestro mensaje. Justo arriba está el camino de llamadas, que de arriba hacia abajo es `ejemplos.py` (la línea que llama a `leer`) → `leer` (`clase.py:77`) → `_convertir_tipos` (`clase.py:182`) → `convertir_valor` (`funciones.py:103`), o sea, el recorrido que hizo la excepción al propagarse, pero al revés. Y más arriba todavía aparece el error original de `int('veinte')` (`funciones.py:101`) unido por "During handling of the above exception, another exception occurred".
> - **Lo que los ejemplos no muestran** (y la consigna pide "situaciones problemáticas"): archivo vacío, fila vacía, filas con distinta cantidad de campos, encabezado vacío o repetido, `encabezado=False`, tabulador. Conviene tener preparados archivitos para mostrarlo en vivo.

---

## 5. Sigamos un dato de punta a punta (Ejemplo 2, variable por variable)

Vamos a hacer de "cámara lenta" del Ejemplo 2 (`ejemplos.py:20-31`). Todos los valores de esta sección salen de correr el código real paso a paso sobre `datos1.csv` (llamando a los métodos internos uno por uno, en el mismo orden que `leer`).

### Paso 0: la configuración (ejemplos.py:21-25)

Después de crear `lector2` y llamar a los cuatro métodos de configuración, el estado del objeto es:

```python
{'delimitador': ',',
 'encabezado': True,
 '_tipos_columnas': {},                       # no se forzó ningún tipo
 '_filtros': [<function <lambda> at 0x...>],  # la lambda de la línea 23 (la dirección cambia en cada corrida)
 '_limite_filas': 2,
 '_rango_filas': (1, 5),                      # tupla
 '_columnas': ['nombre', 'precio']}
```

Todavía no se leyó nada. Ahora `ejemplos.py:27` llama a `lector2.leer("datos1.csv")`.

### Paso 1: `_leer_archivo` (clase.py:84-97) → `lineas`

```python
lineas = ['codigo, nombre, precio, cantidad, disponible',   # índice 0 → línea 1 del archivo
          '001, Cuaderno, 2500.5, 10, true',                 # índice 1 → línea 2
          '002, Lapicera, 800, 25, true',                    # índice 2 → línea 3
          '003, Carpeta, 3200.0, 8, true',                   # índice 3 → línea 4
          '004, Regla, 500, , false',                        # índice 4 → línea 5
          '005, Mochila, 15000.0, 3, true',                  # índice 5 → línea 6
          '006, Goma, 300.5, 50, true']                      # índice 6 → línea 7
```

7 strings, sin el `\r\n` del final. `len(lineas) == 0` es falso, así que no hay error de archivo vacío.

### Paso 2: `_procesar_lineas` (clase.py:99-143) → `encabezados` y `filas_crudas`

| Variable | Valor |
|---|---|
| `primera_linea` (L101) | `'codigo, nombre, precio, cantidad, disponible'` |
| `primeros_elementos` (L105) | `['codigo', 'nombre', 'precio', 'cantidad', 'disponible']` |
| `cant_columnas` (L106) | `5` |
| `encabezados` (L109-117) | `['codigo', 'nombre', 'precio', 'cantidad', 'disponible']` (ninguno vacío ni repetido) |
| `indice_inicio_datos` (L118) | `1` |

Bucle de filas (L126-141), `i` de 1 a 6:

| `i` | `num_fila_archivo` | `elementos` | ¿5 campos? |
|---|---|---|---|
| 1 | 2 | `['001', 'Cuaderno', '2500.5', '10', 'true']` | sí |
| 2 | 3 | `['002', 'Lapicera', '800', '25', 'true']` | sí |
| 3 | 4 | `['003', 'Carpeta', '3200.0', '8', 'true']` | sí |
| 4 | 5 | `['004', 'Regla', '500', '', 'false']` | sí (el vacío cuenta como campo) |
| 5 | 6 | `['005', 'Mochila', '15000.0', '3', 'true']` | sí |
| 6 | 7 | `['006', 'Goma', '300.5', '50', 'true']` | sí |

Resultado: `filas_crudas` es una lista con esas 6 listas. **Todo sigue siendo texto.**

### Paso 3: `_convertir_tipos` (clase.py:145-188) → `tipos_definidos` y `filas_tipadas`

**Control de columnas forzadas (L147-149):** `_tipos_columnas` está vacío, así que el `for` no da ninguna vuelta.

**Parte A: tipo de cada columna (L155-164).** Ninguna está forzada, así que todas se infieren:

| `col_i` | Columna | `valores_columna` | Qué pasa en `inferir_tipo_columna` | Tipo |
|---|---|---|---|---|
| 0 | `codigo` | `['001', '002', '003', '004', '005', '006']` | bool falla en `'001'`; int aprueba los 6 | `int` |
| 1 | `nombre` | `['Cuaderno', 'Lapicera', 'Carpeta', 'Regla', 'Mochila', 'Goma']` | bool, int y float fallan en `'Cuaderno'` | `str` |
| 2 | `precio` | `['2500.5', '800', '3200.0', '500', '15000.0', '300.5']` | bool e int fallan en `'2500.5'`; float aprueba los 6 | `float` |
| 3 | `cantidad` | `['10', '25', '8', '', '3', '50']` | se saca el `''`; bool falla en `'10'`; int aprueba los 5 | `int` |
| 4 | `disponible` | `['true', 'true', 'true', 'false', 'true', 'true']` | bool aprueba los 6 | `bool` |

```python
tipos_definidos = {'codigo': int, 'nombre': str, 'precio': float, 'cantidad': int, 'disponible': bool}
```

(Fijate que acá `codigo` es `int`, a diferencia del Ejemplo 1, porque `lector2` no lo forzó.)

**Parte B: conversión celda por celda (L168-186).** Por ejemplo, para `fila_i = 3` (la Regla), `num_fila_archivo = 3 + 2 = 5`, y:

| Celda | Llamada | Resultado |
|---|---|---|
| codigo | `convertir_valor('004', int, 5, 'codigo')` | `4` |
| nombre | `convertir_valor('Regla', str, 5, 'nombre')` | `'Regla'` |
| precio | `convertir_valor('500', float, 5, 'precio')` | `500.0` |
| cantidad | `convertir_valor('', int, 5, 'cantidad')` | `None` |
| disponible | `convertir_valor('false', bool, 5, 'disponible')` | `False` |

Al final:

```python
filas_tipadas = [
    {'codigo': 1, 'nombre': 'Cuaderno', 'precio': 2500.5,  'cantidad': 10,   'disponible': True},
    {'codigo': 2, 'nombre': 'Lapicera', 'precio': 800.0,   'cantidad': 25,   'disponible': True},
    {'codigo': 3, 'nombre': 'Carpeta',  'precio': 3200.0,  'cantidad': 8,    'disponible': True},
    {'codigo': 4, 'nombre': 'Regla',    'precio': 500.0,   'cantidad': None, 'disponible': False},
    {'codigo': 5, 'nombre': 'Mochila',  'precio': 15000.0, 'cantidad': 3,    'disponible': True},
    {'codigo': 6, 'nombre': 'Goma',     'precio': 300.5,   'cantidad': 50,   'disponible': True},
]
```

Ojo: se convirtieron **las 6 filas**, aunque el rango después se quede con 5 y el resultado final tenga 2.

### Paso 4: `_aplicar_filtros_y_rangos` (clase.py:190-221)

**Validación de columnas (L192-195):** `'nombre'` y `'precio'` están en `encabezados`. Todo bien.

**Rango (L198-200):** `inicio, fin = (1, 5)` → `filas_tipadas[0 : 5]` → las 5 primeras.

```python
filas_en_rango = [Cuaderno, Lapicera, Carpeta, Regla, Mochila]   # (los 5 diccionarios completos)
```

La Goma (fila de datos 6) quedó afuera.

**Filtros + límite (L205-211), vuelta por vuelta.** Recordá: el límite se chequea **al principio** de cada vuelta, y el filtro es `cantidad is not None and cantidad < 15`.

| Vuelta | Fila | `len(filas_filtradas)` al empezar | ¿`>= 2`? (L207) | Filtro (L210) | `filas_filtradas` al terminar la vuelta |
|---|---|---|---|---|---|
| 1 | Cuaderno (cantidad 10) | 0 | no | `10 is not None and 10 < 15` → `True` | `[Cuaderno]` |
| 2 | Lapicera (cantidad 25) | 1 | no | `25 < 15` → `False` | `[Cuaderno]` |
| 3 | Carpeta (cantidad 8) | 1 | no | `8 < 15` → `True` | `[Cuaderno, Carpeta]` |
| 4 | Regla (cantidad `None`) | 2 | **sí → `break`** | no se evalúa | `[Cuaderno, Carpeta]` |
| — | Mochila | — | el bucle ya terminó | no se evalúa | — |

```python
filas_filtradas = [
    {'codigo': 1, 'nombre': 'Cuaderno', 'precio': 2500.5, 'cantidad': 10, 'disponible': True},
    {'codigo': 3, 'nombre': 'Carpeta',  'precio': 3200.0, 'cantidad': 8,  'disponible': True},
]
```

Todavía tienen todas las columnas (por eso el filtro pudo mirar `cantidad`). Y son **los mismos objetos** diccionario que estaban en `filas_tipadas`, no copias.

**Selección de columnas (L214-219):** `_columnas` no es `None`, así que cada fila pasa por `recortar_diccionario(fila, ['nombre', 'precio'])`:

```python
{'codigo': 1, 'nombre': 'Cuaderno', 'precio': 2500.5, ...}  →  {'nombre': 'Cuaderno', 'precio': 2500.5}
{'codigo': 3, 'nombre': 'Carpeta',  'precio': 3200.0, ...}  →  {'nombre': 'Carpeta',  'precio': 3200.0}
```

```python
resultado_final = [{'nombre': 'Cuaderno', 'precio': 2500.5}, {'nombre': 'Carpeta', 'precio': 3200.0}]
```

Se devuelve con el `return` de L219, y `leer` lo devuelve en L82. Es exactamente lo que imprime `ejemplos.py:29`.

### El viaje de un solo dato: la cantidad de la Regla

Para cerrar, seguí **un único valor**, el de la celda vacía de la Regla:

```text
'004, Regla, 500, , false\r\n'   (en el disco, línea 5 del archivo)
   → '004, Regla, 500, , false'                      L89-90: el modo texto pasa \r\n a \n y rstrip lo saca
   → ['004', ' Regla', ' 500', ' ', ' false']        L3 de funciones.py: split por ","
   → ['004', 'Regla', '500', '', 'false']             L6 de funciones.py: strip → la celda queda ''
   → columna cantidad: el '' no vota, la columna es int      funciones.py:38-41 y 56-63
   → convertir_valor('', int, 5, 'cantidad') → None          funciones.py:81-82
   → {'codigo': 4, ..., 'cantidad': None, ...}
   → entra al rango (fila de datos 4 está entre 1 y 5)       clase.py:200
   → al empezar su vuelta ya hay 2 filas: break              clase.py:207-208
   → no aparece en el resultado
```

---

## 6. Lo que tenés que tener clarísimo antes de la defensa

1. **Quién hace qué.** `funciones.py` = 8 **funciones puras**, chicas, una tarea cada una, sin estado. `clase.py` = `LectorCSV`, que guarda **solo la configuración** (en **atributos protegidos**, con `_`) y orquesta el proceso. `ejemplos.py` = el **script** que usa el lector, imprime y arma DataFrames. El lector **nunca imprime**: devuelve datos o lanza excepciones.

2. **El pipeline de `leer` (`clase.py:71-80`):** `_leer_archivo` → `_procesar_lineas` → `_convertir_tipos` → `_aplicar_filtros_y_rangos`. Cada estación entrega una lista completa a la siguiente: renglones → listas de strings → diccionarios con tipos → resultado.

3. **Todo es texto hasta la estación 3.** `separar_linea` = `split(delimitador)` + `strip()` en cada campo. El `strip` es lo que hace que `' nombre'` quede `'nombre'` en `datos1.csv`.

4. **Inferencia por columna entera, en orden bool → int → float → str** (`funciones.py:36-75`). Las celdas vacías no votan; columna toda vacía → `str`. `int` va antes que `float` porque `int("10.0")` falla pero `float("10")` no. Un solo valor raro (`'NA'`, `'veinte'`) vuelve `str` a toda la columna.

5. **Nulos:** solo la celda vacía (o con solo espacios) es nulo, y siempre se guarda como `None`, aunque la columna sea `str` (`funciones.py:81-82`). `'NA'`, `'null'`, `'-'` son texto. En pandas el `None` se ve como `NaN` y la columna entera pasa a float: por eso se muestra también la lista original.

6. **Booleanos:** solo `true`/`false`, sin importar mayúsculas. `bool("false")` da `True` en Python, por eso `convertir_valor` tiene una rama propia para `bool`. `1/0`, `si/no` y `VERDADERO/FALSO` no son booleanos para el lector.

7. **Tipo forzado:** gana siempre sobre la inferencia (`clase.py:158-159`). Si un valor no se puede convertir al tipo forzado, **error con fila y columna**, nunca se cambia el tipo. Dato clave: con tipos inferidos la conversión **no puede fallar** (la inferencia ya probó todo); los errores de conversión solo aparecen con tipos forzados (Ejemplo 4).

8. **Dos numeraciones distintas:** los **mensajes de error** cuentan **líneas del archivo** desde 1 (el encabezado es la 1; por eso `fila_i + 2`, `clase.py:172`). **`establecer_rango`** cuenta **filas de datos** desde 1, con los dos extremos incluidos, y se aplica con `filas_tipadas[inicio - 1 : fin]` (`clase.py:200`). Un rango que se pasa del final no da error.

9. **Orden de las opciones:** rango → filtros → límite → columnas (`clase.py:197-219`, documentado en `clase.py:7-9`). El **límite cuenta filas que cumplen el filtro** y corta apenas junta esa cantidad. Las columnas se recortan al final, así que se puede filtrar por una columna que no se devuelve.

10. **Cortocircuito del `and`:** en `clase.py:207` (`self._limite_filas is not None and ...`) evita comparar con `None` cuando no hay límite; en el filtro del Ejemplo 2 evita `None < 15`. Matiz verificado: en el Ejemplo 2 tal cual está, el límite corta antes de que la Regla llegue al filtro; la guarda se vuelve indispensable si sacás el límite o lo subís a 3.

11. **Errores:** casi todo es `ValueError` (y `FileNotFoundError` para la ruta). Se **propagan** sin capturar por `convertir_valor` → `_convertir_tipos` → `leer` → hasta el `try/except ValueError` de `ejemplos.py:48-52`. El `raise` dentro de un `except` produce encadenamiento implícito ("During handling of the above exception..."); `from error` o `from None` son las alternativas de la cátedra.

12. **Qué se valida al configurar y qué al leer:** al configurar (porque no depende del archivo): delimitador vacío, tipo no soportado, límite negativo, rango inválido. Al leer (porque recién ahí se conoce el encabezado): columna forzada inexistente (`clase.py:147-149`) y columna seleccionada inexistente (`clase.py:192-195`). Lo estructural del archivo (vacío, primera línea vacía, fila vacía, cantidad de campos, encabezado vacío o repetido) se controla en las estaciones 1 y 2.

13. **Encapsulamiento "por convención":** el `_` marca **protegido**, pero Python no lo impide. Los métodos de configuración funcionan como setters con validación y devuelven `None` (no se pueden encadenar; haría falta `return self`). `delimitador` y `encabezado` quedaron públicos (inconsistencia). Los filtros se acumulan y no hay forma de quitarlos. `seleccionar_columnas` guarda la misma lista del usuario (no una copia).

14. **Limitaciones que conviene decir antes de que te las encuentren:** no soporta comillas (`"Rosario, SF"`), ni coma decimal (`1500,50`), ni `VERDADERO/FALSO`; un CSV de Excel con BOM deja un carácter invisible pegado al primer encabezado (se arregla con `encoding="utf-8-sig"`); un archivo que no está en UTF-8 da `UnicodeDecodeError`; el límite **no** ahorra lectura (siempre se lee y se convierte todo el archivo, y un error fuera del rango igual corta).

15. **Para leer los CSV nuevos en vivo:** pararse en la carpeta del proyecto, **mirar el archivo antes** (¿qué separador usa? ¿tiene encabezado?) y hacer:

    ```python
    from modulo.clase import LectorCSV
    import pandas as pd

    lector = LectorCSV(delimitador=";", encabezado=True)   # ajustar a lo que tenga el archivo
    datos = lector.leer("ruta/al/archivo.csv")
    for fila in datos:
        print(fila)
    print(pd.DataFrame(datos))
    ```

    Ojo: si te equivocás de delimitador, muchas veces **no da error**: devuelve una sola columna con el renglón entero. Y si el archivo no tiene encabezado y te olvidás de `encabezado=False`, la primera fila de datos se usa como nombres de columna, en general sin ningún aviso. Si una columna de códigos pierde ceros (`'0341'` → `341`), es `forzar_tipo(columna, str)`.
