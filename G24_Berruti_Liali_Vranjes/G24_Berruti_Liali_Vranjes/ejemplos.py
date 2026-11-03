import pandas as pd
from modulo.clase import LectorCSV


print("EJEMPLO 1: Lectura de datos1.csv (Inferencia y tipo forzado)")
lector1 = LectorCSV(delimitador=",")
lector1.forzar_tipo("codigo", str)
datos_productos = lector1.leer("datos1.csv")

print("\nDatos leídos del archivo:")
for fila in datos_productos:
    print(fila)

print("\nVisualización como DataFrame de pandas:")
tabla_productos = pd.DataFrame(datos_productos)
print(tabla_productos)



print("EJEMPLO 2: Selección sobre datos1.csv (Rango, Filtro, Límite y Columnas)")
lector2 = LectorCSV(delimitador=",")
lector2.establecer_rango(1, 5)
lector2.agregar_filtro(lambda fila: fila["cantidad"] is not None and fila["cantidad"] < 15)
lector2.establecer_limite(2)
lector2.seleccionar_columnas(["nombre", "precio"])

datos_filtrados = lector2.leer("datos1.csv")
print("\nLista de diccionarios filtrada y recortada:")
print(datos_filtrados)
print("\nDataFrame de pandas:")
print(pd.DataFrame(datos_filtrados))

print("EJEMPLO 3: Lectura de datos2.txt con separador punto y coma (;)")
lector3 = LectorCSV(delimitador=";")
datos_envios = lector3.leer("datos2.txt")

print("\nDatos leídos del archivo:")
for fila in datos_envios:
    print(fila)

print("\nDataFrame de pandas:")
print(pd.DataFrame(datos_envios))

print("EJEMPLO 4: Manejo de errores leyendo derror.csv")
lector_error = LectorCSV(delimitador=",")
lector_error.forzar_tipo("cantidad", int)

try:
    lector_error.leer("derror.csv")
except ValueError as error:
    print("El lector detectó el problema y detuvo la lectura:")
    print(error)