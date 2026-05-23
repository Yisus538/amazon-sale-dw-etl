# 📦 Amazon Sale Report — Data Warehouse ETL

Implementación del proceso ETL para construir el Data Warehouse de ventas Amazon India,
siguiendo la **Metodología HEFESTO v3** (Bernabeu & García Mattío).

---

## 🗂️ Estructura del proyecto

```
mi_proyecto_etl/
├── data/
│   ├── 01_raw/          # CSV original intocable
│   ├── 02_interim/      # Snapshots intermedios (.parquet)
│   └── 03_processed/    # Tablas del DW listas para carga (.parquet)
├── notebooks/
│   ├── 01_extract.ipynb    # Extracción y exploración
│   ├── 02_transform.ipynb  # Limpieza + construcción del esquema Estrella
│   └── 03_load.ipynb       # Carga en PostgreSQL + validación
├── src/
│   ├── extract.py       # Funciones de extracción
│   ├── transform.py     # Limpieza, dimensiones, tabla de hechos
│   └── load.py          # Conexión DB y carga
├── config/
│   └── settings.yaml    # Parámetros del proyecto
├── .env                 # Credenciales DB (NO subir a Git)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Cómo ejecutar el ETL

### 1. Crear entorno virtual e instalar dependencias

> **Nota:** si la ruta del proyecto contiene espacios (ej: `BD II/`), crear el venv fuera del proyecto:

```bash
# Con Python 3.12 (recomendado — 3.14 no tiene wheels para psycopg2)
python3.12 -m venv ~/.venvs/amazon_etl
source ~/.venvs/amazon_etl/bin/activate
pip install -r requirements.txt
```

### 2. Configurar credenciales

Editá el archivo `.env` con tus datos de conexión:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=amazon_dw
DB_USER=postgres
DB_PASSWORD=tu_password
```

### 3. Colocar el dataset

Copiar `Amazon_Sale_Report.csv` en `data/01_raw/`.

### 4. Ejecutar el ETL

**Opción A — Script Python directo:**
```bash
~/.venvs/amazon_etl/bin/python run_etl.py
```

**Opción B — Notebooks en orden:**
```bash
~/.venvs/amazon_etl/bin/jupyter lab
```
Correr en este orden:
1. `01_extract.ipynb`   → Extrae y guarda en raw/
2. `02_transform.ipynb` → Construye el esquema estrella
3. `03_load.ipynb`      → Carga en PostgreSQL

---

## 🏗️ Modelo del DW — Esquema Estrella

```
dimTiempo ──────────┐
                    │
dimProducto ────────┼──► factVentas
                    │
dimGeografia ───────┤
                    │
dimCanal ───────────┘
```

### Indicadores (factVentas)
| Campo | Descripción | Fórmula |
|---|---|---|
| cantidad_vendida | Unidades vendidas | SUM(qty) WHERE status != 'Cancelled' |
| monto_total | Monto total vendido | SUM(amount) WHERE status != 'Cancelled' |
| cantidad_cancelada | Unidades canceladas | SUM(qty) WHERE status == 'Cancelled' |
| monto_cancelado | Monto total cancelado | SUM(amount) WHERE status == 'Cancelled' |

---

## 📊 Dataset

- **Fuente:** Amazon Sale Report (Kaggle)
- **Registros:** ~128.975 órdenes
- **Período:** Abril–Junio 2022
- **Moneda:** INR (Rupia India)

---

## 👥 Grupo

| Nombre | Email |
|---|---|
| Martinez Jesus Manuel | jmartinez450@alumnos.iua.edu.ar |
| Bulatovich Juan Cruz | jbulatovich468@alumnos.iua.edu.ar |
| Correa Sofia Agostina | scorrea201@alumnos.iua.edu.ar |
| Bossio Francisco | fbossio156@alumnos.iua.edu.ar |

**Materia:** Base de Datos II | **Año:** 2026
