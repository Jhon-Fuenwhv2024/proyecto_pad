from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
from conexion_db import BaseDatosFCTech

class ScraperCompetencia:
    """
    Clase encargada de extraer datos de precios del mercado para FC TECH.
    Aplica técnicas de Web Scraping con Playwright (ejecuta JavaScript).
    """
    def __init__(self, base_url):
        self.base_url = base_url

    def buscar_producto(self, termino_busqueda):
        """
        Fase 3: Preparación de Datos (Extracción).
        Busca un término y extrae título y precio de los primeros resultados.
        Usa Playwright para renderizar JavaScript (VTEX).
        """
        # Construir URL de búsqueda para VTEX
        url_busqueda = f"{self.base_url}?busca={termino_busqueda.replace(' ', '+')}"
        print(f"\n🔍 Iniciando escaneo en: {url_busqueda}")

        try:
            with sync_playwright() as p:
                # Lanzar navegador en modo headless (sin interfaz visual)
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Navegar a la URL
                print("⏳ Cargando página (ejecutando JavaScript)...")
                page.goto(url_busqueda, wait_until="networkidle", timeout=30000)
                
                # Esperar a que aparezcan los productos o timeout
                try:
                    page.wait_for_selector('[class*="product"]', timeout=5000)
                except:
                    print("⚠️ Esperando alternativas de selectores...")
                
                # Extraer HTML renderizado
                html_renderizado = page.content()
                browser.close()
            
            # Parsear HTML con BeautifulSoup
            soup = BeautifulSoup(html_renderizado, 'html.parser')
            datos_extraidos = []
            
            # Buscar productos - VTEX usa estructura común
            # Intentar múltiples selectores posibles
            selectores = [
                '[class*="productCardContainer"]',
                '[class*="product-card"]',
                'div[data-testid*="product"]',
                'article[class*="product"]'
            ]
            
            resultados = []
            for selector in selectores:
                resultados = soup.select(selector, limit=10)
                if resultados:
                    print(f"✅ Productos encontrados con selector: {selector}")
                    break
            
            if not resultados:
                # Último intento: buscar cualquier div con precio
                elementos_precio = soup.find_all(['div', 'article'], limit=20)
                print(f"⚠️ No se encontraron productos con selectores especializados.")
                print(f"   Analizando {len(elementos_precio)} elementos...")
                return []

            for item in resultados:
                try:
                    # Extraer título
                    titulo_elem = item.find(['h1', 'h2', 'h3', 'span'], class_=lambda x: x and ('title' in x.lower() or 'name' in x.lower()))
                    titulo = titulo_elem.text.strip() if titulo_elem else "Desconocido"
                    
                    # Extraer precio - buscar números con símbolos de moneda
                    precio_elem = item.find(['span', 'div'], class_=lambda x: x and ('price' in x.lower() or 'valor' in x.lower()))
                    precio_str = precio_elem.text.strip() if precio_elem else "0"
                    
                    # Limpiar precio (remover símbolos de moneda, espacios, etc.)
                    precio_numerico = ''.join(c for c in precio_str if c.isdigit() or c in '.,')
                    try:
                        precio_limpio = float(precio_numerico.replace('.', '').replace(',', ''))
                    except (ValueError, AttributeError):
                        precio_limpio = 0.0
                    
                    # Solo agregar si tenemos datos válidos
                    if titulo and titulo != "Desconocido" and precio_limpio > 0:
                        marca_inferida = titulo.split()[0] if titulo else "Genérica"
                        modelo_truncado = titulo[:50]
                        
                        tupla_producto = (
                            None,
                            marca_inferida,
                            modelo_truncado,
                            "Ref. Competencia (Web Scraping)",
                            precio_limpio,
                            0
                        )
                        datos_extraidos.append(tupla_producto)
                
                except Exception as e:
                    print(f"⚠️ Error procesando producto: {e}")
                    continue
                
            print(f"✅ Se extrajeron {len(datos_extraidos)} registros exitosamente.")
            return datos_extraidos

        except Exception as e:
             print(f"❌ Error en Playwright: {e}")
             import traceback
             traceback.print_exc()
             return []

# --- FLUJO PRINCIPAL ---
if __name__ == "__main__":
    # URL Base del e-commerce (fctechstore - sin parámetros de tracking)
    URL_OBJETIVO = "https://www.fctechstore.co/"
    
    # 1. Instanciar Scraper
    scraper = ScraperCompetencia(URL_OBJETIVO)
    
    # Pausa ética (Respeto al robots.txt)
    time.sleep(2)
    
    # 2. Ejecutar búsqueda de un equipo de alta rotación para FC TECH
    datos = scraper.buscar_producto("portatil dell latitude reacondicionado")
    
    # 3. Mostrar datos extraídos antes de insertar (Validación)
    if datos:
        print("\n📊 Muestra de datos limpios listos para Base de Datos:")
        for idx, d in enumerate(datos[:3]): # Mostrar solo los 3 primeros
            print(f"  {idx+1}. Marca: {d[1]} | Modelo: {d[2]} | Precio: ${d[4]}")
            
        print("\n⏳ Iniciando proceso de carga a MySQL...")
        
        # 4. Integración Fase 4 (Carga a Base de Datos)
        db = BaseDatosFCTech('localhost', 'root', '', 'fctech_db')
        db.conectar()
        
        if db.conexion and db.conexion.is_connected():
            # Definir columnas de destino
            columnas_destino = "id_producto, marca, modelo, especificaciones, precio_unitario, stock_actual"
            
            # Ejecutar inserción en lote (Batch Insert)
            db.insertar_lote("dim_productos", columnas_destino, datos)
            
            db.desconectar()
    else:
        print("\n❌ No se obtuvieron datos para insertar.")