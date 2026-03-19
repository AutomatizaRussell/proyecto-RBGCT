from rest_framework import serializers

from .models import EmployeeImport, EmployeeImportRow


class EmployeeImportRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeImportRow
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class EmployeeImportSerializer(serializers.ModelSerializer):
    rows = EmployeeImportRowSerializer(many=True, read_only=True)
    file = serializers.FileField(
        help_text=(
            "Carga un archivo .xlsx con columnas como: "
            "id, area, nombre, correo."
        )
    )

    class Meta:
        model = EmployeeImport
        fields = "__all__"
        read_only_fields = (
            "id",
            "original_filename",
            "status",
            "created_by",
            "total_rows",
            "processed_rows",
            "success_rows",
            "error_rows",
            "summary",
            "started_at",
            "finished_at",
            "created_at",
            "updated_at",
        )

    def validate_file(self, value):
        filename = value.name.lower()
        if not filename.endswith(".xlsx"):
            raise serializers.ValidationError("Solo se permiten archivos Excel con extension .xlsx.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        upload = validated_data["file"]
        return EmployeeImport.objects.create(
            **validated_data,
            original_filename=upload.name,
            created_by=request.user if request.user.is_authenticated else None,
        )
