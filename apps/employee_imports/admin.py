from django.contrib import admin

from .models import EmployeeImport, EmployeeImportRow


class EmployeeImportRowInline(admin.TabularInline):
    model = EmployeeImportRow
    extra = 0
    readonly_fields = ("row_number", "status", "error_detail", "employee")


@admin.register(EmployeeImport)
class EmployeeImportAdmin(admin.ModelAdmin):
    list_display = ("id", "original_filename", "status", "total_rows", "success_rows", "error_rows", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("original_filename",)
    inlines = [EmployeeImportRowInline]
