from django.test import TestCase

from apps.employees.models import Employee


class EmployeeModelTest(TestCase):
    def test_string_representation(self):
        employee = Employee(first_name="Ana", last_name="Lopez", employee_code="EMP001", document_number="123")
        self.assertEqual(str(employee), "Ana Lopez")
