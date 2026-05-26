"""
generar_der.py — Genera el Diagrama Entidad-Relación del DW Amazon India
Produce un PNG con el esquema estrella (HEFESTO v3).
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ── Colores ────────────────────────────────────────────────────────────────
COLOR_DIM   = "#2563EB"   # Azul para dimensiones
COLOR_FACT  = "#DC2626"   # Rojo para tabla de hechos
COLOR_HDR   = "#1E3A5F"   # Encabezado dimensiones
COLOR_HDR_F = "#7F1D1D"   # Encabezado fact
BG          = "#F8FAFC"
TEXT_LIGHT  = "#FFFFFF"
TEXT_DARK   = "#1E293B"
PK_COLOR    = "#FEF3C7"   # Amarillo claro para PK/FK
BORDER      = "#CBD5E1"

# ── Datos de tablas ─────────────────────────────────────────────────────────
tablas = {
    "dimTiempo": {
        "pos": (0.05, 0.35),
        "ancho": 0.20,
        "cols": [
            ("PK", "tiempo_id",    "INTEGER"),
            ("",   "fecha",        "DATE"),
            ("",   "anio",         "INTEGER"),
            ("",   "mes",          "INTEGER"),
            ("",   "trimestre",    "INTEGER"),
            ("",   "dia_semana",   "VARCHAR(15)"),
            ("",   "es_finde",     "BOOLEAN"),
        ],
    },
    "dimProducto": {
        "pos": (0.05, 0.72),
        "ancho": 0.22,
        "cols": [
            ("PK", "producto_id",  "INTEGER"),
            ("",   "sku",          "VARCHAR(50)"),
            ("",   "categoria",    "VARCHAR(50)"),
            ("",   "estilo",       "VARCHAR(50)"),
            ("",   "asin",         "VARCHAR(20)"),
        ],
    },
    "dimGeografia": {
        "pos": (0.73, 0.35),
        "ancho": 0.22,
        "cols": [
            ("PK", "geo_id",       "INTEGER"),
            ("",   "ciudad",       "VARCHAR(100)"),
            ("",   "estado",       "VARCHAR(100)"),
            ("",   "pais",         "VARCHAR(10)"),
            ("",   "codigo_postal","VARCHAR(20)"),
        ],
    },
    "dimCanal": {
        "pos": (0.73, 0.72),
        "ancho": 0.20,
        "cols": [
            ("PK", "canal_id",     "INTEGER"),
            ("",   "canal_venta",  "VARCHAR(50)"),
            ("",   "fulfilled_by", "VARCHAR(50)"),
        ],
    },
    "factVentas": {
        "pos": (0.355, 0.46),
        "ancho": 0.28,
        "cols": [
            ("FK", "tiempo_id",    "INTEGER"),
            ("FK", "producto_id",  "INTEGER"),
            ("FK", "geo_id",       "INTEGER"),
            ("FK", "canal_id",     "INTEGER"),
            ("",   "order_id",     "VARCHAR(30)"),
            ("",   "estado_orden", "VARCHAR(40)"),
            ("",   "courier_status","VARCHAR(30)"),
            ("",   "cantidad",     "INTEGER"),
            ("",   "monto_total",  "NUMERIC(12,2)"),
            ("",   "promociones",  "VARCHAR(100)"),
            ("",   "b2b",          "BOOLEAN"),
        ],
    },
}

ROW_H  = 0.038
HDR_H  = 0.048
PAD    = 0.008

fig, ax = plt.subplots(figsize=(18, 11))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# ── Título ──────────────────────────────────────────────────────────────────
ax.text(0.5, 0.97,
        "Diagrama Entidad-Relación — Data Warehouse Amazon India",
        ha="center", va="top", fontsize=16, fontweight="bold",
        color=TEXT_DARK, fontfamily="DejaVu Sans")
ax.text(0.5, 0.93,
        "Esquema Estrella · Metodología HEFESTO v3 · Schema: amazon_dw",
        ha="center", va="top", fontsize=10, color="#64748B",
        fontfamily="DejaVu Sans")

# Separador
ax.axhline(y=0.91, xmin=0.05, xmax=0.95, color=BORDER, linewidth=1)


def dibujar_tabla(ax, nombre, datos):
    es_fact = nombre == "factVentas"
    color_hdr = COLOR_HDR_F if es_fact else COLOR_HDR
    color_brd = COLOR_FACT if es_fact else COLOR_DIM
    x0, y0 = datos["pos"]
    w = datos["ancho"]
    cols = datos["cols"]
    n = len(cols)
    h_total = HDR_H + n * ROW_H + PAD * 2

    # Sombra
    sombra = FancyBboxPatch(
        (x0 + 0.003, y0 - h_total - 0.003), w, h_total,
        boxstyle="round,pad=0.005", linewidth=0,
        facecolor="#CBD5E1", zorder=1
    )
    ax.add_patch(sombra)

    # Cuerpo
    cuerpo = FancyBboxPatch(
        (x0, y0 - h_total), w, h_total,
        boxstyle="round,pad=0.005",
        linewidth=2, edgecolor=color_brd,
        facecolor="white", zorder=2
    )
    ax.add_patch(cuerpo)

    # Encabezado
    encabezado = FancyBboxPatch(
        (x0, y0 - HDR_H), w, HDR_H,
        boxstyle="round,pad=0.004",
        linewidth=0, facecolor=color_hdr, zorder=3
    )
    ax.add_patch(encabezado)

    ax.text(x0 + w / 2, y0 - HDR_H / 2, nombre,
            ha="center", va="center", fontsize=10, fontweight="bold",
            color=TEXT_LIGHT, zorder=4)

    # Línea separadora bajo header
    ax.plot([x0 + 0.005, x0 + w - 0.005],
            [y0 - HDR_H, y0 - HDR_H],
            color=color_brd, linewidth=1, zorder=4)

    # Filas
    for i, (rol, col, tipo) in enumerate(cols):
        ry = y0 - HDR_H - PAD - (i + 0.5) * ROW_H

        # Fondo PK/FK
        if rol in ("PK", "FK"):
            fila_bg = mpatches.Rectangle(
                (x0 + 0.003, y0 - HDR_H - PAD - (i + 1) * ROW_H + 0.002),
                w - 0.006, ROW_H - 0.003,
                facecolor=PK_COLOR, linewidth=0, zorder=3
            )
            ax.add_patch(fila_bg)

        # Badge PK/FK
        if rol:
            badge_color = "#F59E0B" if rol == "PK" else "#6366F1"
            badge = FancyBboxPatch(
                (x0 + 0.007, ry - 0.012), 0.028, 0.022,
                boxstyle="round,pad=0.002",
                facecolor=badge_color, linewidth=0, zorder=4
            )
            ax.add_patch(badge)
            ax.text(x0 + 0.021, ry, rol,
                    ha="center", va="center", fontsize=6.5,
                    fontweight="bold", color="white", zorder=5)

        col_x = x0 + 0.042 if rol else x0 + 0.013
        ax.text(col_x, ry, col,
                ha="left", va="center", fontsize=7.8,
                color=TEXT_DARK, fontfamily="monospace", zorder=4)
        ax.text(x0 + w - 0.008, ry, tipo,
                ha="right", va="center", fontsize=6.8,
                color="#64748B", fontfamily="monospace", zorder=4)

        # Línea divisoria entre filas
        if i < n - 1:
            line_y = y0 - HDR_H - PAD - (i + 1) * ROW_H
            ax.plot([x0 + 0.005, x0 + w - 0.005],
                    [line_y, line_y],
                    color="#E2E8F0", linewidth=0.5, zorder=4)

    # Retorna el punto de conexión del FK (centro de primera fila FK o PK)
    centro_x = x0 + w / 2
    centro_y = y0 - h_total / 2
    return (centro_x, centro_y, x0, x0 + w, y0, y0 - h_total)


bounds = {}
for nombre, datos in tablas.items():
    bounds[nombre] = dibujar_tabla(ax, nombre, datos)


def punto_borde(b, lado):
    cx, cy, x0, x1, y1, y0 = b
    if lado == "right":  return (x1, cy)
    if lado == "left":   return (x0, cy)
    if lado == "top":    return (cx, y1)
    if lado == "bottom": return (cx, y0)


flechas = [
    ("dimTiempo",    "right", "factVentas", "left",   "tiempo_id"),
    ("dimProducto",  "right", "factVentas", "left",   "producto_id"),
    ("dimGeografia", "left",  "factVentas", "right",  "geo_id"),
    ("dimCanal",     "left",  "factVentas", "right",  "canal_id"),
]

ARROW_COLOR = "#475569"
for dim, lado_dim, fact, lado_fact, label in flechas:
    p1 = punto_borde(bounds[dim],  lado_dim)
    p2 = punto_borde(bounds[fact], lado_fact)

    ax.annotate("",
        xy=p2, xytext=p1,
        arrowprops=dict(
            arrowstyle="-|>",
            color=ARROW_COLOR,
            lw=1.5,
            connectionstyle="arc3,rad=0.0",
        ),
        zorder=1
    )

    mx = (p1[0] + p2[0]) / 2
    my = (p1[1] + p2[1]) / 2
    ax.text(mx, my + 0.012, label,
            ha="center", va="bottom", fontsize=7,
            color=ARROW_COLOR, style="italic",
            bbox=dict(boxstyle="round,pad=0.15", facecolor=BG,
                      edgecolor=BORDER, linewidth=0.5))

# ── Leyenda ──────────────────────────────────────────────────────────────────
leyenda_x, leyenda_y = 0.37, 0.095
items = [
    (COLOR_HDR_F, "Tabla de Hechos"),
    (COLOR_HDR,   "Tabla Dimensión"),
    ("#F59E0B",   "PK — Clave primaria"),
    ("#6366F1",   "FK — Clave foránea"),
]
for i, (color, texto) in enumerate(items):
    bx = leyenda_x + i * 0.155
    ax.add_patch(mpatches.Rectangle((bx, leyenda_y), 0.018, 0.018,
                                     facecolor=color, linewidth=0, zorder=5))
    ax.text(bx + 0.024, leyenda_y + 0.009, texto,
            va="center", fontsize=8, color=TEXT_DARK, zorder=5)

ax.text(0.5, 0.04,
        "Universidad IUA · Base de Datos II · 2026 · Docente: Melisa Caffaratti",
        ha="center", va="center", fontsize=8, color="#94A3B8")

plt.tight_layout(pad=0.3)
out = "data/der_amazon_dw.png"
plt.savefig(out, dpi=180, bbox_inches="tight", facecolor=BG)
print(f"DER guardado en: {out}")
