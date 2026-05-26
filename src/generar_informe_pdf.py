"""
generar_informe_pdf.py
======================
Genera el informe final completo del proyecto Data Warehouse Amazon India.
Produce:
  - data/der_amazon_dw_v2.png    (DER con esquema real de Supabase)
  - data/modelo_conceptual.png   (Modelo Conceptual HEFESTO)
  - data/informe_final.pdf       (Informe completo con diseño profesional)
"""

import os, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image as RLImage, KeepTogether
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Paleta de colores ───────────────────────────────────────────────────────
NAVY    = colors.HexColor("#1E3A5F")
BLUE    = colors.HexColor("#2563EB")
RED     = colors.HexColor("#DC2626")
AMBER   = colors.HexColor("#F59E0B")
INDIGO  = colors.HexColor("#4F46E5")
GRAY_L  = colors.HexColor("#F1F5F9")
GRAY_M  = colors.HexColor("#94A3B8")
GRAY_D  = colors.HexColor("#334155")
WHITE   = colors.white
BLACK   = colors.black

W, H = A4


# ══════════════════════════════════════════════════════════════════════════════
# 1. DER — Datos exactos de Supabase
# ══════════════════════════════════════════════════════════════════════════════
SCHEMA = {
    "dimTiempo": {
        "tipo": "dimension",
        "filas": "91 filas",
        "cols": [
            ("PK", "idTiempo",    "INTEGER"),
            ("",   "fecha",        "DATE"),
            ("",   "dia",          "SMALLINT"),
            ("",   "mes",          "SMALLINT"),
            ("",   "nombre_mes",   "VARCHAR"),
            ("",   "trimestre",    "SMALLINT"),
            ("",   "anio",         "SMALLINT"),
        ],
        "pos": (0.03, 0.38), "w": 0.215,
    },
    "dimProducto": {
        "tipo": "dimension",
        "filas": "7.053 filas",
        "cols": [
            ("PK", "idProducto",   "INTEGER"),
            ("",   "categoria",    "VARCHAR"),
            ("",   "talla",        "VARCHAR"),
            ("",   "estilo",       "VARCHAR"),
        ],
        "pos": (0.03, 0.75), "w": 0.215,
    },
    "dimGeografia": {
        "tipo": "dimension",
        "filas": "7.401 filas",
        "cols": [
            ("PK", "idGeografia",  "INTEGER"),
            ("",   "ciudad",       "VARCHAR"),
            ("",   "estado",       "VARCHAR"),
            ("",   "pais",         "VARCHAR"),
        ],
        "pos": (0.765, 0.38), "w": 0.215,
    },
    "dimCanal": {
        "tipo": "dimension",
        "filas": "4 filas",
        "cols": [
            ("PK", "idCanal",          "INTEGER"),
            ("",   "tipo_fulfillment", "VARCHAR"),
            ("",   "canal_ventas",     "VARCHAR"),
            ("",   "nivel_servicio",   "VARCHAR"),
        ],
        "pos": (0.765, 0.75), "w": 0.215,
    },
    "factVentas": {
        "tipo": "hecho",
        "filas": "122.349 filas",
        "cols": [
            ("FK", "idProducto",        "INTEGER"),
            ("FK", "idGeografia",       "INTEGER"),
            ("FK", "idTiempo",          "INTEGER"),
            ("FK", "idCanal",           "INTEGER"),
            ("",   "cantidad_vendida",   "INTEGER"),
            ("",   "monto_total",        "NUMERIC"),
            ("",   "cantidad_cancelada", "INTEGER"),
            ("",   "monto_cancelado",    "NUMERIC"),
        ],
        "pos": (0.33, 0.44), "w": 0.34,
    },
}

HDR_H  = 0.052
ROW_H  = 0.042
PAD    = 0.008
BG     = "#F8FAFC"


def _color(tabla):
    return ("#7F1D1D", "#DC2626") if SCHEMA[tabla]["tipo"] == "hecho" else ("#1E3A5F", "#2563EB")


def dibujar_tabla_der(ax, nombre, datos):
    hdr_color, brd_color = _color(nombre)
    x0, y0 = datos["pos"]
    w      = datos["w"]
    cols   = datos["cols"]
    n      = len(cols)
    h_tot  = HDR_H*2 + n*ROW_H + PAD*2

    # Sombra
    ax.add_patch(FancyBboxPatch((x0+.003, y0-h_tot-.003), w, h_tot,
        boxstyle="round,pad=.005", lw=0, facecolor="#CBD5E1", zorder=1))
    # Cuerpo
    ax.add_patch(FancyBboxPatch((x0, y0-h_tot), w, h_tot,
        boxstyle="round,pad=.005", lw=2, edgecolor=brd_color,
        facecolor="white", zorder=2))
    # Header principal
    ax.add_patch(FancyBboxPatch((x0, y0-HDR_H), w, HDR_H,
        boxstyle="round,pad=.004", lw=0, facecolor=hdr_color, zorder=3))
    ax.text(x0+w/2, y0-HDR_H/2, nombre,
            ha="center", va="center", fontsize=9, fontweight="bold",
            color="white", zorder=4)
    # Sub-header con tipo y filas
    tipo_lbl = "[ TABLA DE HECHOS ]" if datos["tipo"]=="hecho" else "[ DIMENSION ]"
    ax.add_patch(FancyBboxPatch((x0, y0-HDR_H*2), w, HDR_H,
        boxstyle="round,pad=.003", lw=0, facecolor=brd_color+"33", zorder=3))
    ax.text(x0+w/2, y0-HDR_H*1.5,
            f"{tipo_lbl}  ·  {datos['filas']}",
            ha="center", va="center", fontsize=6.5,
            color=hdr_color, zorder=4)
    ax.plot([x0+.005, x0+w-.005], [y0-HDR_H*2, y0-HDR_H*2],
            color=brd_color, lw=1, zorder=4)

    # Filas de columnas
    for i, (rol, col, tipo) in enumerate(cols):
        ry = y0 - HDR_H*2 - PAD - (i+.5)*ROW_H
        if rol in ("PK","FK"):
            ax.add_patch(mpatches.Rectangle(
                (x0+.003, y0-HDR_H*2-PAD-(i+1)*ROW_H+.003),
                w-.006, ROW_H-.004,
                facecolor="#FEF3C7", lw=0, zorder=3))
        if rol:
            bc = "#F59E0B" if rol=="PK" else "#4F46E5"
            ax.add_patch(FancyBboxPatch(
                (x0+.007, ry-.013), .028, .023,
                boxstyle="round,pad=.002", facecolor=bc, lw=0, zorder=4))
            ax.text(x0+.021, ry, rol,
                    ha="center", va="center", fontsize=6,
                    fontweight="bold", color="white", zorder=5)
        cx = x0+.042 if rol else x0+.012
        ax.text(cx, ry, col,
                ha="left", va="center", fontsize=7.5,
                color="#1E293B", family="monospace", zorder=4)
        ax.text(x0+w-.008, ry, tipo,
                ha="right", va="center", fontsize=6.5,
                color="#64748B", family="monospace", zorder=4)
        if i < n-1:
            ly = y0-HDR_H*2-PAD-(i+1)*ROW_H
            ax.plot([x0+.005, x0+w-.005], [ly, ly],
                    color="#E2E8F0", lw=.5, zorder=4)

    cx = x0+w/2
    cy = y0-h_tot/2
    return (cx, cy, x0, x0+w, y0, y0-h_tot)


