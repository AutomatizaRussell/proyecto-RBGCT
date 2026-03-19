from .exceptions import EmployeeImportValidationError


HEADER_ALIASES = {
    "id": "employee_code",
    "identificacion": "employee_code",
    "codigo": "employee_code",
    "codigo_empleado": "employee_code",
    "employee_code": "employee_code",
    "document_number": "document_number",
    "numero_documento": "document_number",
    "nro_documento": "document_number",
    "documento": "document_number",
    "document": "document_number",
    "tipo_documento": "document_type",
    "document_type": "document_type",
    "area": "department",
    "departamento": "department",
    "department": "department",
    "nombre": "full_name",
    "completo": "full_name",
    "nombres": "first_name",
    "primer_nombre": "first_name",
    "segundo_nombre": "middle_name",
    "nombre_completo": "full_name",
    "full_name": "full_name",
    "first_name": "first_name",
    "apellido": "last_name",
    "apellidos": "last_name",
    "primer_apellido": "last_name",
    "last_name": "last_name",
    "correo": "email",
    "correo_electronico": "email",
    "email": "email",
    "telefono": "phone",
    "celular": "phone",
    "phone": "phone",
    "cargo": "position",
    "puesto": "position",
    "position": "position",
    "fecha_ingreso": "hire_date",
    "ingreso": "hire_date",
    "hire_date": "hire_date",
    "fecha_nacimiento": "birth_date",
    "nacimiento": "birth_date",
    "birth_date": "birth_date",
    "salario": "salary",
    "salary": "salary",
    "estado": "status",
    "status": "status",
}

REQUIRED_COLUMN_GROUPS = {
    "identificacion": {"employee_code", "document_number"},
    "nombre": {"full_name", "first_name"},
}


def normalize_header(header: str) -> str:
    if header is None:
        return ""
    normalized = str(header).strip().lower().replace(" ", "_")
    if not normalized:
        return ""
    return HEADER_ALIASES.get(normalized, normalized)


def validate_headers(headers: list[str]) -> list[str]:
    normalized_headers = [normalize_header(header) for header in headers]
    present_headers = [header for header in normalized_headers if header]
    missing = [
        column_name
        for column_name, accepted_columns in REQUIRED_COLUMN_GROUPS.items()
        if not any(column in present_headers for column in accepted_columns)
    ]
    if missing:
        raise EmployeeImportValidationError(
            "El archivo no contiene las columnas requeridas para importar empleados.",
            missing_columns=missing,
        )
    return normalized_headers
