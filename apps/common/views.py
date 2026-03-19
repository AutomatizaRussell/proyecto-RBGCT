from django.contrib.auth import logout
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Max
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, RedirectView, TemplateView, UpdateView

from .portal_forms import BaseManagementUserForm, ManagementUserCreateForm, ManagementUserPermissionForm, SuperAdminUserPermissionForm
from apps.employee_imports.models import EmployeeImport
from apps.employees.models import Employee
from apps.integrations.models import IntegrationEvent

User = get_user_model()


def get_user_role_label(user):
    return BaseManagementUserForm.get_display_role_label(user)


class RootRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return reverse("dashboard")
        return reverse("login")


class LogoutGetView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("login")

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect("login")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    @staticmethod
    def _format_event_name(event_type: str) -> str:
        friendly_names = {
            "employee_import.completed": "Enviar resultado de importacion de empleados",
            "employee.created": "Enviar nuevo empleado a integraciones",
            "employee.updated": "Enviar actualizacion de empleado",
            "employee.deleted": "Enviar baja de empleado",
        }
        if not event_type:
            return "Sin detalle"
        return friendly_names.get(
            event_type,
            str(event_type).replace(".", " ").replace("_", " ").strip().capitalize(),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        employee_queryset = Employee.objects.all()
        active_queryset = employee_queryset.filter(status=Employee.STATUS_ACTIVE)
        inactive_queryset = employee_queryset.filter(status=Employee.STATUS_INACTIVE)
        pending_events_queryset = IntegrationEvent.objects.filter(status=IntegrationEvent.STATUS_PENDING)
        next_pending_event = pending_events_queryset.first()
        context.update(
            {
                "user_role": get_user_role_label(user),
                "total_employees": employee_queryset.count(),
                "active_employees": active_queryset.count(),
                "inactive_employees": inactive_queryset.count(),
                "total_employees_updated_at": employee_queryset.aggregate(last=Max("updated_at"))["last"],
                "active_employees_updated_at": active_queryset.aggregate(last=Max("updated_at"))["last"],
                "inactive_employees_updated_at": inactive_queryset.aggregate(last=Max("updated_at"))["last"],
                "imports_count": EmployeeImport.objects.count(),
                "pending_events": pending_events_queryset.count(),
                "next_pending_event_name": self._format_event_name(next_pending_event.event_type) if next_pending_event else "Sin eventos pendientes",
                "next_pending_event_created_at": next_pending_event.created_at if next_pending_event else None,
                "can_access_admin": user.is_staff or user.is_superuser,
            }
        )
        return context


class ApiAccessView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "api_access.html"

    def test_func(self):
        user = self.request.user
        return user.is_staff or user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        base_url = self.request.build_absolute_uri("/").rstrip("/")
        endpoints = [
            {"name": "Listado de empleados", "method": "GET", "url": f"{base_url}/api/v1/employees/"},
            {"name": "Detalle de empleado", "method": "GET", "url": f"{base_url}/api/v1/employees/{{id}}/"},
            {"name": "Crear empleado", "method": "POST", "url": f"{base_url}/api/v1/employees/"},
            {"name": "Importar empleados", "method": "POST", "url": f"{base_url}/api/v1/imports/employees/"},
            {"name": "Exportar CSV", "method": "GET", "url": f"{base_url}/api/v1/exports/employees.csv"},
        ]
        context.update(
            {
                "user_role": get_user_role_label(user),
                "can_access_admin": user.is_staff or user.is_superuser,
                "api_endpoints": endpoints,
            }
        )
        return context


class ManagementDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "management/index.html"

    def test_func(self):
        user = self.request.user
        return user.is_staff or user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        users = User.objects.all().order_by("-is_active", "username")
        user_rows = [
            {
                "id": item.id,
                "username": item.username,
                "full_name": item.get_full_name() or "Sin nombre registrado",
                "email": item.email or "Sin correo registrado",
                "is_active": item.is_active,
                "is_superuser": item.is_superuser,
                "is_staff": item.is_staff,
                "role_label": get_user_role_label(item),
                "can_edit_employees": item.has_perm("employees.change_employee"),
                "last_login": item.last_login,
            }
            for item in users
        ]
        context.update(
            {
                "user_role": get_user_role_label(user),
                "can_access_admin": user.is_staff or user.is_superuser,
                "can_manage_full_access": user.is_superuser,
                "total_users": users.count(),
                "active_users": users.filter(is_active=True).count(),
                "employee_editors": sum(1 for item in users if item.has_perm("employees.change_employee")),
                "superusers_count": users.filter(is_superuser=True).count(),
                "groups_count": Group.objects.count(),
                "management_users": user_rows,
                "advanced_admin_url": "/admin/",
                "user_admin_url": "/admin/auth/user/",
                "group_admin_url": "/admin/auth/group/",
            }
        )
        return context


class ManagementUserUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    template_name = "management/user_edit.html"
    model = User
    success_message = "El acceso del usuario fue actualizado correctamente."

    def test_func(self):
        user = self.request.user
        return user.is_staff or user.is_superuser

    def get_form_class(self):
        if self.request.user.is_superuser:
            return SuperAdminUserPermissionForm
        return ManagementUserPermissionForm

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.is_superuser and self.object.is_superuser:
            return redirect("management-dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["current_user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("management-dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        managed_user = self.object
        context.update(
            {
                "user_role": get_user_role_label(user),
                "can_access_admin": user.is_staff or user.is_superuser,
                "can_manage_full_access": user.is_superuser,
                "managed_user": managed_user,
                "managed_user_role": get_user_role_label(managed_user),
                "managed_user_can_edit_employees": managed_user.has_perm("employees.change_employee"),
            }
        )
        return context


class ManagementUserCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    template_name = "management/user_create.html"
    form_class = ManagementUserCreateForm
    success_message = "El usuario fue creado correctamente."

    def test_func(self):
        return self.request.user.is_superuser

    def get_success_url(self):
        return reverse("management-dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update(
            {
                "user_role": get_user_role_label(user),
                "can_access_admin": user.is_staff or user.is_superuser,
                "can_manage_full_access": user.is_superuser,
            }
        )
        return context
