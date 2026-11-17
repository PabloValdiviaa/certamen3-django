from django import forms
from .models import Alumno
class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = [
            "rut", "nombres", "apellido_paterno",
            "apellido_materno", "correo_institucional",
            "carrera", "fecha_ingreso", "activo",
        ]
        labels = {
            "estado_ramo": "Ramo aprobado",
            "activo": "Alumno activo",
        }
        widgets = {
            "fecha_ingreso": forms.DateInput(
                format="%Y-%m-%d", attrs={"type": "date"}
                ),
            }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fecha_ingreso"].input_formats = ["%Y-%m-%d"]
        for campo in self.fields.values():
            if isinstance(campo.widget, forms.CheckboxInput):
                campo.widget.attrs["class"] = "form-check-input"
            else:
                campo.widget.attrs["class"] = "form-control"