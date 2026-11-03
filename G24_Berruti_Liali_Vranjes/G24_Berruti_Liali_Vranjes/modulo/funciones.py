def separar_linea(linea, delimitador):
    """Corta un renglon por el delimitador y quita los espacios sobrantes"""
    partes = linea.split(delimitador)
    campos_limpios = []
    for elemento in partes:
        campos_limpios.append(elemento.strip())
    return campos_limpios


def es_booleano(texto):
    """Devuelve True si el texto es true o false"""
    texto_min = texto.lower()
    if texto_min in ["true", "false"]:
        return True
    return False


def es_entero(texto):
    """Devuelve True si el texto puede convertirse a entero"""
    try:
        int(texto)
        return True
    except ValueError:
        return False


def es_flotante(texto):
    """Devuelve True si el texto puede convertirse a flotante"""
    try:
        float(texto)
        return True
    except ValueError:
        return False


def inferir_tipo_columna(valores_columna):
    """Deduce el tipo de dato de una columna probando en orden: bool, int, float y str."""
    no_vacios = []
    for valor in valores_columna:
        if valor != "":
            no_vacios.append(valor)

    # Si todas las celdas están vacías, la columna queda como str
    if len(no_vacios) == 0:
        return str

    # 1. Probamos si todos son booleanos
    todos_bool = True
    for valor in no_vacios:
        if not es_booleano(valor):
            todos_bool = False
            break
    if todos_bool:
        return bool

    # 2. Probamos si todos son enteros
    todos_int = True
    for valor in no_vacios:
        if not es_entero(valor):
            todos_int = False
            break
    if todos_int:
        return int

    # 3. Probamos si todos son flotantes (incluye mezcla de int y float)
    todos_float = True
    for valor in no_vacios:
        if not es_flotante(valor):
            todos_float = False
            break
    if todos_float:
        return float

    # 4. Si hay mezcla de números y texto, queda como str
    return str


def convertir_valor(texto, tipo_esperado, num_fila, nombre_col):
    """Convierte el texto al tipo de dato que corresponde. Si está vacía devuelve None,
     y si falla la conversión, avisa con un error indicando la fila y la columna."""
    if texto == "":
        return None

    if tipo_esperado == str:
        return texto

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

    if tipo_esperado == int:
        try:
            return int(texto)
        except ValueError:
            raise ValueError(
                f"Error en fila {num_fila}, columna '{nombre_col}': "
                f"el valor '{texto}' no se puede convertir a int."
            )

    if tipo_esperado == float:
        try:
            return float(texto)
        except ValueError:
            raise ValueError(
                f"Error en fila {num_fila}, columna '{nombre_col}': "
                f"el valor '{texto}' no se puede convertir a float."
            )

    raise ValueError(f"Tipo de dato no soportado: {tipo_esperado}")


def cumple_todos_los_filtros(fila_diccionario, lista_funciones_filtro):
    """Evalua las funciones de filtro y devuelve True si la fila cumple todas"""
    for funcion in lista_funciones_filtro:
        if not funcion(fila_diccionario):
            return False
    return True


def recortar_diccionario(fila_diccionario, columnas_elegidas):
    """Arma un nuevo diccionario solp con las columnas seleccionadas"""
    nuevo_diccionario = {}
    for col in columnas_elegidas:
        nuevo_diccionario[col] = fila_diccionario[col]
    return nuevo_diccionario