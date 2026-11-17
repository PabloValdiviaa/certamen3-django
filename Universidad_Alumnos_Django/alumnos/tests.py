import csv
from collections import Counter, defaultdict
from io import BytesIO, StringIO

from django.core.management import call_command
from django.test import TestCase
from openpyxl import load_workbook

from .management.commands.cargar_datos import RUTA_CSV
from .models import Trabajador

REPORTES = {
    "industria": "/alumnos/listados/industria/",
    "horas-edad": "/alumnos/listados/horas-edad/",
    "equilibrio": "/alumnos/listados/equilibrio/",
    "estres-modalidad": "/alumnos/listados/estres-modalidad/",
}
FILTROS = {"industria": "IT", "region": "Europe", "edad_min": "30", "edad_max": "45"}


class ProyectoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("cargar_datos", stdout=StringIO())
        with open(RUTA_CSV, newline="", encoding="utf-8-sig") as archivo:
            cls.csv = list(csv.DictReader(archivo))

    def test_base_de_datos_tiene_todo_el_csv(self):
        self.assertEqual(Trabajador.objects.count(), len(self.csv))

    def test_reportes_del_certamen_2_dan_lo_mismo_que_con_el_csv(self):
        cantidades = Counter(fila["Industry"] for fila in self.csv)
        filas = self.client.get(REPORTES["industria"]).context["filas"]
        self.assertEqual(dict(filas), dict(cantidades))

        horas = defaultdict(list)
        for fila in self.csv:
            horas[int(fila["Age"])].append(float(fila["Hours_Worked_Per_Week"]))
        esperado = [[e, round(sum(h) / len(h), 1)] for e, h in sorted(horas.items())]
        self.assertEqual(self.client.get(REPORTES["horas-edad"]).context["filas"], esperado)

    def test_todas_las_paginas_responden(self):
        for url in ["/alumnos/", "/alumnos/graficos/", "/alumnos/listados/",
                    "/alumnos/graficos/barras-csv/", "/alumnos/graficos/lineas-csv/",
                    "/alumnos/graficos/dispersion/", "/alumnos/graficos/estres-modalidad/",
                    *REPORTES.values()]:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_grafico_dinamico_coincide_con_el_reporte_y_con_el_csv(self):
        grafico = self.client.get("/alumnos/graficos/estres-modalidad/", FILTROS)
        reporte = self.client.get(REPORTES["estres-modalidad"], FILTROS)
        filas = reporte.context["filas"]
        for i, dataset in enumerate(grafico.context["datos_grafico"]["data"]["datasets"]):
            self.assertEqual(dataset["data"], [fila[1 + i] for fila in filas])
        seleccion = [f for f in self.csv if f["Industry"] == "IT" and f["Region"] == "Europe"
                     and 30 <= int(f["Age"]) <= 45]
        self.assertEqual(reporte.context["total"][4], len(seleccion))

    def test_mensaje_sin_datos(self):
        sin_datos = self.client.get("/alumnos/graficos/estres-modalidad/",
                                    {"edad_min": "65", "edad_max": "70"})
        self.assertContains(sin_datos, "No hay datos para la selección actual")
        al_reves = self.client.get(REPORTES["estres-modalidad"], {"edad_min": "50", "edad_max": "30"})
        self.assertContains(al_reves, "No hay datos disponibles")

    def test_cada_reporte_tiene_los_dos_botones(self):
        for nombre, url in REPORTES.items():
            respuesta = self.client.get(url)
            self.assertContains(respuesta, "Descarga en PDF")
            self.assertContains(respuesta, "Descarga en Excel")
            self.assertContains(respuesta, f"/alumnos/listados/{nombre}/pdf/")

    def test_descargas_validas_y_con_filtros(self):
        for nombre, url in REPORTES.items():
            pdf = self.client.get(f"/alumnos/listados/{nombre}/pdf/")
            self.assertEqual(pdf["Content-Type"], "application/pdf")
            self.assertTrue(b"".join(pdf.streaming_content).startswith(b"%PDF"))

            excel = self.client.get(f"/alumnos/listados/{nombre}/excel/")
            hoja = load_workbook(BytesIO(b"".join(excel.streaming_content)))["Reporte"]
            pantalla = self.client.get(url).context
            self.assertEqual([c.value for c in hoja[1]], pantalla["columnas"])
            self.assertEqual([c.value for c in hoja[2]], pantalla["filas"][0])

        excel = self.client.get("/alumnos/listados/estres-modalidad/excel/", FILTROS)
        hoja = load_workbook(BytesIO(b"".join(excel.streaming_content)))["Reporte"]
        pantalla = self.client.get(REPORTES["estres-modalidad"], FILTROS).context
        self.assertEqual([[c.value for c in fila] for fila in hoja.iter_rows(min_row=2, max_row=4)],
                         pantalla["filas"])
