import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from alumnos.models import Trabajador

RUTA_CSV = Path(__file__).resolve().parent.parent.parent / "datos" / "datos.csv"

class Command(BaseCommand):
    help = "Cargar los trabajadores de datos.csv en la base de datos SQLite."

    def handle(self, *args, **options):
        Trabajador.objects.all().delete()  # Evita duplicar datos si se ejecuta dos veces.
        trabajadores = []
        with open(RUTA_CSV, newline="", encoding="utf-8-sig") as archivo:
            for fila in csv.DictReader(archivo):
                trabajadores.append(Trabajador(
                    id_empleado=fila["Employee_ID"],
                    edad=int(fila["Age"]),
                    industria=fila["Industry"],
                    anios_experiencia=int(fila["Years_of_Experience"]),
                    modalidad=fila["Work_Location"],
                    horas_semanales=int(fila["Hours_Worked_Per_Week"]),
                    equilibrio_vida_trabajo=int(fila["Work_Life_Balance_Rating"]),
                    nivel_estres=fila["Stress_Level"],
                    region=fila["Region"],
                ))
        Trabajador.objects.bulk_create(trabajadores)  # Guardar todos de una vez.
        self.stdout.write(self.style.SUCCESS(f"Trabajadores cargados: {len(trabajadores)}"))
