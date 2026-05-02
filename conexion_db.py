import mysql.connector
from mysql.connector import Error

class BaseDatosFCTech:
    """
    Clase para gestionar las operaciones de la base de datos de FC TECH.
    Sigue el paradigma de Programación Orientada a Objetos (POO).
    """

    def __init__(self, host, usuario, password, base_datos):
        # Constructor: Inicializa los atributos de la clase
        self.host = host
        self.usuario = usuario
        self.password = password
        self.base_datos = base_datos
        self.conexion = None
        self.cursor = None

    def conectar(self):
        """Método para establecer la conexión con MySQL."""
        try:
            self.conexion = mysql.connector.connect(
                host=self.host,
                user=self.usuario,
                password=self.password,
                database=self.base_datos
            )
            if self.conexion.is_connected():
                self.cursor = self.conexion.cursor()
                print("✅ Conexión establecida correctamente.")
        except Error as e:
            print(f"❌ Error al conectar a la base de datos: {e}")

    def desconectar(self):
        """Método para cerrar la conexión de forma segura."""
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()
            self.cursor.close()
            print("🔒 Conexión cerrada.")

    def insertar_lote(self, tabla, columnas, datos):
        """
        Método genérico para insertar múltiples filas en cualquier tabla.
        Usa 'executemany' para mayor eficiencia y seguridad (evita Inyección SQL).
        """
        try:
            # Generar los comodines (%s, %s, %s...) según la cantidad de columnas
            placeholders = ", ".join(["%s"] * len(columnas.split(",")))
            query = f"INSERT INTO {tabla} ({columnas}) VALUES ({placeholders})"
            
            self.cursor.executemany(query, datos)
            self.conexion.commit()
            print(f"✅ {self.cursor.rowcount} registros insertados en la tabla '{tabla}'.")
        except Error as e:
            print(f"❌ Error al insertar en '{tabla}': {e}")
            self.conexion.rollback() # Deshace cambios si hay error