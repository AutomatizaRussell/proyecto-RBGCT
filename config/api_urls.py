from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.data_exports.views import EmployeeCsvExportView, EmployeeExcelExportView
from apps.employee_imports.views import EmployeeImportViewSet
from apps.employees.views import EmployeeViewSet
from apps.integrations.views import IntegrationEventViewSet

router = DefaultRouter()
router.register("employees", EmployeeViewSet, basename="employee")
router.register("imports/employees", EmployeeImportViewSet, basename="employee-import")
router.register("integration-events", IntegrationEventViewSet, basename="integration-event")

urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
    path("exports/employees.csv", EmployeeCsvExportView.as_view(), name="employees-export-csv"),
    path("exports/employees.xlsx", EmployeeExcelExportView.as_view(), name="employees-export-xlsx"),
]