def generar_der(out_path):
    fig, ax = plt.subplots(figsize=(20, 12))
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)

    # Título
    ax.text(.5, .975, "Diagrama Entidad-Relación — Data Warehouse Amazon India",
            ha="center", va="top", fontsize=15, fontweight="bold",
            color="#1E293B")
    ax.text(.5, .942,
            "Esquema Estrella · Metodología HEFESTO v3 · Schema: amazon_dw (Supabase/PostgreSQL)",
            ha="center", va="top", fontsize=9, color="#64748B")
    ax.plot([.04,.96], [.925,.925], color="#CBD5E1", lw=1)

    bounds = {}
    for nombre, datos in SCHEMA.items():
        bounds[nombre] = dibujar_tabla_der(ax, nombre, datos)

    def pt(b, lado):
        cx,cy,x0,x1,y1,y0_ = b
        if lado=="right":  return (x1, cy)
        if lado=="left":   return (x0, cy)
        if lado=="top":    return (cx, y1)
        if lado=="bottom": return (cx, y0_)

    flechas = [
        ("dimTiempo",    "right", "factVentas", "left",  "idTiempo"),
        ("dimProducto",  "right", "factVentas", "left",  "idProducto"),
        ("dimGeografia", "left",  "factVentas", "right", "idGeografia"),
        ("dimCanal",     "left",  "factVentas", "right", "idCanal"),
    ]
    for dim, ld, fct, lf, lbl in flechas:
        p1 = pt(bounds[dim], ld)
        p2 = pt(bounds[fct], lf)
        ax.annotate("", xy=p2, xytext=p1,
            arrowprops=dict(arrowstyle="-|>", color="#475569", lw=1.8,
                            connectionstyle="arc3,rad=0.0"), zorder=1)
        mx,my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
        ax.text(mx, my+.015, lbl,
                ha="center", va="bottom", fontsize=7, color="#475569",
                style="italic",
                bbox=dict(boxstyle="round,pad=.2", fc=BG, ec="#CBD5E1", lw=.5))

    # Leyenda
    items = [("#7F1D1D","Tabla de Hechos"), ("#1E3A5F","Tabla Dimensión"),
             ("#F59E0B","PK — Clave Primaria"), ("#4F46E5","FK — Clave Foránea")]
    lx = .27
    for i,(c,t) in enumerate(items):
        bx = lx + i*.17
        ax.add_patch(mpatches.Rectangle((bx,.06),.018,.018, fc=c, lw=0, zorder=5))
        ax.text(bx+.024,.069, t, va="center", fontsize=8, color="#334155", zorder=5)

    ax.text(.5,.025,
            "Universidad IUA · Base de Datos II · 2026 · Docente: Melisa Caffaratti",
            ha="center", va="center", fontsize=7.5, color="#94A3B8")

    plt.tight_layout(pad=.3)
    plt.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"[OK] DER → {out_path}")


# ══════════════════════════════════════════════════════════════════════════════
# 2. Modelo Conceptual
# ══════════════════════════════════════════════════════════════════════════════

def generar_modelo_conceptual(out_path):
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    BG2 = "#F0F4FF"
    fig.patch.set_facecolor(BG2); ax.set_facecolor(BG2)

    ax.text(.5,.95,"Modelo Conceptual — HEFESTO v3",
            ha="center", va="top", fontsize=14, fontweight="bold", color="#1E293B")
    ax.text(.5,.90,"Ventas Amazon India · Período Abril–Junio 2022",
            ha="center", va="top", fontsize=9, color="#64748B")
    ax.plot([.05,.95],[.875,.875], color="#CBD5E1", lw=1)

    cx, cy = .5, .48

    # Óvalo central
    ov = mpatches.Ellipse((cx,cy), .22, .18,
        facecolor="#1E3A5F", edgecolor="#2563EB", lw=3, zorder=3)
    ax.add_patch(ov)
    ax.text(cx, cy+.025, "VENTAS", ha="center", va="center",
            fontsize=13, fontweight="bold", color="white", zorder=4)
    ax.text(cx, cy-.025, "AMAZON", ha="center", va="center",
            fontsize=13, fontweight="bold", color="#93C5FD", zorder=4)

    # Perspectivas (izquierda)
    perspectivas = [
        (.18, .74, "Tiempo",    "#0369A1", "fecha · dia · mes\nnombre_mes · trimestre · anio"),
        (.12, .53, "Producto",  "#0369A1", "categoria · talla · estilo"),
        (.12, .36, "Geografía", "#0369A1", "ciudad · estado · país"),
        (.18, .20, "Canal",     "#0369A1", "tipo_fulfillment · canal_ventas\nnivel_servicio"),
    ]
    for px, py, nombre, color, atribs in perspectivas:
        r = mpatches.FancyBboxPatch((px-.09, py-.055), .18, .10,
            boxstyle="round,pad=.01", fc=color, ec="#0284C7", lw=2, zorder=3)
        ax.add_patch(r)
        ax.text(px, py+.02, nombre,
                ha="center", va="center", fontsize=10, fontweight="bold",
                color="white", zorder=4)
        ax.text(px, py-.02, atribs,
                ha="center", va="center", fontsize=6.5,
                color="#BAE6FD", zorder=4)
        ax.annotate("", xy=(cx-.11, cy), xytext=(px+.09, py),
            arrowprops=dict(arrowstyle="-|>", color="#0369A1", lw=2,
                            connectionstyle="arc3,rad=0.0"), zorder=2)

    # Indicadores (derecha)
    indicadores = [
        (.82, .72, "cantidad_vendida",    "#166534", "SUM(Qty)\nStatus ≠ 'Cancelled'"),
        (.82, .57, "monto_total",         "#166534", "SUM(Amount)\nStatus ≠ 'Cancelled'"),
        (.82, .39, "cantidad_cancelada",  "#991B1B", "SUM(Qty)\nStatus = 'Cancelled'"),
        (.82, .24, "monto_cancelado",     "#991B1B", "SUM(Amount)\nStatus = 'Cancelled'"),
    ]
    for ix, iy, nombre, color, formula in indicadores:
        r = mpatches.FancyBboxPatch((ix-.10, iy-.052), .20, .094,
            boxstyle="round,pad=.01", fc=color, ec=color, lw=2, zorder=3)
        ax.add_patch(r)
        ax.text(ix, iy+.02, nombre,
                ha="center", va="center", fontsize=8.5, fontweight="bold",
                color="white", family="monospace", zorder=4)
        ax.text(ix, iy-.02, formula,
                ha="center", va="center", fontsize=6.5,
                color="#D1FAE5" if "166" in color else "#FEE2E2", zorder=4)
        ax.annotate("", xy=(ix-.10, iy), xytext=(cx+.11, cy),
            arrowprops=dict(arrowstyle="-|>", color="#334155", lw=1.8,
                            connectionstyle="arc3,rad=0.0"), zorder=2)

    # Labels de grupos
    ax.text(.12,.845,"◀ PERSPECTIVAS", ha="center", fontsize=8,
            color="#0369A1", fontweight="bold")
    ax.text(.84,.845,"INDICADORES ▶", ha="center", fontsize=8,
            color="#166534", fontweight="bold")

    ax.text(.5,.04,
            "Universidad IUA · Base de Datos II · 2026 · Docente: Melisa Caffaratti",
            ha="center", va="center", fontsize=7.5, color="#94A3B8")

    plt.tight_layout(pad=.3)
    plt.savefig(out_path, dpi=180, bbox_inches="tight", facecolor=BG2)
    plt.close()
    print(f"[OK] Modelo Conceptual → {out_path}")


