from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .services import EmployeeExportService


class EmployeeCsvExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        content = EmployeeExportService.to_csv()
        response = HttpResponse(content, content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="empleados.csv"'
        return response


class EmployeeExcelExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        content = EmployeeExportService.to_excel()
        response = HttpResponse(
            content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="empleados.xlsx"'
        return response
