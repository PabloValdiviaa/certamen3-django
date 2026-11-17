from django.db import models


class Alumno(models.Model):
    rut = models.CharField("RUT", max_length=12, unique=True)
    nombres = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=60)
    apellido_materno = models.CharField(max_length=60, blank=True)
    correo_institucional = models.EmailField(unique=True)
    carrera = models.CharField(max_length=120)
    fecha_ingreso = models.DateField()
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["apellido_paterno", "apellido_materno", "nombres"]
        verbose_name = "alumno"
        verbose_name_plural = "alumnos"

    def __str__(self):
        return f"{self.rut} - {self.nombres} {self.apellido_paterno}"


class Trabajador(models.Model):
    # Certamen 3: cada fila de datos.csv se guarda como un Trabajador en SQLite.
    id_empleado = models.CharField(max_length=10, unique=True)
    edad = models.IntegerField()
    industria = models.CharField(max_length=40)
    anios_experiencia = models.IntegerField()
    modalidad = models.CharField(max_length=10)
    horas_semanales = models.IntegerField()
    equilibrio_vida_trabajo = models.IntegerField()
    nivel_estres = models.CharField(max_length=10)
    region = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.id_empleado} - {self.industria}"
