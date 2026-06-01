"""
📊 ETL (Extract, Transform, Load) para FC TECH
================================================
Orquesta todo el proceso de carga de datos:
- EXTRACT: Extrae datos del web scraper o archivos JSON
- TRANSFORM: Limpia, valida y normaliza los datos
- LOAD: Carga los datos en la base de datos MySQL

Autor: FC TECH Data Pipeline
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from conexion_db import BaseDatosFCTech
from web_scrapper import ScraperCompetencia

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# CLASE ETL
# ============================================================================

class ETLPipeline:
    """
    Clase principal que orquesta el proceso ETL completo.
    """
    
    def __init__(self, host: str, usuario: str, password: str, base_datos: str):
        """
        Inicializa el pipeline ETL.
        
        Args:
            host: Host del servidor MySQL
            usuario: Usuario de MySQL
            password: Contraseña de MySQL
            base_datos: Nombre de la base de datos
        """
        self.db = BaseDatosFCTech(host, usuario, password, base_datos)
        self.datos_extraidos = {
            'productos': [],
            'clientes': [],
            'ventas': []
        }
        self.datos_transformados = {
            'productos': [],
            'clientes': [],
            'ventas': []
        }
        logger.info("🚀 Pipeline ETL inicializado")
    
    # ========================================================================
    # FASE 1: EXTRACT (Extracción)
    # ========================================================================
    
    def extraer_desde_json(self, ruta_archivo: str) -> bool:
        """
        Extrae datos desde un archivo JSON.
        
        Args:
            ruta_archivo: Ruta al archivo JSON
            
        Returns:
            True si la extracción fue exitosa, False en caso contrario
        """
        try:
            logger.info(f"📂 Leyendo archivo JSON: {ruta_archivo}")
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                datos = json.load(archivo)
            
            self.datos_extraidos['productos'] = datos.get('productos', [])
            self.datos_extraidos['clientes'] = datos.get('clientes', [])
            self.datos_extraidos['ventas'] = datos.get('ventas', [])
            
            logger.info(f"✅ Extracción JSON exitosa:")
            logger.info(f"   - Productos: {len(self.datos_extraidos['productos'])}")
            logger.info(f"   - Clientes: {len(self.datos_extraidos['clientes'])}")
            logger.info(f"   - Ventas: {len(self.datos_extraidos['ventas'])}")
            return True
            
        except FileNotFoundError:
            logger.error(f"❌ Archivo no encontrado: {ruta_archivo}")
            return False
        except json.JSONDecodeError:
            logger.error(f"❌ Error al decodificar JSON en: {ruta_archivo}")
            return False
        except Exception as e:
            logger.error(f"❌ Error durante extracción JSON: {e}")
            return False
    
    def extraer_desde_scraper(self, base_url: str, terminos: List[str]) -> bool:
        """
        Extrae datos desde el web scraper.
        
        Args:
            base_url: URL base del sitio a scrapear
            terminos: Lista de términos a buscar
            
        Returns:
            True si la extracción fue exitosa, False en caso contrario
        """
        try:
            logger.info(f"🌐 Iniciando web scraping en: {base_url}")
            scraper = ScraperCompetencia(base_url)
            productos_scraped = []
            
            for termino in terminos:
                logger.info(f"   🔍 Buscando: {termino}")
                resultados = scraper.buscar_producto(termino)
                productos_scraped.extend(resultados)
            
            self.datos_extraidos['productos'] = productos_scraped
            logger.info(f"✅ Extracción por scraper exitosa: {len(productos_scraped)} productos")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error durante scraping: {e}")
            return False
    
    # ========================================================================
    # FASE 2: TRANSFORM (Transformación)
    # ========================================================================
    
    def validar_producto(self, producto: Dict) -> Tuple[bool, str]:
        """
        Valida que un producto tenga los campos requeridos.
        
        Args:
            producto: Diccionario con datos del producto
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        campos_requeridos = ['id_producto', 'marca', 'modelo', 'precio_unitario']
        
        for campo in campos_requeridos:
            if campo not in producto:
                return False, f"Falta campo requerido: {campo}"
        
        # Validar que el precio sea un número positivo
        try:
            precio = float(producto.get('precio_unitario', 0))
            if precio <= 0:
                return False, f"Precio debe ser positivo, se recibió: {precio}"
        except (ValueError, TypeError):
            return False, f"Precio no es un número válido: {producto.get('precio_unitario')}"
        
        # Validar que el ID sea un número
        try:
            int(producto.get('id_producto'))
        except (ValueError, TypeError):
            return False, f"ID de producto no es un número válido"
        
        return True, ""
    
    def validar_cliente(self, cliente: Dict) -> Tuple[bool, str]:
        """
        Valida que un cliente tenga los campos requeridos.
        
        Args:
            cliente: Diccionario con datos del cliente
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        campos_requeridos = ['id_cliente', 'nombre']
        
        for campo in campos_requeridos:
            if campo not in cliente:
                return False, f"Falta campo requerido: {campo}"
        
        return True, ""
    
    def validar_venta(self, venta: Dict) -> Tuple[bool, str]:
        """
        Valida que una venta tenga los campos requeridos.
        
        Args:
            venta: Diccionario con datos de la venta
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        campos_requeridos = ['id_venta', 'id_producto', 'id_cliente', 'cantidad_vendida']
        
        for campo in campos_requeridos:
            if campo not in venta:
                return False, f"Falta campo requerido: {campo}"
        
        try:
            cantidad = int(venta.get('cantidad_vendida', 0))
            if cantidad <= 0:
                return False, f"Cantidad debe ser positiva"
        except (ValueError, TypeError):
            return False, f"Cantidad no es un número válido"
        
        return True, ""
    
    def transformar_datos(self) -> bool:
        """
        Ejecuta todas las transformaciones de datos.
        
        Returns:
            True si la transformación fue exitosa, False en caso contrario
        """
        logger.info("🔄 Iniciando transformación de datos...")
        
        registros_rechazados = {
            'productos': 0,
            'clientes': 0,
            'ventas': 0
        }
        
        # Transformar productos
        logger.info("   Transformando productos...")
        for producto in self.datos_extraidos['productos']:
            es_valido, mensaje = self.validar_producto(producto)
            if es_valido:
                # Asegurar que los campos numéricos sean del tipo correcto
                producto_limpio = {
                    'id_producto': int(producto['id_producto']),
                    'marca': str(producto['marca']).strip(),
                    'modelo': str(producto['modelo']).strip(),
                    'especificaciones': str(producto.get('especificaciones', '')).strip(),
                    'precio_unitario': float(producto['precio_unitario']),
                    'stock_actual': int(producto.get('stock_actual', 0))
                }
                self.datos_transformados['productos'].append(producto_limpio)
            else:
                logger.warning(f"   ⚠️ Producto rechazado: {mensaje}")
                registros_rechazados['productos'] += 1
        
        # Transformar clientes
        logger.info("   Transformando clientes...")
        for cliente in self.datos_extraidos['clientes']:
            es_valido, mensaje = self.validar_cliente(cliente)
            if es_valido:
                cliente_limpio = {
                    'id_cliente': int(cliente['id_cliente']),
                    'nombre': str(cliente['nombre']).strip(),
                    'segmento_cliente': str(cliente.get('segmento_cliente', '')).strip(),
                    'ciudad_envio': str(cliente.get('ciudad_envio', '')).strip()
                }
                self.datos_transformados['clientes'].append(cliente_limpio)
            else:
                logger.warning(f"   ⚠️ Cliente rechazado: {mensaje}")
                registros_rechazados['clientes'] += 1
        
        # Transformar ventas
        logger.info("   Transformando ventas...")
        for venta in self.datos_extraidos['ventas']:
            es_valido, mensaje = self.validar_venta(venta)
            if es_valido:
                venta_limpia = {
                    'id_venta': int(venta['id_venta']),
                    'fecha_venta': str(venta.get('fecha_venta', datetime.now().strftime('%Y-%m-%d'))),
                    'id_producto': int(venta['id_producto']),
                    'id_cliente': int(venta['id_cliente']),
                    'cantidad_vendida': int(venta['cantidad_vendida']),
                    'precio_total': float(venta.get('precio_total', 0))
                }
                self.datos_transformados['ventas'].append(venta_limpia)
            else:
                logger.warning(f"   ⚠️ Venta rechazada: {mensaje}")
                registros_rechazados['ventas'] += 1
        
        logger.info(f"✅ Transformación completada:")
        logger.info(f"   - Productos: {len(self.datos_transformados['productos'])} (rechazados: {registros_rechazados['productos']})")
        logger.info(f"   - Clientes: {len(self.datos_transformados['clientes'])} (rechazados: {registros_rechazados['clientes']})")
        logger.info(f"   - Ventas: {len(self.datos_transformados['ventas'])} (rechazadas: {registros_rechazados['ventas']})")
        
        return True
    
    # ========================================================================
    # FASE 3: LOAD (Carga)
    # ========================================================================
    
    def convertir_a_tuplas(self, lista_diccionarios: List[Dict], campos_orden: List[str]) -> List[Tuple]:
        """
        Convierte una lista de diccionarios a tuplas en un orden específico.
        
        Args:
            lista_diccionarios: Lista de diccionarios
            campos_orden: Orden de los campos
            
        Returns:
            Lista de tuplas
        """
        tuplas = []
        for item in lista_diccionarios:
            tupla = tuple(item.get(campo) for campo in campos_orden)
            tuplas.append(tupla)
        return tuplas
    
    def cargar_datos(self) -> bool:
        """
        Carga los datos transformados a la base de datos.
        
        Returns:
            True si la carga fue exitosa, False en caso contrario
        """
        try:
            logger.info("💾 Iniciando carga de datos a la base de datos...")
            
            # Conectar a la BD
            self.db.conectar()
            
            if not self.db.conexion or not self.db.conexion.is_connected():
                logger.error("❌ No se pudo establecer conexión con la base de datos")
                return False
            
            # Definir el orden de los campos
            campos_productos = ['id_producto', 'marca', 'modelo', 'especificaciones', 'precio_unitario', 'stock_actual']
            campos_clientes = ['id_cliente', 'nombre', 'segmento_cliente', 'ciudad_envio']
            campos_ventas = ['id_venta', 'fecha_venta', 'id_producto', 'id_cliente', 'cantidad_vendida', 'precio_total']
            
            # Convertir a tuplas
            tuplas_productos = self.convertir_a_tuplas(self.datos_transformados['productos'], campos_productos)
            tuplas_clientes = self.convertir_a_tuplas(self.datos_transformados['clientes'], campos_clientes)
            tuplas_ventas = self.convertir_a_tuplas(self.datos_transformados['ventas'], campos_ventas)
            
            # Insertar datos
            if tuplas_productos:
                logger.info(f"   📦 Insertando {len(tuplas_productos)} productos...")
                self.db.insertar_lote(
                    "dim_productos",
                    "id_producto, marca, modelo, especificaciones, precio_unitario, stock_actual",
                    tuplas_productos
                )
            
            if tuplas_clientes:
                logger.info(f"   👥 Insertando {len(tuplas_clientes)} clientes...")
                self.db.insertar_lote(
                    "dim_clientes",
                    "id_cliente, nombre, segmento_cliente, ciudad_envio",
                    tuplas_clientes
                )
            
            if tuplas_ventas:
                logger.info(f"   💰 Insertando {len(tuplas_ventas)} ventas...")
                self.db.insertar_lote(
                    "fact_ventas",
                    "id_venta, fecha_venta, id_producto, id_cliente, cantidad_vendida, precio_total",
                    tuplas_ventas
                )
            
            logger.info("✅ Carga de datos completada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error durante la carga de datos: {e}")
            return False
        finally:
            self.db.desconectar()
    
    # ========================================================================
    # EJECUTAR PIPELINE COMPLETO
    # ========================================================================
    
    def ejecutar(self, ruta_json: str) -> bool:
        """
        Ejecuta el pipeline ETL completo: Extract → Transform → Load
        
        Args:
            ruta_json: Ruta al archivo JSON de datos
            
        Returns:
            True si el pipeline fue exitoso, False en caso contrario
        """
        logger.info("=" * 70)
        logger.info("🚀 INICIANDO PIPELINE ETL FC TECH")
        logger.info("=" * 70)
        
        # Fase 1: Extract
        if not self.extraer_desde_json(ruta_json):
            logger.error("❌ Pipeline falló en fase EXTRACT")
            return False
        
        # Fase 2: Transform
        if not self.transformar_datos():
            logger.error("❌ Pipeline falló en fase TRANSFORM")
            return False
        
        # Fase 3: Load
        if not self.cargar_datos():
            logger.error("❌ Pipeline falló en fase LOAD")
            return False
        
        logger.info("=" * 70)
        logger.info("✅ PIPELINE ETL COMPLETADO EXITOSAMENTE")
        logger.info("=" * 70)
        return True
    
    def ejecutar_con_scraper(self, base_url: str, terminos: List[str]) -> bool:
        """
        Ejecuta el pipeline ETL usando datos del web scraper.
        
        Args:
            base_url: URL base del sitio a scrapear
            terminos: Lista de términos a buscar
            
        Returns:
            True si el pipeline fue exitoso, False en caso contrario
        """
        logger.info("=" * 70)
        logger.info("🚀 INICIANDO PIPELINE ETL CON WEB SCRAPER")
        logger.info("=" * 70)
        
        # Fase 1: Extract (desde scraper)
        if not self.extraer_desde_scraper(base_url, terminos):
            logger.error("❌ Pipeline falló en fase EXTRACT (scraper)")
            return False
        
        # Fase 2: Transform
        if not self.transformar_datos():
            logger.error("❌ Pipeline falló en fase TRANSFORM")
            return False
        
        # Fase 3: Load
        if not self.cargar_datos():
            logger.error("❌ Pipeline falló en fase LOAD")
            return False
        
        logger.info("=" * 70)
        logger.info("✅ PIPELINE ETL CON SCRAPER COMPLETADO EXITOSAMENTE")
        logger.info("=" * 70)
        return True


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == '__main__':
    # Configuración de la conexión a la BD
    CONFIG_BD = {
        'host': 'localhost',
        'usuario': 'root',
        'password': '',
        'base_datos': 'fctech_db'
    }
    
    # Crear instancia del pipeline
    pipeline = ETLPipeline(**CONFIG_BD)
    
    # Opción 1: Ejecutar ETL desde JSON
    print("\n" + "=" * 70)
    print("1️⃣  EJECUTANDO ETL DESDE JSON")
    print("=" * 70)
    exito = pipeline.ejecutar('datos.json')
    
    if exito:
        print("\n✅ Pipeline completado correctamente")
    else:
        print("\n❌ Pipeline finalizó con errores. Revisa 'etl_pipeline.log'")
    
    # Nota: Para usar el scraper, descomenta el código de abajo
    # print("\n" + "=" * 70)
    # print("2️⃣  EJECUTANDO ETL CON WEB SCRAPER")
    # print("=" * 70)
    # pipeline2 = ETLPipeline(**CONFIG_BD)
    # base_url = "https://ejemplo.com"  # Cambiar con URL real
    # terminos = ["laptop", "computadora", "notebook"]
    # exito = pipeline2.ejecutar_con_scraper(base_url, terminos)
