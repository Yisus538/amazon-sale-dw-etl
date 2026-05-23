"""
Script principal del ETL — Amazon Sale Report DW
Ejecutar: ~/.venvs/amazon_etl/bin/python run_etl.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from extract import ejecutar_extraccion
from transform import ejecutar_transformacion

CSV_PATH = "data/01_raw/Amazon_Sale_Report.csv"
CONFIG_PATH = "config/settings.yaml"

if __name__ == "__main__":
    df_raw = ejecutar_extraccion(CSV_PATH, CONFIG_PATH)
    tablas = ejecutar_transformacion(df_raw, CONFIG_PATH)

    print("\n" + "=" * 50)
    print("RESUMEN FINAL")
    print("=" * 50)
    for nombre, df in tablas.items():
        print(f"  {nombre:<14}: {len(df):>8,} filas")
    print("\nPaso 3 (carga en BD): ejecutar notebooks/03_load.ipynb")
