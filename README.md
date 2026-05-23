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

### 1. Instalar dependencias

```bash
cd mi_proyecto_etl
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

### 4. Ejecutar los notebooks en orden

```bash
cd notebooks
jupyter lab
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
- **Período:** Abril 2022
- **Moneda:** INR (Rupia India)

---

## 👥 Grupo

| Nombre | Email |
|---|---|
| | |
| | |
| | |
| | |

**Materia:** Base de Datos II | **Año:** 2026
