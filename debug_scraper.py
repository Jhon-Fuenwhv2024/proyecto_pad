import requests
from bs4 import BeautifulSoup

# Obtener la página y analizar su estructura
url = "https://www.fctechstore.co/?srsltid=AfmBOoq9oRPHgNa4YiXqFP70FLT1MsfB83iqnt4WSpmnPdxRYD8tk8Bo"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9"
}

try:
    respuesta = requests.get(url, headers=headers, timeout=15)
    respuesta.raise_for_status()
    
    soup = BeautifulSoup(respuesta.text, 'html.parser')
    
    # Guardar HTML para inspeccionar manualmente
    with open('page_debug.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    
    print("✅ HTML guardado en 'page_debug.html'")
    
    # Buscar diferentes patrones posibles
    print("\n🔍 Buscando elementos de productos:\n")
    
    # Patrón 1: Divs con clase producto
    productos_div = soup.find_all('div', class_=lambda x: x and 'product' in x.lower())
    print(f"📦 Divs con 'product' en clase: {len(productos_div)}")
    
    # Patrón 2: Links que podrían ser productos
    links = soup.find_all('a', href=True)
    print(f"🔗 Enlaces totales: {len(links)}")
    
    # Patrón 3: Elementos con "precio" en su contenido
    todos_elementos = soup.find_all(['div', 'span', 'p'])
    elementos_precio = [el for el in todos_elementos if 'precio' in el.get_text().lower()[:50]]
    print(f"💰 Elementos con 'precio': {len(elementos_precio)}")
    
    # Mostrar estructura de contenedores principales
    print("\n🏗️ Estructura de contenedores principales:\n")
    main_containers = soup.find_all(['main', 'article', 'section', 'div'], limit=10)
    for i, container in enumerate(main_containers[:5]):
        classes = container.get('class', [])
        print(f"{i+1}. {container.name} - Clases: {classes}")
    
    print("\n💡 Revisa 'page_debug.html' para ver la estructura completa del HTML")
    
except Exception as e:
    print(f"❌ Error: {e}")
