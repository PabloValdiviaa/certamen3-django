from django.shortcuts import render
from .models import Alumno, Trabajador
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import matplotlib
from django.shortcuts import render, redirect, get_object_or_404
from .forms import AlumnoForm
from collections import Counter, defaultdict
from django.http import FileResponse
from . import reportes
from .exportar import generar_pdf, generar_excel

# Certamen 3: los datos ya no se leen desde datos.csv en cada visita, sino desde
# la tabla Trabajador de la base SQLite (se carga con: python manage.py cargar_datos).

def index(request):
    alumnos = Alumno.objects.all().order_by("apellido_paterno", "nombres")
    return render(request, "alumnos/index.html", {"alumnos": alumnos})

matplotlib.use("Agg") # Dibujar sin abrir una ventana gráfica
def grafico1(request):
    # Dataset del ejemplo: número de alumnos por asignatura
    asignaturas = ["Python", "Bases de datos", "Django", "Redes"]
    cantidades = [18, 14, 21, 11]
    # Crear el gráfico de barras a partir de ambas listas
    figura, eje = plt.subplots(figsize=(8, 4.5))
    barras = eje.bar(asignaturas, cantidades, color="#2874A6")
    eje.set_title("Alumnos por asignatura")
    eje.set_xlabel("Asignatura")
    eje.set_ylabel("Cantidad de alumnos")
    eje.set_ylim(0, max(cantidades) + 5)
    eje.bar_label(barras, padding=3)
    figura.tight_layout()
    # Convertir la imagen PNG a texto para enviarla a HTML
    buffer = BytesIO()
    figura.savefig(buffer, format="png", dpi=120)
    plt.close(figura)
    buffer.seek(0)
    grafico = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()
    contexto = {"grafico": grafico}
    return render(request, "alumnos/grafico1.html", contexto)
def grafico2(request):
    # Dataset: asistencia semanal a un taller
    semanas = [1, 2, 3, 4, 5]
    asistentes = [12, 16, 14, 20, 24]
    figura, eje = plt.subplots(figsize=(8, 4.5))
    eje.plot(semanas, asistentes, marker="o", color="#2874A6", linewidth=2)
    eje.set_title("Asistencia semanal al taller")
    eje.set_xlabel("Semana")
    eje.set_ylabel("Cantidad de asistentes")
    eje.set_xticks(semanas)
    eje.grid(True, alpha=0.3)
    figura.tight_layout()
    buffer = BytesIO()
    figura.savefig(buffer, format="png", dpi=120)
    plt.close(figura)
    buffer.seek(0)
    grafico = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()
    return render(request, "alumnos/grafico2.html", {"grafico": grafico})   
def grafico3(request):
    # Dataset: horas de estudio y notas de ocho estudiantes
    horas = [1, 2, 2, 3, 4, 5, 6, 7]
    notas = [2.8, 3.4, 4.0, 4.2, 5.1, 5.0, 6.2, 6.5]
    figura, eje = plt.subplots(figsize=(8, 4.5))
    eje.scatter(horas, notas, color="#1E8449", s=80)
    eje.set_title("Horas de estudio y notas")
    eje.set_xlabel("Horas de estudio")
    eje.set_ylabel("Nota")
    eje.set_ylim(1, 7)
    eje.grid(True, alpha=0.3)
    figura.tight_layout()
    buffer = BytesIO()
    figura.savefig(buffer, format="png", dpi=120)
    plt.close(figura)
    buffer.seek(0)
    grafico = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()
    return render(request, "alumnos/grafico3.html", {"grafico": grafico})
def grafico4(request):
    # Dataset: alumnos inscritos por actividad
    actividades = ["Programación", "Robótica", "Diseño", "Redes"]
    inscritos = [12, 8, 6, 4]
    figura, eje = plt.subplots(figsize=(7, 5))
    eje.pie(inscritos, labels=actividades, autopct="%1.1f%%",
        startangle=90, colors=["#2874A6", "#1E8449", "#F4D03F", "#AF7AC5"])
    eje.set_title("Inscripciones por actividad")
    eje.axis("equal") # Mantener el círculo sin deformaciones
    figura.tight_layout()
    buffer = BytesIO()
    figura.savefig(buffer, format="png", dpi=120)
    plt.close(figura)
    buffer.seek(0)
    grafico = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()
    return render(request, "alumnos/grafico4.html", {"grafico": grafico})  

def alumno_crear(request):
    if request.method == "POST":
        form = AlumnoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("alumnos:index")
    else:
        form = AlumnoForm()
    contexto = {"form": form, "titulo": "Nuevo alumno"}
    return render(request, "alumnos/alumno_form.html", contexto) 

