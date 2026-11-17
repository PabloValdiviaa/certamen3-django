# Proyecto universidad · aplicación `alumnos`

Las instrucciones completas (integrantes, instalación, dependencias, despliegue en AWS y
videos) están en el [README principal](../README.md).

Ejecución rápida en macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py cargar_datos   # carga datos.csv en la base SQLite
python manage.py runserver
```

En Windows usar `py` en vez de `python` y activar con `.\.venv\Scripts\Activate.ps1`.

Abrir: <http://127.0.0.1:8000/alumnos/>
