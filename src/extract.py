"""
extract.py — Módulo de Extracción
===================================
Responsabilidad: leer el CSV original y guardarlo intacto en 01_raw/
La idea es que raw sea siempre una copia exacta de la fuente.
"""

import os
import shutil
import pandas as pd
import yaml


def cargar_config(path_config: str = "config/settings.yaml") -> dict:
    """Lee el archivo de configuración YAML."""
    with open(path_config, "r") as f:
        return yaml.safe_load(f)


def extraer_csv(path_origen: str, config: dict) -> pd.DataFrame:
    """
    Lee el CSV fuente y lo copia sin modificaciones a la carpeta 01_raw/.

    Args:
        path_origen: ruta completa al CSV original (ej: 'Amazon_Sale_Report.csv')
        config: diccionario con la configuración del proyecto

    Returns:
        DataFrame con los datos crudos
    """
    raw_dir = config["paths"]["raw"]
    os.makedirs(raw_dir, exist_ok=True)

    # Copiar el CSV original a 01_raw/ intacto
    nombre_archivo = config["source"]["filename"]
    destino_raw = os.path.join(raw_dir, nombre_archivo)

    if path_origen != destino_raw:
        shutil.copy2(path_origen, destino_raw)
        print(f"[EXTRACT] ✅ Archivo copiado a: {destino_raw}")
    else:
        print(f"[EXTRACT] ℹ️  El archivo ya está en raw/: {destino_raw}")

    # Leer el CSV
    df = pd.read_csv(destino_raw, low_memory=False)
    print(f"[EXTRACT] ✅ CSV leído: {len(df):,} filas | {len(df.columns)} columnas")

    return df


def guardar_interim(df: pd.DataFrame, config: dict, nombre: str = "01_raw_cargado.parquet") -> str:
    """
    Guarda el DataFrame crudo como parquet en 02_interim/.
    Parquet es más eficiente que CSV para pasos intermedios.

    Args:
        df: DataFrame con los datos crudos
        config: configuración del proyecto
        nombre: nombre del archivo de salida

    Returns:
        ruta del archivo guardado
    """
    interim_dir = config["paths"]["interim"]
    os.makedirs(interim_dir, exist_ok=True)

    ruta_salida = os.path.join(interim_dir, nombre)
    df.to_parquet(ruta_salida, index=False)
    print(f"[EXTRACT] ✅ Guardado en interim: {ruta_salida}")

    return ruta_salida


def ejecutar_extraccion(path_csv: str, path_config: str = "config/settings.yaml") -> pd.DataFrame:
    """
    Función principal del paso de extracción.
    Llama a extraer_csv() y guarda el resultado en interim/.

    Args:
        path_csv: ruta al CSV fuente
        path_config: ruta al archivo de configuración

    Returns:
        DataFrame con los datos crudos
    """
    print("=" * 50)
    print("PASO 1: EXTRACCIÓN")
    print("=" * 50)

    config = cargar_config(path_config)
    df_raw = extraer_csv(path_csv, config)
    guardar_interim(df_raw, config)

    print(f"\n[EXTRACT] Columnas: {list(df_raw.columns)}")
    print(f"[EXTRACT] Tipos:\n{df_raw.dtypes}")
    print(f"\n[EXTRACT] Nulos por columna:\n{df_raw.isnull().sum()}")

    return df_raw
