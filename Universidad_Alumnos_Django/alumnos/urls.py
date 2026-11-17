from django.urls import path
from . import views

app_name = "alumnos"

urlpatterns = [
    path("", views.index, name="index"),
    path("index/", views.index, name="index_page"),
    path("grafico1/", views.grafico1, name="grafico1"),
    path("grafico2/", views.grafico2, name="grafico2"),
    path("grafico3/", views.grafico3, name="grafico3"),
    path("grafico4/", views.grafico4, name="grafico4"),
    path("graficos/dispersion/", views.graficoDispersion, name="graficoDispersion"),
    path("nuevo/", views.alumno_crear, name="alumno_crear"),
    path("<int:pk>/editar/", views.alumno_editar, name="alumno_editar"),
    path("<int:pk>/eliminar/", views.alumno_eliminar, name="alumno_eliminar"),
    path("graficos/barras-csv/", views.graficoBarras, name="graficoBarras"),
    path("graficos/lineas-csv/",views.graficoLineas,name="graficoLineas"),
    path("listados/industria/",views.listadoIndustria,name="listadoIndustria"),
    path("listados/horas-edad/",views.listadoHorasEdad,name="listadoHorasEdad"),
    path("listados/equilibrio/",views.listadoEquilibrio,name="listadoEquilibrio"),
    path("listados/", views.pagina_listados, name="pagina_listados"),
    path("graficos/", views.pagina_graficos, name="pagina_graficos"),
    path("graficos/edad-experiencia/",views.graficoEdadExperiencia,name="graficoEdadExperiencia"),

    # Certamen 3: gráfico dinámico y nuevo reporte
    path("graficos/estres-modalidad/", views.graficoEstresModalidad, name="graficoEstresModalidad"),
    path("listados/estres-modalidad/", views.listadoEstresModalidad, name="listadoEstresModalidad"),

    # Certamen 3: descargas en PDF y Excel de los cuatro reportes
    path("listados/industria/pdf/", views.listadoIndustriaPdf, name="listadoIndustriaPdf"),
    path("listados/industria/excel/", views.listadoIndustriaExcel, name="listadoIndustriaExcel"),
    path("listados/horas-edad/pdf/", views.listadoHorasEdadPdf, name="listadoHorasEdadPdf"),
    path("listados/horas-edad/excel/", views.listadoHorasEdadExcel, name="listadoHorasEdadExcel"),
    path("listados/equilibrio/pdf/", views.listadoEquilibrioPdf, name="listadoEquilibrioPdf"),
    path("listados/equilibrio/excel/", views.listadoEquilibrioExcel, name="listadoEquilibrioExcel"),
    path("listados/estres-modalidad/pdf/", views.listadoEstresModalidadPdf, name="listadoEstresModalidadPdf"),
    path("listados/estres-modalidad/excel/", views.listadoEstresModalidadExcel, name="listadoEstresModalidadExcel"),
]
