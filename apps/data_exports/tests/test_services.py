import csv
from io import BytesIO, StringIO

from django.test import TestCase

from openpyxl import load_workbook

from apps.data_exports.services import EmployeeExportService
from apps.employees.models import Employee


class EmployeeExportServiceTest(TestCase):
    def test_exports_expected_spanish_columns_to_csv(self):
        Employee.objects.create(
            employee_code="A001",
            document_number="A001",
            first_name="Ana",
            last_name="Lopez",
            department="Finanzas",
            email="ana@example.com",
        )

        content = EmployeeExportService.to_csv()
        rows = list(csv.reader(StringIO(content.decode("utf-8-sig")), delimiter=";"))

        self.assertEqual(rows[0], ["id", "area", "nombre", "correo"])
        self.assertEqual(rows[1], ["A001", "Finanzas", "Ana Lopez", "ana@example.com"])

    def test_exports_expected_spanish_columns_to_excel(self):
        Employee.objects.create(
            employee_code="B002",
            document_number="B002",
            first_name="Bruno",
            last_name="Diaz",
            department="Tecnologia",
            email="bruno@example.com",
        )

        content = EmployeeExportService.to_excel()
        workbook = load_workbook(filename=BytesIO(content))
        worksheet = workbook.active

        self.assertEqual(
            [worksheet["A1"].value, worksheet["B1"].value, worksheet["C1"].value, worksheet["D1"].value],
            ["ID", "AREA", "NOMBRE", "CORREO"],
        )
        self.assertEqual(
            [worksheet["A2"].value, worksheet["B2"].value, worksheet["C2"].value, worksheet["D2"].value],
            ["B002", "Tecnologia", "Bruno Diaz", "bruno@example.com"],
        )
