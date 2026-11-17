from io import BytesIO
from xml.sax.saxutils import escape
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from .reportes import formato

# Crean el PDF y el Excel de un reporte a partir del mismo diccionario
# que muestra listado.html (ver reportes.py).


def generar_pdf(datos):
    buffer = BytesIO()
    documento = SimpleDocTemplate(
        buffer, pagesize=landscape(A4), rightMargin=36, leftMargin=36,
        topMargin=36, bottomMargin=36, title=datos["titulo"],
    )
    estilos = getSampleStyleSheet()
    celda = ParagraphStyle("Celda", fontName="Helvetica", fontSize=10, leading=13)

    # Título y explicación, igual que en la página
    elementos = [Paragraph(escape(datos["titulo"]), estilos["Title"]),
                 Paragraph(escape(datos["explicacion"]), estilos["Normal"])]
    for detalle in datos.get("detalles", []):
        elementos.append(Paragraph(escape(detalle), estilos["Normal"]))
    if datos.get("texto_filtros"):
        elementos.append(Paragraph(escape("Filtros: " + datos["texto_filtros"]), estilos["Normal"]))
    elementos.append(Spacer(1, 12))

    # Tabla con encabezados y filas (Paragraph ajusta el texto largo en la celda)
    columnas = datos["columnas"]
    filas = [[Paragraph(escape(columna), celda) for columna in columnas]]
    for fila in datos["filas"]:
        filas.append([Paragraph(escape(formato(valor)), celda) for valor in fila])
    if datos.get("total"):
        filas.append([Paragraph(escape(formato(valor)), celda) for valor in datos["total"]])
    if not datos["filas"]:
        filas.append([Paragraph("No hay datos para los filtros seleccionados.", celda)]
                     + [""] * (len(columnas) - 1))
    ancho = (landscape(A4)[0] - 72) / len(columnas)
    tabla = Table(filas, colWidths=[ancho] * len(columnas), repeatRows=1)
    formato_tabla = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE6F1")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
    if not datos["filas"]:
        formato_tabla.append(("SPAN", (0, 1), (-1, 1)))
    tabla.setStyle(TableStyle(formato_tabla))
    elementos.append(tabla)

    if datos.get("interpretacion"):
        elementos.append(Spacer(1, 12))
        elementos.append(Paragraph(escape("Interpretación: " + datos["interpretacion"]),
                                   estilos["Normal"]))
    documento.build(elementos)
    buffer.seek(0)
    return buffer


def generar_excel(datos):
    libro = Workbook()  # Crear el archivo Excel en memoria.
    hoja = libro.active
    hoja.title = "Reporte"
    hoja.append(datos["columnas"])
    for fila in datos["filas"]:
        hoja.append(fila)  # Los números quedan guardados como números.
    if datos.get("total"):
        hoja.append(datos["total"])
    borde = Side(style="thin", color="D9D9D9")
    for fila in hoja:
        for celda in fila:
            celda.border = Border(left=borde, right=borde, top=borde, bottom=borde)
    for celda in hoja[1]:
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor="1F4E78")
    for numero, columna in enumerate(datos["columnas"], start=1):
        hoja.column_dimensions[get_column_letter(numero)].width = len(columna) + 6
    hoja.freeze_panes = "A2"  # Mantener visible el encabezado al desplazarse.
    buffer = BytesIO()
    libro.save(buffer)
    buffer.seek(0)
    return buffer
