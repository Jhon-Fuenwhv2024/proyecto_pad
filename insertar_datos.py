import json
from conexion_db import BaseDatosFCTech

def cargar_datos_json(archivo_json):
    """
    Carga los datos desde un archivo JSON.
    Retorna un diccionario con productos, clientes y ventas.
    """
    try:
        with open(archivo_json, 'r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
        print(f"✅ Datos cargados correctamente desde '{archivo_json}'.\n")
        return datos
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{archivo_json}'.")
        return None
    except json.JSONDecodeError:
        print(f"❌ Error: El archivo '{archivo_json}' no es un JSON válido.")
        return None

def convertir_a_tuplas(lista_diccionarios, campos_orden):
    """
    Convierte una lista de diccionarios a una lista de tuplas.
    El orden de los campos es especificado por 'campos_orden'.
    """
    tuplas = []
    for item in lista_diccionarios:
        tupla = tuple(item[campo] for campo in campos_orden)
        tuplas.append(tupla)
    return tuplas

if __name__ == '__main__':
    # 1. Cargamos los datos desde el archivo JSON
    datos = cargar_datos_json('datos.json')
    
    if datos is None:
        exit(1)
    
    # 2. Instanciamos el objeto (creamos la base de datos virtual)
    db = BaseDatosFCTech('localhost', 'root', '', 'fctech_db')

    # 3. Llamamos al método para conectar
    db.conectar()

    if db.conexion and db.conexion.is_connected():
        print("⏳ Preparando lotes de datos desde JSON...\n")

        # Convertimos los diccionarios a tuplas en el orden correcto
        productos_orden = ['id_producto', 'marca', 'modelo', 'especificaciones', 'precio_unitario', 'stock_actual']
        clientes_orden = ['id_cliente', 'nombre', 'segmento_cliente', 'ciudad_envio']
        ventas_orden = ['id_venta', 'fecha_venta', 'id_producto', 'id_cliente', 'cantidad_vendida', 'precio_total']

        nuevos_productos = convertir_a_tuplas(datos['productos'], productos_orden)
        nuevos_clientes = convertir_a_tuplas(datos['clientes'], clientes_orden)
        nuevas_ventas = convertir_a_tuplas(datos['ventas'], ventas_orden)

        # 4. Usamos el método genérico para insertar los datos
        db.insertar_lote("dim_productos", "id_producto, marca, modelo, especificaciones, precio_unitario, stock_actual", nuevos_productos)
        db.insertar_lote("dim_clientes", "id_cliente, nombre, segmento_cliente, ciudad_envio", nuevos_clientes)
        db.insertar_lote("fact_ventas", "id_venta, fecha_venta, id_producto, id_cliente, cantidad_vendida, precio_total", nuevas_ventas)

        # 5. Desconectamos
        print("\n")
        db.desconectar()