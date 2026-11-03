# Criterios definidos por el grupo:
# - Encabezados: se usa la primera fila por defecto. Si hay nombres de columnas vacíos
#   o repetidos se detiene la lectura con ValueError. Si encabezado=False, se nombran col_0, col_1...
# - Tipos de datos: orden de inferencia bool -> int -> float -> str. Celdas vacías se guardan
#   como None (si toda una columna está vacía queda como tipo str). Se reconoce 'true' y 'false'
#   como booleanos. Los tipos indicados con forzar_tipo() tienen prioridad.
# - Combinación de opciones: 1) Rango de filas (numeradas desde 1, incluye inicio y fin),
#   2) Filtros, 3) Límite de cantidad de filas y 4) Selección de columnas al final (permite
#   filtrar por columnas que no se incluyen en el resultado).

from modulo.funciones import (
    separar_linea,
    inferir_tipo_columna,
    convertir_valor,
    cumple_todos_los_filtros,
    recortar_diccionario
)


class LectorCSV:
    def __init__(self, delimitador=",", encabezado=True):
        """
        Guarda configuracion predeterminada del lector
        - delimitador: caracter que separa los valores en el archivo
        - encabezado: si la primera fila es el encabezado o no
        """
        if delimitador == "":
            raise ValueError("El delimitador no puede ser vacío.")

        self.delimitador = delimitador
        self.encabezado = encabezado
        self._tipos_columnas = {}       # Diccionario para {columna: tipo}
        self._filtros = []              # Lista de funciones para filtrar
        self._limite_filas = None       # Cantidad máxima de filas a leer
        self._rango_filas = None        # Tupla (inicio, fin) para rango de filas
        self._columnas = None           # Lista de columnas a conservar

    def forzar_tipo(self, columna, tipo_dato):
        """Deﬁne manualmente qué tipo de dato va a tener una columna."""
        if tipo_dato not in [int, float, str, bool]:
            raise ValueError("Tipo no válido. Use int, float, str o bool.") 

        self._tipos_columnas[columna] = tipo_dato

    def agregar_filtro(self, funcion_filtro):
        """Agrega una condición para filtrar las filas que queremos mantener."""
        self._filtros.append(funcion_filtro)

    def establecer_limite(self, limite):
        """Define la cantidad maxima de filas a leer"""
        if limite < 0:
            raise ValueError("El limite de filas no puede ser negativo")
        self._limite_filas = limite

    def establecer_rango(self, inicio, fin):
        """Elige desde qué número de fila hasta cuál queremos procesar (arrancando a contar desde 1)."""
        if inicio < 1 or fin < inicio:
            raise ValueError("Rango invalido: 'inicio' debe ser >= 1 y 'fin' >= 'inicio'")
        self._rango_filas = (inicio, fin)

    def seleccionar_columnas(self, lista_columnas):
        """Define las columnas que se quieren obtener en el resultado"""
        self._columnas = lista_columnas

    def leer(self, ruta_archivo):
        """
        Funcion principal: abre el archivo, separa los datos, les asigna 
        los tipos correctos y aplica los filtros, rangos y columnas
        """
        # 1. Lectura del archivo
        lineas = self._leer_archivo(ruta_archivo)

        # 2. Separamos el encabezado y los datos, controlando errores
        encabezados, filas_crudas = self._procesar_lineas(lineas)

        # 3. Asignamos los tipos (automaticos o los que pidio el usuario)
        filas_tipadas = self._convertir_tipos(encabezados, filas_crudas)

        # 4. Aplicamos rango, filtros, limite y recorte de columnas
        filas_filtradas = self._aplicar_filtros_y_rangos(encabezados, filas_tipadas)

        return filas_filtradas

    def _leer_archivo(self, ruta_archivo):
        """Abre el archivo de texto plano y devuelve sus lineas limpias"""
        try:
            with open(ruta_archivo, "r", encoding="utf-8") as archivo:
                lineas = []
                for linea in archivo:
                    lineas.append(linea.rstrip("\n\r"))
        except FileNotFoundError:
            raise FileNotFoundError(f"No se encontró el archivo en la ruta: {ruta_archivo}")

        if len(lineas) == 0:
            raise ValueError(f"El archivo '{ruta_archivo}' está vacío.")

        return lineas

    def _procesar_lineas(self, lineas):
        """Separa las lineas usando el delimitador configurado"""
        primera_linea = lineas[0]
        if primera_linea.strip() == "":
            raise ValueError("Error en fila 1: La primera línea del archivo está vacía.")

        primeros_elementos = separar_linea(primera_linea, self.delimitador)
        cant_columnas = len(primeros_elementos)

        # Procesamiento del encabezado
        encabezados = []
        if self.encabezado:
            for i in range(cant_columnas):
                nombre = primeros_elementos[i]
                if nombre == "":
                    raise ValueError(f"Error en fila 1, columna {i + 1}: El nombre de la columna está vacío.")
                if nombre in encabezados:
                    raise ValueError(f"Error en fila 1: El nombre de columna '{nombre}' está repetido.")
                encabezados.append(nombre)
            indice_inicio_datos = 1
        else:
            for i in range(cant_columnas):
                encabezados.append(f"col_{i}")
            indice_inicio_datos = 0

        # Procesamiento de las filas de datos
        filas_crudas = []
        for i in range(indice_inicio_datos, len(lineas)):
            num_fila_archivo = i + 1
            linea_actual = lineas[i]

            if linea_actual.strip() == "":
                raise ValueError(f"Error en fila {num_fila_archivo}: Se encontró una fila vacía.")

            elementos = separar_linea(linea_actual, self.delimitador)

            if len(elementos) != cant_columnas:
                raise ValueError(
                    f"Error en fila {num_fila_archivo}: Cantidad incorrecta de elementos. "
                    f"Se esperaban {cant_columnas} columnas, pero se encontraron {len(elementos)}."
                )

            filas_crudas.append(elementos)

        return encabezados, filas_crudas

    def _convertir_tipos(self, encabezados, filas_crudas):
        """Infiere o aplica tipos de datos (int, float, bool, str, None)"""
        for col_forzada in self._tipos_columnas:
            if col_forzada not in encabezados:
                raise ValueError(f"La columna '{col_forzada}' indicada en forzar_tipo no existe en la tabla.")

        cant_columnas = len(encabezados)
        tipos_definidos = {}

        # A. Determinamos el tipo de cada columna
        for col_i in range(cant_columnas):
            nombre_col = encabezados[col_i]

            if nombre_col in self._tipos_columnas:
                tipos_definidos[nombre_col] = self._tipos_columnas[nombre_col]
            else:
                valores_columna = []
                for fila in filas_crudas:
                    valores_columna.append(fila[col_i])
                tipos_definidos[nombre_col] = inferir_tipo_columna(valores_columna)

        # B. Armamos la lista de diccionarios convirtiendo cada valor
        lista_diccionarios = []
        for fila_i in range(len(filas_crudas)):
            elementos_fila = filas_crudas[fila_i]

            if self.encabezado:
                num_fila_archivo = fila_i + 2
            else:
                num_fila_archivo = fila_i + 1

            diccionario_fila = {}
            for col_i in range(cant_columnas):
                nombre_col = encabezados[col_i]
                valor_texto = elementos_fila[col_i]
                tipo_col = tipos_definidos[nombre_col]

                diccionario_fila[nombre_col] = convertir_valor(
                    valor_texto, tipo_col, num_fila_archivo, nombre_col
                )

            lista_diccionarios.append(diccionario_fila)

        return lista_diccionarios

    def _aplicar_filtros_y_rangos(self, encabezados, filas_tipadas):
        """Filtra y recorta los datos aplicando todas las reglas que definió el usuario"""
        if self._columnas is not None:
            for col in self._columnas:
                if col not in encabezados:
                    raise ValueError(f"La columna seleccionada '{col}' no existe en la tabla.")

        # 1er Rango de filas
        if self._rango_filas is not None:
            inicio, fin = self._rango_filas
            filas_en_rango = filas_tipadas[inicio - 1 : fin]
        else:
            filas_en_rango = filas_tipadas

        # 2do Filtros y 3er Límite de cantidad
        filas_filtradas = []
        for fila in filas_en_rango:
            if self._limite_filas is not None and len(filas_filtradas) >= self._limite_filas:
                break

            if cumple_todos_los_filtros(fila, self._filtros):
                filas_filtradas.append(fila)

        # 4to Selección de columnas
        if self._columnas is not None:
            resultado_final = []
            for fila in filas_filtradas:
                fila_recortada = recortar_diccionario(fila, self._columnas)
                resultado_final.append(fila_recortada)
            return resultado_final

        return filas_filtradas