def alumno_editar(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    if request.method == "POST":
        form = AlumnoForm(request.POST, instance=alumno)
        if form.is_valid():
            form.save()
            return redirect("alumnos:index")
    else:
        form = AlumnoForm(instance=alumno)
    contexto = {"form": form, "titulo": "Editar alumno"}
    return render(request, "alumnos/alumno_form.html", contexto)

def alumno_eliminar(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    if request.method == "POST":
        alumno.delete()
        return redirect("alumnos:index")
    return render(
        request, "alumnos/alumno_confirmar_eliminar.html",
        {"alumno": alumno},
    )

def graficoDispersion(request):
    puntos = [{"x": trabajador.horas_semanales,
            "y": trabajador.equilibrio_vida_trabajo,}
        for trabajador in Trabajador.objects.all()]
    configuracion = {
        "type": "scatter",
        "data": {
            "datasets": [{
                "label": "Cada punto representa un trabajador",
                "data": puntos,
                "backgroundColor": "#c0392b",}],},
        "options": {
            "plugins": {
                "legend": {"display": False},
                "tooltip": {
                    "enabled": False,},},
            "scales": {
                "x": {"title": {
                        "display": True,
                        "text": "Horas trabajadas por semana",},},
                "y": {"title": {
                        "display": True,
                        "text": "Calificación del equilibrio vida-trabajo",},},},},}
    return render(request, "alumnos/grafico.html", {
        "titulo": "Horas trabajadas y equilibrio vida-trabajo",
        "explicacion": "Cada punto representa un trabajador.", "datos_grafico": configuracion,})

def graficoBarras(request):
    cantidades = Counter(
        trabajador.industria for trabajador in Trabajador.objects.all())
    configuracion = {
        "type": "bar",
        "data": {
            "labels": list(cantidades.keys()),
            "datasets": [{
                "label": "Cantidad de trabajadores",
                "data": list(cantidades.values()),
                "backgroundColor": "#c0392b",}],},
        "options": {
            "plugins": {
                "legend": {"display": False},
                "tooltip": {"enabled": False},},
            "scales": {
                "x": {
                    "title": {"display": True, "text": "Industria"},},
                "y": {
                    "beginAtZero": True,
                    "title": {"display": True, "text": "Cantidad de trabajadores"},},},},}
    return render(request, "alumnos/grafico.html", {
        "titulo": "Trabajadores por industria",
        "explicacion": "Compara la cantidad de trabajadores registrados en cada industria.",
        "datos_grafico": configuracion,})

def graficoLineas(request):
    horas_por_edad = defaultdict(list)
    for trabajador in Trabajador.objects.all():
        horas_por_edad[trabajador.edad].append(trabajador.horas_semanales)
    edades = sorted(horas_por_edad.keys())
    promedios = [sum(horas_por_edad[edad]) / len(horas_por_edad[edad])
        for edad in edades]
    configuracion = {"type": "line",
        "data": {"labels": [str(edad) for edad in edades],
            "datasets": [{"label": "Promedio de horas semanales",
                "data": promedios, "borderColor": "#2874a6",
                "backgroundColor": "#2874a6", "tension": 0.3,}],},
        "options": {
            "plugins": {"legend": {"display": False},"tooltip": {"enabled": False},},
            "scales": {
                "x": {"title": {"display": True, "text": "Edad"},},
                "y": {"beginAtZero": True,
                    "title": {"display": True,
                        "text": "Promedio de horas trabajadas por semana",},},},},}
    return render(request, "alumnos/grafico.html", {
        "titulo": "Horas semanales promedio según edad",
        "explicacion": "Muestra el promedio de horas trabajadas por semana para cada edad.",
        "datos_grafico": configuracion,})

# Los datos de cada reporte están en reportes.py, para usarlos también en el PDF y el Excel.
def listadoIndustria(request):
    return render(request, "alumnos/listado.html", reportes.datos_industria())

def listadoHorasEdad(request):
    return render(request, "alumnos/listado.html", reportes.datos_horas_edad())

def listadoEquilibrio(request):
    return render(request, "alumnos/listado.html", reportes.datos_equilibrio())

def pagina_listados(request):
    return render(request, "alumnos/pagina_listados.html")

def pagina_graficos(request):
    return render(request, "alumnos/pagina_graficos.html")

def graficoEdadExperiencia(request):
    puntos = []
    for trabajador in Trabajador.objects.all():
        puntos.append({"x": trabajador.edad, "y": trabajador.anios_experiencia,})
    configuracion = {
        "type": "scatter",
        "data": {"datasets": [{"label": "Trabajadores",
                "data": puntos,
                "backgroundColor": "rgba(40, 116, 166, 0.2)",
                "pointRadius": 2,}],},
        "options": {"plugins": {"legend": {"display": False},
                "tooltip": {"enabled": False},},
            "scales": {"x": {"title": {"display": True,
                        "text": "Edad (años)",},},
                "y": {"title": {"display": True,
                        "text": "Años de experiencia",},},},},}
    contexto = {"titulo": "Edad y años de experiencia",
        "explicacion": ("Cada punto representa a un trabajador. "
        "El gráfico compara su edad con sus años de experiencia."),
        "datos_grafico": configuracion,}
    return render(request, "alumnos/grafico.html", contexto)


# ================================ Certamen 3: gráfico dinámico y nuevo reporte
def leer_filtros(request):
    # Los filtros llegan en la dirección, por ejemplo: ?industria=IT&edad_min=30
    return {
        "industria": request.GET.get("industria", ""),
        "region": request.GET.get("region", ""),
        "edad_min": request.GET.get("edad_min", ""),
        "edad_max": request.GET.get("edad_max", ""),
    }

def opciones_filtros():
    # Industrias y regiones distintas que hay en la base, para las listas desplegables.
    trabajadores = Trabajador.objects.all()
    return {
        "industrias": sorted(set(trabajador.industria for trabajador in trabajadores)),
        "regiones": sorted(set(trabajador.region for trabajador in trabajadores)),
    }

def graficoEstresModalidad(request):
    filtros = leer_filtros(request)
    filas = reportes.estres_por_modalidad(filtros)  # La misma función del nuevo reporte.
    configuracion = {
        "type": "bar",
        "data": {
            "labels": [fila[0] for fila in filas],
            "datasets": [
                {"label": "Estrés bajo", "data": [fila[1] for fila in filas],
                 "backgroundColor": "#1E8449"},
                {"label": "Estrés medio", "data": [fila[2] for fila in filas],
                 "backgroundColor": "#D4AC0D"},
                {"label": "Estrés alto", "data": [fila[3] for fila in filas],
                 "backgroundColor": "#C0392B"},],},
        "options": {
            "scales": {
                "x": {"title": {"display": True, "text": "Modalidad de trabajo"},},
                "y": {"beginAtZero": True,
                    "title": {"display": True, "text": "Cantidad de trabajadores"},},},},}
    contexto = opciones_filtros()
    contexto["titulo"] = "Nivel de estrés según modalidad de trabajo"
    contexto["filtros"] = filtros
    contexto["total"] = sum(fila[4] for fila in filas)
    contexto["datos_grafico"] = configuracion
    return render(request, "alumnos/grafico_dinamico.html", contexto)

def listadoEstresModalidad(request):
    filtros = leer_filtros(request)
    contexto = reportes.datos_estres_modalidad(filtros)
    contexto.update(opciones_filtros())
    contexto["filtros"] = filtros
    return render(request, "alumnos/listado.html", contexto)


# ===================================== Certamen 3: descargas en PDF y Excel
# Igual que en la guía: se genera el archivo en memoria y se envía con FileResponse.
def listadoIndustriaPdf(request):
    archivo = generar_pdf(reportes.datos_industria())
    return FileResponse(archivo, as_attachment=True, filename="reporte_industria.pdf")

def listadoIndustriaExcel(request):
    archivo = generar_excel(reportes.datos_industria())
    return FileResponse(archivo, as_attachment=True, filename="reporte_industria.xlsx")

def listadoHorasEdadPdf(request):
    archivo = generar_pdf(reportes.datos_horas_edad())
    return FileResponse(archivo, as_attachment=True, filename="reporte_horas_edad.pdf")

def listadoHorasEdadExcel(request):
    archivo = generar_excel(reportes.datos_horas_edad())
    return FileResponse(archivo, as_attachment=True, filename="reporte_horas_edad.xlsx")

def listadoEquilibrioPdf(request):
    archivo = generar_pdf(reportes.datos_equilibrio())
    return FileResponse(archivo, as_attachment=True, filename="reporte_equilibrio.pdf")

def listadoEquilibrioExcel(request):
    archivo = generar_excel(reportes.datos_equilibrio())
    return FileResponse(archivo, as_attachment=True, filename="reporte_equilibrio.xlsx")

def listadoEstresModalidadPdf(request):
    archivo = generar_pdf(reportes.datos_estres_modalidad(leer_filtros(request)))
    return FileResponse(archivo, as_attachment=True, filename="reporte_estres_modalidad.pdf")

def listadoEstresModalidadExcel(request):
    archivo = generar_excel(reportes.datos_estres_modalidad(leer_filtros(request)))
    return FileResponse(archivo, as_attachment=True, filename="reporte_estres_modalidad.xlsx")
