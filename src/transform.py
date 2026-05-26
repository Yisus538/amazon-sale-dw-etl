"""
! transform.py — Módulo de Transformación
=========================================
Responsabilidad: limpiar, normalizar y construir las tablas de dimensiones
y la tabla de hechos siguiendo el Modelo Lógico del DW (Metodología HEFESTO).

Esquema resultante (Estrella):
  dimTiempo, dimProducto, dimGeografia, dimCanal  →  factVentas
"""

import os
import pandas as pd
import yaml


def cargar_config(path_config: str = "config/settings.yaml") -> dict:
    with open(path_config, "r") as f:
        return yaml.safe_load(f)


# ──────────────────────────────────────────────────────
# ! LIMPIEZA GENERAL
# ──────────────────────────────────────────────────────

def limpiar_dataframe(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Aplica limpieza general al DataFrame crudo:
      - Elimina columnas inútiles
      - Renombra columnas
      - Convierte tipos de datos
      - Rellena valores nulos según config/settings.yaml
    """
    print("[TRANSFORM] Iniciando limpieza...")
    df = df.copy()

    # 1. Eliminar columnas sin valor
    columnas_a_eliminar = ["index", "Unnamed: 22"]
    df.drop(columns=[c for c in columnas_a_eliminar if c in df.columns], inplace=True)

    # 2. Renombrar columnas para facilitar el trabajo
    df.rename(columns={
        "Order ID":          "order_id",
        "Date":              "fecha",
        "Status":            "status",
        "Fulfilment":        "tipo_fulfillment",
        "Sales Channel ":    "canal_ventas",    # tiene espacio al final en el CSV
        "Sales Channel":     "canal_ventas",    # por si no tiene espacio
        "ship-service-level":"nivel_servicio",
        "Style":             "estilo",
        "SKU":               "sku",
        "Category":          "categoria",
        "Size":              "talla",
        "ASIN":              "asin",
        "Courier Status":    "courier_status",
        "Qty":               "qty",
        "currency":          "moneda",
        "Amount":            "amount",
        "ship-city":         "ciudad",
        "ship-state":        "estado",
        "ship-postal-code":  "codigo_postal",
        "ship-country":      "pais",
        "promotion-ids":     "promociones",
        "B2B":               "es_b2b",
        "fulfilled-by":      "fulfilled_by",
    }, inplace=True)

    # 3. Convertir fecha
    fmt = config["source"]["date_format"]
    df["fecha"] = pd.to_datetime(df["fecha"], format=fmt, errors="coerce")

    # 4. Rellenar nulos con valores por defecto desde settings.yaml
    defaults = config["defaults"]
    df["courier_status"] = df["courier_status"].fillna(defaults["courier_status"])
    df["ciudad"]         = df["ciudad"].fillna(defaults["ciudad"])
    df["estado"]         = df["estado"].fillna(defaults["estado"])
    df["pais"]           = df["pais"].fillna(defaults["pais"])
    df["promociones"]    = df["promociones"].fillna(defaults["promociones"])
    df["fulfilled_by"]   = df["fulfilled_by"].fillna(defaults["fulfilled_by"])
    df["amount"]         = df["amount"].fillna(defaults["amount"])
    df["qty"]            = df["qty"].fillna(defaults["qty"])

    # 5. Normalizar strings
    df["ciudad"]   = df["ciudad"].str.strip().str.upper()
    df["estado"]   = df["estado"].str.strip().str.upper()
    df["categoria"] = df["categoria"].str.strip()
    df["talla"]    = df["talla"].str.strip()
    df["tipo_fulfillment"] = df["tipo_fulfillment"].str.strip()
    df["canal_ventas"]     = df["canal_ventas"].str.strip()
    df["nivel_servicio"]   = df["nivel_servicio"].str.strip()

    # 6. Tipos numéricos
    df["qty"]    = df["qty"].astype(int)
    df["amount"] = df["amount"].astype(float)

    print(f"[TRANSFORM] ✅ Limpieza completada. Shape: {df.shape}")
    print(f"[TRANSFORM]    Nulos restantes: {df.isnull().sum().sum()}")

    return df


# ──────────────────────────────────────────────────────
# !CONSTRUCCIÓN DE DIMENSIONES
# ──────────────────────────────────────────────────────

def construir_dim_tiempo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye dimTiempo a partir de las fechas únicas del dataset.
    Granularidad: diaria (Año + Mes + Día + Trimestre).
    """
    fechas = df["fecha"].dropna().unique()
    dim = pd.DataFrame({"fecha": fechas})
    dim["dia"]        = pd.to_datetime(dim["fecha"]).dt.day
    dim["mes"]        = pd.to_datetime(dim["fecha"]).dt.month
    dim["nombre_mes"] = pd.to_datetime(dim["fecha"]).dt.strftime("%B")
    dim["trimestre"]  = pd.to_datetime(dim["fecha"]).dt.quarter
    dim["anio"]       = pd.to_datetime(dim["fecha"]).dt.year
    dim = dim.sort_values("fecha").reset_index(drop=True)
    dim.insert(0, "idTiempo", dim.index + 1)

    print(f"[TRANSFORM] ✅ dimTiempo: {len(dim)} filas")
    return dim


def construir_dim_producto(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye dimProducto a partir de combinaciones únicas de
    categoria + talla + estilo.
    """
    dim = (
        df[["categoria", "talla", "estilo"]]
        .drop_duplicates()
        .sort_values(["categoria", "talla"])
        .reset_index(drop=True)
    )
    dim.insert(0, "idProducto", dim.index + 1)

    print(f"[TRANSFORM] ✅ dimProducto: {len(dim)} filas")
    return dim


def construir_dim_geografia(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye dimGeografia a partir de combinaciones únicas de
    ciudad + estado + país.
    """
    dim = (
        df[["ciudad", "estado", "pais"]]
        .drop_duplicates()
        .sort_values(["pais", "estado", "ciudad"])
        .reset_index(drop=True)
    )
    dim.insert(0, "idGeografia", dim.index + 1)

    print(f"[TRANSFORM] ✅ dimGeografia: {len(dim)} filas")
    return dim


def construir_dim_canal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye dimCanal a partir de combinaciones únicas de
    tipo_fulfillment + canal_ventas + nivel_servicio.
    """
    dim = (
        df[["tipo_fulfillment", "canal_ventas", "nivel_servicio"]]
        .drop_duplicates()
        .sort_values(["tipo_fulfillment", "nivel_servicio"])
        .reset_index(drop=True)
    )
    dim.insert(0, "idCanal", dim.index + 1)

    print(f"[TRANSFORM] ✅ dimCanal: {len(dim)} filas")
    return dim


# ──────────────────────────────────────────────────────
# CONSTRUCCIÓN DE LA TABLA DE HECHOS
# ──────────────────────────────────────────────────────

def construir_fact_ventas(
    df: pd.DataFrame,
    dim_tiempo: pd.DataFrame,
    dim_producto: pd.DataFrame,
    dim_geografia: pd.DataFrame,
    dim_canal: pd.DataFrame,
    config: dict,
) -> pd.DataFrame:
    """
    Construye factVentas haciendo merge con todas las dimensiones
    y agregando los indicadores según la metodología HEFESTO:

      - cantidad_vendida   = SUM(qty)    donde status != 'Cancelled'
      - monto_total        = SUM(amount) donde status != 'Cancelled'
      - cantidad_cancelada = SUM(qty)    donde status == 'Cancelled'
      - monto_cancelado    = SUM(amount) donde status == 'Cancelled'
    """
    print("[TRANSFORM] Construyendo factVentas...")

    estados_cancelados = config["estados_cancelados"]

    # Resolver FKs via merge
    df_fact = df.merge(
        dim_tiempo[["idTiempo", "fecha"]], on="fecha", how="left"
    )
    df_fact = df_fact.merge(
        dim_producto[["idProducto", "categoria", "talla", "estilo"]],
        on=["categoria", "talla", "estilo"], how="left"
    )
    df_fact = df_fact.merge(
        dim_geografia[["idGeografia", "ciudad", "estado", "pais"]],
        on=["ciudad", "estado", "pais"], how="left"
    )
    df_fact = df_fact.merge(
        dim_canal[["idCanal", "tipo_fulfillment", "canal_ventas", "nivel_servicio"]],
        on=["tipo_fulfillment", "canal_ventas", "nivel_servicio"], how="left"
    )

    # Flag de cancelación
    df_fact["es_cancelada"] = df_fact["status"].isin(estados_cancelados)

    claves = ["idProducto", "idGeografia", "idTiempo", "idCanal"]

    # Subconjuntos para vendidas y canceladas
    df_vendidas   = df_fact[~df_fact["es_cancelada"]]
    df_canceladas = df_fact[df_fact["es_cancelada"]]

    agg_vendidas = df_vendidas.groupby(claves).agg(
        cantidad_vendida=("qty", "sum"),
        monto_total=("amount", "sum"),
    ).reset_index()

    agg_canceladas = df_canceladas.groupby(claves).agg(
        cantidad_cancelada=("qty", "sum"),
        monto_cancelado=("amount", "sum"),
    ).reset_index()

    # Join de ambos agregados
    fact = pd.merge(agg_vendidas, agg_canceladas, on=claves, how="outer").fillna(0)

    # Tipos correctos
    for col in ["cantidad_vendida", "cantidad_cancelada"]:
        fact[col] = fact[col].astype(int)
    for col in ["monto_total", "monto_cancelado"]:
        fact[col] = fact[col].astype(float).round(2)

    print(f"[TRANSFORM] ✅ factVentas: {len(fact):,} filas")
    return fact


# ──────────────────────────────────────────────────────
#! GUARDADO EN PROCESSED
# ──────────────────────────────────────────────────────

def guardar_tablas_procesadas(
    dim_tiempo: pd.DataFrame,
    dim_producto: pd.DataFrame,
    dim_geografia: pd.DataFrame,
    dim_canal: pd.DataFrame,
    fact_ventas: pd.DataFrame,
    config: dict,
) -> None:
    """Guarda todas las tablas como parquet en 03_processed/."""
    processed_dir = config["paths"]["processed"]
    os.makedirs(processed_dir, exist_ok=True)

    tablas = {
        "dimTiempo.parquet":    dim_tiempo,
        "dimProducto.parquet":  dim_producto,
        "dimGeografia.parquet": dim_geografia,
        "dimCanal.parquet":     dim_canal,
        "factVentas.parquet":   fact_ventas,
    }

    for nombre, df in tablas.items():
        ruta = os.path.join(processed_dir, nombre)
        df.to_parquet(ruta, index=False)
        print(f"[TRANSFORM] ✅ Guardado: {ruta}")


# ──────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ──────────────────────────────────────────────────────

def ejecutar_transformacion(
    df_raw: pd.DataFrame,
    path_config: str = "config/settings.yaml",
) -> dict:
    """
    Función principal del paso de transformación.
    Recibe el DataFrame crudo y devuelve un dict con todas las tablas.
    """
    print("=" * 50)
    print("PASO 2: TRANSFORMACIÓN")
    print("=" * 50)

    config = cargar_config(path_config)

    # Limpiar
    df_clean = limpiar_dataframe(df_raw, config)

    # Construir dimensiones
    dim_tiempo    = construir_dim_tiempo(df_clean)
    dim_producto  = construir_dim_producto(df_clean)
    dim_geografia = construir_dim_geografia(df_clean)
    dim_canal     = construir_dim_canal(df_clean)

    # Construir tabla de hechos
    fact_ventas = construir_fact_ventas(
        df_clean, dim_tiempo, dim_producto, dim_geografia, dim_canal, config
    )

    # Guardar en processed/
    guardar_tablas_procesadas(
        dim_tiempo, dim_producto, dim_geografia, dim_canal, fact_ventas, config
    )

    print("\n[TRANSFORM] ✅ Transformación completa.")

    return {
        "dimTiempo":    dim_tiempo,
        "dimProducto":  dim_producto,
        "dimGeografia": dim_geografia,
        "dimCanal":     dim_canal,
        "factVentas":   fact_ventas,
    }
