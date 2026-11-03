# Preguntas para la exposición — Lector de datos tabulares (G24: Berruti, Liali, Vranjes)

> **Para qué sirve.** Es un banco de preguntas que los docentes pueden hacer en la defensa oral, cada una con una respuesta sugerida para decir en voz alta. Están agrupadas por tema y numeradas de corrido. Al final hay recetas listas para copiar en la demostración en vivo, una checklist para revisar un CSV nuevo antes de leerlo y un machete de una página.
>
> **Cómo se armó.** Toda respuesta que describe un comportamiento se comprobó ejecutando el código entregado, sin modificarlo (Python 3.12.2, pandas 2.2.2, en Windows). Los mensajes de error están copiados de la salida real. Las respuestas son coherentes con `01_Justificacion_de_decisiones.md` (citado como "01 §…") y con `03_Explicacion_formal_del_codigo.md` (citado como "03 §…"), donde está el detalle si el docente repregunta.
>
> **Convenciones.** `clase.py:207` = archivo `modulo/clase.py`, línea 207; `funciones.py:123` = `modulo/funciones.py`, línea 123. **Fila de datos** = fila de la tabla sin contar el encabezado (la que usa `establecer_rango`). **Línea del archivo** = renglón del archivo contando el encabezado (la que usan los mensajes de error). Dificultad: **[básica]**, **[media]**, **[difícil]**, **[trampa]**.
>
> **Cómo estudiar.** Tapar la respuesta, contestar en voz alta y recién después leer. Las **[trampa]** son las que más conviene repasar: casi todas tienen una respuesta corta y precisa. Si no se sabe algo en la defensa, lo honesto es decir "no lo probamos, pero por el código esperaríamos…" y razonarlo sobre la línea concreta.

---

## Índice

