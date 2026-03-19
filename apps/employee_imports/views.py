from io import BytesIO

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from openpyxl import Workbook
from rest_framework import decorators, response, status, viewsets
from rest_framework.exceptions import ValidationError

from apps.common.permissions import IsStaffOrReadOnly

from .exceptions import EmployeeImportValidationError
from .forms import EmployeeImportUploadForm
from .models import EmployeeImport
from .serializers import EmployeeImportSerializer
from .services import EmployeeImportService


class EmployeeImportViewSet(viewsets.ModelViewSet):
    """
    Gestiona cargas de Excel de empleados.

    El archivo puede enviarse con encabezados técnicos o en español.
    El sistema procesa todas las filas no vacías y guarda el resultado del lote.
    """

    queryset = EmployeeImport.objects.prefetch_related("rows").all()
    serializer_class = EmployeeImportSerializer
    permission_classes = [IsStaffOrReadOnly]
    http_method_names = ["get", "post"]

    def perform_create(self, serializer):
        instance = serializer.save()
        try:
            EmployeeImportService.process(instance)
        except EmployeeImportValidationError as exc:
            raise ValidationError(
                {
                    "file": [exc.message],
                    "missing_columns": exc.missing_columns,
                    "expected_columns": ["employee_code o document_number", "first_name o full_name"],
                }
            ) from exc

    @decorators.action(detail=True, methods=["post"])
    def process(self, request, pk=None):
        import_batch = self.get_object()
        try:
            import_batch = EmployeeImportService.process(import_batch)
        except EmployeeImportValidationError as exc:
            raise ValidationError(
                {
                    "file": [exc.message],
                    "missing_columns": exc.missing_columns,
                    "expected_columns": ["employee_code o document_number", "first_name o full_name"],
                }
            ) from exc
        serializer = self.get_serializer(import_batch)
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class EmployeeImportPortalView(LoginRequiredMixin, FormView):
    template_name = "employee_imports/index.html"
    form_class = EmployeeImportUploadForm
    success_url = reverse_lazy("employee-imports")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        recent_imports = EmployeeImport.objects.prefetch_related("rows").all()[:8]
        context.update(
            {
                "recent_imports": recent_imports,
                "user_role": "Administrador" if (user.is_staff or user.is_superuser) else "Usuario",
                "can_access_admin": user.is_staff or user.is_superuser,
                "supported_columns": EmployeeImportService.get_supported_columns(),
            }
        )
        return context

    def form_valid(self, form):
        upload = form.cleaned_data["file"]
        import_batch = EmployeeImport.objects.create(
            file=upload,
            original_filename=upload.name,
            created_by=self.request.user if self.request.user.is_authenticated else None,
        )

        try:
            EmployeeImportService.process(import_batch)
        except EmployeeImportValidationError as exc:
            messages.error(self.request, exc.message)
        else:
            if import_batch.status == EmployeeImport.STATUS_COMPLETED:
                messages.success(
                    self.request,
                    f"Importación completada. Se procesaron {import_batch.processed_rows} fila(s) y {import_batch.success_rows} quedaron registradas correctamente.",
                )
            elif import_batch.status == EmployeeImport.STATUS_PARTIAL:
                messages.warning(
                    self.request,
                    f"Importación parcial. Se procesaron {import_batch.processed_rows} fila(s): {import_batch.success_rows} correctas y {import_batch.error_rows} con error.",
                )
            else:
                messages.error(
                    self.request,
                    f"La importación no pudo completarse. Se revisaron {import_batch.processed_rows} fila(s) y todas tuvieron errores.",
                )
        return redirect(self.success_url)


class EmployeeImportTemplateView(LoginRequiredMixin, FormView):
    def get(self, request, *args, **kwargs):
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Plantilla Empleados"
        headers = [
            "codigo_empleado",
            "nombres",
            "apellidos",
            "numero_documento",
            "tipo_documento",
            "correo",
            "telefono",
            "cargo",
            "departamento",
            "fecha_ingreso",
            "fecha_nacimiento",
            "estado",
        ]
        worksheet.append(headers)
        worksheet.append(
            [
                "EMP001",
                "Ana",
                "Lopez",
                "123456789",
                "CC",
                "ana@empresa.com",
                "3001234567",
                "Analista",
                "Finanzas",
                "2025-01-15",
                "1992-04-20",
                "activo",
            ]
        )
        buffer = BytesIO()
        workbook.save(buffer)
        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="plantilla-importacion-empleados.xlsx"'
        return response
