# Proyecto PAD - Programación para Análisis de Datos

## 📌 Descripción del Proyecto

Este proyecto gestiona la base de datos de una empresa que vende computadores. El objetivo es analizar datos de productos, clientes y ventas para optimizar el inventario y mejorar la rotación de stock.

**Componentes principales:**
- `conexion_db.py`: Clase POO que gestiona la conexión a MySQL
- `insertar_datos.py`: Script que carga datos desde JSON e inserta en la BD
- `datos.json`: Archivo JSON con productos, clientes y ventas

---

## 📋 Requisitos Previos

Antes de ejecutar el proyecto, asegúrate de tener:

✅ **MySQL Server** instalado y ejecutándose  
✅ **Python 3.7+** en tu sistema  
✅ **Virtual environment** activado

---

## 🚀 Instalación y Configuración

### 1. Crear el Entorno Virtual (Primera vez)

```powershell
python -m venv .venv
```

### 2. Activar el Entorno Virtual

```powershell
.venv\Scripts\Activate.ps1
```

Si recibís un error de permisos, ejecuta primero:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### 3. Instalar Dependencias

```powershell
pip install mysql-connector-python
```

### 4. Configurar la Base de Datos MySQL

Ejecuta estos comandos en MySQL:

```sql
CREATE DATABASE fctech_db;
USE fctech_db;

CREATE TABLE dim_productos (
    id_producto INT PRIMARY KEY,
    marca VARCHAR(50),
    modelo VARCHAR(100),
    especificaciones TEXT,
    precio_unitario DECIMAL(12, 2),
    stock_actual INT
);

CREATE TABLE dim_clientes (
    id_cliente INT PRIMARY KEY,
    nombre VARCHAR(100),
    segmento_cliente VARCHAR(50),
    ciudad_envio VARCHAR(50)
);

CREATE TABLE fact_ventas (
    id_venta INT PRIMARY KEY,
    fecha_venta DATE,
    id_producto INT,
    id_cliente INT,
    cantidad_vendida INT,
    precio_total DECIMAL(12, 2),
    FOREIGN KEY (id_producto) REFERENCES dim_productos(id_producto),
    FOREIGN KEY (id_cliente) REFERENCES dim_clientes(id_cliente)
);
```

---

## 📊 Estructura de Archivos

```
proyecto_pad/
│
├── conexion_db.py          # Clase para gestionar la conexión a MySQL
├── insertar_datos.py       # Script principal que carga y inserta datos
├── datos.json              # Archivo JSON con los datos a insertar
└── README.md               # Este archivo
```

---

## 📝 Archivo datos.json

El archivo JSON contiene tres secciones principales:

### **productos**
Productos disponibles con especificaciones técnicas:
- `id_producto`: ID único del producto
- `marca`: Marca del computador
- `modelo`: Modelo específico
- `especificaciones`: Detalles técnicos
- `precio_unitario`: Precio en pesos
- `stock_actual`: Cantidad en inventario

### **clientes**
Información de clientes corporativos y usuarios finales:
- `id_cliente`: ID único del cliente
- `nombre`: Nombre o razón social
- `segmento_cliente`: Tipo de cliente (Corporativo/Usuario Final)
- `ciudad_envio`: Ciudad de destino

### **ventas**
Registro de transacciones de venta:
- `id_venta`: ID único de la venta
- `fecha_venta`: Fecha de la transacción
- `id_producto`: ID del producto vendido
- `id_cliente`: ID del cliente que compró
- `cantidad_vendida`: Número de unidades vendidas
- `precio_total`: Monto total de la venta

---

## ▶️ Ejecución del Proyecto

### Comando Principal:

```powershell
.venv\Scripts\python.exe insertar_datos.py
```

### ¿Qué hace el script?

1. **Carga** los datos desde `datos.json`
2. **Convierte** diccionarios JSON a tuplas
3. **Conecta** a la base de datos MySQL
4. **Inserta** los datos en 3 tablas:
   - `dim_productos`
   - `dim_clientes`
   - `fact_ventas`
5. **Desconecta** de la base de datos

### Salida Esperada:

```
✅ Datos cargados correctamente desde 'datos.json'.
✅ Conexión establecida correctamente.
⏳ Preparando lotes de datos desde JSON...
✅ 10 registros insertados en la tabla 'dim_productos'.
✅ 10 registros insertados en la tabla 'dim_clientes'.
✅ 10 registros insertados en la tabla 'fact_ventas'.
🔒 Conexión cerrada.
```

---

## 🛠️ Cómo Funciona Internamente

### conexion_db.py

```python
class BaseDatosFCTech:
    - conectar()      : Establece conexión a MySQL
    - desconectar()   : Cierra la conexión
    - insertar_lote() : Inserta múltiples registros de forma segura
```

**Características:**
- ✅ Uso de `executemany()` para mejor eficiencia
- ✅ Prevención de Inyección SQL
- ✅ Manejo de excepciones
- ✅ Commits y Rollbacks automáticos

### insertar_datos.py

**Funciones principales:**
- `cargar_datos_json()`: Lee el archivo JSON con validación
- `convertir_a_tuplas()`: Convierte diccionarios a tuplas ordenadas
- Flujo principal que orquesta la inserción


## 👨‍💻 Autor

Proyecto desarrollado como parte del curso de **Programación para Análisis de Datos** Fuentes Turizo Jhon Jairo

**Fecha**: Mayo 2026