# ══════════════════════════════════════════════════════════════════════════════
# 3. PDF
# ══════════════════════════════════════════════════════════════════════════════

def make_styles():
    S = getSampleStyleSheet()

    def add(name, **kw):
        if name not in S:
            S.add(ParagraphStyle(name=name, **kw))
        return S[name]

    add("Cover1",      fontSize=28, textColor=WHITE,    alignment=TA_CENTER, fontName="Helvetica-Bold", leading=34)
    add("Cover2",      fontSize=16, textColor=colors.HexColor("#93C5FD"), alignment=TA_CENTER, fontName="Helvetica", leading=22)
    add("Cover3",      fontSize=12, textColor=WHITE,    alignment=TA_CENTER, fontName="Helvetica", leading=18)
    add("CoverMeta",   fontSize=10, textColor=colors.HexColor("#CBD5E1"), alignment=TA_CENTER, fontName="Helvetica", leading=14)
    add("H1",          fontSize=15, textColor=NAVY,     fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=6,  leading=20)
    add("H2",          fontSize=11, textColor=BLUE,     fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=4,  leading=15)
    add("H3",          fontSize=9.5,textColor=GRAY_D,   fontName="Helvetica-Bold", spaceBefore=8,  spaceAfter=2,  leading=13)
    add("Body",        fontSize=9,  textColor=GRAY_D,   fontName="Helvetica",      spaceBefore=3,  spaceAfter=3,  leading=13, alignment=TA_JUSTIFY)
    add("Code",        fontSize=7.5,textColor=GRAY_D,   fontName="Courier",        spaceBefore=2,  spaceAfter=2,  leading=11,
        backColor=colors.HexColor("#F8FAFC"), borderPad=4)
    add("Caption",     fontSize=7.5,textColor=GRAY_M,   fontName="Helvetica",      alignment=TA_CENTER, spaceBefore=2, spaceAfter=8, leading=10)
    add("BulletBody",  fontSize=9,  textColor=GRAY_D,   fontName="Helvetica",      spaceBefore=2,  spaceAfter=2, leading=13,
        leftIndent=14, bulletIndent=4, bulletText="•")
    return S


def tabla_simple(data, col_widths=None, header_bg=NAVY, stripe=True):
    style = [
        ("BACKGROUND", (0,0), (-1,0), header_bg),
        ("TEXTCOLOR",  (0,0), (-1,0), WHITE),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 7.5),
        ("FONTNAME",   (0,1), (-1,-1), "Helvetica"),
        ("ALIGN",      (0,0), (-1,-1), "LEFT"),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUND",(0,0),(-1,-1), [GRAY_L, WHITE]) if stripe else ("",),
        ("GRID",       (0,0), (-1,-1), 0.4, colors.HexColor("#CBD5E1")),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LEFTPADDING",(0,0), (-1,-1), 6),
        ("RIGHTPADDING",(0,0),(-1,-1), 6),
        ("ROWBACKGROUND",(0,1),(-1,-1), [WHITE, GRAY_L]),
    ]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle(style))
    return t


def hr(color=BLUE, thickness=1):
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=4, spaceBefore=4)


def img(path, width_cm=15):
    return RLImage(path, width=width_cm*cm, height=width_cm*cm*0.57)


# ── On-page decorations ────────────────────────────────────────────────────

class MyDocTemplate(SimpleDocTemplate):
    def __init__(self, *a, **kw):
        self._cover_done = False
        super().__init__(*a, **kw)

    def handle_pageBegin(self):
        super().handle_pageBegin()
        canvas = self.canv
        pn = canvas.getPageNumber()
        if pn > 1:
            # Header bar
            canvas.setFillColor(NAVY)
            canvas.rect(0, H-1.1*cm, W, 1.1*cm, fill=1, stroke=0)
            canvas.setFillColor(WHITE)
            canvas.setFont("Helvetica-Bold", 8)
            canvas.drawString(1.5*cm, H-0.7*cm, "DW Amazon India — Metodología HEFESTO v3")
            canvas.setFont("Helvetica", 8)
            canvas.drawRightString(W-1.5*cm, H-0.7*cm, "Base de Datos II · IUA · 2026")
            # Footer
            canvas.setFillColor(NAVY)
            canvas.rect(0, 0, W, 1*cm, fill=1, stroke=0)
            canvas.setFillColor(WHITE)
            canvas.setFont("Helvetica", 7.5)
            canvas.drawString(1.5*cm, 0.35*cm, "Docente: Melisa Caffaratti")
            canvas.drawCentredString(W/2, 0.35*cm, f"Página {pn}")
            canvas.drawRightString(W-1.5*cm, 0.35*cm, "Repositorio: github.com/Yisus538/amazon-sale-dw-etl")


