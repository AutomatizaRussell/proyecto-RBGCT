import os
import shutil
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from openpyxl import Workbook

from apps.employee_imports.models import EmployeeImport
from apps.employee_imports.services import EmployeeImportService
from apps.employees.models import Employee


class EmployeeImportServiceTest(TestCase):
    def setUp(self):
        super().setUp()
        self.temp_media_root = os.path.join(os.getcwd(), "media_test_imports")
        os.makedirs(self.temp_media_root, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.temp_media_root, ignore_errors=True)
        super().tearDown()

    def _build_excel_file(self, rows: list[list[str]]) -> SimpleUploadedFile:
        workbook = Workbook()
        worksheet = workbook.active
        for row in rows:
            worksheet.append(row)

        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)
        return SimpleUploadedFile(
            "empleados.xlsx",
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_imports_expected_spanish_columns(self):
        with override_settings(MEDIA_ROOT=self.temp_media_root):
            upload = self._build_excel_file(
                [
                    ["id", "area", "nombre", "correo"],
                    ["A001", "Finanzas", "Ana Lopez", "ana@example.com"],
                ]
            )
            import_batch = EmployeeImport.objects.create(
                file=upload,
                original_filename="empleados.xlsx",
            )

            EmployeeImportService.process(import_batch)

            employee = Employee.objects.get(employee_code="A001")
            self.assertEqual(employee.document_number, "A001")
            self.assertEqual(employee.department, "Finanzas")
            self.assertEqual(employee.first_name, "Ana Lopez")
            self.assertEqual(employee.last_name, "")
            self.assertEqual(employee.email, "ana@example.com")
