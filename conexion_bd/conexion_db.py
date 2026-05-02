import mysql.connector
from mysql.connector import Error

def conectar_y_cargar_datos():
    try:
        # 1. Configuración de la conexión a MySQL (phpMyAdmin)
        # Nota: Ajusta el usuario y contraseña según tu configuración local.
        # Por defecto en XAMPP, el usuario es 'root' y la contraseña es vacía ''.
        conexion = mysql.connector.connect(
            host='localhost',
            database='fctech_db', # Asegúrate de crear esta BD en phpMyAdmin primero
            user='root',
            password=''
        )

        if conexion.is_connected():
            print("✅ Conexión exitosa a la base de datos MySQL (phpMyAdmin)\n")
            cursor = conexion.cursor()

            # --- PREPARACIÓN: Eliminar tablas si ya existen para evitar errores al ejecutar varias veces ---
            cursor.execute("DROP TABLE IF EXISTS fact_ventas;")
            cursor.execute("DROP TABLE IF EXISTS dim_clientes;")
            cursor.execute("DROP TABLE IF EXISTS dim_productos;")

            # --- DDL: CREACIÓN DE TABLAS ---
            print("⏳ Creando tablas...")
            tabla_productos = """
            CREATE TABLE dim_productos (
                id_producto INT PRIMARY KEY,
                marca VARCHAR(50) NOT NULL,
                modelo VARCHAR(100) NOT NULL,
                especificaciones VARCHAR(255),
                precio_unitario DECIMAL(10, 2) NOT NULL,
                stock_actual INT DEFAULT 0
            );
            """
            
            tabla_clientes = """
            CREATE TABLE dim_clientes (
                id_cliente INT PRIMARY KEY,
                nombre VARCHAR(150) NOT NULL,
                segmento_cliente VARCHAR(50),
                ciudad_envio VARCHAR(100)
            );
            """
            
            tabla_ventas = """
            CREATE TABLE fact_ventas (
                id_venta INT PRIMARY KEY,
                fecha_venta DATE NOT NULL,
                id_producto INT NOT NULL,
                id_cliente INT NOT NULL,
                cantidad_vendida INT NOT NULL,
                precio_total DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (id_producto) REFERENCES dim_productos(id_producto),
                FOREIGN KEY (id_cliente) REFERENCES dim_clientes(id_cliente)
            );
            """
            
            cursor.execute(tabla_productos)
            cursor.execute(tabla_clientes)
            cursor.execute(tabla_ventas)
            print("✅ Tablas creadas correctamente.\n")

            # --- DML: INSERCIÓN DE DATOS DE PRUEBA ---
            print("⏳ Insertando datos de prueba...")
            
            insertar_productos = """
            INSERT INTO dim_productos (id_producto, marca, modelo, especificaciones, precio_unitario, stock_actual) VALUES 
            (101, 'Dell', 'OptiPlex 7090 Micro', 'Intel Core i5 10th Gen, 8GB RAM, 256GB SSD', 1199900.00, 15),
            (102, 'Dell', 'OptiPlex 7000 Micro', 'Intel Core i5 12th Gen, 8GB RAM, 512GB SSD', 1469900.00, 8),
            (103, 'HP', 'EliteDesk 800 G4', 'Intel Core i7 8th Gen, 16GB RAM, 512GB SSD', 1350000.00, 20),
            (104, 'Lenovo', 'ThinkPad T490', 'Intel Core i5 8th Gen, 16GB RAM, 256GB SSD', 1250000.00, 5);
            """
            
            insertar_clientes = """
            INSERT INTO dim_clientes (id_cliente, nombre, segmento_cliente, ciudad_envio) VALUES 
            (201, 'Soluciones Tecnológicas SAS', 'Corporativo', 'Bogotá'),
            (202, 'María Fernanda López', 'Usuario Final', 'Medellín'),
            (203, 'Consultores y Asociados Ltda.', 'Corporativo', 'Cali');
            """
            
            insertar_ventas = """
            INSERT INTO fact_ventas (id_venta, fecha_venta, id_producto, id_cliente, cantidad_vendida, precio_total) VALUES 
            (3001, '2023-10-15', 101, 201, 5, 5999500.00),
            (3002, '2023-10-16', 104, 202, 1, 1250000.00),
            (3003, '2023-10-20', 102, 203, 2, 2939800.00),
            (3004, '2023-10-25', 103, 201, 10, 13500000.00);
            """
            
            cursor.execute(insertar_productos)
            cursor.execute(insertar_clientes)
            cursor.execute(insertar_ventas)
            
            # Es MUY importante hacer commit para que los cambios se guarden en phpMyAdmin
            conexion.commit() 
            print("✅ Datos insertados correctamente.\n")

            # --- VALIDACIÓN: CONSULTA DE PRUEBA ---
            print("📊 Realizando consulta de validación (Cruce de Ventas y Productos):")
            consulta_prueba = """
            SELECT v.fecha_venta, p.marca, p.modelo, v.cantidad_vendida, c.nombre
            FROM fact_ventas v
            JOIN dim_productos p ON v.id_producto = p.id_producto
            JOIN dim_clientes c ON v.id_cliente = c.id_cliente;
            """
            cursor.execute(consulta_prueba)
            resultados = cursor.fetchall()
            
            for fila in resultados:
                print(f"Fecha: {fila[0]} | Equipo: {fila[1]} {fila[2]} | Cantidad: {fila[3]} | Cliente: {fila[4]}")

    except Error as e:
        print(f"❌ Error al conectar o ejecutar en MySQL: {e}")
        
    finally:
        # Asegurarse de cerrar la conexión siempre, incluso si hay un error
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()
            print("\n🔒 Conexión a MySQL cerrada.")

# Punto de entrada del script
if __name__ == '__main__':
    conectar_y_cargar_datos()