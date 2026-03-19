# Employee Dashboard MVP

Proyecto base en Django + Django REST Framework para un dashboard administrativo interno orientado a gestion de empleados.

## Incluye

- CRUD REST de empleados
- Importacion de empleados desde Excel
- Exportacion a CSV y Excel
- Registro de eventos para integraciones futuras
- Configuracion lista para SQLite en local y PostgreSQL en produccion
- Estructura modular para crecer sin sobreingenieria

## Estructura

```text
config/                # settings, urls y entrypoints WSGI/ASGI
apps/common/           # utilidades y componentes compartidos
apps/employees/        # dominio principal de empleados
apps/employee_imports/ # carga y procesamiento de archivos Excel
apps/data_exports/     # exportaciones CSV y XLSX
apps/integrations/     # eventos y adaptadores externos
requirements/          # dependencias por entorno
```

## Puesta en marcha

1. Instala Python 3.12 o compatible.
2. Crea un entorno virtual.
3. Instala dependencias:

```bash
pip install -r requirements/local.txt
```

4. Copia variables de entorno:

```bash
copy .env.example .env
```

5. Ejecuta migraciones:

```bash
python manage.py makemigrations
python manage.py migrate
```

6. Crea un superusuario:

```bash
python manage.py createsuperuser
```

7. Inicia el servidor:

```bash
python manage.py runserver
```

## Endpoints principales

- `GET /api/v1/employees/`
- `POST /api/v1/employees/`
- `POST /api/v1/imports/employees/`
- `POST /api/v1/imports/employees/{id}/process/`
- `GET /api/v1/exports/employees.csv`
- `GET /api/v1/exports/employees.xlsx`
- `GET /api/v1/integration-events/`
- `POST /api/v1/integration-events/{id}/deliver/`

## Decisiones tecnicas

- Se usa `JSONField` para metadata flexible y payloads de integracion.
- La logica de importacion/exportacion vive en servicios para no saturar vistas.
- Los eventos de integracion quedan persistidos desde el inicio para facilitar n8n, webhooks y reintentos.
- SQLite es la base local por defecto, pero la estructura evita acoplarse a detalles especificos del motor.

## Siguientes pasos recomendados

- Crear migraciones iniciales
- Agregar autenticacion basada en grupos y permisos
- Incorporar validaciones de negocio especificas para tu archivo Excel real
- Anadir pruebas de API e importacion
