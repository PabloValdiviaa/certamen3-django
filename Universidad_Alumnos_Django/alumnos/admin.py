from django.contrib import admin

from .models import Alumno


@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = (
        "rut",
        "nombres",
        "apellido_paterno",
        "correo_institucional",
        "carrera",
        "activo",
    )
    search_fields = ("rut", "nombres", "apellido_paterno", "correo_institucional")
    list_filter = ("carrera", "activo", "fecha_ingreso")
