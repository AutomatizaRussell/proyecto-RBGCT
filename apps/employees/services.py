from typing import Any

from .models import Employee


class EmployeeService:
    @staticmethod
    def create_employee(validated_data: dict[str, Any]) -> Employee:
        return Employee.objects.create(**validated_data)

    @staticmethod
    def update_employee(employee: Employee, validated_data: dict[str, Any]) -> Employee:
        for field, value in validated_data.items():
            setattr(employee, field, value)
        employee.save()
        return employee