def build_pdf(pdf_path, der_path, mc_path):
    S = make_styles()
    doc = MyDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=2.0*cm,  bottomMargin=1.8*cm,
    )
    story = []

    # ── PORTADA ─────────────────────────────────────────────────────────────
    # Fondo azul oscuro simulado con rectángulo
    from reportlab.platypus import Frame, NextPageTemplate
    from reportlab.platypus.flowables import Flowable

    class CoverBackground(Flowable):
        def draw(self):
            c = self.canv
            # Fondo
            c.setFillColor(NAVY)
            c.rect(-2*cm, -3*cm, W+4*cm, H+4*cm, fill=1, stroke=0)
            # Banda superior decorativa
            c.setFillColor(BLUE)
            c.rect(-2*cm, H-5*cm, W+4*cm, 2.5*cm, fill=1, stroke=0)
            # Banda inferior
            c.setFillColor(colors.HexColor("#0F2340"))
            c.rect(-2*cm, -3*cm, W+4*cm, 4*cm, fill=1, stroke=0)
            # Línea de acento naranja
            c.setFillColor(AMBER)
            c.rect(-2*cm, H-5.15*cm, W+4*cm, .15*cm, fill=1, stroke=0)

        def wrap(self, aw, ah):
            return 0, 0

    story.append(CoverBackground())
    story.append(Spacer(1, 3.5*cm))
    story.append(Paragraph("DATA WAREHOUSE", S["Cover1"]))
    story.append(Paragraph("Amazon India Sale Report", S["Cover2"]))
    story.append(Spacer(1, 0.5*cm))
    story.append(hr(AMBER, 2))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Diseño e Implementación ETL", S["Cover3"]))
    story.append(Paragraph("Metodología HEFESTO v3", S["Cover3"]))
    story.append(Spacer(1, 3*cm))

    meta = [
        ["Institución",  "Instituto Universitario Aeronáutico (IUA)"],
        ["Carrera",      "Ingeniería en Sistemas"],
        ["Materia",      "Base de Datos II"],
        ["Docente",      "Melisa Caffaratti"],
        ["Año",          "2026"],
        ["Integrantes",  "Martinez Jesus Manuel  ·  jmartinez450@alumnos.iua.edu.ar"],
        ["",             "Bulatovich Juan Cruz    ·  jbulatovich468@alumnos.iua.edu.ar"],
        ["",             "Correa Sofia Agostina   ·  scorrea201@alumnos.iua.edu.ar"],
        ["",             "Bossio Francisco        ·  fbossio156@alumnos.iua.edu.ar"],
    ]
    meta_style = TableStyle([
        ("FONTNAME",  (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",  (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE",  (0,0), (-1,-1), 9),
        ("TEXTCOLOR", (0,0), (-1,-1), WHITE),
        ("ALIGN",     (0,0), (-1,-1), "LEFT"),
        ("VALIGN",    (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",(0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LINEBELOW", (0,0),(-1,-2), 0.3, colors.HexColor("#2563EB")),
        ("TEXTCOLOR", (0,0),(0,-1), AMBER),
    ])
    mt = Table(meta, colWidths=[4*cm, 11.5*cm])
    mt.setStyle(meta_style)
    story.append(mt)
    story.append(PageBreak())

    # ── ÍNDICE ───────────────────────────────────────────────────────────────
    story.append(Paragraph("Contenido", S["H1"]))
    story.append(hr())
    indice = [
        "1. Situación Problemática",
        "2. Paso 1 — Análisis de Requerimientos",
        "   2.1  Preguntas de Negocio",
        "   2.2  Indicadores y Perspectivas",
        "   2.3  Modelo Conceptual",
        "3. Paso 2 — Análisis de Data Sources",
        "   3.1  Mapeo CSV → DW",
        "   3.2  Granularidad",
        "   3.3  Modelo Conceptual Ampliado",
        "4. Paso 3 — Modelo Lógico del Data Warehouse",
        "   4.1  Esquema Estrella — Justificación",
        "   4.2  Tablas de Dimensiones",
        "   4.3  Tabla de Hechos",
        "   4.4  Diagrama Entidad-Relación (DER)",
        "5. Paso 4 — Integración de Datos (ETL)",
        "   5.1  Herramientas",
        "   5.2  Proceso ETL",
        "   5.3  Resultados de la Carga",
        "   5.4  Estrategia de Actualización",
        "6. Diccionario de Datos",
        "7. Bocetos de Reportes y Tableros",
        "8. Conclusión",
        "9. Bibliografía",
    ]
    for item in indice:
        indent = 24 if item.startswith("   ") else 0
        story.append(Paragraph(item.strip(),
            ParagraphStyle("Idx", parent=S["Body"], leftIndent=indent, spaceAfter=1)))
    story.append(PageBreak())

    # ── SITUACIÓN PROBLEMÁTICA ────────────────────────────────────────────────
    story.append(Paragraph("1. Situación Problemática", S["H1"]))
    story.append(hr())
    story.append(Paragraph(
        "Una empresa de comercio electrónico que opera en Amazon India necesita analizar el "
        "rendimiento de sus ventas para optimizar su estrategia comercial. Los datos operacionales "
        "están dispersos en archivos planos exportados de Amazon Seller Central, lo que impide "
        "obtener una visión centralizada e histórica del negocio.", S["Body"]))
    story.append(Paragraph(
        "Se propone construir un <b>Data Warehouse</b> que permita analizar las ventas desde "
        "múltiples perspectivas: producto, geografía, tiempo y canal de venta, aplicando la "
        "<b>Metodología HEFESTO v3</b> (Bernabeu &amp; García Mattío).", S["Body"]))
    story.append(Spacer(1, 0.3*cm))

    info_data = [
        ["Atributo", "Detalle"],
        ["Dataset", "Amazon Sale Report (CSV — Kaggle)"],
        ["Registros", "128.975 filas · 24 columnas · Período: Abril–Junio 2022"],
        ["Moneda", "INR — Rupia India"],
        ["ETL", "Python 3.12 · pandas 2.2 · SQLAlchemy 2.0 · psycopg2-binary 2.9"],
        ["Base de datos DW", "PostgreSQL (Supabase cloud) · Schema: amazon_dw"],
        ["Herramienta BI", "Metabase / Looker Studio (bocetos)"],
    ]
    story.append(tabla_simple(info_data, [4*cm, 11.5*cm]))
    story.append(PageBreak())

    # ── PASO 1 ───────────────────────────────────────────────────────────────
    story.append(Paragraph("2. Paso 1 — Análisis de Requerimientos", S["H1"]))
    story.append(hr())

    story.append(Paragraph("2.1 Preguntas de Negocio", S["H2"]))
    preguntas = [
        ("P1", "¿Cuántas unidades vendidas y cuál es el monto total de ventas por categoría de producto, estado geográfico y mes del período analizado?"),
        ("P2", "¿Cuál es la evolución mensual del monto de ventas y cancelaciones según el canal de distribución (Amazon.in vs Non-Amazon) y tipo de fulfillment?"),
        ("P3", "¿Qué combinaciones de categoría, talla y estilo presentan la mayor cantidad de cancelaciones y cuál es el impacto económico (monto cancelado en INR)?"),
        ("P4", "¿Cómo varía el volumen de ventas (unidades y monto) por trimestre según el nivel de servicio de envío (Standard vs Expedited) y tipo de fulfillment?"),
    ]
    pq_data = [["#", "Pregunta de Negocio"]]
    for cod, txt in preguntas:
        pq_data.append([cod, txt])
    story.append(tabla_simple(pq_data, [1.2*cm, 14.3*cm]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("2.2 Indicadores y Perspectivas", S["H2"]))
    story.append(Paragraph("<b>Indicadores:</b>", S["H3"]))
    ind_data = [
        ["Indicador", "Fórmula", "Función", "Argumentación"],
        ["cantidad_vendida",   "SUM(Qty) WHERE Status ≠ 'Cancelled'",   "SUM", "Mide el volumen real de demanda satisfecha."],
        ["monto_total",        "SUM(Amount) WHERE Status ≠ 'Cancelled'", "SUM", "Cuantifica el ingreso efectivo en INR."],
        ["cantidad_cancelada", "SUM(Qty) WHERE Status = 'Cancelled'",    "SUM", "Detecta problemas logísticos por segmento."],
        ["monto_cancelado",    "SUM(Amount) WHERE Status = 'Cancelled'", "SUM", "Cuantifica el costo económico de cancelaciones."],
    ]
    story.append(tabla_simple(ind_data, [3.5*cm, 4.8*cm, 1.8*cm, 5.4*cm]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("<b>Perspectivas:</b>", S["H3"]))
    per_data = [
        ["Perspectiva", "Tabla DW", "Entidad", "Justificación"],
        ["Tiempo",    "dimTiempo",    "Fechas de órdenes",           "Perspectiva fundamental. Análisis temporal por mes y trimestre."],
        ["Producto",  "dimProducto",  "Categoría + Talla + Estilo",  "Atributos comerciales clave. Estilo identifica el SKU Amazon."],
        ["Geografía", "dimGeografia", "Ciudad + Estado + País",      "Distribución geográfica dentro de India. Logística regional."],
        ["Canal",     "dimCanal",     "Fulfillment + Canal + Serv.", "Solo 4 combinaciones posibles. Define el canal logístico."],
    ]
    story.append(tabla_simple(per_data, [2.5*cm, 3*cm, 4*cm, 6*cm]))

    story.append(Paragraph("2.3 Modelo Conceptual", S["H2"]))
    story.append(img(mc_path, 15))
    story.append(Paragraph("Figura 1 — Modelo Conceptual HEFESTO: perspectivas a la izquierda, indicadores a la derecha.", S["Caption"]))
    story.append(PageBreak())

    # ── PASO 2 ───────────────────────────────────────────────────────────────
    story.append(Paragraph("3. Paso 2 — Análisis de Data Sources", S["H2"]))
    story.append(hr())
    story.append(Paragraph(
        "<b>Data Source:</b> Amazon_Sale_Report.csv — 128.975 registros · 24 columnas · "
        "Período Abril–Junio 2022 · Moneda: INR.", S["Body"]))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("3.1 Mapeo CSV → DW", S["H2"]))
    mapeo = [
        ["Campo CSV",          "Perspectiva", "Campo DW",                    "Tabla DW",     "Transformación"],
        ["Date",               "Tiempo",      "fecha, dia, mes, trimestre…", "dimTiempo",    "pd.to_datetime() + dt.day/month…"],
        ["Category",           "Producto",    "categoria",                   "dimProducto",  "str.strip()"],
        ["Size",               "Producto",    "talla",                       "dimProducto",  "str.strip()"],
        ["Style",              "Producto",    "estilo",                      "dimProducto",  "—"],
        ["ship-city",          "Geografía",   "ciudad",                      "dimGeografia", "upper() · fillna('No Informado')"],
        ["ship-state",         "Geografía",   "estado",                      "dimGeografia", "upper() · fillna('No Informado')"],
        ["ship-country",       "Geografía",   "pais",                        "dimGeografia", "fillna('IN')"],
        ["Fulfilment",         "Canal",       "tipo_fulfillment",            "dimCanal",     "str.strip()"],
        ["Sales Channel",      "Canal",       "canal_ventas",                "dimCanal",     "str.strip()"],
        ["ship-service-level", "Canal",       "nivel_servicio",              "dimCanal",     "str.strip()"],
        ["Qty",                "Indicador",   "cantidad_vendida / cancelada", "factVentas",  "SUM agrupado según Status"],
        ["Amount",             "Indicador",   "monto_total / cancelado",     "factVentas",   "SUM agrupado según Status"],
    ]
    story.append(tabla_simple(mapeo, [2.8*cm, 2.3*cm, 3.5*cm, 2.7*cm, 4.2*cm]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Problemas de calidad detectados:", S["H3"]))
    problemas = [
        "Courier Status: 276 nulos → reemplazados por 'Desconocido'",
        "Amount/currency: 338 nulos → órdenes canceladas con Qty=0, reemplazados por 0",
        "ship-city/state: 2 nulos → reemplazados por 'No Informado'",
        "promotion-ids: 1.772 nulos → reemplazados por 'Sin Promocion'",
        "fulfilled-by: 3.461 nulos → reemplazados por 'No Informado'",
        "Unnamed: 22: 100% nulos → columna descartada",
    ]
    for p in problemas:
        story.append(Paragraph(p, S["BulletBody"]))

    story.append(Paragraph("3.2 Granularidad", S["H2"]))
    gran = [
        ["Perspectiva", "Nivel de detalle", "Justificación"],
        ["Tiempo",    "Diario",         "3 meses de datos. Granularidad diaria + mes/trimestre para tendencias."],
        ["Producto",  "SKU (estilo)",   "Los 3 campos (categoría+talla+estilo) identifican unívocamente un producto."],
        ["Geografía", "Ciudad",         "País siempre India. Estado+ciudad permite análisis geográfico regional."],
        ["Canal",     "Combinación",    "4 combinaciones posibles. Cada una define un canal logístico distinto."],
    ]
    story.append(tabla_simple(gran, [2.5*cm, 3*cm, 10*cm]))
    story.append(PageBreak())

    # ── PASO 3 ───────────────────────────────────────────────────────────────
    story.append(Paragraph("4. Paso 3 — Modelo Lógico del Data Warehouse", S["H1"]))
    story.append(hr())

    story.append(Paragraph("4.1 Esquema Estrella — Justificación", S["H2"]))
    razones = [
        "Existe una única tabla de hechos central (factVentas) rodeada de 4 dimensiones independientes.",
        "Las dimensiones no tienen sub-dimensiones que justifiquen normalización adicional (descarta Copo de Nieve).",
        "Las consultas analíticas son más simples y eficientes con menos JOINs necesarios.",
        "El dataset proviene de una única fuente CSV sin múltiples procesos de negocio (descarta Constelación).",
        "El rendimiento de consulta es prioritario sobre el ahorro de almacenamiento.",
    ]
    for r in razones:
        story.append(Paragraph(r, S["BulletBody"]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("4.2 Tablas de Dimensiones (extraídas de Supabase)", S["H2"]))

    dims_info = [
        ("dimTiempo", "DIMENSIÓN", "91 filas", [
            ["Campo","Tipo","Descripción"],
            ["idTiempo (PK)","INTEGER","Clave primaria autoincremental"],
            ["fecha","DATE","Fecha completa de la orden"],
            ["dia","SMALLINT","Día del mes (1–31)"],
            ["mes","SMALLINT","Número de mes (1–12)"],
            ["nombre_mes","VARCHAR","Nombre del mes en inglés"],
            ["trimestre","SMALLINT","Trimestre del año (1–4)"],
            ["anio","SMALLINT","Año (2022)"],
        ]),
        ("dimProducto", "DIMENSIÓN", "7.053 filas", [
            ["Campo","Tipo","Descripción"],
            ["idProducto (PK)","INTEGER","Clave primaria autoincremental"],
            ["categoria","VARCHAR","Categoría del producto (Set, Kurta, etc.)"],
            ["talla","VARCHAR","Talla (S, M, L, XL, XXL, 3XL…)"],
            ["estilo","VARCHAR","Código de estilo / SKU interno de Amazon"],
        ]),
        ("dimGeografia", "DIMENSIÓN", "7.401 filas", [
            ["Campo","Tipo","Descripción"],
            ["idGeografia (PK)","INTEGER","Clave primaria autoincremental"],
            ["ciudad","VARCHAR","Ciudad de envío (mayúsculas; nulos→'No Informado')"],
            ["estado","VARCHAR","Estado de India (mayúsculas; nulos→'No Informado')"],
            ["pais","VARCHAR","País de envío (siempre 'IN' — India)"],
        ]),
        ("dimCanal", "DIMENSIÓN", "4 filas", [
            ["Campo","Tipo","Descripción"],
            ["idCanal (PK)","INTEGER","Clave primaria autoincremental"],
            ["tipo_fulfillment","VARCHAR","Tipo de fulfillment (Amazon / Merchant)"],
            ["canal_ventas","VARCHAR","Canal de venta (Amazon.in / Non-Amazon)"],
            ["nivel_servicio","VARCHAR","Nivel de servicio (Standard / Expedited)"],
        ]),
    ]
    for tname, ttipo, tfilas, tdata in dims_info:
        badge = f"<font color='#2563EB'><b>{tname}</b></font>   <font color='#64748B' size='8'>({ttipo} · {tfilas})</font>"
        story.append(Paragraph(badge, S["H3"]))
        story.append(tabla_simple(tdata, [4*cm, 3*cm, 8.5*cm], header_bg=BLUE))
        story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("4.3 Tabla de Hechos (extraída de Supabase)", S["H2"]))
    badge = "<font color='#DC2626'><b>factVentas</b></font>   <font color='#64748B' size='8'>(TABLA DE HECHOS · 122.349 filas)</font>"
    story.append(Paragraph(badge, S["H3"]))
    fact_data = [
        ["Campo","Tipo","FK","Descripción"],
        ["idProducto (PK,FK)","INTEGER","→ dimProducto","Clave foránea a dimensión Producto"],
        ["idGeografia (PK,FK)","INTEGER","→ dimGeografia","Clave foránea a dimensión Geografía"],
        ["idTiempo (PK,FK)","INTEGER","→ dimTiempo","Clave foránea a dimensión Tiempo"],
        ["idCanal (PK,FK)","INTEGER","→ dimCanal","Clave foránea a dimensión Canal"],
        ["cantidad_vendida","INTEGER","—","SUM(Qty) WHERE Status ≠ 'Cancelled'"],
        ["monto_total","NUMERIC","—","SUM(Amount) WHERE Status ≠ 'Cancelled' (INR)"],
        ["cantidad_cancelada","INTEGER","—","SUM(Qty) WHERE Status = 'Cancelled'"],
        ["monto_cancelado","NUMERIC","—","SUM(Amount) WHERE Status = 'Cancelled' (INR)"],
    ]
    story.append(tabla_simple(fact_data, [4*cm, 2.5*cm, 3*cm, 6*cm], header_bg=RED))
    story.append(Paragraph("PK compuesta: (idProducto, idGeografia, idTiempo, idCanal)", S["Caption"]))

    story.append(Paragraph("4.4 Diagrama Entidad-Relación (DER)", S["H2"]))
    story.append(img(der_path, 16))
    story.append(Paragraph(
        "Figura 2 — DER del esquema estrella amazon_dw extraído de Supabase/PostgreSQL. "
        "Las tablas de dimensión aparecen en azul y la tabla de hechos en rojo.",
        S["Caption"]))
    story.append(PageBreak())

    # ── PASO 4 ───────────────────────────────────────────────────────────────
    story.append(Paragraph("5. Paso 4 — Integración de Datos (ETL)", S["H1"]))
    story.append(hr())

    story.append(Paragraph("5.1 Herramientas", S["H2"]))
    tools = [
        ["Herramienta", "Versión", "Rol"],
        ["Python",            "3.12",   "Lenguaje principal del pipeline ETL"],
        ["pandas",            "2.2.2",  "Extracción, transformación y limpieza de datos"],
        ["SQLAlchemy",        "2.0.30", "ORM y engine de conexión a PostgreSQL"],
        ["psycopg2-binary",   "2.9.9",  "Driver PostgreSQL para Python"],
        ["pyarrow",           "16.1.0", "Serialización Parquet para almacenamiento intermedio"],
        ["python-dotenv",     "1.0.0",  "Gestión segura de credenciales (.env)"],
        ["Jupyter Notebook",  "7.x",    "Entorno interactivo para desarrollo y documentación"],
        ["Supabase",          "cloud",  "PostgreSQL como servicio — base de datos del DW"],
    ]
    story.append(tabla_simple(tools, [4.5*cm, 2.5*cm, 8.5*cm]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("5.2 Proceso ETL — 3 Etapas", S["H2"]))

    etapas = [
        ("ETAPA 1 — EXTRACCIÓN", "src/extract.py  |  notebooks/01_extract.ipynb",
         "Lee Amazon_Sale_Report.csv (128.975 filas, 24 columnas). "
         "Guarda copia intacta en data/01_raw/. "
         "Genera snapshot Parquet en data/02_interim/ para trazabilidad y auditoría."),
        ("ETAPA 2 — TRANSFORMACIÓN", "src/transform.py  |  notebooks/02_transform.ipynb",
         "Elimina columnas inútiles (index, Unnamed: 22, currency). "
         "Renombra 20+ campos a nombres limpios en español. "
         "Convierte tipos: fechas a DATE, cantidades a int, montos a float. "
         "Rellena nulos con defaults de config/settings.yaml. "
         "Normaliza strings: str.strip().upper() en ciudad/estado. "
         "Construye dimensiones por drop_duplicates() + reset_index(). "
         "Construye factVentas por groupby() + agg(SUM) separando ventas y cancelaciones. "
         "Guarda las 5 tablas como Parquet en data/03_processed/."),
        ("ETAPA 3 — CARGA", "src/load.py  |  notebooks/03_load.ipynb",
         "Conecta a PostgreSQL Supabase vía SQLAlchemy (credenciales en .env, nunca en código). "
         "Carga en orden: dimTiempo → dimProducto → dimGeografia → dimCanal → factVentas. "
         "Modo replace (carga inicial): elimina y recrea cada tabla. "
         "Verifica con COUNT(*) por tabla al finalizar."),
    ]
    for etapa, modulo, desc in etapas:
        story.append(KeepTogether([
            Paragraph(etapa, S["H3"]),
            Paragraph(f"<font color='#4F46E5' size='8'>{modulo}</font>", S["Body"]),
            Paragraph(desc, S["Body"]),
            Spacer(1, 0.15*cm),
        ]))

    story.append(Paragraph("5.3 Resultados de la Carga Inicial", S["H2"]))
    res = [
        ["Tabla", "Tipo", "Filas cargadas", "Estado"],
        ["dimTiempo",    "DIMENSIÓN",       "91",      "✓ OK"],
        ["dimProducto",  "DIMENSIÓN",       "7.053",   "✓ OK"],
        ["dimGeografia", "DIMENSIÓN",       "7.401",   "✓ OK"],
        ["dimCanal",     "DIMENSIÓN",       "4",       "✓ OK"],
        ["factVentas",   "TABLA DE HECHOS", "122.349", "✓ OK"],
    ]
    ts_res = TableStyle([
        ("BACKGROUND", (0,0),(-1,0), NAVY),
        ("TEXTCOLOR",  (0,0),(-1,0), WHITE),
        ("FONTNAME",   (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0),(-1,-1), 8),
        ("FONTNAME",   (0,1),(-1,-1), "Helvetica"),
        ("ALIGN",      (2,0),(-1,-1), "CENTER"),
        ("ALIGN",      (0,0),(1,-1), "LEFT"),
        ("BACKGROUND", (0,5),(-1,5), colors.HexColor("#FEF2F2")),
        ("TEXTCOLOR",  (1,5),(1,5),  RED),
        ("FONTNAME",   (0,5),(-1,5), "Helvetica-Bold"),
        ("GRID",       (0,0),(-1,-1), 0.4, colors.HexColor("#CBD5E1")),
        ("TOPPADDING", (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",(0,0),(-1,-1), 7),
    ])
    rt = Table(res, colWidths=[4*cm, 4*cm, 4*cm, 3.5*cm])
    rt.setStyle(ts_res)
    story.append(rt)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("5.4 Estrategia de Actualización", S["H2"]))
    act = [
        ["Componente", "Estrategia", "Modo", "Detalle"],
        ["dimTiempo",    "Borrar + recargar",    "replace", "91 filas. Recarga completa al agregar nuevas fechas."],
        ["dimProducto",  "Borrar + recargar",    "replace", "Detecta nuevas categorías/tallas/estilos."],
        ["dimGeografia", "Borrar + recargar",    "replace", "Detecta nuevas ciudades/estados."],
        ["dimCanal",     "Borrar + recargar",    "replace", "4 combinaciones, recarga trivial."],
        ["factVentas",   "Incremental por fecha","append",  "Filtra Fecha_Desde/Fecha_Hasta e inserta solo filas nuevas."],
    ]
    story.append(tabla_simple(act, [3*cm, 3.5*cm, 2.5*cm, 6.5*cm]))
    story.append(Paragraph("Frecuencia sugerida: mensual, al cierre de cada mes de operaciones.", S["Body"]))
    story.append(PageBreak())

    # ── DICCIONARIO ───────────────────────────────────────────────────────────
    story.append(Paragraph("6. Diccionario de Datos", S["H1"]))
    story.append(hr())

    diccionario = [
        ("dimTiempo", BLUE, [
            ["Columna","Tipo","Rango","Fórmula","Observaciones"],
            ["idTiempo",   "INTEGER", "1–91",            "—",              "PK autoincremental"],
            ["fecha",      "DATE",    "2022-03-31/06-29", "—",              "Fecha única por fila"],
            ["dia",        "SMALLINT","1–31",             "dt.day",         "—"],
            ["mes",        "SMALLINT","4, 5, 6",          "dt.month",       "Abr–Jun 2022"],
            ["nombre_mes", "VARCHAR", "April/May/June",   "dt.strftime(%B)","—"],
            ["trimestre",  "SMALLINT","2",                "dt.quarter",     "Solo Q2 de 2022"],
            ["anio",       "SMALLINT","2022",             "dt.year",        "—"],
        ]),
        ("dimProducto", BLUE, [
            ["Columna","Tipo","Rango","Fórmula","Observaciones"],
            ["idProducto","INTEGER","1–7.053",          "—","PK autoincremental"],
            ["categoria", "VARCHAR","Set, Kurta, Top…", "—","Campo Category del CSV"],
            ["talla",     "VARCHAR","S, M, L…6XL, Free","—","Campo Size del CSV"],
            ["estilo",    "VARCHAR","Alfanumérico",      "—","Campo Style del CSV · SKU Amazon"],
        ]),
        ("dimGeografia", BLUE, [
            ["Columna","Tipo","Rango","Fórmula","Observaciones"],
            ["idGeografia","INTEGER","1–7.401",       "—","PK autoincremental"],
            ["ciudad",    "VARCHAR", "Ciudades India", "—","Mayúsculas · nulos→'No Informado'"],
            ["estado",    "VARCHAR", "Estados India",  "—","Mayúsculas · nulos→'No Informado'"],
            ["pais",      "VARCHAR", "'IN'",           "—","Siempre India · nulos→'IN'"],
        ]),
        ("dimCanal", BLUE, [
            ["Columna","Tipo","Rango","Fórmula","Observaciones"],
            ["idCanal",          "INTEGER","1–4",                "—","PK · Solo 4 combinaciones"],
            ["tipo_fulfillment", "VARCHAR","Amazon/Merchant",    "—","Campo Fulfilment del CSV"],
            ["canal_ventas",     "VARCHAR","Amazon.in/Non-Amzn","—","Campo Sales Channel del CSV"],
            ["nivel_servicio",   "VARCHAR","Standard/Expedited", "—","Campo ship-service-level"],
        ]),
        ("factVentas", RED, [
            ["Columna","Tipo","Rango","Fórmula","Observaciones"],
            ["idProducto",        "INTEGER","1–7.053","—",                                      "FK+PK → dimProducto"],
            ["idGeografia",       "INTEGER","1–7.401","—",                                      "FK+PK → dimGeografia"],
            ["idTiempo",          "INTEGER","1–91",   "—",                                      "FK+PK → dimTiempo"],
            ["idCanal",           "INTEGER","1–4",    "—",                                      "FK+PK → dimCanal"],
            ["cantidad_vendida",  "INTEGER","≥ 0",    "SUM(Qty) Status≠'Cancelled'",            "Excluye canceladas"],
            ["monto_total",       "NUMERIC","≥ 0.0",  "SUM(Amount) Status≠'Cancelled'",         "En INR"],
            ["cantidad_cancelada","INTEGER","≥ 0",    "SUM(Qty) Status='Cancelled'",            "—"],
            ["monto_cancelado",   "NUMERIC","≥ 0.0",  "SUM(Amount) Status='Cancelled'",         "En INR"],
        ]),
    ]
    for tname, tcolor, tdata in diccionario:
        story.append(Paragraph(f"<b>{tname}</b>", ParagraphStyle("DH", parent=S["H3"],
            textColor=tcolor, spaceBefore=10)))
        story.append(tabla_simple(tdata,
            [3.2*cm, 2.2*cm, 3*cm, 3.6*cm, 3.5*cm], header_bg=tcolor))
        story.append(Spacer(1, 0.15*cm))
    story.append(PageBreak())

    # ── BOCETOS ───────────────────────────────────────────────────────────────
    story.append(Paragraph("7. Bocetos de Reportes y Tableros", S["H1"]))
    story.append(hr())

    story.append(Paragraph("Reportes", S["H2"]))
    rep = [
        ["Atributo", "Reporte 1\nVentas por Categ. y Período", "Reporte 2\nPerformance Geográfica", "Reporte 3\nAnálisis de Cancelaciones"],
        ["Agrupamiento",  "Categoría + Mes",          "Estado + Categoría",        "Status + Categoría + Canal"],
        ["Gráfico",       "Barras apiladas",           "Mapa de calor (heatmap)",   "Torta + barras comparativas"],
        ["Parámetro",     "Rango de fechas",           "Categoría seleccionada",    "Canal fulfillment (Amzn/Merch)"],
        ["Función",       "Variación % mes a mes",     "Ranking estados por monto", "Tasa cancelación %"],
        ["Subreporte",    "—",                          "Detalle por ciudad",        "—"],
        ["Responde",      "P1, P2",                    "P1",                        "P3, P4"],
    ]
    story.append(tabla_simple(rep, [3*cm, 4.5*cm, 4.5*cm, 3.5*cm]))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Tableros", S["H2"]))
    tab = [
        ["Atributo", "Tablero 1\nResumen Ejecutivo", "Tablero 2\nMapa Geográfico", "Tablero 3\nFulfillment y Canal"],
        ["Filtros",     "Período, Categoría, Estado",    "Categoría, Fulfillment",     "Canal, Nivel Servicio, Período"],
        ["KPIs",        "Ventas (INR), Unidades,\nTicket Promedio", "—",             "—"],
        ["Gráfico",     "Línea temporal ventas",         "Distribución por estado",    "Amazon vs Merchant (barras)"],
        ["Tabla",       "Top 5 categorías por monto",    "Ranking ciudades",           "Tasa entrega exitosa por canal"],
        ["Interacción", "Filtro cruzado KPIs↔gráfico",  "Click → drill-down ciudad",  "Drill-down nivel de servicio"],
        ["Responde",    "P1, P2",                        "P1",                         "P3, P4"],
    ]
    story.append(tabla_simple(tab, [3*cm, 4.5*cm, 4.5*cm, 3.5*cm]))
    story.append(PageBreak())

    # ── CONCLUSIÓN ───────────────────────────────────────────────────────────
    story.append(Paragraph("8. Conclusión", S["H1"]))
    story.append(hr())
    conclusiones = [
        ("Cobertura metodológica completa",
         "El proyecto aplicó la metodología HEFESTO v3 en sus cuatro etapas: Análisis de Requerimientos, "
         "Análisis de Data Sources, Modelo Lógico y Integración de Datos. Cada etapa generó la entrada "
         "de la siguiente, garantizando trazabilidad y coherencia a lo largo del proceso."),
        ("Calidad de datos",
         "Se detectaron y resolvieron seis tipos de problemas de calidad en el dataset original "
         "(nulos en courier status, amount, city, state, promotion-ids y fulfilled-by). Las decisiones "
         "de limpieza fueron documentadas y configurables vía settings.yaml, asegurando reproducibilidad."),
        ("Modelo dimensional sólido",
         "El Esquema Estrella resultante (factVentas + 4 dimensiones) está correctamente normalizado, "
         "con clave primaria compuesta por los cuatro identificadores foráneos. La separación de ventas "
         "efectivas y cancelaciones en la misma tabla de hechos permite responder las cuatro preguntas "
         "de negocio con consultas simples."),
        ("ETL funcional y escalable",
         "El pipeline Python es modular (extract / transform / load), reproducible y completamente "
         "desacoplado de las credenciales. La carga exitosa de 122.349 filas en Supabase valida el "
         "funcionamiento end-to-end. La arquitectura soporta carga incremental mensual con mínimas "
         "modificaciones (modo append en factVentas + filtro por fechas)."),
        ("Hallazgos del análisis",
         "La categoría 'Set' concentra el mayor volumen de ventas en unidades. Maharashtra y Karnataka "
         "lideran en monto de ventas. El canal Amazon Fulfillment presenta menor tasa de cancelación "
         "que Merchant. El nivel de servicio Expedited predomina en categorías de mayor valor unitario."),
    ]
    for titulo, texto in conclusiones:
        story.append(KeepTogether([
            Paragraph(f"<b>{titulo}</b>", S["H3"]),
            Paragraph(texto, S["Body"]),
            Spacer(1, 0.15*cm),
        ]))
    story.append(PageBreak())

    # ── BIBLIOGRAFÍA ──────────────────────────────────────────────────────────
    story.append(Paragraph("9. Bibliografía", S["H1"]))
    story.append(hr())
    refs = [
        "[1] Bernabeu, R. D. &amp; García Mattío, M. A. (2018). <b>HEFESTO v3.0 — Metodología para la Construcción de un Data Warehouse.</b> Córdoba, Argentina.",
        "[2] The Devastator (2022). <b>Amazon Sale Report — Unlock Profits with E-Commerce Sales Data</b> [Dataset]. Kaggle. https://www.kaggle.com/datasets/thedevastator/unlock-profits-with-e-commerce-sales-data",
        "[3] pandas Development Team (2024). <b>pandas 2.2 Documentation.</b> https://pandas.pydata.org/docs/",
        "[4] SQLAlchemy Authors (2024). <b>SQLAlchemy 2.0 Documentation.</b> https://docs.sqlalchemy.org/en/20/",
        "[5] Supabase, Inc. (2024). <b>Supabase Docs — PostgreSQL Database.</b> https://supabase.com/docs",
        "[6] psycopg (2024). <b>Psycopg 2 Documentation.</b> https://www.psycopg.org/docs/",
        "[7] Python Software Foundation (2024). <b>Python 3.12 Documentation.</b> https://docs.python.org/3.12/",
        "[8] Inmon, W. H. (2005). <b>Building the Data Warehouse</b> (4th ed.). Wiley Publishing.",
        "[9] Kimball, R. &amp; Ross, M. (2013). <b>The Data Warehouse Toolkit</b> (3rd ed.). John Wiley &amp; Sons.",
    ]
    for ref in refs:
        story.append(Paragraph(ref,
            ParagraphStyle("Ref", parent=S["Body"], leftIndent=20, firstLineIndent=-20, spaceAfter=6)))

    doc.build(story)
    print(f"[OK] PDF → {pdf_path}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    base = "data"
    der_path = os.path.join(base, "der_amazon_dw_v2.png")
    mc_path  = os.path.join(base, "modelo_conceptual.png")
    pdf_path = os.path.join(base, "informe_final.pdf")

    print("Generando DER...")
    generar_der(der_path)

    print("Generando Modelo Conceptual...")
    generar_modelo_conceptual(mc_path)

    print("Compilando PDF...")
    build_pdf(pdf_path, der_path, mc_path)

    print("\n✅ Todo generado:")
    print(f"   {der_path}")
    print(f"   {mc_path}")
    print(f"   {pdf_path}")
