# Por qué se eligió cada cosa — Lector de datos tabulares (G24: Berruti, Liali, Vranjes)

> **Para qué sirve este documento.** Para estudiar antes de la defensa oral. No explica *qué* hace el código línea por línea (eso se ve leyéndolo), sino **por qué** es así: por qué una clase, por qué esos métodos, por qué esos nombres, por qué esas estructuras y por qué esos criterios. Para cada decisión importante hay alternativas, ventajas y desventajas y una frase corta para responder en voz alta.
>
> **Cómo se armó.** Todas las afirmaciones sobre el comportamiento del lector se comprobaron ejecutando el código (Python 3.12). Los números de línea son los de los archivos entregados. No conocemos las razones reales que tuvo el grupo: las justificaciones que siguen son **defendibles y honestas**. Cuando una decisión es floja, se dice, y se da la mejor defensa más la mejora posible.
>
> **Convenciones.** `clase.py:105` significa *archivo `modulo/clase.py`, línea 105*. "Fila de datos" es una fila de la tabla (sin contar el encabezado); "línea del archivo" es un renglón del archivo de texto (contando el encabezado). La diferencia importa (ver 5.9).

---

## 0. Índice

1. [Panorama: la arquitectura en un diagrama](#1-panorama-la-arquitectura-en-un-diagrama)
2. [Decisiones de diseño grandes](#2-decisiones-de-diseño-grandes)
   - D1. Combinar POO y programación funcional
   - D2. Separar en dos módulos dentro de un paquete
   - D3. Clase con métodos de configuración (y no una función con muchos parámetros ni un diccionario de opciones)
   - D4. Configuración reutilizable entre lecturas
   - D5. Atributos públicos (`delimitador`, `encabezado`) y protegidos (`_algo`)
   - D6. Métodos protegidos del pipeline y por qué en ese orden
   - D7. Leer todo el archivo en memoria (y no usar generadores)
   - D8. Inferir el tipo mirando TODA la columna
   - D9. Lanzar `ValueError` y detener la lectura (y no saltear filas ni avisar con warnings)
   - D10. `str.split` + `strip` (y no expresiones regulares)
   - D11. `with open(..., encoding="utf-8")`
   - D12. pandas solo en `ejemplos.py`
   - D13. Sin herencia ni polimorfismo explícito (pero con duck typing y funciones de orden superior)
   - D14. Los tipos se representan con las clases `int`, `float`, `str`, `bool`
   - D15. Lista de listas como paso intermedio y lista de diccionarios como resultado
3. [Función por función y método por método](#3-función-por-función-y-método-por-método)
4. [Atributos y variables](#4-atributos-y-variables)
5. [Criterios definidos por el grupo (los que pide la consigna)](#5-criterios-definidos-por-el-grupo)
6. [Relación con la teoría de la cátedra](#6-relación-con-la-teoría-de-la-cátedra)
7. [Limitaciones conocidas y qué cambiaríamos](#7-limitaciones-conocidas-y-qué-cambiaríamos)
8. [Anexo: 15 frases para tener en la punta de la lengua](#8-anexo-15-frases-para-tener-en-la-punta-de-la-lengua)

---

## 1. Panorama: la arquitectura en un diagrama

### 1.1 Archivos

```text
G24_Berruti_Liali_Vranjes/
├── modulo/                 ← PAQUETE (carpeta con módulos). No tiene __init__.py:
│   │                          funciona como "namespace package" (Python >= 3.3).
│   ├── funciones.py        ← MÓDULO: 8 funciones puras y chicas, sin estado (133 líneas)
│   └── clase.py            ← MÓDULO: clase LectorCSV, guarda la CONFIGURACIÓN y
│                              orquesta el proceso (221 líneas)
├── ejemplos.py             ← SCRIPT de demostración: usa LectorCSV, imprime y arma
│                              DataFrames con pandas (52 líneas)
├── datos1.csv              ← coma + espacio después de cada coma, 6 filas, una celda vacía
├── datos2.txt              ← punto y coma, 3 filas
└── derror.csv              ← coma, la línea 3 tiene cantidad = "veinte"
```

### 1.2 Cómo fluye una lectura

```text
Programa usuario (ejemplos.py o la consola)
│
│  lector = LectorCSV(delimitador=",", encabezado=True)      __init__            clase.py:21-36
│  lector.forzar_tipo("codigo", str)                         ┐
│  lector.agregar_filtro(lambda fila: ...)                   │ métodos de
│  lector.establecer_limite(2)                               │ configuración       clase.py:38-63
│  lector.establecer_rango(1, 5)                             │ (setters: validan
│  lector.seleccionar_columnas(["nombre", "precio"])         ┘  y guardan)
│  datos = lector.leer("datos1.csv")                         fachada             clase.py:65-82
▼
leer()
 ├─1─ _leer_archivo(ruta)                       → lineas            : list[str]            clase.py:84-97
 ├─2─ _procesar_lineas(lineas)                  → (encabezados,      : list[str]
 │        └─ separar_linea()   funciones.py:1       filas_crudas)    : list[list[str]]      clase.py:99-143
 ├─3─ _convertir_tipos(encabezados, filas_crudas) → filas_tipadas    : list[dict]           clase.py:145-188
 │        ├─ inferir_tipo_columna()  funciones.py:36
 │        │     └─ es_booleano / es_entero / es_flotante   funciones.py:10, 18, 27
 │        └─ convertir_valor()       funciones.py:78
 └─4─ _aplicar_filtros_y_rangos(encabezados, filas_tipadas) → resultado : list[dict]       clase.py:190-221
          rango (slicing) → filtros (cumple_todos_los_filtros, funciones.py:120)
          → límite (break) → columnas (recortar_diccionario, funciones.py:128)
▼
list[dict]  ──►  ejemplos.py: print(fila) y pd.DataFrame(datos)
```

### 1.3 Quién hace qué

| Pieza | Qué es, con el vocabulario de la cátedra | Responsabilidad | ¿Guarda estado? | ¿Imprime? |
|---|---|---|---|---|
| `modulo/` | Paquete (carpeta con varios módulos) | Agrupar el código reutilizable del lector | — | — |
| `funciones.py` | Módulo de funciones puras | Operaciones chicas sobre texto, columnas y filas | No | No |
| `clase.py` | Módulo con una clase | Guardar la configuración y orquestar el pipeline | Sí, **solo la configuración** | No |
| `ejemplos.py` | Script | Demostrar el uso, mostrar resultados, capturar errores | — | Sí |

### 1.4 Qué entra, qué sale y qué puede fallar en cada etapa

| Etapa | Recibe | Devuelve | Errores que lanza |
|---|---|---|---|
| `_leer_archivo` | ruta | lista de líneas sin `\n`/`\r` | `FileNotFoundError` con mensaje propio; `ValueError` si el archivo tiene 0 bytes. No captura `UnicodeDecodeError` ni `PermissionError`. |
| `_procesar_lineas` | lista de líneas | tupla `(encabezados, filas_crudas)` | `ValueError`: primera línea vacía, nombre de columna vacío o repetido, fila vacía, cantidad incorrecta de campos |
| `_convertir_tipos` | encabezados y filas crudas | lista de diccionarios con valores tipados | `ValueError`: columna de `forzar_tipo` inexistente; valor que no se puede convertir al tipo forzado |
| `_aplicar_filtros_y_rangos` | encabezados y filas tipadas | lista de diccionarios final | `ValueError`: columna seleccionada inexistente. Los errores dentro de un filtro (`KeyError`, `TypeError`) se propagan tal cual. |

### 1.5 La idea en tres líneas

1. **Lo que no tiene estado es función** (separar, detectar un tipo, inferir, convertir, filtrar, recortar) → `funciones.py`.
2. **Lo que tiene estado es objeto**: la configuración, que se arma en varios pasos y se reutiliza → `LectorCSV`.
3. **Lo que muestra queda afuera**: ni la clase ni las funciones imprimen; devuelven datos o lanzan excepciones, y el programa que las usa decide qué mostrar → `ejemplos.py`.

---

## 2. Decisiones de diseño grandes

Cada decisión sigue el mismo esquema: **Qué se hizo / Por qué / Alternativas consideradas / Ventajas y desventajas / Cómo defenderlo en una frase**. Cuando la decisión tiene un punto débil, aparece un apartado **Punto débil y mejora**.

### D1. Combinar POO y programación funcional

**Qué se hizo.** El lector tiene dos mitades: `funciones.py` con 8 funciones puras (`separar_linea`, `es_booleano`, `es_entero`, `es_flotante`, `inferir_tipo_columna`, `convertir_valor`, `cumple_todos_los_filtros`, `recortar_diccionario`) y `clase.py` con la clase `LectorCSV`, que guarda la configuración y llama a esas funciones.

**Por qué.**
- La consigna (3.1) permite POO, programación funcional o una combinación, y pide justificar la elección. El criterio que usamos para repartir el código fue una pregunta: **¿esto necesita recordar algo entre llamadas?**
  - La **configuración** sí: se arma en varios pasos (`forzar_tipo` se llama una vez por columna, `agregar_filtro` una vez por filtro) y tiene que estar disponible cuando se llama a `leer()`. Datos más comportamiento que los usa es justo lo que la cátedra define como objeto.
  - **Separar, detectar tipos, inferir, convertir, filtrar y recortar** no necesitan recordar nada: con la misma entrada dan la misma salida y no tocan nada de afuera. Eso es una **función pura**, y la cátedra (Programación funcional, Fundamentos) destaca que son predecibles, fáciles de probar y de mantener.
- Cada función pura se puede probar sola, sin crear un lector ni un archivo: `es_entero("001")` → `True`, `inferir_tipo_columna(["10", "20", "30.5"])` → `float`.
- Si mañana cambia el criterio de inferencia, se toca una función y la clase no se entera.

**Alternativas consideradas.**
1. **Todo funcional**: una función `leer_tabla(ruta, delimitador=",", tipos=None, filtros=(), ...)`. Se analiza en D3.
2. **Todo POO**: meter también `separar_linea`, `es_entero`, etc. como métodos de `LectorCSV`. Varios de esos métodos no usarían `self` para nada, que es una señal de que no pertenecen a la clase.
3. **Script monolítico**: todo el proceso en un solo bloque de código sin funciones. Imposible de reutilizar y de probar por partes.

**Ventajas y desventajas.**

| Opción | Ventajas | Desventajas |
|---|---|---|
| **Mixto (elegida)** | Cada parte usa la herramienta que le corresponde; funciones probables por separado; la clase solo orquesta | Hay que saber en qué archivo está cada cosa; dos estilos conviviendo |
| Todo funcional | Sin estado: cada llamada es independiente (no hay filtros que se acumulen) | Firma con muchos parámetros; la configuración se repite en cada llamada |
| Todo POO | Todo en un lugar | Métodos que no usan `self`; clase grande; más difícil de probar por partes |
| Monolítico | Rápido de escribir | Ilegible, no reutilizable, imposible de probar por partes |

**Cómo defenderlo en una frase.**
> "Usamos un objeto para lo que tiene estado, que es la configuración, y funciones puras para lo que no lo tiene; así cada pieza se prueba sola y la clase solo coordina."

---

### D2. Separar en dos módulos dentro de un paquete

**Qué se hizo.** La carpeta `modulo/` contiene `funciones.py` y `clase.py`. `clase.py` importa solo lo que usa (`clase.py:11-17`):

```python
from modulo.funciones import (
    separar_linea,
    inferir_tipo_columna,
    convertir_valor,
    cumple_todos_los_filtros,
    recortar_diccionario
)
```

`es_booleano`, `es_entero` y `es_flotante` no se importan porque la clase no las llama: las usa `inferir_tipo_columna` dentro de `funciones.py`. `ejemplos.py` queda fuera del paquete y hace `from modulo.clase import LectorCSV` (`ejemplos.py:2`).

**Por qué.**
- **Modularidad** (Uso de código externo): un módulo es un archivo con código reutilizable y un paquete es una carpeta con varios módulos. Cada archivo tiene una responsabilidad.
- **Módulo vs script** (Scripting): `funciones.py` y `clase.py` contienen solo definiciones, así que importarlos no ejecuta nada. `ejemplos.py` es el script, el que hace algo concreto.
- **Imports explícitos, sin `import *`**: la cátedra desaconseja `from x import *` porque no se sabe cuántos nombres entran ni con cuáles chocan. Importar nombre por nombre deja a la vista de qué depende la clase.

**Alternativas consideradas.**
1. **Un único archivo** `lector.py` con funciones y clase.
2. **Un archivo por etapa** (`lectura.py`, `inferencia.py`, `conversion.py`, `filtros.py`).
3. **La clase dentro de `ejemplos.py`**.

| Opción | Ventajas | Desventajas |
|---|---|---|
| **Paquete con 2 módulos (elegida)** | Separación clara puro / con estado; tamaño de archivo razonable | `from modulo...` solo funciona si la carpeta del proyecto está en `sys.path`: el script que importa tiene que estar en esa carpeta (o la consola abierta ahí) |
| Un solo archivo | Un único import, nada que buscar | Mezcla las dos mitades del diseño; archivo de unas 350 líneas |
| Un archivo por etapa | Máxima separación | Demasiado fragmentado para 8 funciones; muchos imports cruzados |
| Clase en el script | Nada que importar | Importar el lector ejecutaría los ejemplos; viola la consigna (pandas solo en la demo) |

**Punto débil y mejora.**
- La carpeta se llama `modulo` pero, para la cátedra, es un **paquete**. El nombre puede confundir. Un nombre como `lector/` sería más claro.
- No tiene `__init__.py`. Igual se importa (lo verificamos: `modulo.__path__` existe), porque desde Python 3.3 una carpeta sin ese archivo funciona como *namespace package*. Agregar un `__init__.py` vacío lo convierte en un paquete "regular". Los apuntes no hablan de `__init__.py`.
- Los imports son absolutos desde la raíz del proyecto: `python modulo/clase.py` da `ModuleNotFoundError: No module named 'modulo'`. Python agrega a `sys.path` la carpeta del script que se ejecuta (o la carpeta actual, en la consola), así que el programa que importa el lector tiene que estar en la carpeta del proyecto. Ojo con la diferencia: `python <ruta>/ejemplos.py` lanzado desde otra carpeta importa bien, pero falla con `FileNotFoundError` por las rutas relativas de los datos (verificado); para eso sí hay que estar parado en la carpeta del proyecto (3.3).

**Cómo defenderlo en una frase.**
> "Separamos en un módulo de funciones sin estado y otro con la clase que las coordina, dentro de un paquete. El script de demostración queda afuera, así el lector se importa sin efectos colaterales."

---

### D3. Clase con métodos de configuración (y no una función con muchos parámetros ni un diccionario de opciones)

**Qué se hizo.** El constructor recibe solo lo básico del formato (`delimitador`, `encabezado`). Cada opción tiene su propio método: `forzar_tipo`, `agregar_filtro`, `establecer_limite`, `establecer_rango` y `seleccionar_columnas` (`clase.py:38-63`). Al final se llama a `leer(ruta)`.

```python
lector2 = LectorCSV(delimitador=",")
lector2.establecer_rango(1, 5)
lector2.agregar_filtro(lambda fila: fila["cantidad"] is not None and fila["cantidad"] < 15)
lector2.establecer_limite(2)
lector2.seleccionar_columnas(["nombre", "precio"])
datos_filtrados = lector2.leer("datos1.csv")   # ejemplos.py:21-27
```

**Por qué.**
- **Algunas opciones se acumulan.** Se puede forzar el tipo de varias columnas y agregar varios filtros. Un método que se llama N veces lo expresa naturalmente; con una función habría que armar antes un diccionario y una lista.
- **Cada opción se valida en el momento en que se configura** (*fail-fast*): `forzar_tipo("a", list)`, `establecer_limite(-1)` o `establecer_rango(3, 2)` fallan en esa línea, con un mensaje claro, y no recién cuando se lee el archivo. Estos métodos son los **setters** de la cátedra (Encapsulamiento 5.1): validan y después asignan el atributo protegido.
- **Nombres que se explican solos**: `establecer_limite(2)` se entiende sin documentación.
- **`leer()` tiene una firma cortísima** (`leer(ruta_archivo)`), y la interfaz pública es chica: constructor, 5 métodos de configuración y `leer`.

**Alternativas consideradas.**

1. **Una única función con muchos parámetros** (es la que la consigna usa de ejemplo, `leer_tabla`):

   ```python
   leer_tabla(ruta, delimitador=",", encabezado=True, tipos=None,
              filtros=(), limite=None, rango=None, columnas=None)
   ```

   Ventaja real: cada llamada es independiente, no hay estado y no existe el problema de filtros que se acumulan (ver D4). Desventaja: 8 parámetros, todas las validaciones juntas al principio y la configuración se repite si se leen varios archivos iguales.

   **Dato clave para la defensa**: esta interfaz **se puede construir encima de la clase** en pocas líneas. Lo probamos y con la configuración del ejemplo 2 da exactamente el mismo resultado:

   ```python
   def leer_tabla(ruta, delimitador=",", encabezado=True, tipos=None,
                  filtros=(), limite=None, rango=None, columnas=None):
       lector = LectorCSV(delimitador, encabezado)
       for col, tipo in (tipos or {}).items():
           lector.forzar_tipo(col, tipo)
       for f in filtros:
           lector.agregar_filtro(f)
       if limite is not None:
           lector.establecer_limite(limite)
       if rango is not None:
           lector.establecer_rango(*rango)
       if columnas is not None:
           lector.seleccionar_columnas(columnas)
       return lector.leer(ruta)
   # leer_tabla("datos1.csv", rango=(1, 5), filtros=[...], limite=2, columnas=["nombre", "precio"])
   # → [{'nombre': 'Cuaderno', 'precio': 2500.5}, {'nombre': 'Carpeta', 'precio': 3200.0}]
   ```

   O sea, elegir la clase no cierra la puerta a la interfaz funcional.

2. **Un diccionario de opciones**: `LectorCSV({"delimitador": ";", "limite": 2, ...})`. Es flexible, pero un error de tipeo en una clave (`"limte"`) se ignoraría en silencio, salvo que se valide a mano el conjunto de claves permitidas. Además `help()` no muestra qué claves existen y toda la validación termina en un único método lleno de `if`.

3. **Atributos públicos que el usuario asigna directamente** (`lector.limite = 2`). No hay validación. Peor todavía: si el usuario se equivoca en el nombre, Python crea un atributo nuevo sin decir nada. Lo probamos: `lector.limite_filas = 2` (sin guion bajo) no tiene ningún efecto y `leer()` devuelve las 6 filas.

4. **`@property`** (Encapsulamiento 5.4): sintaxis de atributo (`lector.limite = 2`) con validación en el setter y getter incluido. Es una muy buena opción. Los métodos con verbo son igual de claros y `establecer_rango` recibe dos valores, algo que encaja mejor en un método que en una property.

| Opción | Ventajas | Desventajas |
|---|---|---|
| **Métodos de configuración (elegida)** | Opciones acumulables; validación al configurar; nombres autoexplicativos; `leer()` simple | Estado que persiste (filtros acumulados); no se pueden encadenar (devuelven `None`); no hay getters |
| Función `leer_tabla(...)` | Sin estado; una sola llamada | Firma larga; se repite la configuración en cada lectura |
| Diccionario de opciones | Muy flexible | Claves mal escritas pasan sin aviso; sin ayuda en `help()` |
| Atributos públicos | Lo más corto de escribir | Sin validación; un nombre mal escrito crea un atributo nuevo sin error |
| `@property` | Sintaxis de atributo con validación y getter | Más código por opción; el rango de dos valores queda forzado |

**Punto débil y mejora.**
- Los métodos no devuelven nada (o sea, devuelven `None`), así que no se pueden encadenar: `LectorCSV().forzar_tipo("codigo", str).establecer_limite(2)` da `AttributeError: 'NoneType' object has no attribute 'establecer_limite'`. Con `return self` al final de cada método se obtiene el encadenamiento de métodos que muestra la cátedra (Fundamentos de POO, 6.4).
- No hay getters: para consultar la configuración hay que leer atributos protegidos.
- Validan el **valor** pero no el **tipo** (ver 7.2).

**Cómo defenderlo en una frase.**
> "Elegimos un objeto configurable porque las opciones se acumulan y cada una se valida apenas se configura. Si alguien prefiere una única función `leer_tabla`, se escribe en una docena de líneas encima de la clase."

---

### D4. Configuración reutilizable entre lecturas

**Qué se hizo.** El estado del objeto es **solo configuración**. Los datos leídos nunca se guardan como atributo: pasan de una etapa a la siguiente como valores de retorno (`clase.py:71-82`). `_procesar_lineas` devuelve la tupla `(encabezados, filas_crudas)` en lugar de guardarla en `self`. Verificado: `vars(lector)` es igual antes y después de `leer()`.

**Por qué.**
- **El mismo lector puede leer varios archivos con la misma estructura** (por ejemplo, un CSV por mes): se configura una vez y se llama a `leer()` las veces que haga falta.
- **`leer()` es repetible**: con el mismo archivo y la misma configuración da siempre el mismo resultado, porque no deja rastros en el objeto.
- **No quedan datos "viejos"** de una lectura anterior dentro del objeto, y el objeto no retiene en memoria una tabla que ya se devolvió.
- **Los objetos son independientes** (atributos de instancia): en `ejemplos.py` hay cuatro lectores (`lector1`, `lector2`, `lector3`, `lector_error`) y la configuración de uno no afecta a los otros.

**Alternativas consideradas.**
1. **Guardar los datos en el objeto** (`self.datos = ...`) y ofrecer métodos para consultarlos. El objeto pasaría a tener estado de datos además de configuración, con riesgo de consultar datos de una lectura anterior.
2. **Ruta en el constructor**: `LectorCSV("datos1.csv")`. La configuración quedaría atada a un archivo y para leer otro habría que crear otro objeto.
3. **Función sin estado** (ver D3).

| Opción | Ventajas | Desventajas |
|---|---|---|
| **Estado = solo configuración (elegida)** | Reutilizable; `leer()` repetible; objetos independientes | La configuración depende de las columnas del archivo; lo que se configura no se puede deshacer |
| Datos dentro del objeto | Se podrían ofrecer consultas sobre los datos | Estado mutable de datos; datos viejos; más memoria retenida |
| Ruta en el constructor | Un objeto = un archivo, simple de entender | No reutilizable |
| Función sin estado | Nada que se acumule | Configuración repetida en cada llamada |

**Punto débil y mejora.**
- **Los filtros se acumulan** y no hay método para quitarlos: sobre `datos1.csv`, un lector con el filtro `precio > 500` devolvió 4 filas; después de agregarle `precio < 3000`, 2 (verificado, ver 7.2). Mejora: un método `quitar_filtros()`.
- **El límite y el rango no se pueden deshacer**: `establecer_limite(None)` da `TypeError` (compara `None < 0`). `seleccionar_columnas(None)` sí funciona, por casualidad, porque no valida. Mejora: aceptar `None` explícitamente en los setters.
- **La configuración depende de las columnas del archivo**: si `lector1` (con `forzar_tipo("codigo", str)`) lee `datos2.txt`, falla con `"La columna 'codigo' indicada en forzar_tipo no existe en la tabla."` (verificado). Es razonable: la configuración es para archivos con esa estructura.
- **Alias de la lista de columnas**: `seleccionar_columnas` guarda la misma lista que pasó el usuario, no una copia (ver 7.2).

**Cómo defenderlo en una frase.**
> "El objeto recuerda *cómo* leer, no *lo que* leyó: `leer()` no modifica el estado, así que se puede llamar con varios archivos de la misma estructura."

---

### D5. Atributos públicos (`delimitador`, `encabezado`) y protegidos (`_algo`)

**Qué se hizo.** En `__init__` (`clase.py:30-36`):

```python
self.delimitador = delimitador        # público
self.encabezado = encabezado          # público
self._tipos_columnas = {}             # protegido
self._filtros = []                    # protegido
self._limite_filas = None             # protegido
self._rango_filas = None              # protegido
self._columnas = None                 # protegido
```

**Terminología de la cátedra (importante usarla bien en la defensa).** En Python no hay atributos realmente privados. Un nombre que empieza con **un** guion bajo es una **convención** que significa "no tocar desde afuera": la cátedra lo llama atributo **protegido**. Lo que *emula* privacidad es el **doble** guion bajo (`__algo`), que activa el *name mangling* (Python lo guarda como `_LectorCSV__algo`), y la cátedra muestra que también se puede acceder. Entonces: `_limite_filas` es **protegido por convención**, no "privado".

**Por qué.**
- **Los públicos son los parámetros del constructor**, la descripción básica del formato del archivo ("separado por `;`, con encabezado"). Son valores simples (un `str` y un `bool`) que tiene sentido consultar (`lector.delimitador`).
- **Los protegidos tienen estructura interna**: un diccionario de tipos, una lista de funciones, una tupla y `None` como "no configurado". Si el usuario los modificara a mano podría dejar el objeto en un estado incoherente. Por eso solo se cambian a través de los setters, que validan.
- **Mostramos por qué hace falta la protección**: si se saltea la interfaz, `lector._limite_filas = -5` hace que `leer()` devuelva `[]` sin ningún error, y `lector._rango_filas = (0, 2)` también da `[]` (el slice queda `filas[-1:2]`). Es un error lógico silencioso, justo lo que los setters previenen.
- `ejemplos.py` respeta la convención: nunca toca nada que empiece con `_`.

**Alternativas consideradas.**
1. **Todo protegido, más `@property` para `delimitador` y `encabezado`**: es lo que recomienda la cátedra para proteger el estado y mantener la coherencia del objeto.
2. **Todo público**: más simple, sin ninguna protección.
3. **Doble guion bajo** (`__filtros`): no agrega protección real, complica la lectura y solo tiene sentido para evitar choques de nombres con subclases, que acá no existen.

| Opción | Ventajas | Desventajas |
|---|---|---|
| **Mixto (elegida)** | Lo básico es accesible; lo complejo se toca solo con métodos | Inconsistencia: `delimitador` tiene una regla que se puede saltear |
| Todo protegido + `@property` | Toda regla se respeta siempre; getters incluidos | Más código |
| Todo público | Lo más simple | Ninguna validación garantizada |
| Doble guion bajo | "Parece" privado | Solo emula privacidad; innecesario sin herencia |

**Punto débil y mejora.** La regla "el delimitador no puede ser vacío" se controla solo en `__init__` (`clase.py:27-28`). Como el atributo es público, `lector.delimitador = ""` la saltea, y `leer()` falla con `ValueError: empty separator`, el mensaje técnico de `str.split` y no el del grupo. `encabezado` directamente no se valida: `LectorCSV(encabezado="no")` se toma como `True` porque un string no vacío es verdadero. La mejora, con la herramienta de la cátedra, es una property (probada):

```python
@property
def delimitador(self):
    return self._delimitador

@delimitador.setter
def delimitador(self, valor):
    if not isinstance(valor, str) or valor == "":
        raise ValueError("El delimitador debe ser un texto no vacío.")
    self._delimitador = valor
```

Como `__init__` hace `self.delimitador = delimitador`, la validación también corre al construir el objeto.

**Cómo defenderlo en una frase.**
> "Lo que se pasa al construir quedó público; lo que tiene estructura interna quedó protegido y solo se cambia con métodos que validan. Reconocemos que `delimitador` debería ser una property para que su validación no se pueda saltear."

---

### D6. Métodos protegidos del pipeline y por qué en ese orden

**Qué se hizo.** `leer()` (`clase.py:65-82`) es una **fachada**: no hace el trabajo, coordina cuatro métodos protegidos en secuencia, y cada resultado alimenta al siguiente:

```python
lineas = self._leer_archivo(ruta_archivo)                                  # 1
encabezados, filas_crudas = self._procesar_lineas(lineas)                  # 2
filas_tipadas = self._convertir_tipos(encabezados, filas_crudas)           # 3
filas_filtradas = self._aplicar_filtros_y_rangos(encabezados, filas_tipadas)  # 4
return filas_filtradas
```

**Por qué protegidos.** Son el **interior** de la clase. La cátedra usa la analogía del auto: quien maneja usa los pedales (la interfaz pública: configurar y `leer`) y no necesita conocer la caja de cambios (el pipeline). Al marcarlos con `_`, `help(LectorCSV)` no los muestra (verificado), así que la ayuda documenta exactamente la interfaz pública. Además, se puede cambiar cómo se separan o se convierten las filas sin tocar `ejemplos.py`.

**Por qué cuatro métodos y no uno.** Cada etapa tiene una sola responsabilidad y un tipo de error propio (problemas del archivo / de estructura / de tipos / de selección). `leer()` queda como un índice del proceso que se lee en cinco renglones.

**Por qué siguen siendo métodos y no funciones de `funciones.py`.** Necesitan la configuración: `_procesar_lineas` usa `self.delimitador` y `self.encabezado`; `_convertir_tipos` usa `self._tipos_columnas` y `self.encabezado`; `_aplicar_filtros_y_rangos` usa `_rango_filas`, `_filtros`, `_limite_filas` y `_columnas`. Como funciones sueltas necesitarían muchos parámetros. `_leer_archivo` no usa `self`, pero **lee un archivo**, que es interactuar con algo externo: no es una función pura y por eso no corresponde ponerla en `funciones.py`, que contiene solo funciones puras.

**Por qué ese orden.** Es el orden que imponen las **dependencias entre los datos**:

1. **Leer** el archivo: sin líneas no hay nada que hacer.
2. **Separar y validar la estructura** antes de inferir: la inferencia arma columnas con `fila[col_i]`, así que necesita que todas las filas tengan la misma cantidad de campos y que se conozca el encabezado.
3. **Convertir tipos antes de filtrar**: los filtros comparan valores (`fila["cantidad"] < 15`). Sobre texto, eso daría `TypeError` (`'10' < 15`) o, peor, una comparación alfabética entre strings (`'10' < '8'` es `True`).
4. **Filtrar y recortar al final**: trabaja sobre datos ya tipados. Dentro de esta etapa, el orden rango → filtros → límite → columnas se justifica en 5.8.

**Alternativas consideradas.**
1. **Un único método `leer()` largo**, de unas 130 líneas.
2. **Etapas como funciones sueltas** que reciben la configuración por parámetro: más "funcional", con firmas largas.
3. **Otro orden**: filtrar sobre el texto crudo antes de convertir (ahorra conversiones de filas descartadas), pero el usuario tendría que escribir filtros sobre strings.

| Opción | Ventajas | Desventajas |
|---|---|---|
| **4 métodos protegidos coordinados por `leer` (elegida)** | Cada etapa se entiende sola; interfaz pública mínima | El primer error reportado es el de la etapa más temprana, no el de la primera línea del archivo |
| Un único método | Todo a la vista | Difícil de leer, de mantener y de explicar |
| Funciones sueltas | Más puras | Firmas largas; la configuración viaja por todos lados |
| Filtrar antes de convertir | Menos conversiones | Filtros sobre strings: comparaciones incorrectas |

**Consecuencia del orden, para tenerla clara.** Como cada etapa procesa el archivo entero antes de pasar a la siguiente, el error que se informa es el de la **etapa** más temprana. Ejemplo verificado: si la línea 2 tiene un valor no convertible y la línea 3 tiene un campo de más, se informa el de la línea 3 ("Cantidad incorrecta de elementos"), porque la estructura se valida antes que los tipos. Por el mismo motivo, un error de conversión en una fila **fuera del rango pedido** igual detiene la lectura.

**Cómo defenderlo en una frase.**
> "`leer()` es una fachada que coordina cuatro etapas protegidas, en el orden que piden los datos: no se puede inferir sin columnas alineadas, ni filtrar sin tipos."

---

### D7. Leer todo el archivo en memoria (y no usar generadores)

**Qué se hizo.** `_leer_archivo` guarda todas las líneas en una lista (`clase.py:88-90`). Después se construyen `filas_crudas` (lista de listas) y `filas_tipadas` (lista de diccionarios). Mientras dura `leer()` conviven unas tres representaciones del archivo.

**Por qué.**
- **La inferencia necesita ver la columna entera antes de convertir** (D8): para saber si una columna es `int` hay que haber mirado todos sus valores. Con lectura incremental, o se guarda todo igual o hay que leer el archivo dos veces.
- **Un generador es de un solo uso**: lo probamos y la segunda vez que se recorre no da nada (`list(g)` devuelve una lista vacía). No se puede recorrer una vez para inferir y otra para convertir sin volver a abrir el archivo.
- **Las listas permiten índice y slicing**, y eso simplifica el rango (`filas_tipadas[inicio - 1 : fin]`) y la numeración de los errores.
- **Los archivos del TP son chicos**. El costo es lineal: tiempo y memoria O(L·K), con L filas y K columnas.

**Alternativas consideradas.**
1. **Generador + dos pasadas**: `_leer_archivo` como función generadora (probado):

   ```python
   def leer_lineas(ruta):
       with open(ruta, "r", encoding="utf-8") as archivo:
           for linea in archivo:
               yield linea.rstrip("\n\r")
   ```

   Una pasada para inferir los tipos y otra para convertir y filtrar. Usa mucha menos memoria, pero lee el archivo dos veces y el código es más complejo.
2. **Inferir con una muestra** (las primeras N filas): más rápido, pero si la fila N+1 no encaja hay que decidir entre lanzar un error o cambiar el tipo a mitad de camino.
3. **Lectura incremental solo cuando todos los tipos están forzados**: ahí no hace falta inferir y se podría cortar la lectura al llegar al límite.

| Opción | Ventajas | Desventajas |
|---|---|---|
| **Todo en memoria (elegida)** | Simple; indexable; una sola lectura del archivo | Memoria O(L·K); el límite no ahorra lectura |
| Generador + 2 pasadas | Memoria mínima | Lee dos veces; más complejo |
| Muestra de N filas | Rápido | Puede equivocarse con filas posteriores |
| Incremental con tipos forzados | Cortaría en el límite | Dos caminos de código distintos |

**Punto débil.** **El límite no ahorra lectura**: siempre se lee, separa, infiere y convierte todo el archivo; el límite solo corta el bucle de filtrado. En una medición con 200.000 filas, con y sin `establecer_limite(1)` tardó prácticamente lo mismo (alrededor de 0,8 s). Para los tamaños del TP es irrelevante.

**Cómo defenderlo en una frase.**
> "Como inferimos el tipo mirando toda la columna, necesitamos tener todo el archivo antes de convertir; con un generador habría que leerlo dos veces. Para archivos chicos, la lista es más simple."

---

### D8. Inferir el tipo mirando TODA la columna

**Qué se hizo.** En `_convertir_tipos` (`clase.py:160-164`), para cada columna sin tipo forzado se arma `valores_columna` con el valor de **todas** las filas del archivo, no solo las del rango ni solo las que pasan los filtros, y se llama a `inferir_tipo_columna`.

**Por qué.**
- **Criterio "todos o nada"**: una columna es `int` solo si **todos** sus valores no vacíos se pueden leer como `int`. Esto tiene una consecuencia muy buena: **con un tipo inferido la conversión nunca falla**, porque la inferencia usa exactamente las mismas pruebas que la conversión (`int(texto)`, `float(texto)`, comparar con `"true"`/`"false"`). Lo verificamos con todas las combinaciones de hasta 3 valores sacados de una lista de 10 valores típicos. Los errores de conversión solo pueden aparecer con tipos **forzados**.
- **El tipo de una columna no depende de qué filas pidas**: con `establecer_rango(2, 2)` se obtiene solo Lapicera, y su precio sale `800.0` (float), igual que en la lectura completa (verificado). Si se infiriera solo con el rango, ese único valor `"800"` daría `int` (`inferir_tipo_columna(["800"])` → `int`): la misma columna saldría `int` en una consulta y `float` en otra.
- **Hay un círculo que esto evita**: los filtros necesitan valores ya tipados para comparar, así que no se puede inferir "solo con las filas que pasan el filtro".
- **Columnas homogéneas**: todas las filas tienen el mismo tipo en esa columna, que es la idea de "variable" y lo que espera pandas.

**Alternativas consideradas.**
1. **Inferir solo con las filas del rango**: el tipo cambiaría según la consulta.
2. **Inferir con una muestra** (ver D7).
3. **Tipo por celda** (cada valor con su propio tipo): una columna podría tener `10` (int) y `"abc"` (str) mezclados, las comparaciones de los filtros fallarían a mitad de camino y se pierde la idea de columna.

| Opción | Ventajas | Desventajas |
|---|---|---|
| **Toda la columna (elegida)** | Determinista; la conversión no falla nunca con tipos inferidos | Una sola celda rara (`"NA"`, `"15%"`) vuelve `str` a toda la columna |
| Solo el rango | Parece más "local" | El tipo depende de la consulta |
| Muestra | Rápido | Puede equivocarse |
| Tipo por celda | Ningún valor "pierde" su tipo | Columnas heterogéneas; filtros frágiles |

**Cómo defenderlo en una frase.**
> "Inferimos con toda la columna para que el tipo no dependa de qué filas pidas y para garantizar que, si la inferencia dice `int`, todos los valores se pueden convertir a `int`."

---

### D9. Lanzar `ValueError` y detener la lectura (y no saltear filas ni avisar con warnings)

**Qué se hizo.** Ante cualquier problema de estructura (archivo vacío, fila vacía, cantidad de campos distinta, encabezado vacío o repetido) o un valor que no se puede convertir al tipo **forzado**, el lector lanza `ValueError` con un mensaje que dice qué pasó y, cuando corresponde, en qué fila y columna. La lectura se detiene en el primer problema. Ni la clase ni las funciones imprimen nada: verificamos que no hay ningún `print(` en `clase.py` ni en `funciones.py`. Quien usa el lector decide qué hacer con el error (`ejemplos.py:48-52`):

```python
try:
    lector_error.leer("derror.csv")
except ValueError as error:
    print("El lector detectó el problema y detuvo la lectura:")
    print(error)
# → Error en fila 3, columna 'cantidad': el valor 'veinte' no se puede convertir a int.
```

**Por qué.**
- **La consigna lo permite explícitamente** (3.5): no hace falta seguir leyendo ante cualquier problema, se puede detener e informar, siempre que el mensaje identifique qué pasó, la fila y la columna.
- **Un dato mal leído en silencio es peor que un error**: si se salteara una fila con un campo de más, los totales y promedios que calcule el usuario serían incorrectos y nadie se enteraría.
- **Criterio de la cátedra (Excepciones)**: se lanza una excepción cuando una operación no puede cumplir lo que se le pidió con los datos recibidos. Un `print` solo le avisa a quien mira la pantalla; la excepción le avisa **al programa**, que puede capturarla. Los setters de ejemplo de Encapsulamiento usan `print`; el grupo siguió el criterio más nuevo, el de la unidad de Excepciones.
- **Con tipos forzados, la consigna (3.3) prohíbe reemplazar el tipo pedido por uno inferido**. Si el usuario pidió `int` y aparece `"veinte"`, no queda otra que informar el error.
- **Matiz importante: durante la inferencia NO se lanza nada.** `es_entero("veinte")` devuelve `False` (`funciones.py:18-24`): que un valor no sea entero es un resultado esperado, se prueba el siguiente tipo. Solo es error cuando el usuario **exigió** ese tipo.

**Alternativas consideradas.**
1. **Saltear las filas problemáticas y seguir** (modo tolerante). Se pierden datos sin aviso.
2. **Avisar con `warnings.warn` y seguir**. La cátedra reserva el warning para cuando todavía se puede dar un resultado razonable. Para una fila con campos de más no hay resultado razonable (¿qué campo sobra?). Sí habría buenos candidatos para warnings: un rango que cae fuera de la tabla, una columna toda vacía, un `"NA"` que convierte una columna numérica en `str` (ver 7.4).
3. **Juntar todos los errores y reportarlos al final**. Muy útil para corregir un archivo de una vez, pero más complejo.
4. **Devolver un código de error** (por ejemplo `None` o una lista de errores junto con los datos). El llamador lo puede ignorar sin darse cuenta.

| Opción | Ventajas | Desventajas |
|---|---|---|
| **`ValueError` y detener (elegida)** | Imposible ignorar el problema; mensaje con fila y columna; el llamador decide | Un único error por ejecución; un archivo con un detalle no se lee |
| Saltear filas | Siempre devuelve algo | Pérdida silenciosa de datos |
| Warnings | Se lee igual y se avisa | No sirve cuando no hay resultado razonable |
| Juntar errores | Ves todos los problemas juntos | Más complejo; hay que decidir qué devolver |
| Código de error | Sin excepciones | Fácil de ignorar |

**Punto débil y mejora.**
- **Todo es `ValueError`** (salvo la ruta inexistente). Un `except ValueError` en el programa usuario también atrapa errores que no son del lector: por ejemplo `UnicodeDecodeError` (que es subclase de `ValueError`) o un `ValueError` dentro de un filtro. La mejora alineada con la cátedra es una **excepción propia**: `class LectorCSVError(ValueError)`. Al heredar de `ValueError`, el `except ValueError` de `ejemplos.py` la sigue capturando, pero además se puede capturar solo lo del lector, y puede guardar `fila` y `columna` como atributos.
- **Encadenamiento implícito**: en `funciones.py:102-106` y `111-115`, el `ValueError` nuevo se lanza dentro de un `except`. Si nadie lo captura, el traceback muestra dos errores unidos por *"During handling of the above exception, another exception occurred"*. Con `raise ... from error` la relación queda explícita (*"The above exception was the direct cause..."*) y con `from None` se oculta la original (Excepciones 9.2).
- **Los errores dentro de un filtro no dicen la fila**: un `KeyError` por columna mal escrita o un `TypeError` por comparar `None < 15` se propagan con el mensaje técnico de Python.

**Cómo defenderlo en una frase.**
> "Preferimos que el lector se detenga con un mensaje que diga fila y columna antes que devolver datos incorrectos sin avisar; y no imprime: lanza la excepción para que el programa que lo usa decida."

---

### D10. `str.split` + `strip` (y no expresiones regulares)

**Qué se hizo.** `separar_linea` (`funciones.py:1-7`) corta con `linea.split(delimitador)` y le aplica `strip()` a cada campo.

**Por qué.**
- **La consigna permite expresiones regulares pero no las exige** (3.2). Con `split` alcanza para el formato pedido.
- **`split` acepta delimitadores de varios caracteres**: `"a||b|| c".split("||")` funciona (verificado con `" | "` y con `"||"`). Eso cubre la extensión opcional de la consigna, "un delimitador arbitrario, incluso de más de un carácter", **sin escapar nada**. Con `re.split`, delimitadores como `|`, `.` o `+` son caracteres especiales y habría que usar `re.escape`.
- **`strip()` por campo** limpia los espacios que hay después de cada coma en `datos1.csv` (`codigo, nombre, precio`). Sin eso, las claves serían `" nombre"` y `" true"` no se reconocería como booleano. Solo limpia los **bordes**: `"Buenos Aires"` conserva su espacio interno.
- **Es la herramienta de la Unidad 1** (métodos de cadenas) y se entiende sin conocimientos extra.

**Alternativas consideradas.**
1. **Expresión regular** que separa y limpia a la vez: `re.split(r"\s*,\s*", linea)` da `['001', 'Cuaderno', '2500.5', '10', 'true']` para la primera fila de datos de `datos1.csv` (verificado). Es más compacta, pero hay que construir el patrón según el delimitador y escapar los caracteres especiales.
2. **Recorrer carácter por carácter con estado** ("¿estoy dentro de comillas?"). Es la única forma de soportar campos con el delimitador adentro (`"Rosario, SF"`), pero es bastante más código.
3. **Módulo `csv`**: prohibido por la consigna.

| Opción | Ventajas | Desventajas |
|---|---|---|
| **`split` + `strip` (elegida)** | Simple; delimitadores multi-carácter sin escapar | No soporta comillas |
| Regex | Separar y limpiar en un paso | Hay que escapar; menos legible; tampoco resuelve las comillas fácilmente |
| Carácter por carácter | Soportaría comillas y celdas multilínea | Mucho más complejo y propenso a errores |

**Punto débil.** No hay soporte de comillas: `"Rosario, SF",2` da error de cantidad de campos y `"hola"` se conserva con las comillas incluidas. Es una limitación compartida por cualquier solución basada en cortar la línea; la consigna no exige comillas.

**Cómo defenderlo en una frase.**
> "`split` ya acepta separadores de cualquier largo sin escapar nada, y `strip` por campo limpia los bordes sin tocar los espacios internos; una regex no nos agregaba nada para este formato."

---

### D11. `with open(..., encoding="utf-8")`

**Qué se hizo.** `clase.py:86-92`:

```python
try:
    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        lineas = []
        for linea in archivo:
            lineas.append(linea.rstrip("\n\r"))
except FileNotFoundError:
    raise FileNotFoundError(f"No se encontró el archivo en la ruta: {ruta_archivo}")
```

**Por qué.**
- **`encoding="utf-8"` explícito**: la cátedra (Entrada/salida) recomienda incluirlo siempre, porque en Windows el encoding por defecto es cp1252. Lo comprobamos en Windows: un CSV en UTF-8 con "Córdoba", leído sin `encoding`, da "CÃ³rdoba" **sin ningún error**, o sea, datos corruptos en silencio.
- **`with`**: es un *context manager*, cierra el archivo al salir del bloque **aunque ocurra un error en el medio**. La cátedra lo prefiere a `close()` manual (que se puede olvidar o no ejecutarse si algo falla antes) y a `try/finally` para archivos.
- **El archivo está abierto el menor tiempo posible**: dentro del `with` solo se juntan las líneas; separar, inferir, convertir y filtrar se hace con el archivo ya cerrado.
- **`"r"` explícito**: es el modo por defecto, pero deja a la vista que el lector solo lee.
- **`rstrip("\n\r")` y no `strip()`**: `strip()` sin argumentos borra todos los blancos, tabulaciones incluidas. Con delimitador tab y el último campo vacío se perdería una columna: `"1\t2\t\n".strip().split("\t")` da `['1', '2']`, mientras que con `rstrip("\n\r")` da `['1', '2', '']`, que es lo correcto (el último valor queda `None`). El `\r` se incluye por robustez: en modo texto Python ya traduce `\r\n` a `\n` (`datos1.csv` tiene finales CRLF y funciona), pero sacar un `\r` suelto no cuesta nada.
- **`FileNotFoundError` con mensaje propio y el mismo tipo**: el mensaje incluye la ruta y el tipo se mantiene, así quien llama puede seguir capturando `FileNotFoundError`.

**Alternativas consideradas.**
1. **`open` + `close()` manual**: si algo falla antes del `close()`, el archivo queda abierto.
2. **`try/finally`**: funciona, pero para archivos la cátedra recomienda el context manager.
3. **`encoding="utf-8-sig"`**: igual que UTF-8, pero además descarta el BOM que agrega Excel al principio del archivo. Es una mejora de una sola palabra (ver 7.1).
4. **No indicar encoding**: depende del sistema operativo.

| Opción | Ventajas | Desventajas |
|---|---|---|
| **`with` + `utf-8` (elegida)** | Cierre garantizado; mismo resultado en cualquier sistema | No maneja BOM, latin-1 ni UTF-16 |
| `close()` manual | Explícito | Se puede olvidar o saltear por un error |
| `try/finally` | Cierre garantizado | Más verboso para el mismo resultado |
| `utf-8-sig` | Además tolera el BOM de Excel | Ninguna relevante |
| Sin encoding | Menos código | Corrupción silenciosa en Windows |

**Punto débil y mejora.**
- Con un CSV de Excel con BOM, la primera clave queda `'\ufeffcodigo'` (así la muestra el `print` de la fila; verificado) y `forzar_tipo("codigo", ...)` falla con "no existe en la tabla". Se arregla con `encoding="utf-8-sig"`.
- Archivos en latin-1, cp1252 o UTF-16 dan `UnicodeDecodeError` sin mensaje propio.
- La excepción `FileNotFoundError` nueva pierde los atributos `errno` y `filename` de la original (quedan en `None`). Un `raise ... from error` conservaría la relación.

**Cómo defenderlo en una frase.**
> "`with` garantiza que el archivo se cierre aunque algo falle, y el `encoding` explícito evita que en Windows los acentos se corrompan sin aviso, como recomienda la cátedra."

---

### D12. pandas solo en `ejemplos.py`

**Qué se hizo.** El paquete `modulo/` usa solo Python estándar. pandas aparece únicamente en el script de demostración: `import pandas as pd` (`ejemplos.py:1`) y `pd.DataFrame(...)` en `ejemplos.py:15`, `31` y `42`. En cada ejemplo se muestra **primero la lista de diccionarios** y después el DataFrame.

**Por qué.**
- **Lo exige la consigna**: prohíbe usar los lectores de pandas para leer (3.2) y pide que la conversión a DataFrame se haga en el programa de demostración, fuera del código del lector (sección 4).
- **Separación lógica / presentación**: el lector no sabe ni le importa cómo se mostrarán los datos.
- **El lector no depende de instalar nada**: se puede usar en cualquier Python.
- **Se muestra también la lista porque pandas cambia la representación** (la consigna lo advierte). Verificado con `datos1.csv`: la columna `cantidad`, que en la lista tiene `int` y un `None`, en el DataFrame aparece como `10.0, 25.0, 8.0, NaN, ...` porque pandas la pasa a `float64` (el tipo entero de pandas no admite `NaN`). Y en otro caso probado, el texto `"None"` y el nulo `None` se ven idénticos en el DataFrame.

**Alternativas consideradas.**
1. **Un método `a_dataframe()` dentro de `LectorCSV`**: cómodo, pero acopla el lector a pandas y contradice la consigna.
2. **No usar pandas** y mostrar con `print` formateado: no hace falta, la consigna lo sugiere como opción.

| Opción | Ventajas | Desventajas |
|---|---|---|
| **pandas solo en la demo (elegida)** | Cumple la consigna; lector sin dependencias | Hay que instalar pandas para correr `ejemplos.py` (no hay `requirements.txt`) |
| `a_dataframe()` en la clase | Cómodo | Acopla el lector a pandas |
| Sin pandas | Cero dependencias | Tabla menos prolija |

**Cómo defenderlo en una frase.**
> "El lector devuelve datos de Python puro; mostrarlos es responsabilidad del programa que lo usa, y por eso mostramos también la lista, porque pandas cambia `None` por `NaN` y los enteros por flotantes."

---

### D13. Sin herencia ni polimorfismo explícito (pero con duck typing y funciones de orden superior)

**Qué se hizo.** `class LectorCSV:` (`clase.py:20`) no hereda de ninguna clase propia: solo hereda implícitamente de `object` (verificado: `LectorCSV.__mro__ == (LectorCSV, object)`). No hay subclases, clases abstractas ni métodos mágicos propios aparte de `__init__`. Sin embargo, los filtros funcionan por **duck typing** y `cumple_todos_los_filtros` es una **función de orden superior**.

**Por qué.**
- **Hay un único tipo de lector.** Las variantes (coma, punto y coma, tab, separadores de varios caracteres, con o sin encabezado) son **datos** (el valor de `delimitador` y `encabezado`), no comportamientos distintos. Una subclase `LectorTSV` solo cambiaría un valor por defecto: un parámetro es más simple.
- **Los tres principios de la POO, con honestidad**:
  - *Encapsulamiento*: sí, y es el principio más usado (interfaz pública chica, atributos y métodos protegidos, setters con validación).
  - *Herencia*: no explícita.
  - *Polimorfismo*: no con clases propias, pero sí el implícito de Python. El operador `in` se usa sobre una **lista** (`clase.py:115`, `148`, `194`) y sobre un **diccionario** (`clase.py:158`): mismo "mensaje", implementación distinta. Y los filtros: el lector manda a cada uno el mismo mensaje (llamarlo con la fila) y cada uno responde a su manera.
- **Duck typing en los filtros** (`funciones.py:123`: `if not funcion(fila_diccionario):`). No se pregunta de qué clase es el filtro, solo se lo llama. Sirve una `lambda`, una función con `def`, un `functools.partial` o un objeto de una clase con `__call__`: los probamos todos. La consigna pide "una función que evalúe los valores y devuelva un booleano", y con duck typing eso se cumple de la manera más flexible.
- **Funciones como objetos de primera clase**: `self._filtros` es una lista de funciones (`clase.py:33` y `47`), como el ejemplo de la cátedra de guardar funciones en una lista y llamarlas después. Los tipos también se guardan como valores (D14).

**Alternativas consideradas.**
1. **Jerarquía `Lector(ABC)`** con `@abstractmethod leer` y subclases `LectorCSV`, `LectorTSV`, `LectorAnchoFijo`. Tiene sentido solo si hubiera varios formatos con lógica distinta; acá sería sobre-ingeniería.
2. **Una clase `Filtro` abstracta** con un método `evaluar(fila)`. El usuario tendría que escribir una clase por cada condición: mucha ceremonia para una línea de `lambda`.
3. **Objetos preconfigurados con `@classmethod`** (como `Sandwich.jyq()` de la cátedra): `LectorCSV.tsv()` devolvería `cls(delimitador="\t")`. Es la alternativa a crear subclases solo para cambiar un valor por defecto.

| Opción | Ventajas | Desventajas |
|---|---|---|
| **Una clase + duck typing (elegida)** | Simple; cualquier callable sirve de filtro | No hay validación temprana del filtro: `agregar_filtro(5)` falla recién en `leer()` con `TypeError: 'int' object is not callable` |
| Jerarquía con ABC | Contrato formal; extensible a otros formatos | Innecesaria con un solo formato |
| Clase `Filtro` | Contrato explícito para filtros | Mucho código para condiciones simples |
| `@classmethod` preconfigurados | Atajos legibles sin herencia | Poco valor con un solo parámetro |

**Dónde sí tendría sentido la herencia.** En **excepciones propias**: `class LectorCSVError(ValueError)` con hijas como `FormatoArchivoError` o `ConversionTipoError`. Es exactamente el uso de herencia que muestra la unidad de Excepciones.

**Cómo defenderlo en una frase.**
> "No usamos herencia porque hay un solo tipo de lector y las variantes son datos, no comportamientos. El polimorfismo aparece de la forma natural en Python: cualquier cosa que se pueda llamar con una fila sirve como filtro."

---

### D14. Los tipos se representan con las clases `int`, `float`, `str`, `bool`

**Qué se hizo.** El usuario escribe `forzar_tipo("codigo", str)`, pasando **la clase** `str`, no el texto `"str"`. `_tipos_columnas` guarda `{"codigo": str}`, `inferir_tipo_columna` devuelve una clase (`return bool`, `return int`...) y `convertir_valor` compara `tipo_esperado == str` (`funciones.py:84`, `87`, `99`, `108`).

**Por qué.**
- **En Python los tipos son clases** y las clases también son objetos (Fundamentos de POO, "¿Clases o tipos?"), así que pueden ser argumentos y valores de un diccionario.
- **Una sola representación para tipos inferidos y forzados**: `tipos_definidos` (`clase.py:152-164`) mezcla los dos orígenes sin traducir nada.
- **Menos errores de tipeo**: con strings habría que decidir si se acepta `"int"`, `"Int"`, `"entero"`... Con la clase, un nombre mal escrito (`forzar_tipo("a", itn)`) es un `NameError` inmediato. Y si alguien pasa el texto `"int"`, `forzar_tipo` lo rechaza con su propio mensaje (`"Tipo no válido. Use int, float, str o bool."`, verificado).
- **Es lo que espera un usuario de Python**: es el mismo estilo que `dtype=int` en otras bibliotecas.

**Alternativas consideradas.** (a) Strings `"int"`, `"float"`...; (b) constantes propias (`TIPO_ENTERO = "int"`); (c) un `Enum`, que no se ve en la materia.

| Opción | Ventajas | Desventajas |
|---|---|---|
| **Clases de Python (elegida)** | Natural; sin traducción; error inmediato si se escribe mal | Hay que explicar que una clase es un valor |
| Strings | Fácil de leer desde un archivo de configuración | Variantes de escritura; traducción a la clase |
| Constantes propias | Centralizado | Más nombres para aprender |

**Detalle fino.** Aunque los tipos son llamables (`int("10")` da `10`), `convertir_valor` no hace simplemente `tipo_esperado(texto)`, porque **`bool("false")` da `True`** (todo string no vacío es verdadero). Por eso `bool` tiene una rama propia (ver 3.1.6).

**Cómo defenderlo en una frase.**
> "Usamos las clases mismas porque en Python los tipos son objetos: así inferidos y forzados se guardan igual y no hay strings mal escritos."

---

### D15. Lista de listas como paso intermedio y lista de diccionarios como resultado

**Qué se hizo.** `_procesar_lineas` produce `filas_crudas`, una **lista de listas de str** (`clase.py:125-141`). Recién `_convertir_tipos` arma la **lista de diccionarios** con valores tipados (`clase.py:167-188`).

**Por qué.**
- **El resultado es una lista de diccionarios porque lo pide la consigna**, y además es la mejor estructura para este caso: la lista conserva el **orden** de las filas (secuencia ordenada) y cada diccionario es un **registro** al que se accede por nombre (`fila["cantidad"]`). La cátedra advierte que mantener listas paralelas sincronizadas es un "dolor de cabeza" y propone registros.
- **El paso intermedio es lista de listas porque todavía no se pueden convertir los valores**: el tipo de cada columna depende de **todos** sus valores (D8). Con filas como listas, la columna `col_i` se arma con `fila[col_i]` (acceso por índice, O(1)).
- **El paralelismo por índice** (`encabezados[col_i]` y `elementos_fila[col_i]`, `clase.py:178-179`) queda encerrado dentro de `_convertir_tipos` y desaparece al armar los diccionarios.

**Alternativas consideradas.**
1. **Diccionarios de str desde el principio**, convirtiéndolos después en el lugar: mezcla datos crudos y tipados en la misma estructura y obliga a modificar diccionarios ya creados.
2. **Almacenamiento por columnas** (un diccionario de listas, `{"precio": ["2500.5", "800", ...]}`): la inferencia sería más natural (cada columna ya es una lista), pero la salida que pide la consigna es por filas, así que al final habría que reorganizar todo.

| Opción | Ventajas | Desventajas |
|---|---|---|
| **Lista de listas → lista de dicts (elegida)** | Cada etapa con su estructura; inferencia por índice | Dos representaciones en memoria |
| Dicts de str desde el principio | Una sola estructura | Mutación in-place; mezcla crudo y tipado |
| Por columnas | Inferencia directa | Hay que reorganizar a filas al final |

**Cómo defenderlo en una frase.**
> "Usamos listas de listas mientras los valores son texto, porque así se arma cada columna por posición, y recién cuando sabemos el tipo armamos los diccionarios que pide la consigna."

---

## 3. Función por función y método por método

Para cada pieza: **por qué existe**, **por qué ese nombre**, **por qué esos parámetros y ese retorno**, **por qué esa implementación** y, si corresponde, **punto débil**.

### 3.1 `funciones.py`: las 8 funciones puras

Las ocho son **funciones puras**: el resultado depende solo de los argumentos y no modifican nada de afuera. Las listas que crean (`campos_limpios`, `no_vacios`, `nuevo_diccionario`) son locales, así que agregarles elementos no es un efecto secundario. Ninguna imprime ni toca archivos. La única con un matiz es `cumple_todos_los_filtros`: es pura **si los filtros que recibe lo son**.

#### 3.1.1 `separar_linea(linea, delimitador)` — `funciones.py:1-7`

```python
def separar_linea(linea, delimitador):
    partes = linea.split(delimitador)
    campos_limpios = []
    for elemento in partes:
        campos_limpios.append(elemento.strip())
    return campos_limpios
```

- **Por qué existe.** Se usa en dos lugares: para el encabezado (`clase.py:105`) y para cada fila de datos (`clase.py:133`). Sin la función, el mismo código estaría repetido. Además se prueba sola.
- **Nombre.** Verbo + objeto: dice exactamente lo que hace con qué cosa. "Línea" porque opera sobre un renglón del archivo, todavía sin interpretar.
- **Parámetros.** Recibe el delimitador como **parámetro** y no lee `self.delimitador`: así no depende de la clase y sigue siendo pura.
- **Retorno.** Una lista de `str` limpios. Todavía son texto: el tipo se decide después, mirando toda la columna.
- **Implementación.** Lista vacía + `for` + `append` es el patrón de la Unidad 1 para construir una lista nueva. Equivale a la comprensión de listas `[e.strip() for e in linea.split(delimitador)]` (Unidad 3; verificado: mismo resultado). `strip()` va **por campo** y no sobre la línea entera, porque los espacios a limpiar están alrededor de cada separador.
- **Comportamientos a conocer.** Un campo de solo espacios queda `""` y después será `None`. Con `delimitador=None`, `str.split(None)` corta por cualquier secuencia de blancos: funciona para archivos separados por varios espacios, pero no está validado ni documentado (funciona "por accidente").

#### 3.1.2 `es_booleano(texto)` — `funciones.py:10-15`

- **Por qué existe.** Es el "detector" que usa la inferencia para preguntar si un valor es booleano. Separa la **pregunta** (¿es booleano?) de la **conversión** (`convertir_valor`).
- **Nombre.** Prefijo `es_` = predicado: función que responde sí o no. Las tres funciones detectoras siguen el mismo patrón (`es_booleano`, `es_entero`, `es_flotante`).
- **Retorno.** `True` o `False`, nunca una excepción: en la inferencia, que un valor no sea booleano es un resultado normal.
- **Implementación.** `texto.lower()` porque la comparación de cadenas distingue mayúsculas (`"TRUE" == "true"` es `False`); así se reconocen `true`, `True` y `TRUE`. El `if ...: return True` seguido de `return False` es el estilo explícito de los apuntes; es equivalente a `return texto.lower() in ("true", "false")` (verificado).
- **Punto débil.** `["true", "false"]` es una colección **fija** de valores posibles: según la cátedra correspondería una **tupla** (casi el mismo ejemplo que el de los tipos de identificación válidos). Funciona igual; es un detalle de estilo.

#### 3.1.3 `es_entero(texto)` — `funciones.py:18-24`

```python
def es_entero(texto):
    try:
        int(texto)
        return True
    except ValueError:
        return False
```

- **Por qué `try/except` y no `isdigit()`.** `int()` es la **autoridad** sobre qué texto es un entero válido para Python. `isdigit()` falla con signos: `"-5".isdigit()` y `"+5".isdigit()` dan `False`, y `int` los acepta.
- **Por qué solo `except ValueError`.** La cátedra pide capturar solo la excepción específica que se sabe manejar (recuadro "¡A evitar!"): un `except:` sin tipo podría tapar errores de programación.
- **Por qué traduce la excepción a `False`.** En la inferencia, "no es entero" es una respuesta, no un error.
- **Curiosidades verificadas.** `"001"` → `True` (y se convertirá en `1`: por eso los códigos se fuerzan a `str`); `"+5"` → `True`; `"1_000"` → `True` (int acepta guiones bajos); `"10.0"` → `False`.
- **Costo aceptado.** Convierte y descarta el resultado; después `convertir_valor` vuelve a convertir. Es doble trabajo a cambio de separar responsabilidades, y no cambia la complejidad (factor constante).

#### 3.1.4 `es_flotante(texto)` — `funciones.py:27-33`

- Mismo diseño que `es_entero`, con `float()`.
- **Verificado.** Acepta `"2500.5"`, `"800"` (todo entero es flotante: por eso el orden de inferencia pone `int` antes), `"1e3"`, `"nan"`, `"inf"`. Rechaza `"1,5"` (coma decimal). Ojo: `"1.000"` se lee como `1.0`, no como mil.

#### 3.1.5 `inferir_tipo_columna(valores_columna)` — `funciones.py:36-75`

- **Por qué existe.** El criterio de inferencia tiene que estar **en un solo lugar**, documentado (docstring de `funciones.py:37` y comentario `clase.py:4-6`), para poder explicarlo y cambiarlo sin tocar nada más.
- **Parámetro.** Una lista de `str`: los valores de **una** columna, no la tabla entera. Así la función es chica y se llama una vez por columna (`clase.py:164`).
- **Retorno.** Una **clase** (`bool`, `int`, `float` o `str`), no un string (D14).
- **Implementación, paso a paso.**
  1. **`no_vacios`** (`funciones.py:38-41`): los vacíos no "votan". Una celda vacía va a ser `None` sea cual sea el tipo, así que no debe impedir que una columna sea `int`.
  2. **Guarda `if len(no_vacios) == 0: return str`** (`funciones.py:44-45`). Es imprescindible por una razón lógica: un "para todos" sobre un conjunto vacío es verdadero (`all([])` da `True`). Como `todos_bool` arranca en `True`, **sin la guarda una columna toda vacía saldría `bool`** (verificado con una versión sin guarda).
  3. **Tres bloques iguales "bandera + for + break"** (`funciones.py:48-54`, `57-63`, `66-72`). Cada uno es una búsqueda lineal de un **contraejemplo**: la bandera arranca en `True` y, apenas aparece un valor que no cumple, pasa a `False` y el `break` corta, porque ya no tiene sentido mirar el resto (Ejecución repetitiva: `break`).
  4. **`return str`** al final (`funciones.py:75`): si no es nada más, es texto, que siempre puede representar cualquier valor.
- **Por qué banderas y `break` y no `all()`.** `all(es_entero(v) for v in no_vacios)` hace lo mismo, incluido el corte temprano, pero usa una expresión generadora (Unidad 3). La versión con bandera es la de la Unidad 1 y se lee paso a paso.
- **Punto débil y mejora.** Los tres bloques son casi idénticos (código repetido). Una versión más compacta usa una "tabla" de pares (tipo, detector), aprovechando que las funciones son objetos; la probamos con 11 casos y da los mismos resultados:

  ```python
  for tipo, detector in ((bool, es_booleano), (int, es_entero), (float, es_flotante)):
      if all(detector(v) for v in no_vacios):
          return tipo
  return str
  ```

- **Complejidad.** Hasta 4 pasadas sobre la columna (vacíos, bool, int, float): O(4L) = O(L) por columna. Big O descarta la constante.
- El **orden** de las pruebas se justifica en 5.2.

#### 3.1.6 `convertir_valor(texto, tipo_esperado, num_fila, nombre_col)` — `funciones.py:78-117`

- **Por qué existe.** Es el **único lugar** donde un texto se transforma en un valor de Python. Se usa igual para tipos inferidos y forzados.
- **Por qué recibe `num_fila` y `nombre_col` si no los usa para convertir.** Los usa para **armar el mensaje de error**, que la consigna (3.5) exige con fila y columna. Recibirlos como parámetros mantiene la función pura e independiente de la clase. Python evalúa los argumentos antes de llamar a la función (evaluación inmediata), así que se pasan en cada celda; el costo es despreciable (un número y una referencia a un texto que ya existe). El mensaje solo se construye si hay error, porque el f-string está dentro de la rama del `raise`.
- **Por qué `""` → `None` va primero** (`funciones.py:81-82`), antes de mirar el tipo:
  - aplica la regla "celda vacía = nulo" **para cualquier tipo**, incluso `str` (forzar `str` sobre una celda vacía da `None`, no `""`);
  - evita que `int("")` o `float("")` lancen error por una celda vacía, que es un caso válido.
- **Por qué `str` se devuelve tal cual** (`funciones.py:84-85`): el texto ya es `str`, no hay nada que convertir ni que pueda fallar.
- **Por qué `bool` tiene una rama propia** (`funciones.py:87-97`): **`bool("false")` es `True`** (todo string no vacío es verdadero). El constructor `bool()` no sirve para interpretar texto, así que se compara con `"true"`/`"false"` en minúsculas. Hay tres salidas posibles (`True`, `False` o error), de ahí el `if/elif/else`.
- **Por qué `int` y `float` usan `try/except`** (`funciones.py:99-115`): se deja que `int()`/`float()` decidan y, si fallan, se relanza un `ValueError` con un mensaje en castellano que incluye fila, columna, valor y tipo.
- **Por qué `if` sueltos y no `elif`.** Cada rama termina en `return` o `raise`, así que si entró en una, no sigue: son **cláusulas de guarda**. Primero los casos especiales (vacío, str) y después los que convierten.
- **Por qué la línea final `raise ValueError(f"Tipo de dato no soportado: ...")`** (`funciones.py:117`): es **programación defensiva**. En el uso normal no se alcanza, porque `forzar_tipo` ya valida el tipo, pero si alguien llama a la función directamente con `list`, falla con un mensaje claro en vez de devolver `None` en silencio.
- **Punto débil y mejora.** Las ramas `int` y `float` repiten el mismo bloque y lanzan el error nuevo dentro del `except` (encadenamiento implícito). Se pueden unificar usando el nombre de la clase y encadenar explícitamente (probado):

  ```python
  try:
      return tipo_esperado(texto)
  except ValueError as error:
      raise ValueError(
          f"Error en fila {num_fila}, columna '{nombre_col}': "
          f"el valor '{texto}' no se puede convertir a {tipo_esperado.__name__}."
      ) from error
  ```

#### 3.1.7 `cumple_todos_los_filtros(fila_diccionario, lista_funciones_filtro)` — `funciones.py:120-125`

```python
for funcion in lista_funciones_filtro:
    if not funcion(fila_diccionario):
        return False
return True
```

- **Por qué existe.** Aísla la regla "varios filtros se combinan con Y (AND)". Es una **función de orden superior**: recibe funciones y las llama.
- **Nombre.** Es la pregunta que responde: "¿la fila cumple todos los filtros?".
- **Implementación.** El `return False` apenas un filtro falla es un AND con **salida temprana**: los filtros siguientes no se llaman. Con la lista vacía devuelve `True`: sin filtros, todas las filas pasan, coherente con `all([])`.
- **`if not funcion(...)`** usa el valor de verdad del resultado: no exige que el filtro devuelva exactamente `True`/`False`. Consecuencia: un filtro escrito con `def` **sin `return`** devuelve `None`, que cuenta como falso, y descarta todas las filas sin error (verificado).
- **Alternativa equivalente.** `return all(f(fila_diccionario) for f in lista_funciones_filtro)`, equivalente incluso en el corte temprano (verificado). Con `all([...])` usando una lista por comprensión **no** es equivalente: evalúa todos los filtros antes.
- **Punto débil.** El filtro recibe el diccionario real, no una copia: un filtro que modifique la fila modifica el resultado (verificado con un filtro que hacía `fila["precio"] = 0`). Lo razonable es documentar que los filtros no deben modificar la fila.

#### 3.1.8 `recortar_diccionario(fila_diccionario, columnas_elegidas)` — `funciones.py:128-133`

- **Por qué existe.** Implementa la selección de columnas para una fila. Separarla deja el último paso de `_aplicar_filtros_y_rangos` en tres líneas.
- **Por qué crea un diccionario nuevo** y no borra claves del original: no modifica su entrada (función pura) y no necesita saber qué columnas sobran, solo cuáles quiere.
- **Orden.** Recorre `columnas_elegidas` en el orden que pasó el usuario y, como los diccionarios conservan el orden de inserción, el resultado respeta ese orden (`["c", "a"]` da `{'c': ..., 'a': ...}`).
- **¿Puede dar `KeyError`?** En el uso normal no: `_aplicar_filtros_y_rangos` valida antes que todas las columnas existan (`clase.py:192-195`).
- **Alternativa.** Comprensión de diccionarios: `{col: fila_diccionario[col] for col in columnas_elegidas}` (verificado equivalente).
- **Detalle.** El docstring tiene un error de tipeo ("solp").

### 3.2 `clase.py`: la clase `LectorCSV`

#### 3.2.1 El comentario de criterios y los imports — `clase.py:1-17`

- **Por qué un bloque de criterios al principio** (`clase.py:1-9`). La consigna pide documentar los criterios (inferencia, booleanos, nulos, combinación de opciones). Ponerlos arriba del archivo hace que cualquiera que abra la clase los lea primero.
- **Punto débil.** Son comentarios con `#`, no un docstring: `help(LectorCSV)` no los muestra y la clase no tiene docstring (`LectorCSV.__doc__` es `None`, verificado). La cátedra (Encapsulamiento, docstrings) recomienda que la clase y sus métodos tengan docstrings que expliquen su uso, con secciones como *Parameters* y *Returns*. Mejora directa: mover ese bloque a un docstring de clase.
- **Imports** (`clase.py:11-17`): explicados en D2.

#### 3.2.2 Nombre de la clase: `LectorCSV` — `clase.py:20`

- Sustantivo (un objeto **es** algo; los métodos son verbos). Formato con mayúscula inicial en cada palabra, como las clases de los apuntes (`Budin`, `CuentaBancaria`).
- "CSV" en sentido amplio: "valores separados por un carácter". Lee cualquier delimitador. Un nombre como `LectorTabular` describiría mejor esa generalidad; "CSV" es el formato más conocido y el que pide la consigna como mínimo.

#### 3.2.3 `__init__(self, delimitador=",", encabezado=True)` — `clase.py:21-36`

- **Por qué esos dos parámetros y no más.** Son los que describen **el formato del archivo**; todo lo demás (tipos, filtros, límite, rango, columnas) describe **la consulta** y tiene su propio método.
- **Por qué esos valores por defecto.** Son el caso más común que pide la consigna: CSV con coma y la primera fila como encabezado. `LectorCSV()` funciona sin argumentos. Los defaults son valores inmutables (`","` y `True`).
- **Por qué valida `delimitador == ""`** (`clase.py:27-28`). `str.split("")` lanza `ValueError: empty separator`, un mensaje técnico, y recién al leer. Validar en el constructor da un mensaje propio y **antes**: no se puede obtener un lector con delimitador vacío. (Matiz de la cátedra: `__init__` no crea el objeto, lo inicializa; la excepción interrumpe la inicialización y nadie recibe la referencia.)
- **Por qué inicializa los 7 atributos, aunque 3 empiecen en `None`.** Es la recomendación de "atributos opcionales" (Fundamentos de POO 5.1): todos los objetos tienen siempre los mismos atributos, no hay `AttributeError` por atributos que solo existen si se llamó a cierto método, y `None` significa "no configurado".
- **Por qué `{}` y `[]` se crean dentro del cuerpo** y no como valores por defecto de parámetros: así cada objeto tiene su propio diccionario y su propia lista. Si fueran defaults de un parámetro, todos los objetos compartirían la misma lista.
- **Punto débil.** No valida `encabezado` (`"no"` se toma como `True`) ni el tipo de `delimitador` (`delimitador=44` falla recién en `leer()` con `TypeError`). El docstring dice "caracter que separa", aunque se aceptan varios caracteres.

#### 3.2.4 `forzar_tipo(self, columna, tipo_dato)` — `clase.py:38-43`

- **Nombre.** "Forzar" transmite que el tipo del usuario **le gana** a la inferencia (consigna 3.3).
- **Validación** (`clase.py:40-41`): solo `int`, `float`, `str` o `bool`, los cuatro tipos que pide la consigna. Si se pasa otra cosa (`list` o el texto `"int"`) falla al configurar, con un mensaje que dice qué tipos se aceptan.
- **Por qué un diccionario** `{columna: tipo}` (`clase.py:43`): una columna tiene un solo tipo (clave única) y después se busca por nombre (`clase.py:158`). Llamar dos veces sobre la misma columna reemplaza el valor: **gana el último** (verificado).
- **Por qué NO valida que la columna exista.** No puede: el lector se configura **antes** de saber qué archivo va a leer, y el mismo lector puede leer varios archivos. Los nombres de columna recién se conocen al leer el encabezado. Por eso la validación está al principio de `_convertir_tipos` (`clase.py:147-149`), el primer momento en que existen a la vez la configuración y el encabezado, y antes de la inferencia.
- **Punto débil.** No valida el tipo de `columna`; `[int, float, str, bool]` sería más prolijo como tupla o como constante de clase.

#### 3.2.5 `agregar_filtro(self, funcion_filtro)` — `clase.py:45-47`

- **Nombre: "agregar" y no "establecer".** Los filtros **se acumulan** (se combinan con AND); los otros setters **reemplazan** el valor anterior. El verbo marca esa diferencia.
- **Por qué una lista.** Los filtros se aplican en el orden en que se agregaron (importa por el corte temprano), pueden repetirse y se recorren todos.
- **Por qué no valida nada.** Por duck typing: cualquier cosa que se pueda llamar con una fila sirve.
- **Punto débil.** `agregar_filtro(5)` se acepta y falla recién en `leer()` con `TypeError: 'int' object is not callable`. Mejora: `if not callable(funcion_filtro): raise TypeError(...)`. No hay forma de quitar filtros.

#### 3.2.6 `establecer_limite(self, limite)` — `clase.py:49-53`

- **Validación.** Solo rechaza negativos. **El 0 se permite** y devuelve `[]`: pedir cero filas es raro pero no absurdo (igual que el slicing `lista[:0]`). Un límite negativo no tiene significado.
- **`None` como "sin límite"** (valor inicial): distinto de `0`. Por eso se pregunta con `is not None` (`clase.py:207`).
- **Punto débil.** No valida el tipo: `establecer_limite(2.5)` se acepta (y devuelve 3 filas), `establecer_limite("3")` da un `TypeError` técnico, `establecer_limite(None)` no deshace el límite (`TypeError`). Según la cátedra (Excepciones, "¿TypeError o ValueError?"), primero habría que chequear el tipo con `isinstance` y lanzar `TypeError`, y después el valor con `ValueError`.

#### 3.2.7 `establecer_rango(self, inicio, fin)` — `clase.py:55-59`

- **Por qué dos parámetros y no una tupla.** La llamada `establecer_rango(1, 5)` se lee mejor que `establecer_rango((1, 5))`. Adentro sí se guarda como **tupla** (`clase.py:59`), porque es un par fijo que no se modifica, y después se desempaqueta (`inicio, fin = self._rango_filas`, `clase.py:199`).
- **Validación** (`clase.py:57`): `inicio >= 1` (las filas se numeran desde 1) y `fin >= inicio` (un rango al revés no tiene sentido). Un rango de una sola fila (`(3, 3)`) es válido.
- **Por qué no valida que `fin` sea menor o igual a la cantidad de filas.** No se conoce hasta leer. Se eligió el comportamiento del slicing: `(3, 100)` devuelve desde la 3 hasta el final y `(50, 60)` devuelve `[]`, sin error.
- **Punto débil.** No valida tipos: con `establecer_rango(1, 3.0)` el error aparece recién al leer (`slice indices must be integers...`). Un rango completamente fuera de la tabla da `[]` sin aviso (candidato a warning).

#### 3.2.8 `seleccionar_columnas(self, lista_columnas)` — `clase.py:61-63`

- **Por qué una lista.** El orden importa: el resultado respeta el orden pedido. `None` (el valor inicial) significa "todas las columnas".
- **Por qué no valida al configurar.** Igual que `forzar_tipo`, los nombres recién se conocen al leer.
- **Puntos débiles.**
  1. La validación está en `_aplicar_filtros_y_rangos` (`clase.py:192-195`), **después** de convertir todo el archivo. Podría hacerse junto con la de `forzar_tipo`, apenas se conoce el encabezado.
  2. Guarda **la misma lista** del usuario, no una copia (`self._columnas = lista_columnas`): si el usuario después hace `cols.append("precio")`, la próxima lectura incluye `precio` (verificado). Mejora: `self._columnas = list(lista_columnas)`.
  3. Si se pasa un string en vez de una lista, se recorre letra por letra: `seleccionar_columnas("nombre")` da `"La columna seleccionada 'n' no existe en la tabla."`.

#### 3.2.9 `leer(self, ruta_archivo)` — `clase.py:65-82`

- **Nombre.** Es el verbo principal de un lector. Es el único método que **produce datos**.
- **Por qué recibe la ruta y no la recibe el constructor.** El constructor define **cómo** leer; `leer` define **qué** leer. Así la configuración se reutiliza (D4).
- **Por qué variables intermedias con nombre** (`lineas`, `encabezados`, `filas_crudas`, `filas_tipadas`, `filas_filtradas`). Se podría encadenar todo en una línea, pero así el método se lee como una receta, con un comentario numerado por etapa.
- **Retorno.** La lista de diccionarios. No imprime ni la guarda en `self`.

#### 3.2.10 `_leer_archivo(self, ruta_archivo)` — `clase.py:84-97`

- Decisiones de apertura y lectura: D11.
- **Por qué el chequeo de archivo vacío está fuera del `with`** (`clase.py:94-95`): no necesita el archivo abierto, y así queda cerrado antes de seguir. `len(lineas) == 0` solo pasa con un archivo de 0 bytes: un archivo con un único `"\n"` tiene una línea (vacía) y lo detecta la etapa siguiente ("La primera línea del archivo está vacía").
- **Por qué se relanza `FileNotFoundError` y no `ValueError`.** No es un problema del contenido sino de la ruta; mantener el tipo permite que el llamador lo distinga.
- **Punto débil.** No captura `UnicodeDecodeError` (archivo latin-1) ni `PermissionError` (en Windows, si la ruta es una carpeta). `ejemplos.py` solo captura `ValueError`, así que una ruta mal escrita corta el programa con el traceback.

#### 3.2.11 `_procesar_lineas(self, lineas)` — `clase.py:99-143`

- **Por qué valida aparte que la primera línea no esté vacía** (`clase.py:101-103`). Si no, una primera línea vacía con encabezado daría "Error en fila 1, columna 1: El nombre de la columna está vacío." (confuso: no hay ninguna columna), y sin encabezado fijaría un ancho de una columna y la misma línea fallaría enseguida como "Error en fila 1: Se encontró una fila vacía." (probado con una copia del código sin ese chequeo). Con el chequeo aparte, los dos casos dan un único mensaje que dice exactamente qué pasa.
- **`primeros_elementos` y `cant_columnas`** (`clase.py:105-106`). La primera línea (sea encabezado o primera fila de datos) define el **ancho de referencia**: todas las filas deben tener esa cantidad de campos. Se llama `primeros_elementos` y no `nombres` porque, sin encabezado, son datos.
- **Encabezado** (`clase.py:110-118`): un `for` con índice (necesario para informar el número de columna, `i + 1`, en base 1 para las personas). Dentro: nombre vacío → error; nombre repetido → error (`nombre in encabezados`). Los criterios se justifican en 5.1.
- **Sin encabezado** (`clase.py:119-122`): genera `col_0`, `col_1`, ... con f-strings.
- **`indice_inicio_datos`** (1 o 0). Permite usar **un único bucle de filas para los dos casos**: con encabezado los datos empiezan en `lineas[1]`, sin encabezado en `lineas[0]`.
- **Bucle de filas** (`clase.py:126-141`): `range(indice_inicio_datos, len(lineas))` con índice, porque el índice da el número de línea del archivo (`num_fila_archivo = i + 1`, ya que `lineas` incluye el encabezado). Para cada línea: vacía → error; cantidad de campos distinta → error con esperadas y encontradas.
- **Por qué chequea la línea vacía antes de separar.** Para dar el mensaje específico "Se encontró una fila vacía" en vez de uno de cantidad de campos. Consecuencia no buscada: en un archivo de **una sola columna**, una celda vacía es una línea vacía, y da error en vez de `None` (ver 7.1).
- **Retorno.** Una tupla `(encabezados, filas_crudas)`: dos resultados relacionados que salen de la misma pasada, y que `leer` recibe por desempaquetado. Así no se guardan en `self` (D4).
- **Punto débil.** `nombre in encabezados` es búsqueda lineal dentro de un `for`: O(K²) para K columnas, el mismo patrón que `contiene_duplicados` de la Unidad 4. Con un `set` auxiliar de nombres vistos sería O(K). Con 5 columnas no hay diferencia; con 20.000 columnas, 1,29 s contra 0,0024 s (medido).

#### 3.2.12 `_convertir_tipos(self, encabezados, filas_crudas)` — `clase.py:145-188`

- **Validación de columnas forzadas al principio** (`clase.py:147-149`): es el primer lugar donde se conocen a la vez la configuración y el encabezado, y está antes del trabajo pesado (fallar lo antes posible).
- **Parte A: el tipo de cada columna** (`clase.py:154-164`). Si la columna está en `self._tipos_columnas`, se usa ese tipo y **no se infiere**: así se implementa la prioridad del tipo forzado. Si no, se arma `valores_columna` con todas las filas (D8) y se infiere. El resultado va a `tipos_definidos`, un diccionario `{nombre: tipo}` que mezcla forzados e inferidos.
- **Parte B: armar los diccionarios** (`clase.py:166-186`). Doble `for` (filas × columnas): visita cada celda **una vez**, así que es O(L·K), no cuadrático. `num_fila_archivo` es `fila_i + 2` con encabezado (una unidad por pasar a base 1 y otra por el encabezado) y `fila_i + 1` sin encabezado. La cuenta es exacta porque las líneas vacías no se saltean: dan error. Las claves se insertan en el orden de `encabezados`, así cada diccionario respeta el orden de las columnas del archivo.
- **Por qué `tipos_definidos` es un diccionario por nombre y no una lista por posición.** Las dos opciones funcionan; por nombre queda alineado con `_tipos_columnas` y la línea `tipos_definidos[nombre_col]` se lee sola.

#### 3.2.13 `_aplicar_filtros_y_rangos(self, encabezados, filas_tipadas)` — `clase.py:190-221`

- **Validación de columnas seleccionadas** al principio (`clase.py:192-195`): ver el punto débil de 3.2.8.
- **Rango con slicing** (`clase.py:198-202`): `filas_tipadas[inicio - 1 : fin]`. Al inicio se le resta 1 para pasar de "fila 1" (humano) a índice 0 (Python). Al fin **no** se le resta, porque el slicing excluye el extremo derecho: `fin` en base 1 coincide con el tope exclusivo en base 0. Verificado: `(2, 3)` da Lapicera y Carpeta, las filas 2 y 3. Sin rango, `filas_en_rango` es la misma lista (sin copia).
- **Filtros y límite en el mismo bucle** (`clase.py:205-211`):

  ```python
  for fila in filas_en_rango:
      if self._limite_filas is not None and len(filas_filtradas) >= self._limite_filas:
          break
      if cumple_todos_los_filtros(fila, self._filtros):
          filas_filtradas.append(fila)
  ```

  - El límite se chequea **antes** de llamar a los filtros: apenas se juntaron N filas, se corta y no se evalúan filtros de más (con límite 2, el filtro se llamó solo lo necesario).
  - `is not None` va **primero** por el **cortocircuito** del `and`: si no hay límite, la comparación ni se evalúa. Invertido, daría `TypeError` (`0 >= None`).
  - `for` + `break` y no `while`: se recorre una colección conocida y el corte anticipado lo resuelve `break`, sin el riesgo de bucle infinito de un `while` con índice manual.
- **Selección de columnas al final** (`clase.py:214-219`): solo sobre las filas que quedaron, con `recortar_diccionario`. Por qué al final: 5.8 y 5.10.
- **Punto débil del nombre.** Dice "filtros y rangos" pero también aplica el límite y la selección de columnas. `_seleccionar_filas_y_columnas` describiría mejor lo que hace.

### 3.3 `ejemplos.py`: el script de demostración

- **Por qué existe.** La consigna (3.6 y 4) pide ejemplos de uso con sus resultados y que la visualización con pandas esté fuera del lector.
- **Cuatro ejemplos, uno por idea**: (1) inferencia + tipo forzado (`codigo` como `str` para conservar `"001"`); (2) combinación de rango, filtro, límite y columnas; (3) otro delimitador (`;`); (4) manejo de errores con `try/except ValueError`.
- **Por qué `delimitador=","` explícito** aunque es el valor por defecto: hace autoexplicativa la llamada.
- **Por qué muestra la lista y el DataFrame**: D12.
- **Puntos débiles.**
  - No cubre las situaciones problemáticas que la consigna pide probar (archivo vacío, filas vacías, cantidad de campos distinta, encabezado repetido o vacío) ni `encabezado=False`, tab o delimitador de varios caracteres. Tampoco escribe los resultados esperados. Es el incumplimiento parcial más claro (3.6).
  - Las rutas son relativas (`"datos1.csv"`): hay que ejecutarlo parado en la carpeta del proyecto. La cátedra sugiere armar las rutas desde una carpeta base (`pathlib`).
  - No tiene `if __name__ == "__main__":`: si alguien lo importa, se ejecutan los cuatro ejemplos.

---

## 4. Atributos y variables

### 4.1 Atributos de instancia de `LectorCSV`

Verificado: `vars(LectorCSV())` da `{'delimitador': ',', 'encabezado': True, '_tipos_columnas': {}, '_filtros': [], '_limite_filas': None, '_rango_filas': None, '_columnas': None}`.

| Atributo | Visibilidad | Tipo de dato | Valor inicial | Se escribe en | Se lee en | Por qué ese tipo |
|---|---|---|---|---|---|---|
| `delimitador` | público | `str` (uno o más caracteres) | `","` | `clase.py:30` | `clase.py:105`, `133` | Es lo que recibe `str.split`; puede tener varios caracteres |
| `encabezado` | público | `bool` | `True` | `clase.py:31` | `clase.py:110`, `171` | Es una pregunta de sí o no: ¿la primera línea son nombres? |
| `_tipos_columnas` | protegido | `dict` {nombre de columna: clase} | `{}` | `clase.py:43` | `clase.py:147`, `158-159` | Se busca **por nombre**; una columna tiene **un** tipo (clave única); repetir `forzar_tipo` pisa el valor |
| `_filtros` | protegido | `list` de funciones | `[]` | `clase.py:47` | `clase.py:210` (vía `cumple_todos_los_filtros`) | Se **acumulan en orden**, pueden repetirse y se recorren todos |
| `_limite_filas` | protegido | `None` o `int` | `None` | `clase.py:53` | `clase.py:207` | `None` = sin límite, que no es lo mismo que `0` (devuelve `[]`) |
| `_rango_filas` | protegido | `None` o `tuple` (inicio, fin) | `None` | `clase.py:59` | `clase.py:198-199` | Par **fijo** que no se modifica → tupla, como recomienda la cátedra; se desempaqueta en `inicio, fin` |
| `_columnas` | protegido | `None` o `list` de str | `None` | `clase.py:63` | `clase.py:192-194`, `214-217` | Importa el **orden** del resultado; `None` = todas |

**Por qué `None` como "no configurado".** Es la recomendación de la cátedra para atributos opcionales: definirlos en `__init__` con `None`. Así todo lector tiene siempre la misma estructura, y la pregunta "¿el usuario configuró esto?" se responde con `is not None` (`clase.py:192`, `198`, `207`, `214`). `None` es un objeto único, por eso se compara por **identidad** (`is`) y no por valor. Y permite distinguir "sin límite" de "límite 0".

**Por qué `_tipos_columnas` y `_filtros` no empiezan en `None`.** Porque "vacío" ya significa "no configurado" sin ambigüedad: un diccionario vacío es "ningún tipo forzado" y una lista vacía es "ningún filtro" (y `cumple_todos_los_filtros` con lista vacía devuelve `True`). Además, empezar vacíos permite usar directamente `[clave] = ...` y `append` sin preguntar antes si existen.

**Lo que NO es atributo.** Los datos leídos (líneas, filas, encabezados, tipos inferidos) son variables locales de los métodos: el estado del objeto es solo la configuración (D4).

### 4.2 Variables locales importantes

| Variable | Dónde | Tipo | Para qué y por qué ese nombre |
|---|---|---|---|
| `partes` | `funciones.py:3` | `list[str]` | Pedazos crudos que devuelve `split`, todavía con espacios |
| `campos_limpios` | `funciones.py:4` | `list[str]` | Los mismos pedazos con `strip()`: el nombre dice en qué estado están |
| `elemento` | `funciones.py:5` | `str` | Cada pedazo en el `for` (singular de la colección) |
| `texto_min` | `funciones.py:12`, `88` | `str` | El texto en minúsculas, para comparar sin importar mayúsculas |
| `no_vacios` | `funciones.py:38` | `list[str]` | Valores de la columna sin las celdas vacías: los que "votan" en la inferencia |
| `todos_bool`, `todos_int`, `todos_float` | `funciones.py:48`, `57`, `66` | `bool` (bandera) | "Hasta ahora todos cumplen". Arrancan en `True` (suposición optimista) y un contraejemplo las pasa a `False` y corta con `break`. El nombre se lee como la pregunta que responden |
| `nuevo_diccionario` | `funciones.py:130` | `dict` | Remarca que es un diccionario **nuevo**, no el original modificado |
| `lineas` | `clase.py:88`, `71` | `list[str]` | Renglones del archivo sin `\n`/`\r` |
| `primera_linea`, `primeros_elementos` | `clase.py:101`, `105` | `str`, `list[str]` | La primera línea y sus campos. "Elementos" y no "nombres" porque sin encabezado son datos |
| `cant_columnas` | `clase.py:106`, `151` | `int` | Ancho de referencia de la tabla. Es local en dos métodos distintos (no hay conflicto) |
| `encabezados` | `clase.py:109` | `list[str]` | Nombres de las columnas **en orden**: será el orden de las claves de cada fila |
| `nombre` | `clase.py:112` | `str` | Nombre de columna que se está validando |
| `indice_inicio_datos` | `clase.py:118`, `122` | `int` (1 o 0) | Dónde empiezan los datos en `lineas`; permite un único bucle de filas con y sin encabezado |
| `filas_crudas` | `clase.py:125` | `list[list[str]]` | Filas separadas y validadas, todavía como texto ("crudas") |
| `num_fila_archivo` | `clase.py:127`, `172`/`174` | `int` | Número de **línea del archivo** desde 1, solo para los mensajes de error |
| `linea_actual`, `elementos` | `clase.py:128`, `133` | `str`, `list[str]` | La línea en proceso y sus campos |
| `col_forzada` | `clase.py:147` | `str` | Cada columna configurada con `forzar_tipo` |
| `tipos_definidos` | `clase.py:152` | `dict` {nombre: clase} | Tipo final de cada columna, forzado o inferido ("definidos": ya no hay dudas) |
| `valores_columna` | `clase.py:161` | `list[str]` | Todos los valores de una columna, para la inferencia |
| `lista_diccionarios` | `clase.py:167` | `list[dict]` | Resultado de `_convertir_tipos`; en `leer` se recibe como `filas_tipadas` |
| `elementos_fila`, `valor_texto`, `tipo_col`, `diccionario_fila` | `clase.py:169`, `179`, `180`, `176` | varios | Las piezas de la conversión celda por celda |
| `inicio`, `fin` | `clase.py:199` | `int` | Desempaquetado de la tupla del rango, para que el slicing se lea claro |
| `filas_en_rango`, `filas_filtradas`, `resultado_final`, `fila_recortada` | `clase.py:200`/`202`, `205`, `215`, `217` | `list[dict]`, `dict` | Cada etapa del último paso, con un nombre que dice qué se le hizo a las filas |
| `i`, `col_i`, `fila_i` | varios | `int` | Índices. El sufijo `_i` se lee "índice de la columna", "índice de la fila" |

### 4.3 Criterio de nombres

- **En castellano**, como la consigna y el dominio (filas, columnas, encabezado, delimitador). Un lector del código entiende de qué se habla sin traducir.
- **Sin tildes ni ñ en los identificadores** (`num_fila`, `cant_columnas`, `es_booleano`), como aconseja la cátedra. Las tildes aparecen solo en comentarios y mensajes, donde están permitidas.
- **`snake_case`** para funciones, métodos y variables; **mayúscula en cada palabra** para la clase (`LectorCSV`).
- **Verbos para lo que hace algo**: `leer`, `forzar_tipo`, `agregar_filtro`, `establecer_limite`, `establecer_rango`, `seleccionar_columnas`, `separar_linea`, `convertir_valor`, `recortar_diccionario`, `inferir_tipo_columna`.
- **Prefijo `es_` para predicados** (devuelven `True`/`False`) y **`cumple_`** para la pregunta sobre los filtros.
- **Plural para colecciones y singular para cada elemento del `for`**: `lineas`/`linea`, `filas_crudas`/`fila`, `no_vacios`/`valor`.
- **Adjetivos que cuentan el pipeline**: las filas pasan de `crudas` → `tipadas` → `filtradas` → `recortada`. Leyendo solo los nombres se entiende el proceso.
- **Guion bajo inicial = protegido** (interno), sin guion = interfaz pública.

**Puntos débiles de nombres (para reconocerlos si preguntan).**
- `modulo` es el nombre de una carpeta que es un **paquete**.
- `_aplicar_filtros_y_rangos` también aplica límite y columnas.
- `LectorCSV` lee cualquier delimitador.
- Se reutilizan nombres de variable de iteración en bucles seguidos (`i` en `clase.py:111`/`120` y `126`; `valor` en cuatro bucles de `inferir_tipo_columna`). No hay error porque ningún bucle usa el valor que dejó el anterior, pero la cátedra (Repetitiva §3.2, recuadro "Variable de iteración") recomienda que la variable de iteración no tenga el mismo nombre que otra variable del programa.
- `lista_funciones_filtro` incluye el tipo de dato en el nombre (`filtros` alcanzaría).

---

## 5. Criterios definidos por el grupo

La consigna deja varias decisiones a criterio del grupo y pide documentarlas. Están resumidas en el comentario `clase.py:1-9`. Acá van una por una, con **qué hace el código**, **por qué** y **qué alternativa se descartó**.

### 5.1 Encabezado

| Situación | Qué pasa | Dónde |
|---|---|---|
| Caso normal | La primera línea da los nombres de las columnas (sin espacios en los bordes, por el `strip`) | `clase.py:105-117` |
| Nombre vacío (`a,,c` o coma final `a,b,`) | `ValueError`: "Error en fila 1, columna 2: El nombre de la columna está vacío." (con `a,b,` dice "columna 3") | `clase.py:113-114` |
| Nombre repetido (`a,b,a`) | `ValueError`: "Error en fila 1: El nombre de columna 'a' está repetido." | `clase.py:115-116` |
| `Nombre` y `nombre` | Son columnas **distintas** (se respetan mayúsculas) | `clase.py:115` |
| `encabezado=False` | Nombres generados `col_0`, `col_1`, ... y la primera línea es una fila de datos | `clase.py:119-122` |
| Solo encabezado, sin filas | Devuelve `[]` sin error | — |

**Por qué error y no arreglarlo solo.**
- **Repetidos**: cada fila es un diccionario y **las claves tienen que ser únicas**. Si se permitieran, la segunda columna pisaría a la primera y se perderían datos sin aviso: `dict(zip(["a", "b", "a"], [1, 2, 3]))` da `{'a': 3, 'b': 2}` (verificado).
- **Vacíos**: una clave `""` sería inaccesible en la práctica (`fila[""]`) y casi siempre indica un error en el archivo (una coma de más, o un CSV exportado por pandas con el índice).
- **Alternativa descartada: renombrar automáticamente** (`a`, `b`, `a_2`; o `columna_2` para el vacío). Es más tolerante, pero inventa nombres que el usuario no escribió y que después tiene que adivinar para filtrar o seleccionar. Preferimos que el usuario corrija el archivo o use `encabezado=False`.
- **Por qué distinguir mayúsculas**: los nombres son claves de diccionario, y para Python `"Nombre"` y `"nombre"` son claves distintas. Unificarlas obligaría a elegir cuál conservar.
- **Por qué `col_0` desde 0**: es la convención de índices de Python. Ojo con la inconsistencia: el mensaje de error de nombre vacío cuenta columnas desde 1 ("columna 2"). Hay que saberlo explicar: el mensaje es para una persona; el nombre generado sigue la convención de Python.

### 5.2 Orden de inferencia: bool → int → float → str

**Qué hace el código.** `inferir_tipo_columna` (`funciones.py:36-75`) prueba, sobre los valores **no vacíos** de la columna, si **todos** son booleanos; si no, si todos son enteros; si no, si todos son flotantes; si no, la columna es `str`.

**Por qué ese orden: de lo más específico a lo más general.**
- **`int` antes que `float` es imprescindible.** Todo entero también se puede leer como flotante: `es_flotante("10")` da `True`. Si `float` se probara primero, una columna de cantidades (`10`, `25`, `8`) saldría `10.0`, `25.0`, `8.0`. Al revés no pasa, porque `int("10.0")` y `int("30.5")` fallan. Así se resuelve el ejemplo de la consigna: `10`, `20`, `30.5` → `float` (verificado), el único tipo que representa todos los valores.
- **`str` al final** porque es el comodín: cualquier texto es un `str` válido. Si estuviera primero, nunca se inferiría otro tipo.
- **`bool` primero porque es el más restrictivo** (solo dos textos posibles). Dato honesto para la defensa: con los literales actuales, ningún texto es a la vez booleano y numérico (lo verificamos: `"true"`, `"false"` y sus variantes no pasan `int()` ni `float()`), así que la posición de `bool` respecto de `int`/`float` **no cambia ningún resultado hoy**. Importaría si se agregaran `"1"`/`"0"` como booleanos: ahí `bool` primero haría que una columna de unos y ceros saliera booleana.
- Verificado: `["1", "0"]` → `int` (no `bool`); `["TRUE", "False", ""]` → `bool`; `["true", "1"]` → `str`.

**Alternativa descartada.** Elegir el tipo "de la mayoría" de los valores: una columna con `10`, `20`, `abc` sería `int` y `abc` no se podría convertir. El criterio "todos o nada" garantiza que la conversión de un tipo inferido nunca falla (D8).

### 5.3 Columna toda vacía → `str`

**Qué hace.** Si no hay ningún valor no vacío, `inferir_tipo_columna` devuelve `str` (`funciones.py:44-45`) y todos los valores quedan `None`.

**Por qué.**
- No hay ninguna información para decidir; cualquier tipo numérico o booleano sería inventado. `str` es el tipo más general y el que no supone nada.
- Los valores son `None` igual, así que el tipo elegido no cambia ningún valor del resultado.
- La guarda es necesaria por la lógica de "para todos": sin ella, la bandera `todos_bool` quedaría en `True` con cero valores y la columna saldría `bool` (ver 3.1.5).

**Alternativas.** Lanzar un error (demasiado estricto: una columna vacía es válida); avisar con un warning (sería una mejora, ver 7.4).

### 5.4 Mezcla de tipos en una columna

| Mezcla | Resultado | Por qué |
|---|---|---|
| Enteros y decimales (`10`, `20`, `30.5`) | `float` | Es el único tipo que representa todos; los enteros pasan a `10.0` |
| Números y texto (`10`, `abc`) | `str` (todos los valores como texto) | "Todos o nada": no se puede convertir `abc` a número, y convertir solo una parte dejaría una columna con dos tipos |
| Booleanos y números (`true`, `1`) | `str` | Ningún tipo salvo `str` acepta los dos |
| Números y un marcador de nulo textual (`10`, `NA`) | `str` | Solo la celda vacía es nulo (5.6) |

**Alternativas descartadas.** (a) Convertir lo que se pueda y dejar el resto como texto: columna heterogénea, los filtros numéricos fallarían a mitad de la lectura con `TypeError`. (b) Lanzar error: en la **inferencia** una mezcla no es un error del archivo, es información; el error queda reservado para los tipos **forzados**. Con `str` no se pierde información: el usuario puede forzar el tipo o limpiar los datos.

**Costo, para reconocerlo.** Una sola celda rara (`"NA"`, `"15%"`, `"1 500"`) vuelve `str` toda la columna, incluidos los números "buenos".

### 5.5 Booleanos reconocidos

**Qué hace.** Solo `true` y `false`, **sin importar mayúsculas** (`.lower()`, `funciones.py:12` y `88`) y sin importar espacios en los bordes (por el `strip` de `separar_linea`). `True`, `TRUE`, ` false ` → booleanos.

**Por qué esos.** Son las formas que generan Python (`True`/`False`), Excel en inglés (`TRUE`/`FALSE`) y JSON (`true`/`false`), y no son ambiguas.

**Por qué no otros.**
- `1`/`0`: chocan con los enteros (una columna de cantidades con unos y ceros saldría booleana).
- `si`/`no`, `yes`/`no`, `T`/`F`: dependen del idioma y del contexto; `"no"` puede ser un dato de texto.
- `VERDADERO`/`FALSO`: no se contemplaron, y es lo que exporta Excel en castellano. Es una limitación (7.1).

**Con tipo forzado `bool`**, cualquier otro valor da error: `forzar_tipo(col, bool)` sobre `"1"` o `"si"` → `ValueError` (verificado). No hay conversión "creativa".

### 5.6 Nulos = `None`

**Qué hace.** Una celda **vacía** (o con solo espacios, que el `strip` deja vacía) se guarda como `None`, **para cualquier tipo**, incluso con tipo forzado `str` (`funciones.py:81-82`).

**Por qué `None`.** La cátedra lo dice explícitamente: para representar la ausencia de información se usa `None`; `0` o `""` son valores concretos, no ausencia. Una celda vacía es como un campo de un formulario que quedó sin completar. Python no tiene un `NA` como R.

**Por qué solo la celda vacía y no `"NA"`, `"NULL"`, `"None"`, `"-"`.** Porque esos textos pueden ser **datos reales** (un apodo "None", el código de Namibia "NA", un guion como valor). Una regla única y visible ("vacío = nulo") es predecible. El costo es que un CSV exportado desde R (que escribe `NA`) da columnas `str` (7.4).

**Dos detalles para tener claros.**
- `"nan"` en una columna numérica se infiere `float` y queda `float("nan")`, **no** `None`, porque `float()` acepta ese texto. Hay dos representaciones distintas de "falta el dato" y un filtro con `is not None` no descarta un `nan`.
- Al pasar a pandas, `None` se ve como `NaN` o `None` según la columna; por eso se muestra también la lista (D12).

### 5.7 Prioridad de los tipos forzados

**Qué hace.** Si una columna está en `_tipos_columnas`, `_convertir_tipos` usa ese tipo y **ni siquiera infiere** (`clase.py:158-159`). Si un valor no se puede convertir, `ValueError` con fila, columna, valor y tipo. Nunca se cambia a otro tipo.

**Por qué.** Lo pide la consigna (3.3): el tipo del usuario tiene prioridad y no se debe reemplazar por uno inferido. Sirve cuando la inferencia "acierta técnicamente pero no es lo que se necesita":

| Caso | Inferido | Forzando `str` |
|---|---|---|
| Código `001` (ejemplo 1) | `1` (int) | `"001"` |
| Código postal `0341` | `341` | `"0341"` |
| Teléfono `+543414567890` | `543414567890` (pierde el `+`) | `"+543414567890"` |
| Código `12E3` | `12000.0` (lo lee como notación científica) | `"12E3"` |

**Ejemplos de error verificados.** Forzar `int` sobre `precio` de `datos1.csv` → "Error en fila 2, columna 'precio': el valor '2500.5' no se puede convertir a int." Forzar `int` sobre `"veinte"` → el ejemplo 4.

### 5.8 Combinación de opciones: rango → filtros → límite → columnas

**Qué hace.** `_aplicar_filtros_y_rangos` (`clase.py:190-221`): primero recorta por rango, después evalúa los filtros, corta al juntar `límite` filas que cumplen y al final elige las columnas. Está documentado en `clase.py:7-9`.

**Comparación con los órdenes alternativos (todo verificado con `datos1.csv`).**

| Configuración | Resultado del lector | Con el orden alternativo |
|---|---|---|
| `establecer_rango(1, 3)` + filtro `cantidad < 15` (sin `None`) | Cuaderno, Carpeta (de las filas 1 a 3, cumplen dos) | Filtro primero y después "filas 1 a 3 de las que cumplen": Cuaderno, Carpeta, **Mochila** |
| `establecer_limite(2)` + el mismo filtro | Cuaderno, Carpeta (sigue hasta juntar 2 que cumplen) | "Mirar las primeras 2 filas y filtrar": solo Cuaderno. **Esto igual se puede pedir** con `establecer_rango(1, 2)` + filtro (verificado: Cuaderno) |
| Filtro `disponible is False` + `seleccionar_columnas(["nombre"])` | `[{'nombre': 'Regla'}]` | Si se recortaran las columnas antes, el filtro daría `KeyError: 'disponible'` |

**Por qué cada paso está donde está.**
1. **Rango primero.** El rango habla de **posiciones en el archivo** ("las filas 1 a 5"), algo que tiene sentido antes de filtrar. Después del filtro, "la fila 3" significaría "la tercera que cumple", que cambia según el filtro. Además el slicing es barato y achica las filas que evalúan los filtros.
2. **Filtros antes que el límite.** La consigna plantea dos opciones (examinar las primeras N filas o seguir hasta obtener N que cumplan). Elegimos la segunda porque es lo que normalmente se quiere ("dame 2 productos con poco stock"), y porque **la primera sigue disponible** combinando rango y filtro. Con la otra elección, la segunda semántica no se podría expresar.
3. **Columnas al final.** El filtro ve la fila **completa y ya tipada**, así que se puede filtrar por columnas que no se devuelven (5.10). Además se recortan solo las filas que quedaron (como mucho `límite`).

### 5.9 Numeración de filas y columnas

Hay **dos numeraciones** a propósito, y conviene tenerlas clarísimas:

| Dónde | Qué cuenta | Desde | Ejemplo |
|---|---|---|---|
| `establecer_rango(inicio, fin)` | **Filas de datos** (sin el encabezado) | 1, con los dos extremos incluidos | `(2, 3)` → Lapicera y Carpeta |
| Mensajes de error | **Líneas del archivo** (el encabezado es la línea 1) | 1 | El `"veinte"` de `derror.csv` está en la segunda fila de datos y el error dice "fila 3" |
| Error de nombre de columna vacío | Columnas | 1 | `a,,c` → "columna 2" |
| Nombres generados sin encabezado | Columnas | 0 | `col_0`, `col_1` |

**Por qué.**
- **Rango desde 1 y con extremos incluidos**: es como cuenta una persona ("de la fila 1 a la 5" incluye la 1 y la 5). Adentro se traduce al slicing de Python con `inicio - 1 : fin` (3.2.13).
- **Errores por línea del archivo**: el mensaje sirve para **encontrar el problema en el archivo**, y los editores de texto numeran las líneas desde 1, contando el encabezado. La cuenta es exacta porque las líneas vacías no se saltean (dan error): índice de la lista y línea del archivo se corresponden siempre (`num_fila_archivo = i + 1` en `clase.py:127`; `fila_i + 2` o `fila_i + 1` en `clase.py:171-174`).
- **Pregunta trampa probable**: "¿por qué el error dice fila 3 si es la segunda fila?". Respuesta: porque cuenta líneas del archivo y la línea 1 es el encabezado.
- **Otra trampa**: el DataFrame de pandas numera su índice desde 0, así que `establecer_rango(1, 5)` corresponde a los índices 0 a 4 del DataFrame completo.

**Punto débil.** Que el mensaje diga "fila" para algo que es una línea del archivo puede confundir; decir "línea 3 del archivo" sería más preciso. Y la columna se numera desde 1 en un mensaje y desde 0 en los nombres generados.

### 5.10 Filtrar por columnas que no se incluyen en el resultado

**Sí se puede.** La selección de columnas es el último paso, así que los filtros reciben la fila completa y tipada. Verificado: filtro `fila["disponible"] is False` con `seleccionar_columnas(["nombre"])` → `[{'nombre': 'Regla'}]`. Por la misma razón, un filtro puede combinar varias columnas (por ejemplo `fila["precio"] > 1000 and fila["disponible"]`). Si alguna de esas columnas puede tener `None`, el filtro tiene que contemplarlo, como hace el ejemplo 2 con `fila["cantidad"] is not None and ...`.

**Alternativa descartada.** Recortar antes de filtrar: obligaría a incluir en el resultado todas las columnas que use el filtro, justo lo que la consigna da como ejemplo de algo deseable ("nombres y precios de los productos con menos de diez unidades").

### 5.11 Manejo de errores

| Situación | Comportamiento | Mensaje (verificado) | Dónde |
|---|---|---|---|
| Ruta inexistente | `FileNotFoundError` | "No se encontró el archivo en la ruta: X" | `clase.py:91-92` |
| Archivo vacío (0 bytes) | `ValueError` | "El archivo 'X' está vacío." | `clase.py:94-95` |
| Primera línea vacía | `ValueError` | "Error en fila 1: La primera línea del archivo está vacía." | `clase.py:102-103` |
| Solo encabezado | Devuelve `[]` | — | — |
| Fila vacía en el medio (o línea en blanco al final por doble salto de línea) | `ValueError` | "Error en fila 3: Se encontró una fila vacía." | `clase.py:130-131` |
| Un único salto de línea al final | Se lee normal | — | — |
| Fila con más o menos campos | `ValueError` | "Error en fila 3: Cantidad incorrecta de elementos. Se esperaban 3 columnas, pero se encontraron 2." | `clase.py:135-139` |
| Celda vacía | **No es error**: `None` | — | `funciones.py:81-82` |
| Valor raro con tipo inferido | **No es error**: la columna queda `str` | — | `funciones.py:75` |
| Valor no convertible con tipo forzado | `ValueError` | "Error en fila 3, columna 'cantidad': el valor 'veinte' no se puede convertir a int." | `funciones.py:94-115` |
| Columna de `forzar_tipo` inexistente | `ValueError` (al leer) | "La columna 'zz' indicada en forzar_tipo no existe en la tabla." | `clase.py:148-149` |
| Columna seleccionada inexistente | `ValueError` (al leer) | "La columna seleccionada 'zz' no existe en la tabla." | `clase.py:194-195` |
| Delimitador vacío | `ValueError` (al construir) | "El delimitador no puede ser vacío." | `clase.py:27-28` |
| Tipo no soportado en `forzar_tipo` | `ValueError` (al configurar) | "Tipo no válido. Use int, float, str o bool." | `clase.py:40-41` |
| Límite negativo | `ValueError` (al configurar) | "El limite de filas no puede ser negativo" | `clase.py:51-52` |
| Rango inválido (`(0, 3)`, `(3, 2)`) | `ValueError` (al configurar) | "Rango invalido: 'inicio' debe ser >= 1 y 'fin' >= 'inicio'" | `clase.py:57-58` |

**Por qué filas vacías = error y no "saltearlas".** Una línea en blanco en medio de los datos suele indicar un archivo mal armado (dos archivos pegados, un corte). Saltearla en silencio ocultaría el problema. Además, al no saltear nada, el número de línea de los mensajes siempre es exacto. El costo: un archivo con dos saltos de línea al final da error, y en un archivo de una sola columna no se puede representar un nulo (7.1).

**Por qué la distinta cantidad de campos es error y no se completa con `None`.** Si sobra un campo, no hay forma de saber cuál sobra (¿una coma dentro de un texto?, ¿una columna corrida?). Si falta uno, no se sabe cuál falta. Completar o recortar podría correr todos los valores de columna sin aviso.

**Por qué los errores de configuración saltan al configurar y los de columnas al leer.** Lo que no depende del archivo (delimitador vacío, tipo no soportado, límite negativo, rango al revés) se valida en el setter: falla lo antes posible. Lo que depende del archivo (que una columna exista) solo se puede validar cuando se conoce el encabezado.

---

## 6. Relación con la teoría de la cátedra

Esta sección sirve para dos preguntas típicas de la defensa: **"¿qué vieron en la materia que aparezca en el código?"** y **"¿por qué no usaron X, si lo vimos?"**. Cada fila dice dónde está el concepto en el código, en qué apunte se ve y si es una aplicación buena o discutible. Las valoraciones son honestas: cuando algo se podría haber hecho mejor con lo que da la cátedra, se dice.

**Cómo se citan los apuntes.** "U2 Encapsulamiento §5.1" significa *Unidad 2, apunte `02_oop/02_encapsulamiento.pdf`, sección 5.1*. Los nombres cortos son:

| Unidad | Nombre corto → archivo |
|---|---|
| U1 (`01_programacion_en_python/`) | Introducción → `01_introduccion.pdf` · Funciones → `02_funciones.pdf` · Condicionales → `03_ejecucion_condicional.pdf` · Colecciones → `04_colecciones_de_datos.pdf` · Repetitiva → `05_ejecucion_repetitiva.pdf` · Código externo → `06_uso_de_codigo_externo.pdf` · Scripting → `07_scripting.pdf` · E/S → `08_io.pdf` |
| U2 (`02_oop/`) | Fundamentos de POO → `01_fundamentos.pdf` · Encapsulamiento → `02_encapsulamiento.pdf` · Herencia → `03_herencia.pdf` · Polimorfismo → `04_polimorfismo.pdf` · Excepciones → `05_excepciones.pdf` |
| U3 (`03_programacion_funcional/`) | Fundamentos de PF → `01_fundamentos.pdf` · Recursión → `02_recursion.pdf` · Orden superior → `03_funciones_de_orden_superior.pdf` · Evaluación → `04_estrategias_de_evaluacion.pdf` · Generadores → `05_generadores.pdf` |
| U4 (`04_estructuras_lineales/`) | Arreglos → `01_arreglos.pdf` · Estructuras lineales → `02_estructuras_lineales.pdf` · Ordenamiento → `03_ordenamiento.pdf` |

### 6.1 Unidad 1: las herramientas básicas

| Concepto | Dónde aparece | Apunte | Por qué es buena (o discutible) aplicación |
|---|---|---|---|
| Funciones chicas, una tarea cada una | `funciones.py:1-133` (8 funciones). `separar_linea` se reutiliza en `clase.py:105` y `133` | U1 Funciones §1-2 | **Buena.** Cada función es un "mini-programa" con un nombre que dice qué hace; se reutiliza y se prueba sola. |
| No mezclar devolver un valor con efectos colaterales | No hay ningún `print` en `modulo/`; todos están en `ejemplos.py`. `leer` devuelve el resultado (`clase.py:82`) | U1 Funciones §4 | **Buena.** El apunte desaconseja que una función calcule e imprima a la vez. Acá calcular y mostrar están separados, y por eso el lector sirve para cualquier programa. |
| Varios valores de retorno y desempaquetado | `return encabezados, filas_crudas` (`clase.py:143`) recibido en `clase.py:74`; `inicio, fin = self._rango_filas` (`clase.py:199`) | U1 Funciones §3.4; Introducción §3.3 | **Buena.** Dos resultados de la misma pasada viajan juntos sin guardarlos en `self`. |
| Argumentos por defecto | `__init__(self, delimitador=",", encabezado=True)` (`clase.py:21`) | U1 Funciones §7 | **Buena.** `LectorCSV()` cubre el caso más común. Los defaults son inmutables y el `{}` y el `[]` se crean en el cuerpo (`clase.py:32-33`). |
| `None` como ausencia de información | Celda vacía → `None` (`funciones.py:81-82`); opciones sin configurar (`clase.py:34-36`) | U1 Introducción §2.4 | **Buena.** Es literalmente el criterio del apunte: `0` y `""` son valores, `None` es "no hay dato". |
| Conversión entre tipos | `int()`/`float()` en `funciones.py:21`, `30`, `101`, `110`; rama propia de `bool` (`funciones.py:87-97`) | U1 Introducción §2.5 | **Buena.** Se delega en los constructores de Python, y se evita la trampa de `bool("false")`, que da `True`. |
| Comparación de cadenas y `.lower()` | `funciones.py:12` y `88`; en cambio `clase.py:115` compara nombres sin normalizar | U1 Introducción §4.3 y §5.3 | **Buena.** Es una decisión explícita: booleanos sin importar mayúsculas, nombres de columna respetando mayúsculas (son claves distintas). |
| Identidad: `is` / `is not` con `None` | `clase.py:192`, `198`, `207`, `214`; `ejemplos.py:23` | U1 Introducción §4.3 | **Buena.** `None` es un objeto único, así que se pregunta por identidad. |
| Operadores lógicos y su prioridad | `inicio < 1 or fin < inicio` (`clase.py:57`); `clase.py:207` | U1 Introducción §4.2 y §4.3 (la tabla de prioridades que pone las comparaciones por encima de `not`/`and`/`or` está en §4.3) | **Buena.** Las comparaciones se resuelven antes que `and`/`or`, así que no hacen falta paréntesis. El cortocircuito se ve en U3 (6.3). |
| f-strings | Mensajes en `funciones.py:94-97`, `103-106`, `112-115`, `117` y `clase.py:92`, `95`, `114`, `116`, `131`, `137-138`, `149`, `195`; nombres generados en `clase.py:121` | U1 Introducción §5.2 | **Buena, con un matiz.** Arman mensajes con fila, columna y valor en una línea. Pero escribir `'{col}'` entre comillas hace que una columna pedida como `2024` (número) se muestre como `'2024'` (7.2). |
| `split`, `strip`, `rstrip` | `funciones.py:3` y `6`; `clase.py:90`, `102`, `130` | U1 Introducción §5.4 (`strip`) y §6, Apéndice (tabla de métodos de cadenas, donde está `split`); el `rstrip("\n")` al leer un archivo aparece en U4 Estructuras lineales §2.5 | **Buena, con un matiz.** `split` acepta separadores de varios caracteres y `rstrip("\n\r")` no se lleva los tabs. El matiz: el `strip()` de la línea entera antes de separar hace que `,,` sea una fila de `None` pero una fila de tabs sea error (7.1). |
| Reglas y consejos de nombres | Todo el código | U1 Introducción §3.1 | **Buena.** Descriptivos, `snake_case`, sin tildes ni ñ (ver 4.3). |
| Listas y el patrón "lista vacía + `for` + `append`" | `funciones.py:4-6`, `38-41`; `clase.py:88-90`, `109-117`, `125-141`, `167-186`, `205-211`, `215-218` | U1 Colecciones §2; Repetitiva §3 | **Buena.** No se sabe de antemano cuántas filas hay y el orden importa. Es el patrón de U1; en U3 se escribiría con comprehensions (6.4). |
| Indexación desde 0 y numeración para personas | `i + 1` (`clase.py:114`, `127`); `fila_i + 2` / `fila_i + 1` (`clase.py:172-174`); `col_{i}` (`clase.py:121`) | U1 Colecciones §2.5 | **Buena, con un matiz.** Los mensajes usan base 1, como un editor de texto; los nombres generados usan base 0 (5.9). |
| Slicing | `filas_tipadas[inicio - 1 : fin]` (`clase.py:200`) | U1 Colecciones §2.6 | **Buena.** Traduce "filas 1 a N, extremos incluidos" al slice que excluye el final, sin bucles. |
| `in` / `not in` y `len()` | Listas: `clase.py:40`, `115`, `148`, `194`, `funciones.py:13`. Diccionario: `clase.py:158`. `len`: `clase.py:94`, `106`, `135` | U1 Colecciones §2.8 y §4.2 | **Buena.** Son las validaciones centrales (repetidos, columnas inexistentes, cantidad de campos). Sobre listas es búsqueda lineal (6.3). |
| Tuplas para lo que no cambia | Rango como tupla (`clase.py:59`); pero listas fijas en `clase.py:40` y `funciones.py:13` | U1 Colecciones §3.3 | **Discutible (detalle).** El rango está bien. Los tipos válidos y los literales `"true"`/`"false"` son colecciones fijas: el apunte pediría tupla, con un ejemplo casi igual (tipos de identificación válidos). |
| Diccionarios: claves únicas y orden de inserción | Cada fila (`clase.py:176-186`); `_tipos_columnas` (`clase.py:43`); `recortar_diccionario` (`funciones.py:130-133`) | U1 Colecciones §4 | **Buena.** Las claves únicas justifican el error por encabezado repetido; el orden de inserción explica que el resultado respete el orden de las columnas. |
| Estructuras anidadas (registros) | Lista de listas (`clase.py:125-141`) → lista de diccionarios (`clase.py:167-188`) | U1 Colecciones §4.5 (estructuras anidadas) y §3.3 (donde aparece el "dolor de cabeza" de las listas paralelas) | **Buena.** Evita las listas paralelas que el apunte llama "dolor de cabeza" (D15). |
| `for` con `range` (recorrer con índice) | `clase.py:111`, `120`, `126`, `155`, `168`, `177` | U1 Repetitiva §3.3 | **Buena.** El índice hace falta para numerar errores y alinear cada valor con su encabezado. `enumerate` sería más idiomático (6.5). |
| `break` | `funciones.py:52`, `61`, `70`; `clase.py:208` | U1 Repetitiva §4.1 | **Buena.** Corta apenas aparece un contraejemplo o apenas se junta el límite. |
| Valor de verdad de un objeto | `if not funcion(...)` (`funciones.py:123`); `if self.encabezado:` (`clase.py:110`, `171`) | No tiene un apartado propio: aparece en U1 Colecciones §5 (`all(s)` usa `bool(e)`) y en U2 Polimorfismo §4 (`__bool__` y `bool(obj)`) | **Discutible.** Es flexible, pero un filtro escrito sin `return` descarta todo sin error y `encabezado="no"` cuenta como `True` (7.2). |
| Módulos, paquetes e imports explícitos | `clase.py:11-17`; `ejemplos.py:1-2` | U1 Código externo §2-3 | **Buena, con un matiz.** Nada de `import *`; se importa solo lo que se usa. La carpeta se llama `modulo` pero es un paquete (D2). |
| Script vs módulo | `modulo/` solo tiene definiciones; `ejemplos.py` es el script | U1 Scripting §2 | **Buena.** Importar el lector no ejecuta nada. Falta el `if __name__ == "__main__":` en el script (6.4). |
| Abrir y leer archivos: modo `"r"`, `encoding="utf-8"`, `with` | `clase.py:87-90` | U1 E/S §2.3 y §2.5 | **Buena.** Es exactamente la recomendación del apunte (encoding explícito por Windows, `with` para cerrar siempre). Límites: BOM y latin-1 (7.1). |
| `FileNotFoundError` | `clase.py:91-92` | U1 E/S §2.3; U2 Excepciones §9.2 | **Buena, con un matiz.** Mensaje propio con la ruta y el mismo tipo de excepción; pero se relanza sin `from` (6.4). |
| Rutas relativas | `"datos1.csv"`, `"datos2.txt"`, `"derror.csv"` en `ejemplos.py:8`, `27`, `35`, `49` | U1 E/S §3.3 y §3.4 (el consejo de partir de un directorio base está en §3.4) | **Discutible.** Funcionan solo si se ejecuta parado en la carpeta del proyecto; el apunte aconseja armar las rutas desde una carpeta base. `leer()` igual acepta un `Path`, porque `open()` lo acepta. |

### 6.2 Unidad 2: la clase y las excepciones

| Concepto | Dónde aparece | Apunte | Por qué es buena (o discutible) aplicación |
|---|---|---|---|
| Clase como molde, objeto como instancia | `class LectorCSV:` (`clase.py:20`); cuatro instancias independientes en `ejemplos.py:6`, `21`, `34`, `45` | U2 Fundamentos de POO §3-4 | **Buena.** La configuración es estado que se arma en varios pasos y se reutiliza: justo lo que justifica un objeto (D1, D4). |
| Los tipos son clases | Se guardan y comparan clases: `clase.py:40`, `43`; `inferir_tipo_columna` devuelve clases (`funciones.py:45`, `54`, `63`, `72`, `75`) | U2 Fundamentos de POO §3 (recuadro "¿Clases o tipos?") | **Buena.** Inferidos y forzados se guardan igual, sin traducir strings (D14). |
| `__init__` con parámetros por defecto | `clase.py:21-36` | U2 Fundamentos de POO §4 y §4.1 | **Buena, con un matiz.** Valida el delimitador vacío (`clase.py:27-28`), pero no `encabezado` ni el tipo de `delimitador`. |
| `self` | Primer parámetro de todos los métodos (`clase.py:21`, `38`, `45`, `49`, `55`, `61`, `65`, `84`, `99`, `145`, `190`) | U2 Fundamentos de POO §6 | **Buena.** Los métodos protegidos leen la configuración sin recibirla por parámetro. |
| Atributos de instancia y atributos opcionales en `None` | `clase.py:30-36` | U2 Fundamentos de POO §5 y §5.1 | **Buena.** Todos los lectores tienen siempre la misma estructura y `None` significa "no configurado". |
| Métodos que modifican estado y métodos que devuelven resultados | Configuración: `clase.py:38-63`. Resultado: `leer` (`clase.py:65-82`) | U2 Fundamentos de POO §6.1-6.3 | **Buena.** Separación nítida: unos preparan el objeto, `leer` es el único que produce datos. |
| Interior e interfaz pública | Públicos `clase.py:21-82`; protegidos `clase.py:84-221` | U2 Encapsulamiento §1 (Prefacio, analogía del auto), §2 y §3.2 | **Buena.** `help(LectorCSV)` muestra solo la interfaz pública; es la analogía del auto (D6). |
| Docstrings | Docstrings breves (de una a cinco líneas) en todas las funciones y métodos (`funciones.py:2`, `11`, `19`, `28`, `37`, `79-80`, `121`, `129`; `clase.py:22-26`, `39`, ...) | U2 Encapsulamiento §4.1 | **Discutible.** Hay docstrings, pero la clase no tiene (`LectorCSV.__doc__` es `None`), no hay secciones *Parameters*/*Returns* y los criterios están en un comentario (`clase.py:1-9`) que `help()` no muestra. |
| Setters que validan | `forzar_tipo` (`clase.py:38-43`), `establecer_limite` (`49-53`), `establecer_rango` (`55-59`) | U2 Encapsulamiento §5.1 | **Buena, con un matiz.** Lanzan `ValueError` en lugar de imprimir (mejor que el ejemplo del apunte). Pero validan el valor y no el tipo, y no hay getters (7.2). |
| Atributos y métodos protegidos (un guion bajo) | `clase.py:32-36`; métodos `clase.py:84`, `99`, `145`, `190` | U2 Encapsulamiento §5.2 | **Buena, con un matiz.** Convención bien usada y respetada por `ejemplos.py`. `delimitador` quedó público y su validación se puede saltear (D5). |
| Duck typing | `if not funcion(fila_diccionario):` (`funciones.py:123`); `agregar_filtro` acepta cualquier cosa (`clase.py:45-47`) | U2 Encapsulamiento §4.2 (recuadro "Duck typing") | **Buena, con un matiz.** Cualquier cosa que se pueda llamar sirve de filtro; el costo es que no se valida al agregarlo (7.2). |
| Polimorfismo | Implícito: `in` sobre una lista (`clase.py:115`) y sobre un diccionario (`clase.py:158`); los filtros reciben el mismo "mensaje" (`funciones.py:123`) | U2 Polimorfismo §1-2 | **Aceptable.** No hay jerarquía propia (6.4); el polimorfismo aparece en la forma natural de Python (D13). |
| Excepciones en lugar de `print` | Todos los `raise` (`clase.py:28`, `41`, `52`, `58`, `92`, `95`, `103`, `114`, `116`, `131`, `136`, `149`, `195`; `funciones.py:94`, `103`, `112`, `117`) y la captura en `ejemplos.py:48-52` | U2 Excepciones §1 y §5 | **Muy buena.** El lector señala que no puede cumplir lo pedido y el programa que lo usa decide qué hacer (D9). |
| Construir la excepción: tipo + mensaje con el valor | `funciones.py:94-97`, `103-106`, `112-115` | U2 Excepciones §5.1 | **Buena, con un matiz.** Fila, columna, valor y tipo pedido. Los mensajes de configuración (`clase.py:41`, `52`, `58`) no dicen qué valor se recibió. |
| ¿`TypeError` o `ValueError`? | Todo es `ValueError` (más `FileNotFoundError`) | U2 Excepciones §4 (recuadro) | **Discutible.** `ValueError` es correcto para `'veinte'`. Pero un argumento de tipo equivocado en la configuración termina en un `TypeError` técnico de Python, no en uno propio (7.2). |
| Propagación y traceback | `funciones.py:103` → `clase.py:182` → `clase.py:77` → `ejemplos.py:49` | U2 Excepciones §3 y §5.2 | **Buena.** Los métodos internos no capturan nada: el error sube hasta quien sabe qué hacer con él. |
| `try/except` con excepciones específicas | `funciones.py:20-24`, `29-33`, `100-106`, `109-115`; `clase.py:86-92`; `ejemplos.py:48-52` | U2 Excepciones §6 (recuadro "¡A evitar!", en §6.7) | **Buena.** No hay ningún `except:` sin tipo ni `except Exception`. |
| ¿Lanzar o devolver un valor? | `es_entero` traduce el error a `False` (`funciones.py:23-24`); `convertir_valor` lanza (`funciones.py:102-106`) | U2 Excepciones §5 y recuadro "¿Warning o excepción?" (§8.4) | **Buena.** En la inferencia, "no es entero" es una respuesta esperada; con un tipo forzado, es un contrato que no se puede cumplir. |

### 6.3 Unidades 3 y 4: el núcleo funcional y el costo

| Concepto | Dónde aparece | Apunte | Por qué es buena (o discutible) aplicación |
|---|---|---|---|
| Funciones puras | Las 8 de `funciones.py:1-133` | U3 Fundamentos de PF §2 | **Buena.** Misma entrada, misma salida, sin tocar nada de afuera: se prueban sin crear un lector. `cumple_todos_los_filtros` es pura solo si los filtros lo son. |
| Efectos secundarios contenidos | Solo los métodos de configuración modifican `self` (`clase.py:43`, `47`, `53`, `59`, `63`); `leer` no lo modifica | U3 Fundamentos de PF §2.1 | **Buena.** Diseño "núcleo puro + objeto con estado". `leer` no es pura (depende del archivo), pero no deja rastros en el objeto (D4). |
| Referencias a objetos mutables | `self._columnas = lista_columnas` (`clase.py:63`); el filtro recibe el diccionario real (`funciones.py:123`) | U3 Fundamentos de PF §2.1 | **Discutible.** La lista guardada se puede cambiar desde afuera y un filtro puede modificar la fila del resultado (7.2). |
| Funciones como objetos de primera clase | Lista de funciones (`clase.py:33`, `47`); tipos como valores de un diccionario (`clase.py:43`, `152-164`) | U3 Fundamentos de PF §3 | **Buena.** El criterio de filtrado se inyecta sin que el lector lo conozca de antemano. |
| Funciones de orden superior | `cumple_todos_los_filtros` (`funciones.py:120-125`) | U3 Fundamentos de PF §3.1; Orden superior §1 | **Buena.** Recibe funciones y las combina con AND. |
| `lambda` | `ejemplos.py:23` | U3 Fundamentos de PF §4 | **Buena.** Es el uso que propone el apunte: una condición corta, de un solo uso, pasada como argumento. |
| Evaluación inmediata | `num_fila_archivo` y `nombre_col` se pasan en cada celda (`clase.py:182-184`); cada etapa de `leer` produce la lista completa (`clase.py:71-80`) | U3 Evaluación §3 | **Aceptable.** Es lo que impone Python; el costo es mínimo y el texto del error solo se arma si hay error. |
| Cortocircuito del `and` | `clase.py:207`; `ejemplos.py:23`; el `return False` temprano de `funciones.py:123-124` | U3 Evaluación §4.1 | **Muy buena.** El orden de los operandos evita `0 >= None` y `None < 15`. Es probablemente la pregunta teórica más directa sobre el código. |
| Iterables e iteradores | `for linea in archivo` (`clase.py:89`) | U3 Generadores §4 | **Buena.** El archivo es un iterador; recorrerlo con `for` es lo idiomático (y por eso cada línea trae su `\n`). |
| Listas como arreglos: `append` al final y lectura por índice | `append` en todo el pipeline; lecturas `clase.py:112`, `128`, `169`, `179` | U4 Arreglos §2.1 | **Buena.** Las operaciones dominantes son O(1) (amortizado en el `append`). Nunca se usa `insert(0, x)` ni `pop(0)`. |
| Búsqueda lineal | `in` sobre listas (`clase.py:115`, `148`, `194`); las banderas con `break` (`funciones.py:48-72`) buscan un contraejemplo | U4 Arreglos §2.1 y §3.4 | **Aceptable.** La cantidad de columnas es chica; sobre muchas columnas convendría un `set` (6.4). |
| Big O del lector | Todo `leer` | U4 Arreglos §4 | **Buena.** O(L·K) para L filas y K columnas: lineal en el tamaño del archivo. Las hasta cuatro pasadas de la inferencia son una constante que Big O descarta. |
| Complejidad cuadrática escondida | `nombre in encabezados` dentro de un `for` (`clase.py:111-117`) | U4 Arreglos §4.4 | **Discutible (detalle).** Es el mismo patrón que `contiene_duplicados` del apunte: O(K²). Con un `set` sería O(K) (3.2.11). |
| Complejidad espacial | `lineas`, `filas_crudas` y `filas_tipadas` vivas a la vez (`clase.py:71-80`) | U4 Ordenamiento §8; U3 Generadores §3 | **Aceptable.** Memoria O(L·K) a cambio de simplicidad (D7). |
| Mantenibilidad vs eficiencia | Doble conversión: `funciones.py:21` y `30` prueban, `funciones.py:101` y `110` vuelven a convertir | U4 Arreglos §1 | **Buena.** Se priorizó tener funciones separadas y claras a costa de un factor constante. |

### 6.4 Lo que la teoría ofrece y NO se usó (las diez preguntas más probables)

| Concepto (apunte) | Dónde encajaría | Por qué no se usó | ¿Lo agregaríamos? |
|---|---|---|---|
| **Herencia** (U2 Herencia §2; clases abstractas §2.5) | Subclases por formato (`LectorTSV`) o una clase abstracta `Lector` | Hay un solo tipo de lector y las variantes son **datos** (el delimitador), no comportamientos distintos. `LectorCSV.__mro__` es `(LectorCSV, object)`: solo la herencia implícita de `object` (D13). | Solo para **excepciones propias** (ver abajo), que es el uso de herencia que muestra la unidad de Excepciones. Una jerarquía de lectores sería sobre-ingeniería. |
| **`@property`** (U2 Encapsulamiento §5.4) | `delimitador`, y opcionalmente `limite` | Se prefirieron métodos con verbo (`establecer_limite`), que se leen solos y validan igual; `establecer_rango` recibe dos valores, algo que encaja mejor en un método. | **Sí, para `delimitador`**: hoy es público y `lector.delimitador = ""` saltea la validación (D5 tiene el código probado). |
| **Excepciones propias** (U2 Excepciones §7 y §9.1) | `class LectorCSVError(ValueError)` con hijas como `ConversionTipoError` | `ValueError` describe bien "valor inválido" y la consigna solo pide un mensaje con fila y columna. | **Sí.** Al heredar de `ValueError`, el `except ValueError` de `ejemplos.py` la sigue capturando (verificado), pero además permite distinguir los errores del lector de cualquier otro `ValueError` (por ejemplo, un `UnicodeDecodeError`, que también es `ValueError`). |
| **`raise ... from`** (U2 Excepciones §9.2) | `funciones.py:102-106` y `111-115`; `clase.py:91-92` | Se relanza una excepción nueva dentro del `except` para dar un mensaje propio. Con el `try/except` de `ejemplos.py` solo se ve el mensaje, así que no se nota. | **Sí.** Sin `from`, el traceback dice "During handling of the above exception, another exception occurred", como si fueran dos errores. `from error` declara la causa; `from None` la oculta (con cuidado, porque se pierde información). |
| **Generadores y `yield`** (U3 Generadores §2-3) | `_leer_archivo` como función generadora | La inferencia necesita **toda** la columna antes de convertir, y un generador se agota (la segunda vez que se recorre no da nada): habría que leer el archivo dos veces (D7). Para archivos chicos la lista es más simple e indexable. | Solo si hubiera que leer archivos enormes, con doble pasada. |
| **Comprehensions** (U3 Orden superior §3) | `separar_linea` (`funciones.py:3-7`), `no_vacios` (`funciones.py:38-41`), `recortar_diccionario` (`funciones.py:130-133`), `resultado_final` (`clase.py:215-218`) | Se usó el patrón de U1 (lista vacía + `for` + `append`), que se lee paso a paso. Las versiones con comprehension dan el mismo resultado (verificado para `separar_linea` y `recortar_diccionario`). | **Sí, como mejora de estilo**: el apunte las presenta como la forma preferida frente a `map`/`filter`. |
| **`all()`** (U1 Colecciones §5) | `cumple_todos_los_filtros` y las tres banderas de `inferir_tipo_columna` | Con una expresión generadora es material de U3; la versión manual muestra explícitamente la salida temprana. Es equivalente, incluido el corte (verificado). | Opcional. Ojo con `all([])`, que da `True`: por eso la guarda de la columna vacía (`funciones.py:44-45`) es imprescindible en las dos versiones. |
| **Conjuntos (`set`)** (U4 Arreglos §2.2) | Detectar encabezados repetidos (`clase.py:115`) | Con pocas columnas la diferencia no se nota y la lista igual hace falta para conservar el orden. | **Sí, es barato**: un `set` auxiliar de nombres vistos baja de O(K²) a O(K) (con 20.000 columnas: 1,29 s contra 0,0024 s, ver 3.2.11). |
| **`__init__.py`** (no figura en los apuntes) | `modulo/__init__.py` vacío | No hace falta: desde Python 3.3 una carpeta sin ese archivo se importa igual, como *namespace package* (verificado: `modulo.__path__` existe y `modulo.__file__` es `None`). | **Sí**, vacío: lo vuelve un paquete "regular" y deja clara la intención. Si preguntan, aclarar que no está en los apuntes. |
| **`if __name__ == "__main__":`** (U1 Scripting §3) | `ejemplos.py` | `ejemplos.py` no se pensó para ser importado, y los módulos (`funciones.py`, `clase.py`) solo tienen definiciones, así que no lo necesitan. | **Sí, en `ejemplos.py`**: hoy `import ejemplos` ejecuta los cuatro ejemplos e imprime 42 líneas (verificado). |

### 6.5 Otros conceptos de la teoría que no aparecen (respuesta corta)

| Concepto (apunte) | Por qué no se usó | ¿Convendría? |
|---|---|---|
| `return self` y encadenamiento (U2 Fundamentos de POO §6.4) | No era requisito; una llamada por línea es igual de clara. | Sí: una línea por método y permite `LectorCSV().forzar_tipo(...).establecer_limite(2)` (7.2). |
| Getters (U2 Encapsulamiento §5.1) | La consigna no pide consultar la configuración. | Con `@property` vendrían incluidos. |
| Doble guion bajo y *name mangling* (U2 Encapsulamiento §5.3) | Solo **emula** privacidad y sirve para evitar choques de nombres con subclases, que no hay. | No. |
| Atributos de clase y `@classmethod` (U2 Encapsulamiento §6) | No hacían falta. | Una constante `TIPOS_VALIDOS = (int, float, str, bool)` sí; constructores como `LectorCSV.tsv()` aportan poco. |
| Herencia múltiple, MRO, `super()` (U2 Herencia §3) | No hay jerarquía. | No. |
| Métodos mágicos como `__repr__` (U2 Polimorfismo §3.2) | No hacen falta para leer; hoy `repr(lector)` muestra `<modulo.clase.LectorCSV object at ...>`. | Sí, para depurar: mostrar la configuración. |
| Anotaciones de tipo (U2 Encapsulamiento §4.2) | No eran obligatorias, y el apunte aclara que anotar no valida nada. | Opcional, como documentación (`def leer(self, ruta_archivo: str) -> list[dict]:`). |
| Warnings (U2 Excepciones §8) | Se eligieron dos extremos: error que detiene o comportamiento silencioso. | Sí, para los casos con resultado razonable pero sospechoso (7.4). |
| `isinstance` + `TypeError` (U2 Excepciones §4) | Se validaron valores, no tipos. | Sí (7.4). |
| `map`, `filter`, `reduce` (U3 Orden superior §2) | El apunte los presenta como menos idiomáticos que las comprehensions, y el `for` con `break` combina filtro y límite en un solo recorrido. | No. |
| Expresión condicional (U3 Orden superior §2.3; Evaluación §4.3) | El `if/else` en bloque de `clase.py:171-174` es más explícito. | Opcional (estilo). |
| Closures y `functools.partial` (U3 Fundamentos de PF §6; Orden superior §4) | No hacen falta **dentro** del lector. | Sirven **al usuario** para armar filtros parametrizables: `agregar_filtro` acepta cualquier callable (D13). |
| Decoradores (U3 Orden superior §5) | No se pidió nada que los necesite. | Solo para medir tiempos. |
| `*args` (U3 Fundamentos de PF §5.1) | Se eligió recibir una lista en `seleccionar_columnas`. | Opcional: `seleccionar_columnas("nombre", "precio")` evitaría el error de pasar un solo string (7.2). |
| Recursión (U3 Recursión) | Recorrer filas no es un problema recursivo y el límite de recursión de Python (1000 llamadas por defecto) no alcanza para un CSV grande. | No. |
| `while` y `continue` (U1 Repetitiva §4 y §4.2) | Siempre se recorren colecciones conocidas; el único corte anticipado se resuelve con `for` + `break`. | No (`continue` podría usarse en `funciones.py:39-41`, es indistinto). |
| `enumerate` (U1 Colecciones §5) | Se usó `range(...)` con índice, el patrón visto en Repetitiva. | Opcional. |
| `pathlib` y rutas desde una carpeta base (U1 E/S §3) | Las rutas de `ejemplos.py` son relativas. | Sí, para que la demo funcione desde cualquier carpeta. |
| `argparse` (U1 Scripting §4) | No era requisito. | Útil para la defensa: leer un CSV nuevo sin editar código. |
| Pilas, colas, listas enlazadas, búsqueda binaria, ordenamiento (U4) | El lector necesita acceso por índice y conservar el orden del archivo; no ordena nada. Una lista enlazada haría O(N) cada acceso por posición. | No. |

### 6.6 El mapa en cuatro líneas (para decir en voz alta)

- **U1 da las herramientas**: listas, diccionarios, `split`/`strip`, `with open(..., encoding="utf-8")`, `None` para los nulos.
- **U2 da la estructura**: una clase que encapsula la configuración, setters que validan, atributos protegidos y excepciones en lugar de `print`.
- **U3 da el núcleo**: funciones puras, filtros como funciones de primera clase, cortocircuito como guarda contra `None`.
- **U4 da el vocabulario para hablar del costo**: O(L·K) en tiempo y memoria, búsqueda lineal en los encabezados y el `set` como mejora.

---

## 7. Limitaciones conocidas y qué cambiaríamos

La consigna pide poder explicar "las limitaciones de la solución", y en la defensa van a leer CSV que no conocemos. Conviene decir estas limitaciones **antes** de que aparezcan, con la causa exacta en el código. Todo lo que sigue se probó ejecutando el lector tal como fue entregado; los mensajes están copiados de la salida real.

### 7.1 Limitaciones del formato de entrada

| Situación | Qué hace el lector (verificado) | Por qué pasa | Cómo salir del paso en vivo |
|---|---|---|---|
| **BOM** al principio del archivo (Excel, opción "CSV UTF-8") | La primera clave queda `'\ufeffcodigo'` (el carácter U+FEFF, invisible, pegado adelante). Impresa sola se ve igual que `codigo`; en el `print` de la fila aparece como `'\ufeffcodigo'`, porque el `repr` escapa ese carácter. `forzar_tipo("codigo", str)` da `"La columna 'codigo' indicada en forzar_tipo no existe en la tabla."`. Sin encabezado, el primer valor queda `'\ufeff1'` y **toda** `col_0` pasa a `str` | `encoding="utf-8"` (`clase.py:87`) no descarta el BOM, y `strip()` tampoco lo saca porque Python no lo considera un espacio (`"\ufeff".isspace()` es `False`) | Ninguna desde afuera del código. La solución es una palabra: `encoding="utf-8-sig"` (7.4, punto 2) |
| Archivo en **latin-1 / cp1252** (o UTF-16) | `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf3 in position N: invalid continuation byte` (`0xf3` es la `ó` en latin-1; `N` es la posición de ese byte y depende del archivo), sin mensaje propio. Como `UnicodeDecodeError` es subclase de `ValueError`, el `except ValueError` de `ejemplos.py:50` la captura y muestra ese texto técnico | Solo se captura `FileNotFoundError` (`clase.py:91`) | Volver a guardar el archivo como UTF-8 |
| Booleanos **`VERDADERO`/`FALSO`** (Excel en castellano) | La columna queda `str`. Con `forzar_tipo("activo", bool)`: `"Error en fila 2, columna 'activo': el valor 'VERDADERO' no se puede convertir a bool."` | Solo se reconocen `true`/`false` (`funciones.py:13`, `89-92`), como está documentado (5.5) | Dejarlos como texto y filtrar con `fila["activo"] == "VERDADERO"` |
| **Coma decimal** de Excel en castellano (`1500,50`, archivo con `;`) | `precio` queda `str` (`'1500,50'`); un filtro `fila["precio"] < 2000` da `TypeError: '<' not supported between instances of 'str' and 'int'`; forzar `float` da `"... el valor '1500,50' no se puede convertir a float."`. Si el archivo usa `,` como separador, la coma decimal parte el número: `"Se esperaban 2 columnas, pero se encontraron 3."` | `float()` solo acepta punto decimal, y no hay ninguna opción para indicar otro separador decimal | Ninguna con la configuración actual. Es la mejora 12 de 7.4 |
| **Comillas** y **celdas multilínea** | `"Rosario, SF",2` da error de cantidad de campos. `"hola"` se conserva con las comillas. Con el encabezado entre comillas, la clave es `'"precio"'` y `fila["precio"]` da `KeyError`. Una celda con un salto de línea adentro da el error en la línea **siguiente** (`"Error en fila 3: ... se encontraron 1."`), no donde empieza | Se corta cada línea con `split` (`funciones.py:3`), sin estado de "dentro de comillas"; y se lee línea a línea, no registro a registro (D10) | Si las comillas no encierran ningún delimitador, el archivo se lee, pero las claves y los textos conservan las comillas (`fila['"precio"']`) y un número entre comillas queda `str`; si encierran un delimitador o un salto de línea, no se puede leer |
| Archivo de **una sola columna** con un valor faltante | `"Error en fila 3: Se encontró una fila vacía."`: es **imposible** representar un nulo | En un archivo de una columna, la celda vacía **es** una línea vacía, y la línea vacía se rechaza antes de separar (`clase.py:130-131`). Choca con la regla "celda vacía = `None`" (5.6) | Ninguna; reconocerlo como caso en que dos criterios propios chocan |
| `,,` es una fila de `None`, pero una fila de **tabs** o de **espacios** es error | `a,b,c` + `,,` → `{'a': None, 'b': None, 'c': None}`. La misma fila con `\t\t` (delimitador tab) o con espacios (delimitador espacio) → `"Error en fila 3: Se encontró una fila vacía."`. Además, las filas `,,` que Excel deja al final se devuelven como filas de `None` sin aviso | El chequeo es `linea_actual.strip() == ""` (`clase.py:130`), y `strip()` borra tabs y espacios pero no comas | Saber explicarlo: la misma "fila sin datos" es válida o es error según el separador |
| **Delimitador equivocado** | **No da error.** Un archivo con `;` leído con el `,` por defecto devuelve una sola columna con la línea entera: `{'producto;precio;stock': 'Yerba;1500;10'}`. Si además hay coma decimal, el error dice `"Se esperaban 1 columnas, pero se encontraron 2."`, que no menciona el delimitador | No hay detección del separador; una sola columna es una tabla válida | **Señal de alarma**: si el resultado tiene una sola clave larga, el delimitador está mal |
| **Separador espacio** | `Buenos Aires` se parte en dos campos (`"Se esperaban 2 columnas, pero se encontraron 3."`); un espacio invisible al final de la línea o dos espacios seguidos dan el mismo error | `split(" ")` corta en **cada** espacio y genera campos vacíos | Con `delimitador=None`, `str.split(None)` corta por cualquier grupo de blancos y tolera espacios dobles, pero funciona "por accidente" (no está validado ni documentado, 3.1.1) y sigue partiendo `Buenos Aires` |
| **`1.000`** (punto de miles) | Una columna `1.000`, `2.500` se infiere `float` y da **`1.0` y `2.5`, sin ningún aviso**. Si aparece `2.500.000`, toda la columna queda `str`. `1 500` (miles con espacio) también vuelve `str` toda la columna, incluido el `2000` | `float("1.000")` es válido en Python: el punto es decimal | Forzar `str` y no hacer cuentas con esa columna |
| **Códigos que parecen números** | `00123` → `123`; `+543414567890` → `543414567890` (pierde el `+`); código postal `0341` → `341`; `12E3` → `12000.0` (lo lee como notación científica); `30.123.456` queda `str` por suerte | La inferencia acepta todo lo que `int()`/`float()` aceptan (5.2) | `forzar_tipo(col, str)` conserva todos (verificado). Es justo el caso que pone la consigna |

**Otros casos del mismo estilo, para no sorprenderse:**
- **Archivo sin encabezado leído con `encabezado=True`** (el default): la primera fila de datos se usa como nombres sin avisar (`{'Yerba': 'Azucar', '1500': 980, '10': 0}`). Al revés, un archivo **con** encabezado leído con `encabezado=False` vuelve `str` todas las columnas, porque el nombre de la columna es un texto más en la inferencia.
- **Marcadores de nulo** como `NA`, `NULL`, `N/A`, `-`: no son `None` y vuelven `str` la columna (5.6). `nan` sí se lee, como `float("nan")`, que no es `None`.
- **Fechas**: `2024-01-15` queda `str`; `2024` y `20240115` se infieren `int`.
- **CSV de pandas sin `index=False`** (encabezado que empieza con coma): `"Error en fila 1, columna 1: El nombre de la columna está vacío."`. Se puede leer con `encabezado=False`.

**Antes de leer un CSV nuevo en la defensa (30 segundos con un editor de texto):** ¿qué separador usa?, ¿la primera línea es encabezado?, ¿hay coma decimal o puntos de miles?, ¿hay comillas?, ¿hay códigos con ceros adelante o con `+`?, ¿hay `NA`?, ¿es una sola columna? Y después de leer: si sale una sola clave larga, el delimitador está mal; si la primera clave "existe pero no se encuentra", es el BOM.

### 7.2 Limitaciones de la interfaz y la configuración

| Limitación | Ejemplo verificado | Por qué pasa |
|---|---|---|
| **Los setters validan el valor pero no el tipo** | `establecer_rango(1, 3.0)` se acepta y falla recién al leer: `TypeError: slice indices must be integers or None or have an __index__ method`. `establecer_limite(2.5)` se acepta y devuelve **3** filas. `establecer_limite("3")` o `establecer_rango("1", "3")` dan `TypeError: '<' not supported between instances of 'str' and 'int'`. `establecer_limite(True)` se toma como límite 1 | Solo se compara (`clase.py:51`, `57`); un `float` pasa la comparación y rompe después en el slicing (`clase.py:200`). Con 2.5, el corte `len(filas_filtradas) >= 2.5` recién se cumple con 3 filas. `True` pasa porque `bool` es subclase de `int` |
| Lo mismo en el constructor | `LectorCSV(encabezado="no")` lee con encabezado (un string no vacío es verdadero). `LectorCSV(delimitador=44)` falla al leer con `TypeError: must be str or None, not int`. `lector.delimitador = ""` después de construir da `ValueError: empty separator` | Solo se valida `delimitador == ""` (`clase.py:27-28`), y `delimitador` es público (D5) |
| **`agregar_filtro` no valida que el argumento se pueda llamar** | `agregar_filtro(5)` se acepta y `leer()` falla con `TypeError: 'int' object is not callable` | `clase.py:45-47` solo hace `append` (duck typing, D13) |
| **Los filtros se acumulan y no hay forma de quitarlos** | Un lector con `precio > 500` devolvió 4 filas; después de agregar `precio < 3000`, 2 | `_filtros` solo crece (`clase.py:47`); no existe un método para vaciarla |
| **El límite y el rango no se pueden deshacer** | `establecer_limite(None)` y `establecer_rango(None, None)` dan `TypeError: '<' not supported between instances of 'NoneType' and 'int'`. En cambio `seleccionar_columnas(None)` sí vuelve a "todas", por casualidad | Los setters comparan `None < 0` (`clase.py:51`, `57`); `seleccionar_columnas` no valida nada (`clase.py:63`) |
| **Alias de la lista de columnas** | `cols = ["nombre"]; lector.seleccionar_columnas(cols); cols.append("precio")` → la lectura siguiente devuelve también `precio` (`lector._columnas is cols` es `True`). Además, `seleccionar_columnas("nombre")` recorre el texto letra por letra: `"La columna seleccionada 'n' no existe en la tabla."` | `self._columnas = lista_columnas` (`clase.py:63`) guarda la misma lista, no una copia, y no se controla que sea una lista |
| **Los métodos devuelven `None` y no se encadenan** | `LectorCSV().forzar_tipo("codigo", str).establecer_limite(2)` → `AttributeError: 'NoneType' object has no attribute 'establecer_limite'` | Ningún método de configuración tiene `return` (`clase.py:38-63`) |
| **Mensajes confusos con nombres de columna numéricos** | En `provincia,2023,2024`, `seleccionar_columnas(["provincia", 2024])` da `"La columna seleccionada '2024' no existe en la tabla."`, aunque la columna existe (como texto `"2024"`). Lo mismo con `forzar_tipo(2024, int)` | Las claves siempre son `str`, y los mensajes ponen el valor entre comillas (`'{col}'`), así que el número `2024` se ve igual que el texto `'2024'` |
| **Los errores dentro de un filtro no dicen la fila** | Con `fila["cantida"]` (mal escrita): `KeyError: 'cantida'`. Con `fila["cantidad"] > 3` sobre `datos1.csv`: `TypeError: '>' not supported between instances of 'NoneType' and 'int'` (por la Regla), sin decir qué fila | El filtro se llama sin `try` (`funciones.py:123`) y el error sube tal cual |
| Y esos errores **dependen del rango y del límite** | El mismo filtro `fila["cantidad"] > 3` funciona con `establecer_rango(1, 3)` (Cuaderno, Lapicera, Carpeta) o con `establecer_limite(2)` (Cuaderno, Lapicera), porque la Regla nunca se evalúa | Los filtros solo se aplican a las filas del rango, y el bucle corta al juntar el límite (`clase.py:206-208`). Los errores de **conversión**, en cambio, frenan siempre (7.3) |
| Filtros mal escritos que **no** dan error | Un filtro con `def` sin `return` devuelve `[]` sin avisar. Un filtro que hace `fila["precio"] = 0` modifica el resultado (Cuaderno sale con precio `0`) | Se usa el valor de verdad del resultado (`None` cuenta como falso) y el filtro recibe el diccionario real, no una copia (3.1.7) |
| No hay forma de **consultar** la configuración | No hay getters y `repr(lector)` muestra `<modulo.clase.LectorCSV object at ...>` | No se definieron getters, properties ni `__repr__` (6.5) |

### 7.3 Limitaciones de eficiencia y de las pruebas

**Eficiencia.** Para los archivos del TP nada de esto se nota; son respuestas para "¿y si el archivo fuera enorme?".

| Limitación | Dato verificado | Por qué pasa |
|---|---|---|
| **El límite no ahorra lectura** | Con un archivo de 80.000 filas: 0,24 s sin límite y 0,26 s con `establecer_limite(1)` (en D7 hay otra medición con 200.000 filas: alrededor de 0,8 s en los dos casos). Los segundos exactos cambian según la máquina y la corrida; lo que se repite siempre es que los dos tiempos son prácticamente iguales | `leer` lee, separa, infiere y convierte el archivo entero (`clase.py:71-77`); el límite solo corta el último bucle (`clase.py:207-208`) |
| **Un error de conversión fuera del rango igual frena la lectura** | Con `establecer_rango(1, 1)` y un `x` en la fila 4 de una columna forzada a `int`: `"Error en fila 4, columna 'b': el valor 'x' no se puede convertir a int."`. Pasa lo mismo si esa columna no está en `seleccionar_columnas` | El rango y la selección se aplican **después** de convertir todas las filas y todas las columnas (D6) |
| **Una columna seleccionada mal escrita se detecta al final** | Con una columna inexistente en `seleccionar_columnas` y un error de conversión en el archivo, se informa primero el de conversión | La validación está en `clase.py:192-195`, después de `_convertir_tipos` |
| **Todo en memoria** | Mientras dura `leer` conviven `lineas`, `filas_crudas` y `filas_tipadas`, más la copia que hace el slicing del rango | Diseño elegido en D7: la inferencia necesita la columna entera. Memoria O(L·K) |
| **Doble conversión** | Cada celda de una columna numérica se convierte dos veces: `es_entero`/`es_flotante` prueban `int()`/`float()` y descartan el resultado (`funciones.py:21`, `30`), y después `convertir_valor` vuelve a convertir (`funciones.py:101`, `110`) | Separar "¿es entero?" de "convertir" (3.1.3). Es un factor constante: no cambia el O(L·K) |
| **Búsqueda lineal en los encabezados** | `nombre in encabezados` dentro del `for` es O(K²); con 20.000 columnas, 1,29 s contra 0,0024 s con un `set` (3.2.11). También son lineales los `in encabezados` de `clase.py:148` y `194` | Se usa una lista, que es búsqueda lineal (U4) |

**Pruebas.** Es la parte de la consigna (3.6) que quedó cumplida a medias, y conviene reconocerlo sin vueltas:
- `ejemplos.py` tiene cuatro ejemplos: inferencia con tipo forzado, combinación de opciones, otro delimitador y un error de conversión. **Faltan ejemplos de los casos problemáticos que pide la consigna**: archivo vacío, fila vacía, filas con distinta cantidad de campos, encabezado vacío o repetido. Tampoco se muestran `encabezado=False`, el tabulador ni un delimitador de varios caracteres, que el lector soporta.
- **No hay resultados esperados escritos**: se imprime lo que sale y hay que comparar a ojo. La consigna pide "ejemplos de uso con sus resultados esperados".
- Hay un único archivo con errores (`derror.csv`), y solo prueba un valor no convertible.
- La demo depende de ejecutarse parada en la carpeta del proyecto (rutas relativas), no tiene `if __name__ == "__main__":` y no hay `requirements.txt` para pandas.

### 7.4 Qué cambiaríamos con más tiempo

**Criterio de prioridad**: primero lo que la consigna pide y está incompleto; después lo que puede fallar con un CSV nuevo en la defensa; después la robustez de la interfaz; y al final calidad de código y eficiencia. Todas las mejoras se probaron sobre copias del código (sin tocar la entrega).

1. **Ejemplos y pruebas con resultado esperado.** Por cada caso, un archivo chico y una comparación:
   ```python
   assert lector2.leer("datos1.csv") == [{"nombre": "Cuaderno", "precio": 2500.5}, {"nombre": "Carpeta", "precio": 3200.0}]
   ```
   y para los errores, un `try/except ValueError as e:` que compare `str(e)` con el mensaje esperado (archivo vacío, fila vacía, campos de más, encabezado repetido). **Por qué:** es lo único de la consigna cumplido a medias (3.6), y demuestra que el lector "se comporta de acuerdo con lo que documentaron" (sección 5 de la consigna).

2. **`encoding="utf-8-sig"` en `clase.py:87`.** Una palabra. **Por qué:** Excel guarda "CSV UTF-8" con BOM, y es probable que un docente traiga un archivo así. Con `utf-8-sig`, un archivo con BOM da la clave `codigo` y uno sin BOM se lee exactamente igual (verificado).

3. **Warnings para lo "razonable pero sospechoso"** (`import warnings`). Cuatro avisos de una o dos líneas cada uno:
   ```python
   if valores_columna and all(v == "" for v in valores_columna):   # en _convertir_tipos
       warnings.warn(f"La columna '{nombre_col}' está completamente vacía; se dejó como str.")
   ```
   - columna numérica que quedó `str` por un `NA`: avisar si `inferir_tipo_columna` de los valores **sin** `"NA"`, `"NULL"`, `"N/A"`, `"-"` da `int` o `float`;
   - rango fuera de la tabla: `if inicio > len(filas_tipadas): warnings.warn(...)`;
   - delimitador probablemente equivocado: `if cant_columnas == 1 and any(s in primera_linea for s in (";", "\t", ",", "|") if s != self.delimitador): warnings.warn(...)`.

   **Por qué:** es exactamente el criterio de la cátedra para un warning: hay un resultado razonable, pero la persona debería enterarse. Hoy esas situaciones pasan en silencio (7.1). No cambia ningún resultado actual.

4. **Validar tipos con `isinstance` y lanzar `TypeError`** en los setters y el constructor:
   ```python
   if not isinstance(limite, int):
       raise TypeError(f"El límite debe ser un entero; se recibió {limite!r}.")
   ```
   (lo mismo para `inicio`/`fin`, `delimitador` como `str` y `encabezado` como `bool`). **Por qué:** es el recuadro "¿TypeError o ValueError?" de Excepciones: tipo equivocado → `TypeError`, valor inválido → `ValueError`. El error aparece al configurar y con un mensaje propio, no al leer con uno técnico. (Ojo: `True` igual pasa, porque `bool` es subclase de `int`.)

5. **`callable()` en `agregar_filtro`:** `if not callable(funcion_filtro): raise TypeError("El filtro debe ser una función.")`. **Por qué:** fallar al configurar, como el resto de los setters.

6. **Poder deshacer la configuración:** `def quitar_filtros(self): self._filtros = []`, y en `establecer_limite`/`establecer_rango`, `if limite is None: self._limite_filas = None` antes de comparar. **Por qué:** sin esto, para reutilizar un lector (D4) con otra consulta hay que crear uno nuevo.

7. **Copiar la lista de columnas:** `self._columnas = list(lista_columnas)` en `clase.py:63`, más un `TypeError` si llega un `str` suelto. **Por qué:** corta el alias con la lista del usuario y evita el error de las letras sueltas.

8. **Excepción propia y `raise ... from`:**
   ```python
   class LectorCSVError(ValueError): pass
   raise LectorCSVError(f"Error en fila {num_fila}, columna '{nombre_col}': ...") from error
   ```
   **Por qué:** al heredar de `ValueError`, `ejemplos.py` la sigue capturando (verificado), pero el programa usuario puede distinguir los errores del lector de cualquier otro `ValueError`; y `from error` deja escrita la causa en el traceback en lugar de "During handling of the above exception...". Es la herencia y el encadenamiento que muestra Excepciones (§7 y §9.2).

9. **`return self` en los cinco métodos de configuración.** **Por qué:** permite `LectorCSV().forzar_tipo("codigo", str).establecer_limite(2).leer("datos1.csv")` (verificado), como el encadenamiento de Fundamentos de POO §6.4.

10. **Errores de filtro con la fila:** envolver la llamada de `clase.py:210` en `try/except (KeyError, TypeError) as error:` y relanzar `LectorCSVError(f"Un filtro falló con la fila {fila}: {error!r}") from error`. **Por qué:** hoy un `KeyError` o un `TypeError` dentro del filtro no dice dónde ocurrió.

11. **Valores nulos configurables:** un parámetro `valores_nulos=("",)` en el constructor y, al principio de `_convertir_tipos`:
    ```python
    filas_crudas = [["" if e in self.valores_nulos else e for e in fila] for fila in filas_crudas]
    ```
    **Por qué:** con `valores_nulos=("", "NA")`, un CSV de R da `None` donde dice `NA` y la columna vuelve a ser `int` (verificado). Con el valor por defecto, el comportamiento es idéntico al actual.

12. **Separador decimal y booleanos configurables:** con `separador_decimal=","`, normalizar cada celda que *parezca* número:
    ```python
    candidato = texto.replace(".", "").replace(",", ".")
    return candidato if es_flotante(candidato) else texto
    ```
    (verificado: `'1500,50'` → `1500.5`, `'1.234,5'` → `1234.5`, y `'Hola, mundo'` queda intacto). Y los booleanos en dos tuplas, `VERDADEROS = ("true", "verdadero")` y `FALSOS = ("false", "falso")`, usadas por `es_booleano` y `convertir_valor`. **Por qué:** es el CSV que más probablemente traiga un docente argentino, y hoy no se puede leer bien ni forzando tipos.

13. **Filas vacías coherentes:** cambiar la condición de `clase.py:130` por `if linea_actual == "" and cant_columnas > 1:`. **Por qué:** una fila de tabs pasa a ser una fila de `None`, igual que `,,`, y un archivo de una columna puede tener nulos (verificado: `edad` con un hueco da `{'edad': None}`); una línea realmente vacía en una tabla de varias columnas sigue siendo error.

14. **Mensajes más precisos:** `{col!r}` en lugar de `'{col}'` (así `2024` se muestra sin comillas y `'2024'` con comillas), incluir el valor recibido en los mensajes de configuración (`clase.py:41`, `52`, `58`) y decir "línea N del archivo" en vez de "fila N".

15. **Calidad y teoría:** `delimitador` como `@property` (código en D5); el bloque de criterios de `clase.py:1-9` como docstring de la clase, para que lo muestre `help()`; `TIPOS_VALIDOS = (int, float, str, bool)` como tupla; un `__init__.py` vacío; `if __name__ == "__main__":` y rutas armadas con `Path(__file__).parent / "datos1.csv"` en `ejemplos.py`; un `__repr__` que muestre la configuración; un `requirements.txt` con `pandas`.

16. **Eficiencia:** validar las columnas seleccionadas junto con las de `forzar_tipo`, al principio de `_convertir_tipos` (hoy está en `clase.py:192-195`, después de convertir todo); un `set` de nombres vistos en el chequeo de repetidos; y, solo para archivos enormes, lectura con generadores en dos pasadas, o cortar la lectura al llegar al límite cuando todos los tipos están forzados.

17. **Comillas al estilo CSV** (lo más caro, por eso al final): separar carácter por carácter con un estado "¿estoy dentro de comillas?", para soportar `"Rosario, SF"` y celdas con saltos de línea. **Por qué al final:** es mucho más código y propenso a errores, y la consigna no lo exige.

---

## 8. Anexo: 15 frases para tener en la punta de la lengua

Respuestas cortas para decir en voz alta. Cada una resume una sección del documento; si el docente repregunta, la sección indicada tiene el detalle.

1. **"¿Cómo está organizado?"** (D1, D2)
   > "En dos módulos: `funciones.py`, con funciones puras que hacen una sola cosa (separar, detectar tipos, convertir, filtrar), y `clase.py`, con `LectorCSV`, que guarda la configuración y coordina el proceso. El script de ejemplos queda afuera y es el único que imprime."

2. **"¿Por qué una clase y no una función con muchos parámetros?"** (D3, D4)
   > "Porque la configuración se arma en varios pasos (varios tipos forzados, varios filtros), cada paso se valida apenas se configura, y el mismo lector se puede reutilizar con varios archivos: el objeto recuerda *cómo* leer, no *lo que* leyó."

3. **"¿Por qué no usaron herencia?"** (D13, 6.4)
   > "Porque hay un solo tipo de lector y las variantes, como el separador, son datos, no comportamientos distintos. Donde sí la usaríamos es en una excepción propia que herede de `ValueError`."

4. **"¿Qué significa el guion bajo en `_filtros`?"** (D5)
   > "Que el atributo es protegido: por convención no se toca desde afuera. En Python no hay atributos realmente privados; por eso la configuración se cambia con métodos que validan."

5. **"¿Cómo deciden el tipo de una columna?"** (5.2)
   > "Probamos bool, int, float y str, en ese orden, sobre los valores no vacíos, y una columna es de un tipo solo si todos sus valores lo son. `int` va antes que `float` porque todo entero también se puede leer como flotante: con `10`, `20` y `30.5` sale `float`."

6. **"¿Por qué miran toda la columna y no solo las filas pedidas?"** (D8)
   > "Para que el tipo no dependa de la consulta, y porque así, si la inferencia dice `int`, la conversión nunca falla. Los errores de conversión solo pueden aparecer con tipos forzados."

7. **"¿Qué es un nulo para ustedes?"** (5.6)
   > "Una celda vacía, o con solo espacios, y se guarda como `None` para cualquier tipo. Textos como `NA` o `NULL` no los tomamos como nulos porque pueden ser datos reales; es una limitación que reconocemos."

8. **"¿Qué pasa si fuerzo un tipo y un valor no se puede convertir?"** (5.7, D9)
   > "El lector se detiene con un `ValueError` que dice fila, columna, valor y tipo pedido. Nunca reemplaza el tipo que pidió el usuario por otro, como pide la consigna."

9. **"¿En qué orden se combinan rango, filtro, límite y columnas?"** (5.8)
   > "Primero el rango, que habla de posiciones en el archivo; después los filtros; el límite cuenta filas que cumplen el filtro; y al final se eligen las columnas, por eso se puede filtrar por una columna que no se devuelve. Si se quieren 'las primeras N filas y filtrar', se pide con rango más filtro."

10. **"¿Por qué el error dice 'fila 3' si es la segunda fila de datos?"** (5.9)
    > "Porque los mensajes cuentan líneas del archivo, y la línea 1 es el encabezado; así se encuentra el problema en un editor de texto. En cambio, el rango cuenta filas de datos desde 1, con los dos extremos incluidos."

11. **"¿Por qué lanzan excepciones en lugar de imprimir un aviso?"** (D9)
    > "Porque un `print` solo le avisa a quien mira la pantalla, y la excepción le avisa al programa, que decide qué hacer. Además preferimos que el lector se detenga a que devuelva datos mal leídos sin avisar."

12. **"¿Para qué está el `is not None` en el filtro del ejemplo?"** (5.10, 6.3)
    > "Por el cortocircuito del `and`: si la cantidad es `None`, la comparación `< 15` ni se evalúa y no hay `TypeError`. El mismo truco usa el lector en `clase.py:207` para el límite."

13. **"¿Por qué muestran la lista y además el DataFrame?"** (D12)
    > "Porque el lector devuelve Python puro y pandas cambia la representación: la columna `cantidad`, con un `None`, aparece como `10.0, 25.0, ...` con `NaN`. La lista muestra lo que realmente devolvimos."

14. **"¿Qué limitaciones tiene?"** (7.1-7.3)
    > "No soporta comillas ni coma decimal, no reconoce `VERDADERO`/`FALSO`, el BOM de Excel ensucia la primera columna, un delimitador equivocado no da error, y en un archivo de una sola columna no se puede representar un nulo. Además, el límite no ahorra lectura, porque se convierte todo el archivo antes de filtrar."

15. **"¿Qué cambiarían primero?"** (7.4)
    > "Agregaríamos ejemplos con resultados esperados para los casos problemáticos, que es lo que la consigna pide y nos quedó corto; después `encoding="utf-8-sig"` para el BOM, warnings para lo sospechoso pero no fatal, y validar tipos en los setters con `isinstance` y `TypeError`."