| Sección | Preguntas | Cantidad |
|---|---|---|
| [A. Generales y organización del código](#a-generales-y-organización-del-código) | 1 a 10 | 10 |
| [B. Decisiones de diseño y alternativas](#b-decisiones-de-diseño-y-alternativas) | 11 a 21 | 11 |
| [C. Programación orientada a objetos](#c-programación-orientada-a-objetos) | 22 a 37 | 16 |
| [D. Programación funcional](#d-programación-funcional) | 38 a 50 | 13 |
| [E. Lectura del archivo y separación de campos](#e-lectura-del-archivo-y-separación-de-campos) | 51 a 62 | 12 |
| [F. Encabezados](#f-encabezados) | 63 a 71 | 9 |
| [G. Tipos e inferencia](#g-tipos-e-inferencia) | 72 a 83 | 12 |
| [H. Tipos forzados](#h-tipos-forzados) | 84 a 92 | 9 |
| [I. Nulos y booleanos](#i-nulos-y-booleanos) | 93 a 101 | 9 |
| [J. Filas, columnas, filtros, límite y rango](#j-filas-columnas-filtros-límite-y-rango) | 102 a 118 | 17 |
| [K. Errores y excepciones](#k-errores-y-excepciones) | 119 a 132 | 14 |
| [L. ¿Qué pasa si...? Casos borde](#l-qué-pasa-si-casos-borde) | 133 a 149 | 17 |
| [M. pandas y visualización](#m-pandas-y-visualización) | 150 a 156 | 7 |
| [N. Complejidad y eficiencia](#n-complejidad-y-eficiencia) | 157 a 164 | 8 |
| [O. Calidad de código, documentación y pruebas](#o-calidad-de-código-documentación-y-pruebas) | 165 a 174 | 10 |
| [P. Limitaciones y mejoras](#p-limitaciones-y-mejoras) | 175 a 182 | 8 |
| [Q. Preguntas trampa y de precisión](#q-preguntas-trampa-y-de-precisión) | 183 a 200 | 18 |
| [R. Teoría de la cátedra aplicada](#r-teoría-de-la-cátedra-aplicada) | 201 a 211 | 11 |
| [S. Demostración en vivo con un CSV nuevo](#s-demostración-en-vivo-con-un-csv-nuevo) | 212 a 220 | 9 |
| [Demostración en vivo: recetas](#demostración-en-vivo-recetas) | — | 11 recetas |
| [Checklist: 10 cosas a revisar en un CSV antes de leerlo](#checklist-10-cosas-a-revisar-en-un-csv-antes-de-leerlo) | — | 10 |
| [Machete de una página](#machete-de-una-página) | — | 20 datos |

**Total: 220 preguntas.**

---

## A. Generales y organización del código

**1. ¿Qué hace su programa, en una frase?** [básica]

**Respuesta sugerida:** Lee un archivo de texto plano con una tabla (CSV o con otro separador) y devuelve una lista de diccionarios: un diccionario por fila, con los nombres de columna como claves y los valores ya convertidos a `int`, `float`, `bool`, `str` o `None`. El usuario configura cómo leer (tipos forzados, filtros, límite, rango, columnas) y después llama a `leer(ruta)`. Todo el análisis del texto lo hicimos nosotros con `str.split`, sin el módulo `csv` ni pandas.

**2. ¿Cómo está organizado el código?** [básica]

**Respuesta sugerida:** En tres archivos. `modulo/funciones.py` tiene 8 funciones puras y chicas: separar una línea, detectar y convertir tipos, evaluar filtros y recortar columnas. `modulo/clase.py` tiene la clase `LectorCSV`, que guarda la configuración y coordina el proceso en `leer()`. `ejemplos.py` es el script de demostración: es el único que imprime y el único que usa pandas.

**3. ¿Cuál es el recorrido de una lectura, de punta a punta?** [media]

**Respuesta sugerida:** `leer()` (clase.py:65-82) llama a cuatro métodos protegidos en orden: `_leer_archivo` abre el archivo y junta las líneas; `_procesar_lineas` separa encabezado y filas y valida la estructura; `_convertir_tipos` decide el tipo de cada columna y arma los diccionarios; `_aplicar_filtros_y_rangos` aplica rango, filtros, límite y columnas. Cada etapa recibe lo que devolvió la anterior: líneas → lista de listas de `str` → lista de diccionarios tipados → resultado final.

**4. ¿Cómo se usa el lector desde otro programa?** [básica]

**Respuesta sugerida:** Se importa la clase, se crea un lector, se configura y se lee:

```python
from modulo.clase import LectorCSV
lector = LectorCSV(delimitador=";")
lector.forzar_tipo("codigo", str)
datos = lector.leer("archivo.csv")
```

El programa tiene que estar en la carpeta del proyecto (o tenerla en `sys.path`) para que funcione `from modulo...`.

**5. ¿Qué tiene cada archivo de datos que entregaron?** [básica]

**Respuesta sugerida:** `datos1.csv` son productos separados por coma, con un espacio después de cada coma, 6 filas, y la Regla tiene la cantidad vacía para mostrar el `None`. `datos2.txt` son envíos separados por punto y coma, 3 filas. `derror.csv` tiene `veinte` en la columna `cantidad` (línea 3 del archivo), para mostrar el error de conversión cuando se fuerza `int`.

**6. ¿Qué muestra cada ejemplo de `ejemplos.py`?** [básica]

**Respuesta sugerida:** El 1 (L5-16) lee `datos1.csv` con inferencia y `forzar_tipo("codigo", str)`, para conservar `'001'`. El 2 (L20-31) combina rango (1, 5), un filtro, límite 2 y selección de columnas. El 3 (L33-42) lee `datos2.txt` con `;`. El 4 (L44-52) fuerza `int` en `cantidad` sobre `derror.csv` y captura el `ValueError`. En los tres primeros se muestran la lista y el DataFrame; en el 4, el mensaje de error.

**7. ¿`modulo` es un módulo o un paquete? ¿Por qué no tiene `__init__.py`?** [media]

**Respuesta sugerida:** Con la terminología de la cátedra es un paquete: una carpeta con varios módulos (`funciones.py` y `clase.py`). No tiene `__init__.py` y se importa igual porque, desde Python 3.3, una carpeta sin ese archivo funciona como *namespace package* (verificamos que `modulo.__path__` existe). Reconocemos que llamar `modulo` a una carpeta confunde y que un `__init__.py` vacío sería más prolijo.

**8. ¿Por qué `clase.py` importa cinco funciones y no las ocho? ¿Por qué no `import *`?** [media]

**Respuesta sugerida:** Importa solo lo que usa (clase.py:11-17): `separar_linea`, `inferir_tipo_columna`, `convertir_valor`, `cumple_todos_los_filtros` y `recortar_diccionario`. `es_booleano`, `es_entero` y `es_flotante` las llama `inferir_tipo_columna` dentro de `funciones.py`, así que la clase no las necesita. No usamos `import *` porque la cátedra lo desaconseja: no se sabe qué nombres entran ni con cuáles chocan.

**9. ¿Desde dónde hay que ejecutar `ejemplos.py`? ¿Qué pasa si lo corro desde otra carpeta?** [media]

**Respuesta sugerida:** Desde la carpeta del proyecto: `cd` a `G24_Berruti_Liali_Vranjes` y `python ejemplos.py`. Desde otra carpeta el import funciona (Python agrega la carpeta del script a `sys.path`), pero falla la lectura con `FileNotFoundError: No se encontró el archivo en la ruta: datos1.csv`, porque las rutas de los datos son relativas al directorio de trabajo (verificado). La mejora es armar la ruta con `Path(__file__).parent / "datos1.csv"`.

**10. ¿Se puede ejecutar `python modulo/clase.py`?** [media]

**Respuesta sugerida:** No: da `ModuleNotFoundError: No module named 'modulo'` (verificado), porque así Python busca módulos en la carpeta `modulo/` y el import `from modulo.funciones` necesita la raíz del proyecto. Igual no tendría sentido: `clase.py` solo tiene definiciones, es un módulo y no un script. Desde la raíz, `python -m modulo.clase` no da error, pero tampoco hace nada.

---

## B. Decisiones de diseño y alternativas

**11. ¿Por qué combinaron POO y programación funcional?** [media]

**Respuesta sugerida:** Usamos un criterio: ¿esto necesita recordar algo entre llamadas? La configuración sí (se arma en varios pasos y se usa al leer), por eso vive en un objeto. Separar, inferir, convertir, filtrar y recortar no: con la misma entrada dan la misma salida, así que son funciones puras en `funciones.py`. Así cada función se prueba sola (`inferir_tipo_columna(["10", "20", "30.5"])` da `float`) y la clase solo coordina (01 §D1).

**12. ¿Por qué una clase con métodos de configuración y no una función `leer_tabla(ruta, ...)` con muchos parámetros?** [media]

**Respuesta sugerida:** Porque hay opciones que se acumulan (varios tipos forzados, varios filtros), cada opción se valida apenas se configura (`establecer_limite(-1)` falla en esa misma línea) y el mismo lector sirve para varios archivos con la misma estructura. La función tiene la ventaja de no tener estado, y la reconocemos. Igual, una `leer_tabla` se escribe encima de la clase en una docena de líneas (01 §D3), así que elegir la clase no cierra esa puerta.

**13. ¿Por qué no un diccionario de opciones, tipo `LectorCSV({"limite": 2, ...})`?** [media]

**Respuesta sugerida:** Porque una clave mal escrita (`"limte"`) pasaría sin aviso, salvo que validáramos a mano el conjunto de claves, y `help()` no mostraría qué opciones existen. Con métodos, un nombre mal escrito da `AttributeError` enseguida y cada método valida lo suyo.

**14. ¿Por qué el objeto guarda solo configuración y no los datos leídos?** [media]

**Respuesta sugerida:** Para que el lector sea reutilizable y `leer()` sea repetible: los datos pasan de una etapa a la otra como valores de retorno (clase.py:71-82) y nunca se guardan en `self`. Lo verificamos: `vars(lector)` es igual antes y después de leer. Así no quedan datos viejos de una lectura anterior ni se retiene en memoria una tabla que ya se devolvió.

**15. ¿Por qué la ruta se pasa en `leer()` y no en el constructor?** [básica]

**Respuesta sugerida:** Porque el objeto describe *cómo* leer, no *qué* leer. Con la ruta en el constructor, la configuración quedaría atada a un archivo y para leer otro (por ejemplo, un CSV por mes) habría que crear otro objeto. En el constructor van solo las dos cosas que describen el formato: `delimitador` y `encabezado`.

**16. ¿Por qué `leer()` está partido en cuatro métodos protegidos?** [media]

**Respuesta sugerida:** Cada etapa tiene una sola responsabilidad y su propio tipo de error: archivo, estructura, tipos y selección. `leer()` queda como un índice del proceso en cinco renglones, una fachada. Siguen siendo métodos, y no funciones de `funciones.py`, porque necesitan la configuración (`self.delimitador`, `self._tipos_columnas`, `self._filtros`…); como funciones sueltas tendrían firmas larguísimas.

**17. ¿Por qué el pipeline va en ese orden: leer, separar, convertir, filtrar?** [media]

**Respuesta sugerida:** Lo imponen las dependencias de los datos. No se puede inferir el tipo sin columnas alineadas, por eso primero se valida la cantidad de campos. Y no se puede filtrar sin tipos: sobre texto, `'10' < '8'` da `True` porque compara alfabéticamente, y `'10' < 15` da `TypeError`. Por eso los filtros reciben valores ya convertidos.

**18. ¿Por qué usaron `str.split` + `strip` y no expresiones regulares?** [media]

**Respuesta sugerida:** La consigna permite regex pero no las exige, y `split` alcanza: acepta delimitadores de varios caracteres sin escapar nada (`" | "` y `"||"` funcionan), mientras que con `re.split` caracteres como `|`, `.` o `+` son especiales y habría que usar `re.escape`. `strip()` por campo limpia los bordes y respeta los espacios internos (`Buenos Aires`). Ni `split` ni una regex simple resuelven las comillas, que la consigna no exige.

**19. ¿Por qué el resultado intermedio es una lista de listas y el final una lista de diccionarios?** [media]

**Respuesta sugerida:** El final es lista de diccionarios porque lo pide la consigna y porque cada diccionario es un registro al que se accede por nombre (`fila["cantidad"]`), en el orden de la lista. El intermedio (`filas_crudas`) es lista de listas porque todavía no se pueden convertir los valores: el tipo depende de toda la columna, y con listas la columna se arma por posición (`fila[col_i]`, clase.py:162-163). Recién cuando se conoce el tipo se arman los diccionarios (clase.py:167-186).

**20. ¿Por qué representan los tipos con las clases `int`, `float`, `str`, `bool` y no con textos como `"int"`?** [media]

**Respuesta sugerida:** Porque en Python los tipos son clases y las clases son objetos: pueden ser argumentos y valores de un diccionario (`{"codigo": str}`). Así los tipos inferidos y los forzados se guardan igual en `tipos_definidos` (clase.py:152-164), sin traducir nada. Si alguien pasa el texto `"int"`, `forzar_tipo` lo rechaza con `Tipo no válido. Use int, float, str o bool.` (verificado).

**21. ¿Por qué leen todo el archivo en memoria y no usan generadores?** [difícil]

**Respuesta sugerida:** Porque la inferencia necesita ver toda la columna antes de convertir, y un generador es de un solo uso: habría que leer el archivo dos veces (una para inferir y otra para convertir) o materializarlo igual. Además, las listas permiten el slicing del rango y la numeración exacta de los errores. El costo es memoria O(L·K) y que el límite no ahorra lectura; para los tamaños del TP es irrelevante (01 §D7).

---

## C. Programación orientada a objetos

**22. ¿`LectorCSV` es una clase o un objeto? ¿Cuántos objetos crean en `ejemplos.py`?** [básica]

**Respuesta sugerida:** `LectorCSV` es la clase, el molde (clase.py:20). Cada `LectorCSV(...)` crea un objeto, una instancia con sus propios atributos. En `ejemplos.py` hay cuatro: `lector1`, `lector2`, `lector3` y `lector_error`, y la configuración de uno no afecta a los otros porque son atributos de instancia.

**23. ¿Qué hace `__init__`? ¿Crea el objeto?** [básica]

**Respuesta sugerida:** Es el método de inicialización: no crea la instancia (eso lo hace Python antes) ni devuelve nada; deja el objeto en un estado inicial válido. Valida que el delimitador no sea vacío (clase.py:27-28) y asigna los 7 atributos (clase.py:30-36). Tiene valores por defecto (`","` y `True`), por eso `LectorCSV()` funciona sin argumentos.

**24. ¿Por qué hay un `raise` dentro de `__init__`?** [media]

**Respuesta sugerida:** Para que no pueda existir un lector inválido. `LectorCSV(delimitador="")` lanza `ValueError: El delimitador no puede ser vacío.` y la asignación a la variable nunca se completa, así que nadie se queda con ese objeto. Si no lo validáramos ahí, el error aparecería recién al leer y con el mensaje técnico de `str.split` (`empty separator`).

**25. ¿Qué es `self`?** [básica]

**Respuesta sugerida:** Es la instancia sobre la que se llama el método; Python lo pasa automáticamente. `lector1.leer("datos1.csv")` es lo mismo que `LectorCSV.leer(lector1, "datos1.csv")` (verificado: dan el mismo resultado). Gracias a `self`, `leer()` llama a `self._leer_archivo(...)` y los métodos leen la configuración (`self.delimitador`, `self._filtros`). Las funciones de `funciones.py` no tienen `self` porque no usan estado.

**26. ¿Qué atributos tiene un lector y qué guarda cada uno?** [básica]

**Respuesta sugerida:** Siete (clase.py:30-36): `delimitador` (str), `encabezado` (bool), `_tipos_columnas` (diccionario columna → tipo), `_filtros` (lista de funciones), `_limite_filas` (int o `None`), `_rango_filas` (tupla `(inicio, fin)` o `None`) y `_columnas` (lista o `None`). Todos son de configuración; ninguno guarda datos leídos.

**27. ¿Por qué inicializan `_limite_filas`, `_rango_filas` y `_columnas` en `None` dentro de `__init__`?** [media]

**Respuesta sugerida:** Para que todas las instancias tengan siempre los mismos atributos aunque el usuario no llame al setter, y no haya `AttributeError` al leer. `None` significa "no configurado" y se pregunta con `is not None` (clase.py:192, 198, 207, 214). Ojo que no es lo mismo que 0: sin límite se devuelven todas las filas, pero `establecer_limite(0)` devuelve `[]`.

**28. ¿Qué significa el guion bajo en `_filtros`? ¿Es privado?** [media]

**Respuesta sugerida:** Con la terminología de la cátedra es un atributo **protegido**: el guion bajo es una convención que dice "no tocar desde afuera", pero Python no lo impide. Lo que emula privacidad es el doble guion bajo, que hace *name mangling* (`_LectorCSV__algo`), y aun así se puede acceder. Por eso la configuración se cambia con métodos que validan.

**29. ¿Qué pasa si alguien toca un atributo protegido desde afuera?** [difícil]

**Respuesta sugerida:** Python lo permite y se saltean las validaciones. Lo probamos: `lector._limite_filas = -5` hace que `leer()` devuelva `[]` sin error, y `lector._rango_filas = (0, 2)` también da `[]` (el slice queda `filas[-1:2]`). Son errores lógicos silenciosos, justo lo que `establecer_limite` y `establecer_rango` previenen.

**30. ¿Por qué `delimitador` y `encabezado` son públicos y el resto protegido? ¿Es consistente?** [difícil]

**Respuesta sugerida:** Son los parámetros del constructor, valores simples que describen el formato y que tiene sentido consultar. Lo demás tiene estructura interna y solo se cambia con setters. Reconocemos la inconsistencia: `lector.delimitador = ""` saltea la validación de clase.py:27-28 y `leer()` falla con `ValueError: empty separator`, el mensaje de `str.split` (verificado). La solución de la cátedra es una `@property` con un setter que valide, usada también desde `__init__` (código en 01 §D5).

**31. ¿Sus métodos `establecer_*` son setters? ¿Dónde están los getters?** [media]

**Respuesta sugerida:** Sí, funcionan como los setters de la cátedra: validan y después asignan el atributo protegido (clase.py:38-63). La diferencia es que lanzamos `ValueError` en vez de imprimir un aviso, siguiendo la unidad de Excepciones. No hay getters: para consultar la configuración hay que leer atributos con guion bajo. Con `@property` tendríamos sintaxis de atributo con validación y getter incluido; elegimos verbos porque se leen claro y `establecer_rango` recibe dos valores.

**32. ¿Cómo aparece el encapsulamiento en su TP?** [media]

**Respuesta sugerida:** Es el principio que más usamos. El usuario ve una interfaz chica (constructor, cinco métodos de configuración y `leer`) y no necesita conocer el interior: los cuatro métodos protegidos del pipeline y los atributos protegidos. Al marcar el interior con `_`, `help(LectorCSV)` no lo muestra (verificado), y podemos cambiar cómo se separan o convierten las filas sin tocar `ejemplos.py`. También encapsulamos en funciones: cada una de `funciones.py` hace una sola tarea.

**33. ¿Usaron herencia? ¿Por qué no?** [media]

**Respuesta sugerida:** No hay herencia explícita: `LectorCSV` hereda implícitamente de `object` (`LectorCSV.__mro__` es `(LectorCSV, object)`, verificado). Hay un solo tipo de lector y las variantes (coma, punto y coma, tab, separador de varios caracteres, con o sin encabezado) son datos, no comportamientos distintos, así que alcanza con parámetros. Donde sí tendría sentido es en una excepción propia: `class LectorCSVError(ValueError)`.

**34. ¿Por qué no hicieron subclases como `LectorTSV` o `LectorPuntoYComa`?** [media]

**Respuesta sugerida:** Porque solo cambiarían un valor por defecto, sin cambiar comportamiento: `LectorCSV(delimitador="\t")` hace lo mismo con menos código. Si quisiéramos atajos preconfigurados, la cátedra muestra `@classmethod` (como `Sandwich.jyq()`): un `LectorCSV.tsv()` que devuelva `cls(delimitador="\t")`, sin jerarquía. Una clase abstracta `Lector(ABC)` tendría sentido solo con varios formatos de lógica distinta.

**35. ¿Hay polimorfismo en su código?** [difícil]

**Respuesta sugerida:** No con clases propias, pero sí el que trae Python. El operador `in` se usa sobre una lista (clase.py:115, 148, 194) y sobre un diccionario (clase.py:158), con implementaciones distintas. Y en los filtros: el lector les manda a todos el mismo mensaje, llamarlos con la fila (funciones.py:123), y cada uno responde a su manera; sirve una `lambda`, un `def`, un `functools.partial` o un objeto con `__call__` (probamos los cuatro). Eso es *duck typing*.

**36. ¿Qué se ve si hacen `print(lector)`?** [básica]

**Respuesta sugerida:** La representación por defecto, `<modulo.clase.LectorCSV object at 0x...>`, porque no definimos `__repr__` ni `__str__` (verificado). Un `__repr__` que muestre la configuración (delimitador, encabezado, tipos forzados, límite…) ayudaría a depurar. Según la cátedra, `__repr__` es la representación para desarrolladores y `__str__` la legible para usuarios.

**37. ¿Se pueden encadenar los métodos, como `lector.forzar_tipo(...).establecer_limite(2)`?** [media]

**Respuesta sugerida:** No: los métodos de configuración no tienen `return`, devuelven `None`, y la segunda llamada se hace sobre `None`: `AttributeError: 'NoneType' object has no attribute 'establecer_limite'` (verificado). Para el encadenamiento de métodos que muestra la cátedra, cada método tendría que terminar con `return self`.

---

## D. Programación funcional

**38. ¿Qué es una función pura y cuáles de las suyas lo son?** [básica]

**Respuesta sugerida:** Es una función cuya salida depende solo de sus argumentos y que no tiene efectos secundarios: no modifica nada de afuera, no imprime, no lee archivos. Las 8 de `funciones.py` lo son; `cumple_todos_los_filtros` lo es siempre que los filtros que recibe sean puros. Por eso se pueden probar solas: `es_entero("001")` da `True`.

**39. `separar_linea` hace `append` sobre una lista. ¿No es un efecto secundario?** [media]

**Respuesta sugerida:** No. Un efecto secundario es un cambio observable fuera del ámbito de la función. `campos_limpios` se crea adentro (funciones.py:4) y se devuelve; la entrada es un `str`, que es inmutable, y no se toca. Desde afuera la función solo transforma datos; equivale a `[e.strip() for e in linea.split(delimitador)]`.

**40. ¿`leer()` es una función pura?** [media]

**Respuesta sugerida:** No. Su resultado depende del contenido del archivo y de la configuración guardada en `self`, no solo de la ruta, y leer un archivo es interactuar con algo externo. Lo que sí cumple es que no modifica el objeto: dos lecturas dan lo mismo y `vars(lector)` no cambia (verificado). Los métodos de configuración sí modifican `self`, a propósito.

**41. ¿Dónde usan funciones como objetos de primera clase?** [media]

**Respuesta sugerida:** En tres lugares. `self._filtros` es una lista de funciones (clase.py:33 y 47) que `cumple_todos_los_filtros` recorre y llama (funciones.py:122-123). Los tipos `int`, `float`, `str` y `bool` se guardan como valores de diccionarios (clase.py:43 y 152-164) e `inferir_tipo_columna` devuelve uno. Y en `ejemplos.py:23` se pasa una `lambda` como argumento.

**42. ¿`cumple_todos_los_filtros` es una función de orden superior?** [básica]

**Respuesta sugerida:** Sí: recibe funciones como argumento (la lista de filtros) y las invoca (funciones.py:120-125). Es la variedad de orden superior que acepta funciones; no devuelve funciones.

**43. ¿Qué es la `lambda` del ejemplo 2 y por qué usaron una?** [básica]

**Respuesta sugerida:** `lambda fila: fila["cantidad"] is not None and fila["cantidad"] < 15` (ejemplos.py:23) es una función anónima de una sola expresión: recibe una fila (un diccionario) y devuelve un booleano. Se usa porque la condición es corta y aparece una sola vez. Para algo más largo o reutilizable conviene un `def` con nombre.

**44. ¿Qué es el cortocircuito y dónde lo usan?** [media]

**Respuesta sugerida:** En `A and B`, si `A` es falso Python no evalúa `B` (evaluación no estricta). En el filtro del ejemplo 2, si la cantidad es `None` no se evalúa `None < 15`, que daría `TypeError`. El lector lo usa en clase.py:207, `self._limite_filas is not None and len(filas_filtradas) >= self._limite_filas`: con el orden invertido y sin límite saldría `TypeError: '>=' not supported between instances of 'int' and 'NoneType'` (verificado). También `cumple_todos_los_filtros` corta en el primer filtro que da falso (funciones.py:123-124).

**45. Reescriban `cumple_todos_los_filtros` con `all`. ¿Es exactamente equivalente?** [difícil]

**Respuesta sugerida:** `return all(f(fila_diccionario) for f in lista_funciones_filtro)`. Es equivalente incluso en el cortocircuito, porque la expresión generadora es perezosa: si el primer filtro da falso, el segundo no se llama (verificado). Con una lista por comprensión, `all([f(fila) for f in ...])`, se evalúan todos antes de decidir (verificado). Con la lista vacía las dos dan `True`, igual que nuestro `for`.

**46. ¿Por qué no usaron `map`, `filter` ni comprensiones?** [media]

**Respuesta sugerida:** Elegimos `for` explícitos por claridad y porque filtro y límite se combinan con un `break` en el mismo bucle (clase.py:206-211). Reconocemos que la cátedra presenta las comprensiones como la alternativa preferida: `separar_linea` sería `[e.strip() for e in linea.split(delimitador)]` y `recortar_diccionario` sería `{c: fila[c] for c in columnas_elegidas}`. Con `filter` habría que recorrerlo con un `for` y cortar al llegar al límite, porque `list(filter(...))[:n]` evalúa todas las filas.

**47. ¿Su lector usa evaluación perezosa o generadores?** [difícil]

**Respuesta sugerida:** No como estrategia. El archivo se recorre con un iterador (`for linea in archivo`), pero se materializa enseguida en la lista `lineas` (clase.py:88-90) y cada etapa produce listas completas: evaluación inmediata. La razón es la inferencia, que necesita la columna entera, y un generador se agota después de una pasada. Lo único "perezoso" es el corte por límite, que evita evaluar filtros de más.

**48. ¿Cómo armarían un filtro reutilizable "columna menor que X"?** [difícil]

**Respuesta sugerida:** Con una fábrica de funciones, un *closure*:

```python
def menor_que(col, umbral):
    def filtro(fila):
        return fila[col] is not None and fila[col] < umbral
    return filtro

lector.agregar_filtro(menor_que("cantidad", 15))
```

Sobre `datos1.csv` da Cuaderno, Carpeta y Mochila (verificado). `filtro` recuerda `col` y `umbral` aunque `menor_que` ya terminó; también se puede hacer con `functools.partial`.

**49. ¿Usaron recursión? ¿Convendría?** [media]

**Respuesta sugerida:** No, todo es iterativo. Recorrer filas no es un problema recursivo, y cada llamada recursiva apila un contexto: Python corta cerca de los 1000 niveles (`sys.getrecursionlimit()` da 1000), así que un archivo de miles de líneas procesado recursivamente daría `RecursionError`. La cátedra señala que el equivalente iterativo suele ser más eficiente y no desborda la pila.

**50. ¿Usaron decoradores? ¿Para qué servirían acá?** [media]

**Respuesta sugerida:** No. Un decorador como el `timer` de la cátedra podría envolver `leer()` para medir tiempos, por ejemplo para mostrar que el límite no acelera la lectura. La función envoltorio tiene que recibir `*args` y `**kwargs` y devolver lo que devuelve la original.

---

## E. Lectura del archivo y separación de campos

**51. ¿Por qué `with open(...)`? ¿Dónde cierran el archivo?** [básica]

**Respuesta sugerida:** `with` es un *context manager*: cierra el archivo al salir del bloque aunque ocurra un error en el medio, por eso no hay `close()` ni hace falta `finally`. El archivo está abierto solo mientras se juntan las líneas (clase.py:87-90); separar, inferir, convertir y filtrar se hace con el archivo ya cerrado.

**52. ¿Por qué ponen `encoding="utf-8"`? ¿Qué pasa si no lo ponen?** [media]

**Respuesta sugerida:** Porque la cátedra recomienda indicarlo siempre: en Windows el encoding por defecto es cp1252 (lo comprobamos: `locale.getpreferredencoding(False)` da `'cp1252'`). Un CSV UTF-8 con `Córdoba` leído sin `encoding` da `CÃ³rdoba` sin ningún error, o sea datos corruptos en silencio (verificado). Con `utf-8` explícito el resultado es el mismo en cualquier sistema.

**53. ¿Por qué `rstrip("\n\r")` y no `strip()`?** [difícil]

**Respuesta sugerida:** `strip()` sin argumentos borra todo el blanco de los bordes, tabs incluidos. Con delimitador tab y el último campo vacío se perdería una columna: `"1\t2\t\n".strip().split("\t")` da `['1', '2']`, mientras que con `rstrip("\n\r")` da `['1', '2', '']`, que es lo correcto (verificado). Los espacios de cada campo se sacan después, campo por campo, en `separar_linea` (funciones.py:6).

**54. Si el modo texto ya convierte `\r\n` en `\n`, ¿para qué sacan también `\r`?** [media]

**Respuesta sugerida:** Por robustez, y no cuesta nada. Es cierto que `datos1.csv` tiene finales CRLF y Python ya entrega `\n` en modo texto. Pero si quedara un `\r` suelto, por ejemplo si se abriera con `newline=""`, quedaría pegado al último campo. Además, un archivo con finales solo `\r` (Mac viejo) también se lee bien (verificado), gracias a los *universal newlines* de `open`.

**55. ¿Por qué recorren el archivo con `for` y no con `read()` o `readlines()`?** [básica]

**Respuesta sugerida:** `readlines()` daría lo mismo: una línea por elemento con el `\n` al final, que igual hay que sacar. Con el `for` se recorre y se limpia en una sola pasada (clase.py:89-90). `read()` devuelve todo en un único string que después habría que cortar.

**56. ¿Qué hace `separar_linea`?** [básica]

**Respuesta sugerida:** Corta el renglón con `linea.split(delimitador)` (funciones.py:3) y le aplica `strip()` a cada pedazo (funciones.py:5-6); devuelve una lista de strings limpios. Por ejemplo, `"001, Cuaderno, 2500.5"` con `","` da `['001', 'Cuaderno', '2500.5']`.

**57. ¿Por qué hacen `strip()` en cada campo?** [media]

**Respuesta sugerida:** Porque `datos1.csv` tiene un espacio después de cada coma (`codigo, nombre, precio`). Sin `strip`, las claves serían `' nombre'` y `' true'` no se reconocería como booleano. `strip()` solo limpia los bordes, así que `Buenos Aires` conserva su espacio interno; además saca tabs y espacios no separables (NBSP) de los bordes (verificado).

**58. ¿Soportan delimitadores de más de un carácter?** [básica]

**Respuesta sugerida:** Sí, porque `str.split` acepta separadores de cualquier largo: `" | "` y `"||"` funcionan sin escapar nada (verificado). Es la extensión opcional que menciona la consigna. El único valor que se rechaza es el vacío (`LectorCSV(delimitador="")`, clase.py:27-28).

**59. ¿Y si el separador es el espacio?** [difícil]

**Respuesta sugerida:** Funciona solo con archivos muy prolijos. `split(" ")` corta en cada espacio, así que `Buenos Aires` se parte en dos, y dos espacios seguidos o un espacio invisible al final de la línea generan campos de más: `Error en fila 2: Cantidad incorrecta de elementos. Se esperaban 2 columnas, pero se encontraron 3.` (verificado). Con la coma, en cambio, un espacio final se tolera porque el `strip` lo limpia.

**60. ¿Qué pasa con un archivo exportado de Excel como "CSV UTF-8"?** [difícil]

**Respuesta sugerida:** Excel suele agregar un BOM, un carácter invisible (U+FEFF) al principio del archivo. Con `encoding="utf-8"` queda pegado a la primera clave: al imprimir una fila se ve `{'\ufeffid': 1, ...}`, porque el `repr` de las claves muestra el carácter escapado, y `seleccionar_columnas(["id"])` o `forzar_tipo("id", ...)` dicen que la columna no existe (verificado). `strip()` no lo saca porque Python no lo considera un espacio. Se arregla con una palabra: `encoding="utf-8-sig"` en clase.py:87.

**61. ¿Puedo pasarle a `leer()` un `Path` en vez de un string?** [básica]

**Respuesta sugerida:** Sí, porque `open()` acepta objetos `Path`: `LectorCSV(delimitador=";").leer(Path(carpeta) / "datos2.txt")` funciona (verificado). La cátedra recomienda `pathlib` para armar rutas que anden en cualquier sistema operativo; en `ejemplos.py` no lo usamos, y por eso dependemos de la carpeta de trabajo.

**62. ¿Por qué no soportan comillas?** [media]

**Respuesta sugerida:** Porque cortamos cada línea con `split`, sin un estado de "estoy dentro de comillas". Entonces `"Rosario, SF",2` da error de cantidad de campos, y si las comillas no encierran un delimitador se conservan en el valor y hasta en las claves (`fila['"precio"']`). Soportarlas exige recorrer carácter por carácter; es la mejora más cara y la consigna no la pide.

---

## F. Encabezados

**63. ¿Qué hacen con la primera fila?** [básica]

**Respuesta sugerida:** Por defecto (`encabezado=True`) la usan como nombres de columna, ya sin espacios en los bordes (clase.py:105-117). Cada nombre se valida: no puede estar vacío ni repetirse. Los datos empiezan en la segunda línea (`indice_inicio_datos = 1`, clase.py:118).

**64. ¿Qué pasa si un nombre de columna está vacío?** [básica]

**Respuesta sugerida:** Se detiene con `ValueError`: con `a,,c` el mensaje es `Error en fila 1, columna 2: El nombre de la columna está vacío.` (clase.py:113-114). Una coma final (`a,b,`) da "columna 3", y un nombre de solo espacios también cuenta como vacío por el `strip` (verificado). No lo renombramos porque una clave `""` sería inaccesible en la práctica y casi siempre indica un error en el archivo.

**65. ¿Y si hay nombres repetidos? ¿Por qué no los renombran?** [media]

**Respuesta sugerida:** Sale `Error en fila 1: El nombre de columna 'a' está repetido.` (clase.py:115-116). Cada fila es un diccionario y las claves son únicas: si se permitieran, la segunda columna pisaría a la primera sin aviso (`dict(zip(['a', 'b', 'a'], [1, 2, 3]))` da `{'a': 3, 'b': 2}`, verificado). Renombrar (`a_2`) inventaría nombres que el usuario después tiene que adivinar para filtrar o seleccionar.

**66. ¿`Nombre` y `nombre` son la misma columna?** [trampa]

**Respuesta sugerida:** No: se distinguen mayúsculas, porque para Python son claves de diccionario distintas. Un archivo con encabezado `Nombre,nombre` se lee sin error y da `{'Nombre': 'A', 'nombre': 'B'}` (verificado). Unificarlas obligaría a decidir cuál conservar.

**67. ¿Cómo leen un archivo sin encabezado?** [básica]

**Respuesta sugerida:** Con `LectorCSV(encabezado=False)`: la primera línea pasa a ser una fila de datos y las columnas se llaman `col_0`, `col_1`, … (clase.py:119-122). Para forzar un tipo, filtrar o seleccionar hay que usar esos nombres, por ejemplo `lector.forzar_tipo("col_0", str)`.

**68. ¿Qué pasa si el archivo no tiene encabezado y me olvido de `encabezado=False`?** [trampa]

**Respuesta sugerida:** No da error: la primera fila de datos se usa como nombres y se pierde como dato. Con `Yerba,1500,10` / `Azucar,980,0` / `Cafe,3200,5` sale `{'Yerba': 'Azucar', '1500': 980, '10': 0}` (verificado). Y si la primera fila tiene valores repetidos (`10,10,5`), el error dice que el nombre de columna `'10'` está repetido. No es detectable en general; por eso hay que mirar el archivo antes de leerlo.

**69. ¿Y al revés: un archivo con encabezado leído con `encabezado=False`?** [difícil]

**Respuesta sugerida:** El encabezado se toma como una fila más: la primera fila del resultado es `{'col_0': 'producto', 'col_1': 'precio', 'col_2': 'stock'}`. Y, como la inferencia mira toda la columna, el texto del nombre vuelve `str` a todas las columnas; la segunda fila sale `{'col_0': 'Yerba', 'col_1': '1500.5', 'col_2': '10'}` (verificado). Es un buen ejemplo en vivo de que una sola celda de texto arrastra a toda la columna.

**70. ¿Por qué `col_0` empieza en 0 si el error de nombre vacío cuenta columnas desde 1?** [trampa]

**Respuesta sugerida:** Son dos públicos distintos: el mensaje de error es para una persona que busca el problema en el archivo ("columna 2"), y el nombre generado sigue la convención de índices de Python. Reconocemos que es una inconsistencia menor de convenciones (03 §7.4).

**71. Un CSV generado con `df.to_csv()` de pandas sin `index=False`, ¿lo pueden leer?** [difícil]

**Respuesta sugerida:** Con la configuración por defecto no: el encabezado empieza con coma (`,nombre,precio`) y sale `Error en fila 1, columna 1: El nombre de la columna está vacío.` (verificado). Se puede leer con `encabezado=False`, aunque la fila de nombres queda como datos: la columna de precio sale `str` por el texto `precio`, y la del índice sale `int` con un `None` en la primera fila (verificado). Lo correcto es reexportarlo con `index=False`.

---

## G. Tipos e inferencia

**72. ¿Cómo deciden el tipo de una columna?** [básica]

**Respuesta sugerida:** `inferir_tipo_columna` (funciones.py:36-75) mira los valores no vacíos de la columna y prueba en orden: si todos son booleanos, `bool`; si no, si todos son enteros, `int`; si no, si todos son flotantes, `float`; si no, `str`. Una columna es de un tipo solo si **todos** sus valores lo son ("todo o nada").

**73. ¿Por qué ese orden: bool, int, float, str?** [media]

**Respuesta sugerida:** Va de lo más específico a lo más general. `int` antes que `float` es imprescindible: todo entero se puede leer como flotante, pero no al revés (`int("10.0")` da `ValueError`); si `float` fuera primero, ninguna columna saldría `int`. `str` va al final porque acepta cualquier texto. La posición de `bool` hoy no cambia ningún resultado, porque ningún `true`/`false` es numérico, pero importaría si se aceptaran `1`/`0` como booleanos.

**74. Una columna tiene `10`, `20` y `30.5`. ¿Qué tipo sale?** [básica]

**Respuesta sugerida:** `float`, con valores `10.0`, `20.0` y `30.5` (verificado). Es el único tipo que representa todos los valores sin perder información; es justo el ejemplo de la consigna.

**75. ¿Y si hay números y texto mezclados?** [básica]

**Respuesta sugerida:** La columna queda `str` y todos los valores se guardan como texto, incluidos los números (`'10'`, `'NA'`). No convertimos "lo que se pueda" porque quedaría una columna con dos tipos y los filtros numéricos fallarían a mitad de camino. En la inferencia, una mezcla no es un error: el error lo reservamos para los tipos forzados.

**76. ¿Y si toda la columna está vacía?** [media]

**Respuesta sugerida:** El tipo es `str` y todos sus valores son `None` (funciones.py:44-45). No hay información para decidir y `str` es el tipo que no supone nada; como los valores son `None`, el tipo elegido no cambia ningún valor del resultado.

**77. ¿Para qué sirve el `if len(no_vacios) == 0: return str`? ¿Qué pasaría sin él?** [difícil]

**Respuesta sugerida:** Sin esa guarda, una columna toda vacía saldría `bool`. La bandera `todos_bool` arranca en `True` (funciones.py:48) y el `for` no tiene ningún valor para ponerla en `False`: es como `all([])`, que da `True`, porque un "para todo" sobre un conjunto vacío es verdadero. Con la guarda, el resultado es `str` de forma explícita.

**78. ¿Para qué está el `break` en `inferir_tipo_columna`?** [básica]

**Respuesta sugerida:** Para cortar apenas un valor no cumple (funciones.py:52, 61 y 70): si un valor no es entero, la columna ya no puede ser `int` y no hace falta mirar el resto. Es lo mismo que haría `all(...)` con una expresión generadora; lo escribimos con bandera y `break` por claridad.

**79. ¿Por qué `es_entero` usa `try/except` y no `isdigit()`?** [media]

**Respuesta sugerida:** Porque `int()` es la autoridad sobre qué texto es un entero válido: acepta signos y espacios, y `isdigit()` no (`'-5'.isdigit()` y `'+5'.isdigit()` dan `False`, verificado). La función captura solo `ValueError`, la excepción esperada, y la traduce a `True`/`False`. Devuelve un booleano porque, al inferir, que un valor no sea entero es un resultado normal, no un error.

**80. ¿Qué números reconoce y cuáles no?** [media]

**Respuesta sugerida:** Gracias a `int()` y `float()` reconoce negativos (`-5`), signo más (`+5`), decimales con punto, notación científica (`1e3` → `1000.0`), `inf` y `nan` (verificado). No reconoce coma decimal (`1,5`), porcentajes (`15%`), negativos contables (`(500)`), miles con espacio (`1 500`) ni el signo menos Unicode (`−5`, el que sale de copiar desde Word o un PDF): cualquiera de esos vuelve `str` toda la columna.

**81. ¿Por qué el tipo se infiere con todo el archivo y no solo con las filas del rango?** [difícil]

**Respuesta sugerida:** Para que el tipo no dependa de la consulta: con `establecer_rango(2, 2)` sale solo Lapicera y su precio es `800.0` (`float`), igual que en la lectura completa; si se infiriera solo con ese valor, `"800"` daría `int` (verificado). Además, como la inferencia usa las mismas pruebas que la conversión, con un tipo inferido la conversión nunca falla. Y no se puede inferir "con las filas que pasan el filtro", porque el filtro necesita los valores ya tipados.

**82. ¿Qué tipos salen al leer `datos1.csv` sin forzar nada?** [básica]

**Respuesta sugerida:** `codigo` → `int` (`001` → `1`), `nombre` → `str`, `precio` → `float` (mezcla `800` y `2500.5`), `cantidad` → `int` con un `None` (la Regla) y `disponible` → `bool` (verificado). Por eso el ejemplo 1 fuerza `codigo` a `str`.

**83. ¿Cómo saben en vivo qué tipo se infirió para cada columna?** [media]

**Respuesta sugerida:** Mirando el tipo de los valores:

```python
{col: sorted({type(f[col]).__name__ for f in datos}) for col in datos[0]}
```

Con un archivo que tiene una cantidad vacía da algo como `{'stock': ['NoneType', 'int'], ...}` (verificado). No hay un método que devuelva los tipos: `tipos_definidos` es una variable local de `_convertir_tipos` (clase.py:152).

---

## H. Tipos forzados

**84. ¿Cómo se fuerza el tipo de una columna?** [básica]

**Respuesta sugerida:** Con `lector.forzar_tipo("codigo", str)` antes de leer (clase.py:38-43). Se llama una vez por cada columna que se quiera forzar y queda guardado en el diccionario `_tipos_columnas` (si se repite una columna, gana la última llamada). Solo acepta `int`, `float`, `str` o `bool`; cualquier otra cosa da `ValueError: Tipo no válido. Use int, float, str o bool.`

**85. ¿Qué prioridad tiene el tipo forzado sobre la inferencia?** [básica]

**Respuesta sugerida:** Total: si la columna está en `_tipos_columnas`, `_convertir_tipos` usa ese tipo y ni siquiera infiere (clase.py:158-159). Lo pide la consigna: el tipo indicado por el usuario no se reemplaza por uno inferido.

**86. ¿Qué pasa si un valor no se puede convertir al tipo forzado?** [básica]

**Respuesta sugerida:** La lectura se detiene con un `ValueError` que dice fila, columna, valor y tipo. Con `derror.csv` y `forzar_tipo("cantidad", int)`: `Error en fila 3, columna 'cantidad': el valor 'veinte' no se puede convertir a int.` (funciones.py:103-106). Nunca cambiamos a otro tipo. Sin forzar, esa columna se infiere `str` (`'10'`, `'veinte'`, `'8'`) y no hay error (verificado).

**87. ¿Para qué sirve forzar `str`? Den ejemplos.** [media]

**Respuesta sugerida:** Para columnas que parecen números pero son códigos: `00123` se infiere `123` y forzado queda `'00123'`; un código postal `0341` pasaría a `341`; un teléfono `+543414567890` pierde el `+`; y un código `12E3` se leería como notación científica, `12000.0` (todo verificado). Forzando `str` se conservan tal cual.

**88. Fuerzo `int` sobre la columna `precio` de `datos1.csv`. ¿Qué pasa?** [media]

**Respuesta sugerida:** Error en la primera fila de datos: `Error en fila 2, columna 'precio': el valor '2500.5' no se puede convertir a int.` (verificado). `int()` no acepta texto con punto decimal (`int("10.0")` también falla), y no redondeamos porque sería cambiar el dato sin avisar.

**89. ¿Y si fuerzo `float` sobre una columna de enteros, o `str` sobre una de booleanos?** [media]

**Respuesta sugerida:** Funcionan: `cantidad` forzada a `float` da `10.0, 25.0, 8.0, None, …` y `disponible` forzada a `str` da `'true'`, `'false'` como texto (verificado). Forzar `str` nunca falla, porque cualquier texto es un `str` válido.

**90. ¿Qué acepta `bool` forzado?** [media]

**Respuesta sugerida:** Solo `true` y `false`, sin importar mayúsculas (funciones.py:87-97). `'1'`, `'0'`, `'si'` o `'VERDADERO'` dan error, por ejemplo `Error en fila 2, columna 'activo': el valor 'VERDADERO' no se puede convertir a bool.` (verificado). No hacemos conversiones "creativas".

**91. ¿Cuándo se valida que la columna de `forzar_tipo` exista?** [media]

**Respuesta sugerida:** Recién en `leer()`, al principio de `_convertir_tipos` (clase.py:147-149), porque antes de leer el archivo no se conoce el encabezado: `La columna 'zz' indicada en forzar_tipo no existe en la tabla.` En cambio, el tipo se valida al configurar (clase.py:40-41). Si se llama dos veces sobre la misma columna, gana la última, porque es un diccionario.

**92. ¿Forzar `int` acepta `1e3`, `nan` o `True`?** [difícil]

**Respuesta sugerida:** No: los tres dan error, por ejemplo `el valor '1e3' no se puede convertir a int.`, porque `int()` no los acepta aunque `1e3` sea matemáticamente un entero (verificado). Con `float` forzado, `1e3` da `1000.0` y `nan` se acepta. Es coherente con la regla: se usa exactamente la conversión de Python para el tipo pedido.

---

## I. Nulos y booleanos

**93. ¿Cómo representan los nulos?** [básica]

**Respuesta sugerida:** Una celda vacía, o con solo espacios (el `strip` la deja vacía), se guarda como `None`, para cualquier tipo (funciones.py:81-82). Usamos `None` porque representa la ausencia de valor, mientras que `0` o `""` son valores concretos.

**94. Si fuerzo `str`, ¿la celda vacía queda `""`?** [trampa]

**Respuesta sugerida:** No, queda `None`: el chequeo `if texto == ""` está antes de mirar el tipo (funciones.py:81-82). Así un nulo es siempre `None`, sea cual sea el tipo de la columna.

**95. ¿`NA`, `NULL`, `N/A` o `-` cuentan como nulos?** [media]

**Respuesta sugerida:** No: solo la celda vacía es nulo, y esos textos vuelven `str` a toda la columna (verificado con `NULL`, `None`, `N/A`, `-` y `null`). Lo decidimos así porque pueden ser datos reales (un apodo "None", el código "NA" de Namibia) y una regla única es predecible. El costo es que un CSV exportado de R da columnas `str`; la mejora sería una lista configurable de marcadores de nulo.

**96. ¿Qué booleanos reconocen?** [básica]

**Respuesta sugerida:** Solo `true` y `false`, sin importar mayúsculas y aunque tengan espacios en los bordes: `True`, `TRUE` y ` false ` son booleanos (verificado). Son las formas de Python, de Excel en inglés y de JSON, y no son ambiguas. `yes`/`no`, `si`/`no`, `T`/`F` y `VERDADERO`/`FALSO` quedan como texto.

**97. ¿Por qué no aceptan `1` y `0` como booleanos?** [media]

**Respuesta sugerida:** Porque chocan con los enteros: una columna de cantidades con unos y ceros saldría booleana. Verificado: `["1", "0"]` se infiere `int`. Y `["true", "1"]` queda `str`, porque solo `str` contiene a los dos.

**98. ¿Por qué `convertir_valor` no hace simplemente `bool(texto)`?** [trampa]

**Respuesta sugerida:** Porque `bool("false")` da `True`: todo string no vacío es verdadero (verificado). Por eso `bool` tiene una rama propia que pasa a minúsculas y compara con `"true"` y `"false"` (funciones.py:87-92). `int` y `float` sí se convierten llamando a `int()` y `float()`.

**99. Una columna tiene `true`, `FALSE` y una celda vacía. ¿Qué sale?** [básica]

**Respuesta sugerida:** `bool`, con `True`, `False` y `None` (verificado). Los vacíos no participan de la inferencia.

**100. ¿Qué pasa con `nan` en una columna numérica?** [difícil]

**Respuesta sugerida:** `float("nan")` es válido, así que la columna se infiere `float` y ese valor queda `nan`, **no** `None` (verificado). Hay dos representaciones de "falta el dato": un filtro con `is not None` deja pasar el `nan`, y `nan < 20` da `False` sin error, así que un filtro numérico lo descarta en silencio.

**101. Un filtro `lambda f: not f["activo"]`, ¿qué hace con un `activo` vacío?** [trampa]

**Respuesta sugerida:** Lo incluye: `None` es falso, así que `not None` es `True` (verificado: devuelve la fila con `None` y la de `False`). Si se quieren solo los falsos de verdad hay que escribir `f["activo"] is False`. Al revés, `lambda f: f["activo"]` descarta los `None` en silencio.

---

## J. Filas, columnas, filtros, límite y rango

**102. ¿Cómo se pide una cantidad de filas?** [básica]

**Respuesta sugerida:** Con `lector.establecer_limite(n)` (clase.py:49-53). Un límite negativo da `ValueError: El limite de filas no puede ser negativo`, y `0` devuelve `[]`.

**103. ¿Cómo se pide un rango de filas? ¿Cómo se numeran?** [básica]

**Respuesta sugerida:** Con `lector.establecer_rango(inicio, fin)` (clase.py:55-59). Se cuentan filas de **datos** desde 1 (la 1 es la primera después del encabezado) y los dos extremos están incluidos: `(2, 3)` da Lapicera y Carpeta. `inicio < 1` o `fin < inicio` dan `ValueError: Rango invalido: 'inicio' debe ser >= 1 y 'fin' >= 'inicio'`.

**104. Expliquen la línea `filas_tipadas[inicio - 1 : fin]`.** [media]

**Respuesta sugerida:** El usuario cuenta desde 1 con los dos extremos incluidos; Python indexa desde 0 y el slicing excluye el final. Al inicio se le resta 1 para pasarlo a base 0; al fin no, porque el slice ya lo excluye y queda justo hasta la fila `fin`. Ejemplo: `(2, 3)` → `[1:3]` → filas de datos 2 y 3 (clase.py:200).

**105. ¿Qué pasa si el rango se pasa del final?** [básica]

**Respuesta sugerida:** No hay error, porque el slicing de Python no falla si se pasa del final: `(3, 100)` devuelve desde la fila 3 hasta la última y `(50, 60)` sobre 6 filas devuelve `[]`. Sería un buen caso para un *warning*.

**106. ¿Cómo se seleccionan columnas? ¿En qué orden salen?** [básica]

**Respuesta sugerida:** Con `lector.seleccionar_columnas(["nombre", "precio"])` (clase.py:61-63). Salen en el orden de la lista del usuario, no en el del archivo, porque `recortar_diccionario` arma un diccionario nuevo recorriendo esa lista (funciones.py:128-133). Una columna inexistente da `La columna seleccionada 'zz' no existe en la tabla.`

**107. ¿Cómo se filtran filas? ¿Qué tiene que devolver el filtro?** [básica]

**Respuesta sugerida:** Con `lector.agregar_filtro(funcion)`, donde la función recibe una fila (un diccionario ya tipado) y devuelve un booleano; se conservan las filas para las que da verdadero. Se usa su valor de verdad (`if not funcion(fila_diccionario)`, funciones.py:123), así que cualquier valor "truthy" cuenta como verdadero.

**108. ¿Qué pasa con varios filtros?** [básica]

**Respuesta sugerida:** Se combinan con AND: la fila tiene que cumplir todos (funciones.py:120-125). Sobre `datos1.csv`, el filtro del ejemplo 2 más `precio > 3000` da Carpeta y Mochila (verificado). Para un OR hay que escribirlo dentro de un solo filtro: `lambda f: cond1(f) or cond2(f)`.

**109. ¿En qué orden se aplican rango, filtros, límite y columnas? ¿Dónde está documentado?** [media]

**Respuesta sugerida:** Primero el rango, después los filtros, el límite cuenta filas que cumplen y al final se eligen las columnas (clase.py:198-219). Está documentado en el comentario de criterios, clase.py:7-9. El rango va primero porque habla de posiciones en el archivo; las columnas van al final para que el filtro vea la fila completa.

**110. Si pido 2 filas y un filtro, ¿miran las primeras 2 filas o siguen hasta tener 2 que cumplan?** [media]

**Respuesta sugerida:** Siguen hasta juntar 2 que cumplan, y cortan apenas las tienen (clase.py:206-211). Con el filtro `precio < 1000` y límite 2 se examinan las filas 1 a 4 y se devuelven Lapicera y Regla, no las dos primeras del archivo (verificado). La otra semántica igual se puede pedir: `establecer_rango(1, 2)` más el filtro.

**111. ¿Se puede filtrar por una columna que no se devuelve?** [básica]

**Respuesta sugerida:** Sí, porque la selección de columnas es el último paso y el filtro ve la fila completa. Ejemplo verificado: filtro `fila["disponible"] is False` con `seleccionar_columnas(["nombre"])` da `[{'nombre': 'Regla'}]`. Es la situación del ejemplo de la consigna: nombres y precios de los productos con menos de diez unidades, donde se filtra por la cantidad pero no se la devuelve.

**112. Recorran el ejemplo 2 paso a paso.** [media]

**Respuesta sugerida:** El rango (1, 5) deja Cuaderno, Lapicera, Carpeta, Regla y Mochila. El filtro deja las de cantidad no nula y menor a 15: Cuaderno (10), Carpeta (8) y Mochila (3); la Regla tiene `None` y el `is not None` la descarta sin error. El límite 2 corta en Cuaderno y Carpeta, y la selección deja nombre y precio: `[{'nombre': 'Cuaderno', 'precio': 2500.5}, {'nombre': 'Carpeta', 'precio': 3200.0}]`.

**113. ¿Qué cambiaría si el filtro se aplicara antes que el rango?** [difícil]

**Respuesta sugerida:** Cambiaría el resultado. Con `establecer_rango(1, 3)` y el filtro de cantidad menor a 15, el lector da Cuaderno y Carpeta (de las filas 1 a 3, cumplen dos); si se filtrara primero y después se tomaran "las 3 primeras que cumplen", saldrían Cuaderno, Carpeta y Mochila (verificado). Elegimos el rango primero para que "la fila 3" signifique la tercera del archivo, no la tercera que cumple.

**114. ¿Qué pasa si combino límite 0 con un filtro?** [media]

**Respuesta sugerida:** Devuelve `[]` y el filtro ni se llama, porque el control del límite está antes de evaluar el filtro (clase.py:207-210). Lo verificamos con un filtro que cuenta sus llamadas: cero llamadas.

**115. ¿Pueden quitar un filtro o el límite después de configurarlo?** [media]

**Respuesta sugerida:** No. Los filtros se acumulan y no hay método para quitarlos: un lector con `precio > 500` dio 4 filas y, al agregarle `precio < 3000`, 2 (verificado). `establecer_limite(None)` y `establecer_rango(None, None)` dan `TypeError` porque comparan `None < 0` o `None < 1`. Hoy hay que crear otro lector; la mejora es un `quitar_filtros()` y aceptar `None` en los setters.

**116. ¿Qué pasa si le paso a `seleccionar_columnas` un string en vez de una lista?** [trampa]

**Respuesta sugerida:** Un `str` es una secuencia, así que el `for` lo recorre letra por letra: `seleccionar_columnas("nombre")` da `La columna seleccionada 'n' no existe en la tabla.` (verificado). Una tupla sí funciona. Un generador, en cambio, falla en silencio: la validación de clase.py:193-195 lo agota y después cada fila sale como diccionario vacío, `[{}, {}, ...]` (verificado). No validamos el tipo del argumento; es una limitación.

**117. Si hago `cols = ["nombre"]`, `seleccionar_columnas(cols)` y después `cols.append("precio")`, ¿qué devuelve `leer()`?** [difícil]

**Respuesta sugerida:** Devuelve nombre y precio: clase.py:63 guarda la misma lista, no una copia (`lector._columnas is cols` da `True`, verificado). Es un alias: el estado interno cambia desde afuera sin pasar por ningún método. Se arregla copiando: `self._columnas = list(lista_columnas)`.

**118. ¿Qué pasa con `seleccionar_columnas([])` o con nombres repetidos en la selección?** [media]

**Respuesta sugerida:** Con `[]` cada fila sale como diccionario vacío: `[{}, {}, ...]`. Con `["precio", "precio", "nombre"]` no hay error y `precio` aparece una sola vez, porque la clave se pisa a sí misma (verificado). No validamos duplicados en la selección, a diferencia del encabezado.

---

## K. Errores y excepciones

**119. Ante un problema, ¿el lector sigue o se detiene?** [básica]

**Respuesta sugerida:** Se detiene en el primer problema y lanza una excepción con un mensaje que dice qué pasó y, cuando corresponde, la fila y la columna. La consigna lo permite explícitamente. Preferimos detenernos antes que devolver datos mal leídos sin avisar: si salteáramos una fila con un campo de más, los cálculos del usuario serían incorrectos y nadie se enteraría.

**120. ¿Por qué lanzan excepciones en vez de imprimir un mensaje?** [media]

**Respuesta sugerida:** Porque un `print` solo le avisa a quien mira la pantalla; la excepción le avisa al programa, que decide qué hacer. En `ejemplos.py:48-52` la capturamos con `try/except ValueError` y mostramos el mensaje. En `clase.py` y `funciones.py` no hay ningún `print`.

**121. ¿Por qué `ValueError`? ¿Cuándo correspondería `TypeError`?** [difícil]

**Respuesta sugerida:** `ValueError` es cuando el tipo es adecuado pero el valor no: `'veinte'` es un texto, como todo lo que viene del archivo, pero no representa un entero. `TypeError` es cuando el tipo no admite la operación. Con ese criterio, `establecer_limite("3")` debería dar un `TypeError` nuestro; hoy da el `TypeError` técnico de la comparación, `'<' not supported between instances of 'str' and 'int'` (verificado). La mejora es validar primero con `isinstance` (→ `TypeError`) y después el valor (→ `ValueError`).

**122. ¿Qué errores detectan al configurar y cuáles al leer? ¿Por qué?** [media]

**Respuesta sugerida:** Al configurar, lo que no depende del archivo: delimitador vacío, tipo no soportado, límite negativo y rango inválido. Al leer, lo que depende del archivo: que existan las columnas de `forzar_tipo` (clase.py:147-149) y de `seleccionar_columnas` (clase.py:192-195), porque antes no se conoce el encabezado. La idea es fallar lo antes posible.

**123. ¿Por qué capturan `FileNotFoundError` y lanzan otro `FileNotFoundError`?** [difícil]

**Respuesta sugerida:** Para dar un mensaje propio con la ruta (`No se encontró el archivo en la ruta: ...`, clase.py:91-92) sin cambiar el tipo, así quien llama puede seguir haciendo `except FileNotFoundError`. Tiene costos: la excepción nueva pierde `errno` y `filename` (quedan en `None`, verificado) y el traceback muestra las dos encadenadas. Alternativas: no capturarla, o `raise ... from error`.

**124. Si no capturan el error de `derror.csv`, ¿cómo se lee el traceback?** [difícil]

**Respuesta sugerida:** De abajo hacia arriba. La última línea dice `ValueError: Error en fila 3, columna 'cantidad': el valor 'veinte' no se puede convertir a int.` Subiendo se ve el camino: programa principal → `leer` (clase.py:77) → `_convertir_tipos` (clase.py:182) → `convertir_valor` (funciones.py:103). Más arriba aparece el `ValueError` original de `int('veinte')` (funciones.py:101), unido por "During handling of the above exception, another exception occurred", porque lanzamos el nuestro dentro del `except` (verificado).

**125. ¿Qué cambiaría con `raise ... from error` o con `raise ... from None`?** [difícil]

**Respuesta sugerida:** Con `from error` la relación queda explícita y el traceback dice "The above exception was the direct cause of the following exception". Con `from None` se oculta la original y solo se ve la nuestra. En `convertir_valor`, `from None` sería razonable porque nuestro mensaje ya incluye el valor, pero `from error` es más conservador porque no borra información de diagnóstico. En `ejemplos.py` no se nota, porque solo se imprime el mensaje.

**126. ¿Por qué `except ValueError` y no `except:` o `except Exception`?** [media]

**Respuesta sugerida:** Porque solo hay que capturar lo que se espera y se sabe manejar. Un `except:` sin tipo puede tapar errores de lógica y hasta atrapar un Ctrl+C. Todas nuestras capturas son específicas: `ValueError` en funciones.py:23, 32, 102 y 111; `FileNotFoundError` en clase.py:91; y `ValueError` en ejemplos.py:50.

**127. ¿Qué errores NO captura el lector?** [difícil]

**Respuesta sugerida:** Los que vienen de Python o del código del usuario: un archivo en latin-1 da `UnicodeDecodeError`; una ruta que es una carpeta da `PermissionError` en Windows; un filtro con una columna mal escrita da `KeyError`; un filtro que compara `None < 15` da `TypeError`; y algo que no es función pasado como filtro da `TypeError: 'int' object is not callable` (todo verificado). Ninguno de esos mensajes dice la fila.

**128. El `except ValueError` de `ejemplos.py`, ¿atrapa un archivo mal codificado? ¿Y una ruta mal escrita?** [trampa]

**Respuesta sugerida:** El archivo mal codificado sí, porque `UnicodeDecodeError` es subclase de `ValueError`, aunque muestra el mensaje técnico de Python. La ruta mal escrita no: `FileNotFoundError` no es subclase de `ValueError` (es un `OSError`), así que cortaría el programa (verificado con `issubclass`). En la demo conviene `except (ValueError, FileNotFoundError)`.

**129. ¿Por qué no crearon sus propias excepciones?** [media]

**Respuesta sugerida:** `ValueError` describe bien los casos y la consigna pide sobre todo mensajes claros con fila y columna. Igual sería una mejora: hoy un `except ValueError` también atrapa errores que no son del lector, como un `UnicodeDecodeError` o un `ValueError` dentro de un filtro. Con `class LectorCSVError(ValueError)`, el `except ValueError` de siempre sigue funcionando y además se puede capturar solo lo del lector, guardando fila y columna como atributos.

**130. ¿Pensaron en usar warnings?** [media]

**Respuesta sugerida:** No los usamos. Según la cátedra, un warning corresponde cuando hay un resultado razonable pero conviene avisar. Candidatos claros: un rango fuera de la tabla que devuelve `[]`, una columna toda vacía que queda `str`, un `NA` que vuelve `str` una columna numérica, o un delimitador probablemente equivocado (una sola columna). Para una fila con campos de más no hay resultado razonable, así que ahí va una excepción.

**131. Si la línea 2 tiene un valor no convertible y la línea 3 tiene un campo de más, ¿qué error informa?** [trampa]

**Respuesta sugerida:** El de la línea 3: `Error en fila 3: Cantidad incorrecta de elementos. Se esperaban 2 columnas, pero se encontraron 3.` (verificado). Cada etapa procesa todo el archivo antes de pasar a la siguiente, y la estructura (`_procesar_lineas`) se valida antes que los tipos (`_convertir_tipos`). El primer error informado es el de la etapa más temprana, no necesariamente el de la primera línea con problemas.

**132. ¿Un error de conversión fuera del rango pedido también frena la lectura?** [trampa]

**Respuesta sugerida:** Sí. Con `establecer_rango(1, 1)` sobre `derror.csv` y `cantidad` forzada a `int`, igual sale el error de la fila 3; y lo mismo si `cantidad` no está entre las columnas seleccionadas (verificado). Se convierte todo el archivo antes de aplicar rango y columnas. Los errores dentro de un filtro, en cambio, solo aparecen en las filas que el filtro llega a evaluar.

---

## L. ¿Qué pasa si...? Casos borde

**133. ¿Qué pasa si el archivo está vacío (0 bytes)?** [básica]

**Respuesta sugerida:** `ValueError: El archivo '<ruta>' está vacío.` (clase.py:94-95).

**134. ¿Y si el archivo tiene solo el encabezado?** [básica]

**Respuesta sugerida:** Devuelve `[]`, sin error (verificado): es una tabla válida sin filas.

**135. ¿Y si la primera línea está en blanco?** [básica]

**Respuesta sugerida:** `Error en fila 1: La primera línea del archivo está vacía.` (clase.py:102-103).

**136. ¿Y si hay una línea en blanco en el medio?** [básica]

**Respuesta sugerida:** Se detiene con `Error en fila 3: Se encontró una fila vacía.` (clase.py:130-131), con el número de la línea que corresponda. No la salteamos porque suele indicar un archivo mal armado (dos archivos pegados, un corte), y así el número de línea de los mensajes siempre es exacto.

**137. ¿Y si el archivo termina con uno o con dos saltos de línea?** [media]

**Respuesta sugerida:** Con uno no pasa nada: no aparece una línea extra. Con dos aparece una línea vacía al final y sale el error de fila vacía; por ejemplo, `a,b` / `1,2` más dos saltos da `Error en fila 3: Se encontró una fila vacía.` (verificado). Si un docente trae un archivo así, la salida es borrar esa línea final.

**138. ¿Y si una fila tiene un campo de más o de menos?** [básica]

**Respuesta sugerida:** `Error en fila N: Cantidad incorrecta de elementos. Se esperaban X columnas, pero se encontraron Y.` (clase.py:135-139). No completamos con `None` ni recortamos porque no hay forma de saber qué campo sobra o falta: podríamos correr todos los valores de columna sin aviso.

**139. ¿Y si una fila tiene solo comas, como `,,`?** [difícil]

**Respuesta sugerida:** Es una fila válida de nulos: `{'a': None, 'b': None, 'c': None}` (verificado). Pero la misma fila "sin datos" con tabs (`\t\t`, con delimitador tab) da error de fila vacía, porque el chequeo `linea_actual.strip() == ""` (clase.py:130) se hace antes de separar y `strip()` borra tabs y espacios pero no comas. Además, las filas `,,` que Excel deja al final se devuelven como filas de `None` sin aviso.

**140. ¿Y si el archivo tiene una sola columna y falta un valor?** [difícil]

**Respuesta sugerida:** Es imposible representar ese nulo: en un archivo de una columna, la celda vacía *es* una línea vacía, y da `Error en fila 3: Se encontró una fila vacía.` (verificado). Ahí chocan dos criterios nuestros: "línea vacía = error" y "celda vacía = `None`". Una mejora sería tratar la línea vacía como nulo cuando hay una sola columna.

**141. ¿Y si me equivoco de delimitador?** [trampa]

**Respuesta sugerida:** No da error: un archivo con `;` leído con la coma por defecto devuelve una sola columna con la línea entera, `{'producto;precio;stock': 'Yerba;1500;10'}` (verificado). Si además hay comas adentro (coma decimal), sale `Se esperaban 1 columnas, pero se encontraron 2.`, que no menciona el delimitador. Señal de alarma: si el resultado tiene una sola clave larga, el delimitador está mal.

**142. ¿Y si un campo tiene una coma entre comillas, como `"Rosario, SF"`?** [media]

**Respuesta sugerida:** Error de cantidad de campos, porque `split` también corta esa coma: `Error en fila 2: Cantidad incorrecta de elementos. Se esperaban 2 columnas, pero se encontraron 3.` (verificado). No soportamos comillas.

**143. ¿Y si una celda tiene un salto de línea adentro (Alt+Enter en Excel)?** [difícil]

**Respuesta sugerida:** Trabajamos línea por línea, no registro por registro, así que el registro se parte en dos. Con `1,"hola` / `chau"` en la última columna, la línea 2 tiene justo 2 campos y pasa; recién falla la 3: `Error en fila 3: Cantidad incorrecta de elementos. Se esperaban 2 columnas, pero se encontraron 1.` (verificado). El error se informa en la línea siguiente a donde empieza el problema.

**144. ¿Y si el archivo está en latin-1 o en UTF-16?** [media]

**Respuesta sugerida:** Sale `UnicodeDecodeError` sin mensaje propio, por ejemplo `'utf-8' codec can't decode byte 0xf3 in position 14: invalid continuation byte` (0xf3 es la `ó` en latin-1; verificado). Como es subclase de `ValueError`, el `except` de `ejemplos.py` la atraparía igual. En vivo, la salida es volver a guardar el archivo como UTF-8.

**145. ¿Y si la ruta no existe, o es una carpeta?** [básica]

**Respuesta sugerida:** Ruta inexistente: `FileNotFoundError: No se encontró el archivo en la ruta: <ruta>` (clase.py:91-92). Carpeta: en Windows sale `PermissionError: [Errno 13] Permission denied`, que no capturamos (verificado).

**146. ¿Y si el CSV viene de Excel en castellano (`;`, coma decimal y `VERDADERO`/`FALSO`)?** [difícil]

**Respuesta sugerida:** Con `delimitador=";"` se lee, pero `1500,50` queda `str` y `VERDADERO` también (verificado). Un filtro `precio < 2000` da `TypeError`, y forzar `float` da `el valor '1500,50' no se puede convertir a float.` Hoy no hay forma de configurarlo: es una limitación reconocida, y la mejora es un parámetro de separador decimal y listas configurables de booleanos (ver 177).

**147. ¿Y si hay números con punto de miles, como `1.000` o `2.500`?** [trampa]

**Respuesta sugerida:** Se leen como decimales: `1.000` → `1.0` y `2.500` → `2.5`, sin ningún aviso, porque para Python el punto es decimal (verificado). Si aparece `2.500.000`, toda la columna queda `str`. En vivo: forzar `str` y no hacer cuentas con esa columna.

**148. ¿Y si hay fechas?** [media]

**Respuesta sugerida:** No hay tipo fecha (la consigna no lo pide): `2024-01-15`, `15/01/2024` y `10:30` quedan `str`, pero un año suelto (`2024`) y una fecha compacta (`20240115`) se infieren `int` (verificado). Si hace falta, se fuerza `str`.

**149. ¿Y si los encabezados vienen entre comillas, como los exporta R?** [difícil]

**Respuesta sugerida:** Las comillas quedan en las claves y en los valores: `{'"nombre"': '"Yerba"', '"precio"': '"1500"', ...}`, así que `fila["precio"]` da `KeyError` y hay que escribir `fila['"precio"']` (verificado). Los números entre comillas quedan `str`.

---

## M. pandas y visualización

**150. ¿Por qué pandas aparece solo en `ejemplos.py`?** [básica]

**Respuesta sugerida:** Porque la consigna no permite usar sus lectores y pide que la conversión a DataFrame se haga fuera del lector. El paquete `modulo` usa solo Python estándar, así que no depende de instalar nada; mostrar los datos es responsabilidad del programa que lo usa (`ejemplos.py:1`, `15`, `31` y `42`).

**151. ¿Por qué en el DataFrame la cantidad aparece como `10.0`, `25.0`, `NaN`?** [trampa]

**Respuesta sugerida:** Porque pandas convierte `None` en `NaN`, que es un float, y su tipo entero (`int64`) no admite `NaN`: pasa toda la columna a `float64` (verificado con `df.dtypes`). Nuestra lista tiene `10` (int) y `None`. Por eso la consigna pide poder mostrar también la lista original.

**152. ¿Por qué muestran la lista y además el DataFrame?** [básica]

**Respuesta sugerida:** Porque pandas cambia la representación: `None` pasa a `NaN` y los enteros a flotantes. Y en otro caso que probamos, el texto `'None'` y el nulo `None` se ven idénticos en el DataFrame; solo `df.isna()` los distingue (verificado). La lista muestra lo que realmente devolvió el lector.

**153. ¿Qué tipos (dtypes) quedan en el DataFrame del ejemplo 1?** [media]

**Respuesta sugerida:** `codigo` y `nombre` → `object` (strings), `precio` → `float64`, `cantidad` → `float64` (por el `NaN`) y `disponible` → `bool` (verificado). Si `disponible` tuviera un `None`, la columna quedaría `object` (también verificado).

**154. ¿Qué índice usa el DataFrame y cómo se relaciona con su rango?** [trampa]

**Respuesta sugerida:** pandas numera desde 0, así que `establecer_rango(1, 5)` corresponde a los índices 0 a 4 del DataFrame completo. Y si el resultado viene filtrado o recortado, el índice vuelve a empezar en 0, porque el DataFrame se arma con la lista que devolvimos.

**155. ¿Qué pasa si el resultado es una lista vacía y la paso a `pd.DataFrame`?** [básica]

**Respuesta sugerida:** Da un DataFrame vacío, sin filas ni columnas (`shape` igual a `(0, 0)`), sin error (verificado). Pasa, por ejemplo, con un rango fuera de la tabla o con un filtro que no deja nada.

**156. ¿Cómo instalan pandas?** [básica]

**Respuesta sugerida:** Es un paquete externo: `python -m pip install pandas`, idealmente en un entorno virtual. Lo importamos con el alias `pd`, que es la convención. Nos faltó un `requirements.txt` con `pandas`.

---

## N. Complejidad y eficiencia

**157. ¿Cuál es la complejidad temporal de `leer()`?** [media]

**Respuesta sugerida:** O(L·K), con L filas y K columnas: cada celda se separa, se revisa en la inferencia (como mucho tres pasadas de prueba por columna, una constante) y se convierte una vez. Se suman O(K²) del control de nombres repetidos y O(R·F) de evaluar F filtros sobre las R filas del rango. En la práctica crece casi lineal con la cantidad de filas.

**158. La inferencia recorre la columna hasta tres veces. ¿No es O(3N)?** [media]

**Respuesta sugerida:** En notación O se descartan las constantes: O(3N) = O(N). Además cada pasada corta con `break` apenas un valor no cumple. El peor caso es una columna de enteros cuyo último valor es texto: la pasada de `bool` corta en el primer valor, pero las de `int` y `float` recorren la columna entera antes de descartarse (unas 2N pruebas).

**159. ¿Cuánto cuesta `nombre in encabezados`?** [difícil]

**Respuesta sugerida:** `in` sobre una lista es búsqueda lineal, O(K). Dentro del `for` de K nombres (clase.py:111-117) suma O(K²): es un bucle anidado escondido. Con un `set` de nombres vistos (tabla hash) quedaría O(K); con cinco columnas no se nota, pero en una medición con 20.000 columnas fue más de un segundo contra milésimas (01 §3.2.11).

**160. ¿El límite hace que se lea menos del archivo?** [trampa]

**Respuesta sugerida:** No. Siempre se lee, separa, infiere y convierte el archivo entero (clase.py:71-77); el límite solo corta el último bucle (clase.py:207-208). Lo medimos con 80.000 filas: sin límite y con `establecer_limite(1)` tardó prácticamente lo mismo, alrededor de un cuarto de segundo en los dos casos.

**161. ¿Cuánta memoria usa?** [media]

**Respuesta sugerida:** O(L·K). Mientras dura `leer()` conviven `lineas`, `filas_crudas` y `filas_tipadas`, unas tres representaciones del archivo, más la copia que hace el slicing del rango. Para archivos chicos no importa; para archivos enormes habría que procesar con generadores en dos pasadas.

**162. ¿Cuánto cuestan `append` y el acceso por índice en una lista?** [media]

**Respuesta sugerida:** La lista de Python es un arreglo dinámico de referencias: el acceso por índice es O(1) y `append` al final es O(1) amortizado (cuando se llena, copia todo a un bloque más grande, pero repartido entre todos los `append` da constante). Insertar o sacar al principio sería O(N). El lector solo usa `append` al final, índices y slicing.

**163. ¿Por qué lista y no lista enlazada? ¿Usan pila o cola?** [difícil]

**Respuesta sugerida:** Necesitamos acceso por índice (`lineas[i]`, `fila[col_i]`, el slicing del rango), que en un arreglo es O(1) y en una enlazada O(N); la ventaja de la enlazada, insertar al principio, no la usamos. Tampoco usamos pila ni cola: las filas se procesan en orden, pero con `for` y no sacándolas del frente; un `lineas.pop(0)` dentro de un bucle costaría O(N) cada vez y O(N²) en total.

**164. ¿Hay trabajo repetido en la conversión?** [media]

**Respuesta sugerida:** Sí, un factor constante: `es_entero` y `es_flotante` llaman a `int()` y `float()` y descartan el resultado (funciones.py:21 y 30), y después `convertir_valor` vuelve a convertir (funciones.py:101 y 110). Es el precio de separar "¿es entero?" de "convertir"; no cambia el O(L·K).

---

## O. Calidad de código, documentación y pruebas

**165. ¿Dónde documentaron los criterios que pide la consigna?** [básica]

**Respuesta sugerida:** En el comentario del principio de `clase.py` (L1-9): encabezado (vacíos o repetidos dan error, `col_0`, `col_1`… sin encabezado), orden de inferencia, nulos como `None`, booleanos `true`/`false`, prioridad de los tipos forzados y orden de combinación de las opciones. Además, cada método y cada función tiene un docstring breve (de una línea, salvo los de `__init__`, `leer` y `convertir_valor`, que ocupan algunas más).

**166. ¿`help(LectorCSV)` muestra esos criterios?** [trampa]

**Respuesta sugerida:** No: los comentarios con `#` no son docstrings, y la clase no tiene docstring (`LectorCSV.__doc__` es `None`, verificado). `help()` muestra los docstrings de los métodos públicos y no lista los protegidos. La mejora es pasar esos criterios a un docstring de clase con secciones de parámetros, retorno y excepciones.

**167. ¿Cómo probaron que el lector funciona?** [media]

**Respuesta sugerida:** Con `ejemplos.py`: cuatro ejemplos que cubren la lectura habitual con inferencia y tipo forzado, la combinación de opciones, otro delimitador y un error de conversión. Reconocemos que se imprime el resultado y se compara a ojo: no hay resultados esperados escritos ni comparaciones automáticas.

**168. La consigna pide ejemplos de los casos problemáticos. ¿Dónde están?** [difícil]

**Respuesta sugerida:** Es la parte que nos quedó corta, y lo reconocemos. Hay un solo archivo con error (`derror.csv`, un valor no convertible); faltan ejemplos de archivo vacío, fila vacía, filas con distinta cantidad de campos y encabezado vacío o repetido, y tampoco se muestran `encabezado=False`, el tab ni un delimitador de varios caracteres, aunque el lector los soporta. Todos esos casos los probamos por fuera y sabemos qué mensaje da cada uno; lo primero que agregaríamos es un ejemplo por caso con su resultado esperado.

**169. ¿Cómo escribirían una prueba con resultado esperado?** [media]

**Respuesta sugerida:** Con `assert` para los casos que funcionan y `try/except` para los errores, así la prueba falla sola si el comportamiento cambia:

```python
assert lector2.leer("datos1.csv") == [{"nombre": "Cuaderno", "precio": 2500.5},
                                      {"nombre": "Carpeta", "precio": 3200.0}]
try:
    LectorCSV().leer("vacio.csv")
except ValueError as e:
    assert "está vacío" in str(e)
else:
    assert False, "debió lanzar ValueError"
```

**170. ¿Por qué `ejemplos.py` no tiene `if __name__ == "__main__":`?** [media]

**Respuesta sugerida:** No lo pusimos porque `ejemplos.py` no está pensado para importarse. Pero si alguien lo importa, se ejecutan los cuatro ejemplos: lo probamos y salen 42 líneas impresas. La buena práctica es encerrar la demo en esa guarda; los módulos del paquete no la necesitan porque solo tienen definiciones.

**171. ¿Qué detalles de prolijidad cambiarían?** [básica]

**Respuesta sugerida:** El docstring de `forzar_tipo` tiene la ligadura "ﬁ" en "Deﬁne", copiada de un PDF (clase.py:39); hay un typo, "solp", en el docstring de `recortar_diccionario` (funciones.py:129); y sobran espacios al final de clase.py:41 y de clase.py:67. Además, las colecciones fijas `[int, float, str, bool]` (clase.py:40) y `["true", "false"]` (funciones.py:13) serían más claras como tuplas.

**172. ¿Usaron anotaciones de tipo?** [media]

**Respuesta sugerida:** No (`LectorCSV.leer.__annotations__` está vacío). Podríamos poner `def leer(self, ruta_archivo: str) -> list[dict]:`. Son opcionales y mejoran la claridad, pero Python no las controla al ejecutar: aun con anotaciones, `LectorCSV(encabezado="no")` se seguiría tomando como verdadero.

**173. ¿Por qué los nombres están en castellano y son tan largos?** [básica]

**Respuesta sugerida:** Para que el código se lea como la descripción del problema: `cumple_todos_los_filtros`, `establecer_limite`, `filas_crudas`, `filas_tipadas`. Los nombres de las variables cuentan en qué etapa está el dato (crudo, tipado, filtrado), y mantuvimos el mismo idioma en todo el código.

**174. ¿Qué le falta al proyecto para correr desde cualquier lado?** [media]

**Respuesta sugerida:** Un `requirements.txt` con `pandas`, un `__init__.py` vacío en `modulo/`, las rutas de `ejemplos.py` armadas con `Path(__file__).parent` para no depender de la carpeta de trabajo, y la guarda `if __name__ == "__main__":`. Para leer archivos nuevos sin editar código, un script con `argparse` que reciba la ruta y el delimitador.

---

## P. Limitaciones y mejoras

**175. ¿Cuáles son las principales limitaciones?** [media]

**Respuesta sugerida:** No soporta comillas ni coma decimal, no reconoce `VERDADERO`/`FALSO`, el BOM de Excel ensucia la primera columna, un delimitador equivocado no da error y en un archivo de una sola columna no se puede representar un nulo. Además, el límite no ahorra lectura y los setters validan el valor pero no el tipo.

**176. ¿Qué cambiarían primero?** [media]

**Respuesta sugerida:** Primero lo que la consigna pide y quedó corto: ejemplos con resultado esperado para los casos problemáticos. Después lo que puede fallar con un CSV nuevo: `encoding="utf-8-sig"` para el BOM y warnings para lo sospechoso (delimitador probablemente equivocado, columna vacía, rango fuera de la tabla). Después la robustez de la interfaz: `isinstance` con `TypeError` en los setters y `callable()` en `agregar_filtro`.

**177. ¿Cómo soportarían la coma decimal y `VERDADERO`/`FALSO`?** [difícil]

**Respuesta sugerida:** Con parámetros en el constructor. Para la coma decimal, un `separador_decimal=","` que normalice cada celda que parezca número antes de inferir: sacar los puntos de miles y cambiar la coma por punto, solo si el resultado es un float válido. Para los booleanos, dos tuplas configurables, por ejemplo `("true", "verdadero")` y `("false", "falso")`, que usen tanto `es_booleano` como `convertir_valor`.

**178. ¿Cómo harían configurables los nulos?** [media]

**Respuesta sugerida:** Con un parámetro `valores_nulos=("",)` y, antes de inferir, reemplazando por `""` todo valor que esté en esa tupla. Con `valores_nulos=("", "NA")`, un CSV de R daría `None` donde dice `NA` y la columna volvería a ser numérica. Con el valor por defecto, el comportamiento sería idéntico al actual.

**179. ¿Cómo validarían mejor la configuración?** [media]

**Respuesta sugerida:** Validando el tipo antes que el valor, como el ejemplo de la cátedra: `if not isinstance(limite, int): raise TypeError(...)` y después el rango de valores con `ValueError`. Lo mismo para `inicio`/`fin`, `delimitador` (texto no vacío) y `encabezado` (booleano), más `callable()` en `agregar_filtro`. Hoy `establecer_rango(1, 3.0)` se acepta y falla al leer con `TypeError: slice indices must be integers or None or have an __index__ method` (verificado).

**180. ¿Cómo harían que los errores de un filtro digan la fila?** [difícil]

**Respuesta sugerida:** Envolviendo la llamada al filtro en `try/except (KeyError, TypeError) as error` y relanzando una excepción propia que incluya la fila, con `from error` para conservar la causa. Hoy un `KeyError: 'cantidd'` o un `TypeError` por comparar `None` sube sin decir dónde ocurrió.

**181. ¿Cómo soportarían comillas?** [difícil]

**Respuesta sugerida:** Recorriendo cada línea carácter por carácter con un estado "estoy dentro de comillas": el delimitador solo corta cuando se está afuera, y dos comillas seguidas adentro valen como una comilla literal. Para celdas multilínea habría que seguir leyendo líneas hasta cerrar las comillas, o sea trabajar por registro y no por línea. Es mucho más código y propenso a errores; por eso queda al final de la lista.

**182. Si el archivo fuera enorme, ¿qué cambiarían?** [difícil]

**Respuesta sugerida:** Lectura con generadores en dos pasadas: una para inferir los tipos y otra para convertir y filtrar, con memoria mínima a cambio de leer el archivo dos veces. Si todos los tipos están forzados, no hace falta inferir y se podría cortar la lectura al llegar al límite. También validaríamos las columnas seleccionadas al principio, y no después de convertir todo.

---

## Q. Preguntas trampa y de precisión

**183. El error de `derror.csv` dice "fila 3", pero `veinte` está en la segunda fila de datos. ¿Está mal?** [trampa]

**Respuesta sugerida:** No: hay dos numeraciones, a propósito. Los mensajes de error cuentan **líneas del archivo** desde 1, con el encabezado como línea 1, para encontrar el problema en un editor (`fila_i + 2` en clase.py:172). `establecer_rango` cuenta **filas de datos** desde 1: `veinte` es la fila que seleccionaría `establecer_rango(2, 2)`. Sin encabezado las dos numeraciones coinciden (`fila_i + 1`, clase.py:174).

**184. ¿Por qué la correspondencia entre índice de la lista y línea del archivo es exacta?** [trampa]

**Respuesta sugerida:** Porque ninguna línea se saltea: las líneas vacías dan error en vez de ignorarse. Entonces la posición en la lista siempre corresponde a la misma línea del archivo (`num_fila_archivo = i + 1`, clase.py:127). Si salteáramos líneas vacías, habría que llevar la cuenta aparte.

**185. ¿Qué devuelve `bool("false")`?** [trampa]

**Respuesta sugerida:** `True`, porque todo string no vacío es verdadero (verificado). Por eso no convertimos con `bool(texto)`: comparamos el texto en minúsculas con `"true"` y `"false"` (funciones.py:87-92).

**186. ¿`es_booleano(" true ")` da `True`? Entonces, ¿cómo reconocen ` true ` en el archivo?** [trampa]

**Respuesta sugerida:** `es_booleano(" true ")` da `False`, porque la función no hace `strip` (verificado). Pero dentro del lector nunca le llega un valor con espacios: `separar_linea` ya limpió los bordes de cada campo (funciones.py:6). Por eso un `  true  ` en el archivo se lee como `True`.

**187. ¿Qué es `1.000` para su lector?** [trampa]

**Respuesta sugerida:** El flotante `1.0`, no mil: para Python el punto es separador decimal (`float("1.000")` da `1.0`, verificado). Una columna de importes con punto de miles se lee mal sin ningún aviso; hay que forzarla a `str`.

**188. ¿`nan` y `None` son lo mismo?** [trampa]

**Respuesta sugerida:** No. `None` es la celda vacía; `nan` es un float que sale del texto `"nan"` (`float("nan")`). `nan is None` es `False`, y `nan == nan` también es `False` (verificado). Un filtro con `is not None` deja pasar los `nan`.

**189. Escriben en vivo un filtro con `def` y se olvidan el `return`. ¿Qué pasa?** [trampa]

**Respuesta sugerida:** No hay error: la función devuelve `None`, que es falso, y se descartan todas las filas; `leer()` devuelve `[]` (verificado). Si el resultado sale vacío de forma sospechosa, lo primero es revisar el `return`.

**190. Leo con el delimitador equivocado y no sale error. ¿Es un bug?** [trampa]

**Respuesta sugerida:** Es una limitación: una tabla de una sola columna es válida, así que el lector no tiene cómo saber que el separador era otro. Sale una única clave con la línea entera; por ejemplo, `datos2.txt` leído con coma da la clave `'id_envio; destino; costo; entregado'` (verificado). La mejora sería un warning cuando hay una sola columna y la primera línea contiene `;`, un tab o `|`.

**191. `establecer_limite(2.5)`, ¿qué hace? ¿Y `establecer_limite(True)`?** [trampa]

**Respuesta sugerida:** `2.5` se acepta y devuelve **3** filas, porque el corte es `len(filas_filtradas) >= 2.5`, que recién se cumple con 3. `True` se toma como límite 1, porque `bool` es subclase de `int` (los dos verificados). Validamos el valor pero no el tipo.

**192. `lector.limite_filas = 2` (sin guion bajo). ¿Qué pasa?** [trampa]

**Respuesta sugerida:** Nada útil: Python crea un atributo nuevo que el lector nunca lee, y `leer()` devuelve las 6 filas sin error (verificado). Por eso la configuración se hace con los métodos y no asignando atributos.

**193. `LectorCSV(encabezado="False")`, ¿lee sin encabezado?** [trampa]

**Respuesta sugerida:** No: el string `"False"` no está vacío, así que es verdadero, y se lee con encabezado (verificado). Hay que pasar el booleano `False`. Del constructor solo validamos que el delimitador no sea `""`.

**194. Escribo `delimitador="\\t"` (o lo leo de un `input()`). ¿Es un tab?** [trampa]

**Respuesta sugerida:** No: `"\\t"` son dos caracteres, una barra y una t. Un archivo con tabs se lee como una sola columna, sin error (verificado). El tab es `"\t"`.

**195. ¿Con `delimitador=", "` se puede leer `datos1.csv`?** [trampa]

**Respuesta sugerida:** Sí, y da lo mismo que con `","`, porque en ese archivo todas las comas van seguidas de un espacio (verificado). Pero es frágil: una sola coma sin espacio dejaría una fila con menos campos. Con `","` el espacio lo limpia el `strip`.

**196. ¿El tipo de una columna puede cambiar según el rango que pido?** [trampa]

**Respuesta sugerida:** No: la inferencia usa todas las filas del archivo, no solo las del rango ni las filtradas. Con `establecer_rango(2, 2)` el precio de Lapicera sale `800.0`, igual que en la lectura completa (verificado).

**197. ¿Por qué `establecer_rango(2, 3)` devuelve 2 filas y no 1?** [trampa]

**Respuesta sugerida:** Porque los dos extremos están incluidos: filas de datos 2 y 3, Lapicera y Carpeta. Internamente es `filas_tipadas[1:3]`: el slice excluye el final, y por eso al `fin` no se le resta 1.

**198. Si no hay filtros, ¿`cumple_todos_los_filtros` da `True` o `False`?** [trampa]

**Respuesta sugerida:** `True`: el `for` no entra y se llega al `return True` (funciones.py:125). Es el mismo resultado que `all([])`: si no hay condiciones, todas las filas pasan.

**199. ¿Por qué `'1'` y `'0'` no se leen como booleanos, si en Python `True == 1`?** [trampa]

**Respuesta sugerida:** Porque la inferencia trabaja sobre el texto del archivo, no sobre valores de Python, y solo `true`/`false` son booleanos (funciones.py:13). `["1", "0"]` se infiere `int` (verificado). Aceptarlos haría que una columna de cantidades con unos y ceros saliera booleana.

**200. ¿`'10' < '8'` es verdadero o falso?** [trampa]

**Respuesta sugerida:** Verdadero, porque entre strings la comparación es alfabética, carácter por carácter, y `'1'` va antes que `'8'` (verificado). Es una de las razones para convertir los tipos antes de filtrar: con texto, un filtro numérico daría resultados incorrectos sin ningún error.

---

## R. Teoría de la cátedra aplicada

**201. ¿Por qué usan `for` y nunca `while`?** [básica]

**Respuesta sugerida:** La cátedra dice que el `for` va cuando se recorren todos los elementos de una colección y el `while` cuando no se sabe cuántas veces se va a iterar. Nosotros siempre recorremos colecciones conocidas: líneas, columnas, filas y filtros. El único corte anticipado, el límite, se hace con `for` + `break` (clase.py:206-208), sin el riesgo de un bucle infinito por un índice manual.

**202. ¿Por qué el rango es una tupla? ¿Y por qué los tipos válidos están en una lista?** [media]

**Respuesta sugerida:** El rango `(inicio, fin)` es un par fijo que no se modifica: para eso va una tupla, que es inmutable (clase.py:59). `[int, float, str, bool]` (clase.py:40) y `["true", "false"]` (funciones.py:13) también son colecciones fijas y, según la cátedra, también corresponderían tuplas. Funciona igual (`str in (int, float, str, bool)` da `True`); es una mejora de estilo que reconocemos.

**203. ¿Por qué usan `range(len(...))` y no `enumerate`?** [media]

**Respuesta sugerida:** Porque necesitamos el índice para dos cosas: numerar la fila en los mensajes (`i + 1`, `fila_i + 2`) y buscar la misma posición en `encabezados` y en la fila. `enumerate` sería más prolijo y daría los mismos pares: `enumerate(lineas[1:], start=2)` es equivalente (verificado). Lo dejamos con índices por claridad.

**204. ¿Qué diferencia hay entre módulo, paquete y script en su proyecto?** [básica]

**Respuesta sugerida:** Módulo: un archivo con código reutilizable (`funciones.py`, `clase.py`). Paquete: una carpeta con módulos (`modulo/`). Script: un archivo que se ejecuta para hacer algo concreto (`ejemplos.py`). Importar un módulo ejecuta su código de arriba a abajo; como los nuestros solo tienen definiciones, importarlos no imprime ni lee nada.

**205. ¿Qué valor tiene `__name__` dentro de `clase.py`?** [media]

**Respuesta sugerida:** Cuando se importa, `'modulo.clase'` (verificado): el nombre del archivo sin `.py`, con el nombre del paquete adelante. Si se ejecutara directamente valdría `'__main__'`, que es lo que pregunta la guarda `if __name__ == "__main__":`.

**206. ¿Qué es *duck typing* y dónde aparece?** [media]

**Respuesta sugerida:** Lo que importa es qué puede hacer un objeto y no de qué clase es. En `cumple_todos_los_filtros` llamamos `funcion(fila_diccionario)` sin chequear el tipo (funciones.py:123): sirve cualquier cosa que se pueda llamar con una fila. La desventaja es que no hay validación temprana: `agregar_filtro(5)` se acepta y falla recién en `leer()` con `TypeError: 'int' object is not callable` (verificado).

**207. ¿Qué es una clase abstracta y la necesitaban?** [media]

**Respuesta sugerida:** Es una clase que hereda de `ABC` y marca métodos con `@abstractmethod`: no se puede instanciar y obliga a las hijas a implementar esos métodos, como un contrato. No la necesitábamos porque hay una sola implementación; tendría sentido con varios formatos (`class Lector(ABC)` con `leer` abstracto).

**208. ¿Por qué `is not None` y no `!= None`?** [básica]

**Respuesta sugerida:** Porque `None` es un objeto único y se compara por identidad, con `is`. Además `is` no depende de cómo cada tipo define `==`. Lo usamos en clase.py:192, 198, 207 y 214 y en el filtro del ejemplo 2.

**209. ¿Cómo se lee `self._limite_filas is not None and len(filas_filtradas) >= self._limite_filas` sin paréntesis?** [media]

**Respuesta sugerida:** Las comparaciones tienen más prioridad que el `and`, así que se lee como `(… is not None) and (len(…) >= …)`. Y el `and` evalúa de izquierda a derecha con cortocircuito: si no hay límite, la segunda parte ni se calcula (clase.py:207).

**210. ¿Usaron `*args` o parámetros con valores por defecto?** [media]

**Respuesta sugerida:** Valores por defecto sí: `def __init__(self, delimitador=",", encabezado=True)` (clase.py:21). `*args` no, pero `seleccionar_columnas(self, *columnas)` sería una buena mejora: se llamaría `seleccionar_columnas("nombre", "precio")`, guardaría una tupla inmutable y eliminaría el problema del string recorrido letra por letra.

**211. ¿Usaron expresiones condicionales? ¿Dónde podrían?** [media]

**Respuesta sugerida:** No. En clase.py:171-174 quedaría `num_fila_archivo = fila_i + 2 if self.encabezado else fila_i + 1`, y `es_booleano` podría ser `return texto.lower() in ("true", "false")`. Las expresiones condicionales también son no estrictas: solo se evalúa la rama elegida.

---

## S. Demostración en vivo con un CSV nuevo

**212. Les damos un CSV nuevo. ¿Cuáles son sus primeros pasos?** [básica]

**Respuesta sugerida:** Primero lo miramos como texto: separador, si la primera línea es encabezado, comillas, coma decimal, códigos con ceros adelante y celdas vacías (ver la checklist). Después abrimos Python parados en la carpeta del proyecto, creamos el lector con el delimitador que corresponde, forzamos `str` en las columnas de códigos y leemos. Mostramos la lista y el DataFrame y explicamos los tipos que salieron.

**213. Leyeron el archivo y sale una sola clave larga. ¿Qué pasó?** [media]

**Respuesta sugerida:** El delimitador está mal: la línea no se cortó y quedó entera como una sola columna. Se arregla creando el lector con el separador del archivo, por ejemplo `LectorCSV(delimitador=";")` o `LectorCSV(delimitador="\t")`. Otra pista del mismo problema: `forzar_tipo` sobre una columna que "sí está" dice que no existe en la tabla (verificado).

**214. ¿Por qué esta columna numérica salió como texto? ¿Cómo encuentran al culpable?** [media]

**Respuesta sugerida:** Porque al menos un valor no vacío de la columna no es un número válido para Python (un `NA`, un `15%`, una coma decimal, un espacio de miles) y la inferencia es "todo o nada". Para encontrarlo:

```python
from modulo.funciones import es_flotante
[v for v in (f["porc"] for f in datos) if v is not None and not es_flotante(v)]
```

Con una columna `10`, `15%`, vacío, `20` devuelve `['15%']` (verificado). Después se decide: dejarla como texto o limpiar el archivo.

**215. "Muéstrennos los nombres de los productos con precio mayor a 1000." ¿Cómo lo escriben?** [básica]

**Respuesta sugerida:**

```python
lector = LectorCSV()
lector.agregar_filtro(lambda fila: fila["precio"] is not None and fila["precio"] > 1000)
lector.seleccionar_columnas(["nombre"])
print(lector.leer("datos1.csv"))
```

Sobre `datos1.csv` da Cuaderno, Carpeta y Mochila (verificado). El `is not None` protege por si el archivo nuevo tiene precios vacíos.

**216. El archivo no tiene encabezado. ¿Cómo lo leen y cómo filtran?** [básica]

**Respuesta sugerida:** Con `LectorCSV(encabezado=False)` y usando los nombres generados: `lector.agregar_filtro(lambda f: f["col_2"] > 5)` o `lector.forzar_tipo("col_0", str)`. Ojo: `col_0` es la **primera** columna (base 0).

**217. ¿Cómo muestran rápido cuántas filas leyeron y qué columnas hay?** [básica]

**Respuesta sugerida:** `len(datos)` da la cantidad de filas y `list(datos[0].keys())` las columnas, en el orden del archivo (o en el de `seleccionar_columnas`). Si `datos` está vacío, `datos[0]` da `IndexError`, así que conviene chequear antes con `if datos:`.

**218. Les pedimos el promedio de una columna con nulos. ¿Cómo lo calculan?** [media]

**Respuesta sugerida:** Sacando los `None` antes: `valores = [f["cantidad"] for f in datos if f["cantidad"] is not None]` y después `sum(valores) / len(valores)`; en `datos1.csv` da `19.2` (verificado). `sum` con un `None` adentro da `TypeError`. Con pandas, `pd.DataFrame(datos)["cantidad"].mean()` ignora los `NaN` solo y da lo mismo.

**219. ¿Y ordenar por una columna con nulos?** [difícil]

**Respuesta sugerida:** `sorted(datos, key=lambda f: f["cantidad"])` da `TypeError` por el `None` (verificado). Hay que decidir dónde van los nulos, por ejemplo al final:

```python
sorted(datos, key=lambda f: (f["cantidad"] is None, f["cantidad"] or 0))
```

La tupla ordena primero por "¿es nulo?" (`False` antes que `True`) y después por el valor.

**220. Les damos un archivo separado por una cantidad variable de espacios (columnas "alineadas"). ¿Lo pueden leer?** [difícil]

**Respuesta sugerida:** Con `delimitador=" "` no: los espacios dobles generan campos vacíos y ya el encabezado falla con "Error en fila 1, columna 2: El nombre de la columna está vacío." (verificado). Pero `LectorCSV(delimitador=None)` sí funciona, porque `separar_linea` hace `linea.split(None)` y `str.split(None)` corta por cualquier secuencia de blancos: `id   nombre      nota` → `{'id': 1, 'nombre': 'Ana', 'nota': 8.5}` (verificado). Ojo: es un comportamiento heredado de `str.split` que no está validado ni documentado en el código (el constructor solo rechaza `""`), y no sirve si algún texto tiene espacios adentro.

---

## Demostración en vivo: recetas

Todos estos fragmentos se ejecutaron tal cual sobre archivos de prueba (sin tocar el proyecto) y dieron el resultado que se indica. Reemplazar `nuevo.csv` y los nombres de columna por los del archivo que den los docentes.

### Receta 0. Pararse en la carpeta correcta

En la terminal (PowerShell o la que sea), ir a la carpeta que contiene `ejemplos.py` y la carpeta `modulo/`, y abrir Python ahí:

```text
cd "C:\...\G24_Berruti_Liali_Vranjes\G24_Berruti_Liali_Vranjes"
python
```

Ya dentro de Python, comprobar dónde estamos:

```python
import os
print(os.getcwd())          # tiene que ser la carpeta de ejemplos.py
```

- Si el CSV nuevo está en otra carpeta, pasar la ruta completa como *raw string*, para que las barras invertidas no se interpreten como escapes: `lector.leer(r"C:\Users\...\Descargas\nuevo.csv")`.
- Si por algún motivo Python está abierto en otra carpeta: `import sys; sys.path.insert(0, r"C:\...\G24_Berruti_Liali_Vranjes\G24_Berruti_Liali_Vranjes")` antes del import, y rutas completas para los datos.
- Atajo: `python -i ejemplos.py` corre los cuatro ejemplos y deja la consola abierta con `LectorCSV` y `pd` ya importados.

### Receta 1. Espiar el archivo antes de leerlo

```python
with open("nuevo.csv", encoding="utf-8") as archivo:
    for _ in range(3):
        print(repr(archivo.readline()))
```

`repr` muestra lo invisible: un tab aparece como `\t`, el BOM como `\ufeff` al principio y el fin de línea como `\n`. Con eso se decide el delimitador y si hay encabezado. Ejemplo de salida: `'codigo,producto,precio,stock,activo\n'`.

### Receta 2. CSV con coma (configuración por defecto)

```python
from modulo.clase import LectorCSV
import pandas as pd

lector = LectorCSV()                 # delimitador="," y encabezado=True
datos = lector.leer("nuevo.csv")
for fila in datos:
    print(fila)
print(pd.DataFrame(datos))
```

### Receta 3. Punto y coma

```python
datos = LectorCSV(delimitador=";").leer("nuevo_pyc.csv")
```

### Receta 4. Tabulador

```python
datos = LectorCSV(delimitador="\t").leer("nuevo.tsv")     # "\t", no "\\t"
```

### Receta 5. Sin encabezado

```python
lector = LectorCSV(encabezado=False)
lector.forzar_tipo("col_0", str)     # las columnas se llaman col_0, col_1, ...
datos = lector.leer("sin_enc.csv")
# [{'col_0': '00123', 'col_1': 'Yerba', 'col_2': 1500.5}, ...]
```

### Receta 6. Forzar códigos como texto

```python
lector = LectorCSV()
lector.forzar_tipo("codigo", str)    # conserva '00123'; sin esto sale 123
datos = lector.leer("nuevo.csv")
# [f["codigo"] for f in datos] -> ['00123', '00456', '00789', '01000']
```

### Receta 7. Filtrar con nulos de forma segura

```python
lector = LectorCSV()
lector.agregar_filtro(lambda fila: fila["stock"] is not None and fila["stock"] < 20)
datos = lector.leer("nuevo.csv")
```

El `is not None and` va **primero**: por el cortocircuito, si el valor es `None` la comparación no se evalúa y no hay `TypeError`. Para booleanos con nulos, usar `fila["activo"] is True` o `is False`, no `not fila["activo"]`.

### Receta 8. Rango + filtro + límite + columnas

```python
lector = LectorCSV()
lector.forzar_tipo("codigo", str)
lector.establecer_rango(1, 3)                          # filas de datos 1 a 3, inclusive
lector.agregar_filtro(lambda fila: fila["activo"] is True)
lector.establecer_limite(1)                            # 1 fila que cumpla
lector.seleccionar_columnas(["codigo", "precio"])      # se aplica al final
res = lector.leer("nuevo.csv")
print(res)                   # [{'codigo': '00123', 'precio': 1500.5}]
print(pd.DataFrame(res))
```

Para decirlo en voz alta: "primero el rango, después el filtro, el límite cuenta las que cumplen y al final las columnas".

### Receta 9. Mostrar la lista, el DataFrame y los tipos

```python
for fila in datos:
    print(fila)
print(pd.DataFrame(datos))
print(len(datos), list(datos[0].keys()) if datos else "sin filas")
print({col: sorted({type(f[col]).__name__ for f in datos}) for col in datos[0]})
# {'codigo': ['int'], 'producto': ['str'], 'precio': ['float'], 'stock': ['NoneType', 'int'], 'activo': ['bool']}
```

La última línea muestra qué tipo quedó en cada columna; sirve para explicar por qué el DataFrame muestra `10.0` y `NaN` donde la lista tiene `10` y `None`.

### Receta 10. Leer un error con `try/except`

```python
lector = LectorCSV(delimitador=";")
lector.forzar_tipo("producto", int)
try:
    datos = lector.leer("nuevo_pyc.csv")
except (ValueError, FileNotFoundError) as error:
    print(type(error).__name__, "->", error)
# ValueError -> Error en fila 2, columna 'producto': el valor 'Yerba' no se puede convertir a int.
```

Se captura también `FileNotFoundError` porque no es subclase de `ValueError`: una ruta mal escrita cortaría el programa con solo `except ValueError`.

---

## Checklist: 10 cosas a revisar en un CSV antes de leerlo

1. **Separador.** ¿Coma, punto y coma, tab, `|`, espacio? (Receta 1: el tab se ve como `\t`.) Con el separador equivocado no hay error: sale una sola columna.
2. **Encabezado.** ¿La primera línea tiene nombres o ya son datos? Si son datos → `encabezado=False`; si no, se pierde la primera fila sin aviso.
3. **Nombres de columna.** ¿Hay alguno vacío, repetido, entre comillas, o el encabezado empieza con coma (índice de pandas)? Vacío o repetido → `ValueError` en la fila 1.
4. **BOM y encoding.** ¿`repr` muestra `\ufeff` al principio? La primera clave va a quedar `'\ufeff...'`. ¿Se ven bien los acentos? Si el archivo está en latin-1 → `UnicodeDecodeError`: volver a guardarlo como UTF-8.
5. **Números con formato local.** Coma decimal (`1500,50`), punto de miles (`1.000` → `1.0`), `%`, paréntesis, signo menos raro: la columna queda `str` (o, con puntos de miles, se lee mal en silencio).
6. **Códigos que parecen números.** Ceros adelante (`00123`, `0341`), `+` en teléfonos, `E` en códigos (`12E3`) → `forzar_tipo(col, str)`.
7. **Nulos.** Celdas vacías → `None`. `NA`, `NULL`, `-` vuelven `str` la columna; `nan` queda `float('nan')`. Los filtros sobre columnas con nulos llevan `is not None and ...`.
8. **Booleanos.** `true`/`false` en cualquier mayúscula funcionan; `VERDADERO`/`FALSO`, `si`/`no`, `1`/`0` quedan como texto o como `int`.
9. **Líneas problemáticas.** Línea en blanco en el medio o dos saltos de línea al final → error de fila vacía. Filas `,,` al final (Excel) → filas de `None`. Archivo de una sola columna con huecos → error.
10. **Campos por fila.** ¿Todas las filas tienen la misma cantidad de separadores? Una coma dentro de comillas o una celda con salto de línea → error de cantidad de elementos (a veces en la línea siguiente).

**Después de leer:** una sola clave larga → delimitador equivocado. "La columna 'x' no existe" cuando sí existe → BOM o delimitador. Resultado vacío inesperado → filtro sin `return`, rango fuera de la tabla o límite 0. Una columna numérica salió `str` → buscar el valor culpable (pregunta 214).

---

## Machete de una página

1. **Arquitectura:** `funciones.py` (8 funciones puras) + `clase.py` (`LectorCSV`: guarda la configuración y coordina) + `ejemplos.py` (4 ejemplos; único que imprime y usa pandas). Sin `csv` ni pandas en el lector: `str.split` + `strip`.
2. **Pipeline de `leer()`** (clase.py:71-80): `_leer_archivo` → `_procesar_lineas` → `_convertir_tipos` → `_aplicar_filtros_y_rangos`. Devuelve una lista de diccionarios.
3. **Interfaz pública:** `LectorCSV(delimitador=",", encabezado=True)`, `forzar_tipo`, `agregar_filtro`, `establecer_limite`, `establecer_rango`, `seleccionar_columnas`, `leer(ruta)`. Los métodos de configuración devuelven `None` (no se encadenan).
4. **7 atributos** (clase.py:30-36): `delimitador` y `encabezado` públicos; `_tipos_columnas`, `_filtros`, `_limite_filas`, `_rango_filas`, `_columnas` **protegidos** (un guion bajo = convención, no privado). El objeto guarda *cómo* leer, no *lo que* leyó.
5. **Inferencia** (funciones.py:36-75): `bool` → `int` → `float` → `str`, sobre los valores no vacíos, "todo o nada", con **toda** la columna del archivo (no depende del rango ni del filtro).
6. **`int` antes que `float`:** todo entero es un float válido, pero `int("10.0")` falla. `10, 20, 30.5` → `float`. Mezcla número/texto → `str`. Columna toda vacía → `str` con `None`.
7. **Nulo** = celda vacía o con solo espacios → `None`, para cualquier tipo (incluso `str` forzado). `NA`/`NULL` no son nulos; `"nan"` → `float('nan')`, que **no** es `None`.
8. **Booleanos:** solo `true`/`false`, sin importar mayúsculas. `bool("false")` es `True`, por eso hay una rama propia (funciones.py:87-92). `1`/`0` → `int`.
9. **Tipo forzado:** prioridad total, ni se infiere (clase.py:158-159). Si no convierte → `ValueError` con fila, columna, valor y tipo; nunca se cambia el tipo. Forzar `str` conserva `00123`.
10. **Combinación:** rango → filtros → límite → columnas (clase.py:198-219; documentado en clase.py:7-9).
11. **El límite cuenta filas que cumplen** el filtro; "primeras N y filtrar" se pide con `establecer_rango(1, N)` + filtro. Columnas al final → se puede filtrar por una columna que no se devuelve.
12. **Dos numeraciones:** el rango cuenta filas de **datos** desde 1, extremos incluidos (`[inicio - 1 : fin]`); los errores cuentan **líneas del archivo** (encabezado = línea 1, `fila_i + 2`). `veinte` = fila de datos 2 = "fila 3" del error.
13. **Encabezado:** vacío o repetido → `ValueError`; `Nombre` ≠ `nombre`; con `encabezado=False` → `col_0`, `col_1`, … (base 0).
14. **Errores de estructura** → `ValueError` y se detiene: archivo vacío, primera línea vacía, fila vacía, cantidad de campos distinta. Solo encabezado → `[]`. Un salto de línea final está bien; dos → error. Rango fuera de la tabla → `[]` sin error.
15. **Excepciones, no `print`:** el paquete no imprime; `ejemplos.py:48-52` captura `ValueError`. `FileNotFoundError` con mensaje propio (no es subclase de `ValueError`). `raise` dentro de `except` → encadenamiento implícito; mejora: `from error`.
16. **Configuración vs lectura:** delimitador vacío, tipo inválido, límite negativo y rango inválido fallan al configurar; columnas inexistentes de `forzar_tipo`/`seleccionar_columnas`, al leer.
17. **Cortocircuito:** `is not None and ...` en el filtro del ejemplo 2 (ejemplos.py:23) y en el límite (clase.py:207). Varios filtros = AND con salida temprana.
18. **Eficiencia:** tiempo y memoria O(L·K); nombres repetidos O(K²) por `in` sobre lista. El límite **no** ahorra lectura, y un error de conversión fuera del rango igual frena la lectura.
19. **pandas:** `None` → `NaN` y la columna `int` pasa a `float64` (`10.0`); por eso se muestra también la lista. DataFrame indexa desde 0.
20. **Limitaciones para decir antes de que pregunten:** sin comillas, sin coma decimal, sin `VERDADERO`/`FALSO`, BOM de Excel (se arregla con `utf-8-sig`), delimitador equivocado sin error, archivo de una columna sin nulos posibles, setters sin validación de tipo, y faltan ejemplos de casos problemáticos con resultado esperado.
