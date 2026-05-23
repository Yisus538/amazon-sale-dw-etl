"""
load.py — Módulo de Carga
===========================
Responsabilidad: leer los parquet de 03_processed/ y cargarlos
en la base de datos PostgreSQL (DW final).

Soporta dos modos:
  - carga_inicial:      'replace' — borra y recrea las tablas
  - carga_incremental:  'append'  — agrega sin borrar (para actualizaciones)
"""

import os
import pandas as pd
import yaml
from sqlalchemy import create_engine, text
from dotenv import load_dotenv


def cargar_config(path_config: str = "config/settings.yaml") -> dict:
    with open(path_config, "r") as f:
        return yaml.safe_load(f)


def crear_engine(config: dict):
    """
    Crea el engine de SQLAlchemy leyendo credenciales desde .env
    Nunca hardcodear usuario/password en el código.
    """
    load_dotenv()

    host     = os.getenv("DB_HOST", "localhost")
    port     = os.getenv("DB_PORT", "5432")
    nombre   = os.getenv("DB_NAME", "amazon_dw")
    usuario  = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")

    url = f"postgresql+psycopg2://{usuario}:{password}@{host}:{port}/{nombre}"
    engine = create_engine(url, echo=False)

    # Verificar conexión
    try:
        with engine.connect() as con:
            con.execute(text("SELECT 1"))
        print(f"[LOAD] ✅ Conexión exitosa a {host}:{port}/{nombre}")
    except Exception as e:
        raise ConnectionError(f"[LOAD] ❌ No se pudo conectar a la DB: {e}")

    return engine


def cargar_tabla(
    df: pd.DataFrame,
    nombre_tabla: str,
    engine,
    schema: str = "amazon_dw",
    modo: str = "replace",
) -> None:
    """
    Carga un DataFrame en la base de datos.

    Args:
        df: DataFrame a cargar
        nombre_tabla: nombre de la tabla destino en el DW
        engine: SQLAlchemy engine
        schema: schema de PostgreSQL donde están las tablas
        modo: 'replace' para carga inicial | 'append' para incremental
    """
    df.to_sql(
        nombre_tabla,
        engine,
        schema=schema,
        if_exists=modo,
        index=False,
        method="multi",
        chunksize=1000,
    )
    print(f"[LOAD] ✅ Tabla '{schema}.{nombre_tabla}' cargada: {len(df):,} filas (modo: {modo})")


def verificar_carga(engine, config: dict) -> None:
    """Hace un COUNT(*) de cada tabla para verificar que la carga fue correcta."""
    print("\n[LOAD] Verificando conteo de filas:")
    schema = config["database"].get("schema", "amazon_dw")
    tablas = config["database"]["tablas"].values()

    with engine.connect() as con:
        for tabla in tablas:
            try:
                resultado = con.execute(text(f'SELECT COUNT(*) FROM {schema}."{tabla}"'))
                count = resultado.fetchone()[0]
                print(f"  → {tabla}: {count:,} filas")
            except Exception as e:
                print(f"  → {tabla}: ERROR — {e}")


def ejecutar_carga(
    tablas: dict,
    path_config: str = "config/settings.yaml",
    modo: str = "replace",
) -> None:
    """
    Función principal del paso de carga.

    Args:
        tablas: dict con los DataFrames de dimensiones y hechos
                {'dimTiempo': df, 'dimProducto': df, ...}
        path_config: ruta al archivo de configuración
        modo: 'replace' para carga inicial | 'append' para incremental
    """
    print("=" * 50)
    print("PASO 3: CARGA")
    print("=" * 50)
    print(f"[LOAD] Modo: {'CARGA INICIAL (replace)' if modo == 'replace' else 'ACTUALIZACIÓN (append)'}")

    config = cargar_config(path_config)
    engine = crear_engine(config)
    schema = config["database"].get("schema", "amazon_dw")

    # Orden de carga: primero dimensiones, luego hechos
    orden_carga = [
        "dimTiempo",
        "dimProducto",
        "dimGeografia",
        "dimCanal",
        "factVentas",
    ]

    for nombre in orden_carga:
        if nombre in tablas:
            cargar_tabla(tablas[nombre], nombre, engine, schema, modo)
        else:
            print(f"[LOAD] ⚠️  Tabla '{nombre}' no encontrada en el dict de entrada")

    verificar_carga(engine, config)

    print("\n[LOAD] ✅ Carga completada.")


def cargar_desde_processed(
    path_config: str = "config/settings.yaml",
    modo: str = "replace",
) -> None:
    """
    Alternativa: lee los parquet de 03_processed/ y los carga directamente.
    Útil para re-cargar sin re-correr la transformación.
    """
    config = cargar_config(path_config)
    processed_dir = config["paths"]["processed"]

    nombres = {
        "dimTiempo":    "dimTiempo.parquet",
        "dimProducto":  "dimProducto.parquet",
        "dimGeografia": "dimGeografia.parquet",
        "dimCanal":     "dimCanal.parquet",
        "factVentas":   "factVentas.parquet",
    }

    tablas = {}
    for nombre, archivo in nombres.items():
        ruta = os.path.join(processed_dir, archivo)
        tablas[nombre] = pd.read_parquet(ruta)
        print(f"[LOAD] 📂 Leído: {ruta} ({len(tablas[nombre]):,} filas)")

    ejecutar_carga(tablas, path_config, modo)
