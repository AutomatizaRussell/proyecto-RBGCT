from rest_framework import serializers

from .models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField(read_only=True)
    estado_texto = serializers.CharField(source="get_status_display", read_only=True)
    codigo_empleado = serializers.CharField(source="employee_code", read_only=True)
    numero_documento = serializers.CharField(source="document_number", read_only=True)
    tipo_documento = serializers.CharField(source="document_type", read_only=True)
    nombres = serializers.CharField(source="first_name", read_only=True)
    apellidos = serializers.CharField(source="last_name", read_only=True)
    correo = serializers.CharField(source="email", read_only=True)
    telefono = serializers.CharField(source="phone", read_only=True)
    cargo = serializers.CharField(source="position", read_only=True)
    departamento = serializers.CharField(source="department", read_only=True)
    fecha_ingreso = serializers.DateField(source="hire_date", read_only=True)
    fecha_nacimiento = serializers.DateField(source="birth_date", read_only=True)
    salario_valor = serializers.DecimalField(source="salary", max_digits=12, decimal_places=2, read_only=True)

    INPUT_ALIASES = {
        "codigo_empleado": "employee_code",
        "codigo": "employee_code",
        "id_empleado": "employee_code",
        "nombres": "first_name",
        "primer_nombre": "first_name",
        "apellidos": "last_name",
        "apellido": "last_name",
        "numero_documento": "document_number",
        "documento": "document_number",
        "tipo_documento": "document_type",
        "correo": "email",
        "correo_electronico": "email",
        "telefono": "phone",
        "celular": "phone",
        "cargo": "position",
        "puesto": "position",
        "departamento": "department",
        "area": "department",
        "fecha_ingreso": "hire_date",
        "fecha_nacimiento": "birth_date",
        "estado": "status",
        "salario_valor": "salary",
    }

    class Meta:
        model = Employee
        fields = (
            "id",
            "employee_code",
            "codigo_empleado",
            "first_name",
            "nombres",
            "last_name",
            "apellidos",
            "nombre_completo",
            "document_type",
            "tipo_documento",
            "document_number",
            "numero_documento",
            "email",
            "correo",
            "phone",
            "telefono",
            "position",
            "cargo",
            "department",
            "departamento",
            "hire_date",
            "fecha_ingreso",
            "birth_date",
            "fecha_nacimiento",
            "salary",
            "salario_valor",
            "status",
            "estado_texto",
            "metadata",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_fields(self):
        fields = super().get_fields()
        ordered_fields = list(self.Meta.fields)
        return {name: fields[name] for name in ordered_fields if name in fields}

    def to_internal_value(self, data):
        if hasattr(data, "copy"):
            data = data.copy()
        else:
            data = dict(data)

        for alias, canonical in self.INPUT_ALIASES.items():
            if alias in data and canonical not in data:
                data[canonical] = data[alias]

        return super().to_internal_value(data)

    def get_nombre_completo(self, obj):
        return " ".join(part for part in [obj.first_name, obj.last_name] if part).strip()

    def validate_document_number(self, value):
        queryset = Employee.objects.filter(document_number=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Ya existe un empleado con ese número de documento.")
        return value

    def validate_employee_code(self, value):
        queryset = Employee.objects.filter(employee_code=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Ya existe un empleado con ese código.")
        return value
