from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from apps.common.views import ApiAccessView, DashboardView, LogoutGetView, ManagementDashboardView, ManagementUserCreateView, ManagementUserUpdateView, RootRedirectView
from apps.employee_imports.views import EmployeeImportPortalView, EmployeeImportTemplateView
from apps.employees.views import EmployeeDetailView, EmployeeListView, EmployeeUpdateView

urlpatterns = [
    path("", RootRedirectView.as_view(), name="root"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", LogoutGetView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("management/", ManagementDashboardView.as_view(), name="management-dashboard"),
    path("management/users/create/", ManagementUserCreateView.as_view(), name="management-user-create"),
    path("management/users/<int:pk>/", ManagementUserUpdateView.as_view(), name="management-user-edit"),
    path("employees/", EmployeeListView.as_view(), name="employee-list"),
    path("employees/<int:pk>/", EmployeeDetailView.as_view(), name="employee-detail"),
    path("employees/<int:pk>/edit/", EmployeeUpdateView.as_view(), name="employee-edit"),
    path("imports/", EmployeeImportPortalView.as_view(), name="employee-imports"),
    path("imports/template.xlsx", EmployeeImportTemplateView.as_view(), name="employee-import-template"),
    path("api-access/", ApiAccessView.as_view(), name="api-access"),
    path("admin/", admin.site.urls),
    path("api/v1/", include("config.api_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
