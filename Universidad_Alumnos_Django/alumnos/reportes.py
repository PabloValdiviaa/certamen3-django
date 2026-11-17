from collections import Counter, defaultdict
from .models import Trabajador

# Datos de los cuatro reportes, leídos desde la base SQLite (tabla Trabajador).
# Cada función devuelve el diccionario que muestra listado.html. Las vistas de
# PDF y Excel usan el mismo diccionario, así los archivos coinciden con la página.

MODALIDADES = [("Remote", "Remoto"), ("Hybrid", "Híbrido"), ("Onsite", "Presencial")]

def formato(valor):
    # Mostrar los decimales con coma, igual que en la página.
    return str(valor).replace(".", ",")


# ---------------------------------------------- Reportes del Certamen 2
def datos_industria():
    cantidades = Counter(trabajador.industria for trabajador in Trabajador.objects.all())
    filas_tabla = [
        [industria, cantidad]
        for industria, cantidad in sorted(
            cantidades.items(),
            key=lambda elemento: elemento[1],
            reverse=True)]
    return {
        "titulo": "Trabajadores por industria",
        "explicacion": (
            "La tabla muestra cuántos trabajadores pertenecen "
            "a cada industria."),
        "columnas": ["Industria", "Cantidad de trabajadores"],
        "filas": filas_tabla,
        "url_pdf": "alumnos:listadoIndustriaPdf",
        "url_excel": "alumnos:listadoIndustriaExcel",
    }

def datos_horas_edad():
    horas_por_edad = defaultdict(list)
    for trabajador in Trabajador.objects.all():
        horas_por_edad[trabajador.edad].append(trabajador.horas_semanales)
    filas_tabla = [
        [edad, round(sum(horas) / len(horas), 1)]
        for edad, horas in sorted(horas_por_edad.items())
        if horas]
    return {
        "titulo": "Horas trabajadas según edad",
        "explicacion": (
            "La tabla muestra el promedio de horas trabajadas según diferentes edades."
        ),
        "columnas": ["Edad", "Promedio de horas por semana"],
        "filas": filas_tabla,
        "url_pdf": "alumnos:listadoHorasEdadPdf",
        "url_excel": "alumnos:listadoHorasEdadExcel",
    }

def datos_equilibrio():
    horas_por_calificacion = defaultdict(list)
    for trabajador in Trabajador.objects.all():
        horas_por_calificacion[trabajador.equilibrio_vida_trabajo].append(
            trabajador.horas_semanales)
    filas_tabla = [
        [calificacion, len(horas), round(sum(horas) / len(horas), 1)]
        for calificacion, horas in sorted(horas_por_calificacion.items())
        if horas]
    return {
        "titulo": "Equilibrio entre vida y trabajo",
        "explicacion": (
            "La tabla muestra cuántos trabajadores tienen cada "
            "calificación de equilibrio y sus horas semanales promedio."),
        "columnas": [
            "Calificación de equilibrio",
            "Cantidad de trabajadores",
            "Promedio de horas por semana"],
        "filas": filas_tabla,
        "url_pdf": "alumnos:listadoEquilibrioPdf",
        "url_excel": "alumnos:listadoEquilibrioExcel",
    }


# ------------------------------- Certamen 3: gráfico dinámico y nuevo reporte
def trabajadores_filtrados(filtros):
    # Aplicar a la tabla Trabajador solo los filtros que el usuario eligió.
    trabajadores = Trabajador.objects.all()
    if filtros["industria"]:
        trabajadores = trabajadores.filter(industria=filtros["industria"])
    if filtros["region"]:
        trabajadores = trabajadores.filter(region=filtros["region"])
    if filtros["edad_min"].isdigit():
        trabajadores = trabajadores.filter(edad__gte=int(filtros["edad_min"]))
    if filtros["edad_max"].isdigit():
        trabajadores = trabajadores.filter(edad__lte=int(filtros["edad_max"]))
    return trabajadores

def estres_por_modalidad(filtros):
    # Una fila por modalidad: [modalidad, bajo, medio, alto, total, % estrés alto].
    # La usan el gráfico dinámico y el nuevo reporte, por eso siempre coinciden.
    trabajadores = trabajadores_filtrados(filtros)
    filas = []
    for codigo, modalidad in MODALIDADES:
        grupo = trabajadores.filter(modalidad=codigo)
        bajo = grupo.filter(nivel_estres="Low").count()
        medio = grupo.filter(nivel_estres="Medium").count()
        alto = grupo.filter(nivel_estres="High").count()
        total = bajo + medio + alto
        porcentaje_alto = round(alto * 100 / total, 1) if total > 0 else 0.0
        filas.append([modalidad, bajo, medio, alto, total, porcentaje_alto])
    return filas

def datos_estres_modalidad(filtros):
    filas = estres_por_modalidad(filtros)
    total = sum(fila[4] for fila in filas)
    fila_total = None
    interpretacion = ""
    if total > 0:
        alto = sum(fila[3] for fila in filas)
        fila_total = ["Total", sum(fila[1] for fila in filas),
                      sum(fila[2] for fila in filas), alto, total,
                      round(alto * 100 / total, 1)]
        con_datos = [fila for fila in filas if fila[4] > 0]
        mayor = max(con_datos, key=lambda fila: fila[5])
        menor = min(con_datos, key=lambda fila: fila[5])
        interpretacion = (
            f"Con estos filtros, la modalidad con más estrés alto es {mayor[0].lower()} "
            f"({formato(mayor[5])} %) y la que tiene menos es {menor[0].lower()} "
            f"({formato(menor[5])} %).")
        if mayor[5] - menor[5] < 5:
            interpretacion += (" La diferencia es pequeña, así que la modalidad de "
                               "trabajo no parece influir en el nivel de estrés.")
    else:
        filas = []
    return {
        "titulo": "Nivel de estrés según modalidad de trabajo",
        "explicacion": (
            "La tabla muestra los datos del gráfico dinámico: cuántos trabajadores "
            "tienen estrés bajo, medio y alto en cada modalidad de trabajo."),
        "detalles": [
            "Origen de los datos: tabla Trabajador de la base de datos SQLite, cargada "
            "desde datos.csv (dataset Impact of Remote Work on Mental Health, Kaggle).",
            "Variables: modalidad de trabajo, nivel de estrés, industria, región y edad.",
            "Filtros: industria, región y rango de edad. Sin filtros se consideran "
            "los 5.000 trabajadores.",
            "Cálculos: se cuentan los trabajadores de cada modalidad y nivel de estrés. "
            "El % de estrés alto es alto / total × 100.",
        ],
        "texto_filtros": (
            f"Industria: {filtros['industria'] or 'Todas'} · "
            f"Región: {filtros['region'] or 'Todas'} · "
            f"Edad: {filtros['edad_min'] or 'sin mínimo'} a {filtros['edad_max'] or 'sin máximo'}"),
        "columnas": ["Modalidad de trabajo", "Estrés bajo", "Estrés medio",
                     "Estrés alto", "Total", "% estrés alto"],
        "filas": filas,
        "total": fila_total,
        "interpretacion": interpretacion,
        "url_pdf": "alumnos:listadoEstresModalidadPdf",
        "url_excel": "alumnos:listadoEstresModalidadExcel",
    }
