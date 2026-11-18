# Remote Work & Mental Health en Django

Proyecto semestral del Taller de Visualización de Datos. Aplicación Django que muestra
gráficos y reportes del dataset *Impact of Remote Work on Mental Health* (Kaggle, 5.000
trabajadores). Esta versión corresponde al **Certamen 3, parte 1** y continúa el proyecto
del Certamen 2 (<https://github.com/Joba-13/Persentaciondjango>).

## Integrantes

- Joaquín Barahona
- Ignacio Ramírez
- Pablo Valdivia
- Nicolás Ojeda

## Entrega

| | Enlace |
|---|---|
| Dirección del sitio en AWS | <http://3.89.32.242:8000/alumnos/> (AWS Academy: la IP cambia si se reinicia el laboratorio) |
| Video 1: proceso de despliegue | <https://github.com/PabloValdiviaa/certamen3-django/releases/download/videos-certamen3/Video1-Despliegue-AWS.mp4> |
| Video 2: presentación del software y explicación del código | <https://github.com/PabloValdiviaa/certamen3-django/releases/download/videos-certamen3/Video2-Presentacion-software.mp4> |
| Archivos `proyecto.rar` y `videoPresentación.rar` (respaldo) | <https://github.com/PabloValdiviaa/certamen3-django/releases/tag/entrega-certamen3> |

`proyecto.rar` contiene este README y la carpeta `Universidad_Alumnos_Django`.
`videoPresentación.rar` contiene el video 1 y el video 2.

## Cambios del Certamen 3

1. **Nuevo gráfico dinámico** (menú Gráficos → *Nivel de estrés según modalidad*):
   cantidad de trabajadores con estrés bajo, medio y alto en cada modalidad de trabajo.
   Se puede filtrar por industria, región y rango de edad.
2. **Nuevo reporte** (menú Reportes → *Nivel de estrés según modalidad*): tabla con los
   mismos datos y filtros del gráfico, explicación de los datos e interpretación.
3. **Descarga en PDF** y 4. **Descarga en Excel** al final de los cuatro reportes. Los
   archivos respetan los filtros del reporte.
5. **Base de datos:** los datos de `datos.csv` se cargan en la base SQLite (modelo
   `Trabajador`, comando `cargar_datos`) y los gráficos y reportes la leen desde ahí. En
   AWS la base se crea dentro de la instancia EC2.

Se conservan los tres gráficos, los tres listados (ahora llamados reportes) y la
navegación del Certamen 2.

## Dependencias

Python 3.12 o superior y los paquetes de `Universidad_Alumnos_Django/requirements.txt`:
Django 5.1.14, matplotlib, reportlab (PDF) y openpyxl (Excel).

## Instalación y ejecución local

Windows (PowerShell):

```powershell
cd Universidad_Alumnos_Django
py -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py manage.py migrate
py manage.py cargar_datos
py manage.py runserver
```

macOS o Linux:

```bash
cd Universidad_Alumnos_Django
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py cargar_datos
python manage.py runserver
```

Abrir <http://127.0.0.1:8000/alumnos/>. `migrate` crea las tablas en `db.sqlite3` y
`cargar_datos` copia los 5.000 registros de `alumnos/datos/datos.csv` a la tabla
`Trabajador`.

## Despliegue en AWS

SQLite no es un servidor de base de datos sino un archivo (`db.sqlite3`). Por eso no se
usa Amazon RDS: la base se crea en el disco de una instancia **EC2**, en la misma carpeta
del proyecto, y Django la lee desde ahí.

### 1. Crear la instancia EC2

En la consola de AWS → EC2 → *Launch instance* (en **AWS Academy Learner Lab**, primero
*Start Lab* y esperar el punto verde):

- Imagen: **Ubuntu Server 24.04 LTS**. Tipo: **t3.micro** o **t2.micro** (capa gratuita).
- *Key pair*: `vockey` en AWS Academy (o crear uno y guardar el archivo `.pem`).
- *Security group*, reglas de entrada:
  - SSH, puerto 22, origen *Anywhere* (viene así por defecto; *EC2 Instance Connect* lo
    necesita porque se conecta desde los servidores de AWS).
  - *Custom TCP*, puerto **8000**, origen *Anywhere* (0.0.0.0/0), para entrar al sitio
    desde cualquier navegador.
- Lanzar la instancia y copiar su **Public IPv4 address**.

### 2. Instalar el proyecto en la instancia

Conectarse con *Connect → EC2 Instance Connect* (o `ssh -i clave.pem ubuntu@<IP>`) y
ejecutar:

```bash
sudo apt update
sudo apt install -y python3-venv git
git clone https://github.com/PabloValdiviaa/certamen3-django.git
cd certamen3-django/Universidad_Alumnos_Django
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Crear la base de datos SQLite en la instancia

```bash
python manage.py migrate
python manage.py cargar_datos
```

Esto crea `db.sqlite3` en la instancia y carga los 5.000 trabajadores.

### 4. Configurar Django para la dirección del servidor

Abrir `nano universidad/settings.py` y agregar la IP pública a `ALLOWED_HOSTS`:

```python
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "<IP-pública>"]
```

Sin este cambio Django rechaza las visitas que llegan a la IP de la instancia
(error 400, *Bad Request*).

### 5. Ejecutar el servidor

```bash
nohup python manage.py runserver 0.0.0.0:8000 > servidor.log 2>&1 &
```

`0.0.0.0` hace que Django acepte conexiones desde fuera de la instancia y `nohup` lo
mantiene funcionando al cerrar la conexión. Si la instancia se reinicia, hay que repetir
este paso (y actualizar `ALLOWED_HOSTS` si cambió la IP). En AWS Academy la instancia se
detiene al terminar la sesión del laboratorio y al volver a iniciarla cambia la IP pública.

### 6. Comprobar desde un navegador externo

Abrir `http://<IP-pública>:8000/alumnos/` desde otro computador o desde un celular con
datos móviles y probar el gráfico dinámico, el nuevo reporte y las descargas en PDF y Excel.
