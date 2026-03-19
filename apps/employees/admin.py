from django.contrib import admin

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("employee_code", "first_name", "last_name", "document_number", "status", "department")
    search_fields = ("employee_code", "first_name", "last_name", "document_number", "email")
    list_filter = ("status", "department", "position")
