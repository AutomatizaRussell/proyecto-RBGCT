from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse
from django.views.generic import DetailView, ListView, UpdateView
from rest_framework import viewsets

from apps.common.permissions import IsStaffOrReadOnly

from .forms import EmployeeUpdateForm
from .models import Employee
from .serializers import EmployeeSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsStaffOrReadOnly]
    filterset_fields = ["status", "department", "position"]
    search_fields = ["employee_code", "first_name", "last_name", "document_number", "email"]
    ordering_fields = ["employee_code", "first_name", "last_name", "created_at", "updated_at"]


class EmployeeListView(LoginRequiredMixin, ListView):
    template_name = "employees/list.html"
    model = Employee
    context_object_name = "employees"
    paginate_by = 12

    def get_queryset(self):
        queryset = Employee.objects.all()
        search = self.request.GET.get("search", "").strip()
        status_filter = self.request.GET.get("status", "").strip()
        department_filter = self.request.GET.get("department", "").strip()

        if search:
            queryset = queryset.filter(
                Q(employee_code__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(document_number__icontains=search)
                | Q(email__icontains=search)
            )

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if department_filter:
            queryset = queryset.filter(department=department_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update(
            {
                "user_role": "Administrador" if (user.is_staff or user.is_superuser) else "Usuario",
                "can_access_admin": user.is_staff or user.is_superuser,
                "can_edit_employees": user.has_perm("employees.change_employee"),
                "search_value": self.request.GET.get("search", "").strip(),
                "selected_status": self.request.GET.get("status", "").strip(),
                "selected_department": self.request.GET.get("department", "").strip(),
                "status_choices": Employee.STATUS_CHOICES,
                "department_choices": (
                    Employee.objects.exclude(department="")
                    .order_by("department")
                    .values_list("department", flat=True)
                    .distinct()
                ),
            }
        )
        return context


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    template_name = "employees/detail.html"
    model = Employee
    context_object_name = "employee"

    FIELD_LABELS = {
        "employee_code": "Código de empleado",
        "document_number": "Número de documento",
        "document_type": "Tipo de documento",
        "first_name": "Nombres",
        "last_name": "Apellidos",
        "full_name": "Nombre completo",
        "email": "Correo electrónico",
        "phone": "Teléfono",
        "position": "Cargo",
        "department": "Área o departamento",
        "hire_date": "Fecha de ingreso",
        "birth_date": "Fecha de nacimiento",
        "salary": "Salario",
        "status": "Estado",
    }

    @classmethod
    def _humanize_extra_label(cls, key: str) -> str:
        return cls.FIELD_LABELS.get(key, str(key).replace("_", " ").capitalize())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        employee = self.object
        raw_metadata = (employee.metadata or {}).get("raw", {})
        extra_fields = [
            (self._humanize_extra_label(key), value)
            for key, value in raw_metadata.items()
            if value not in ("", None, [], {})
        ]
        context.update(
            {
                "user_role": "Administrador" if (user.is_staff or user.is_superuser) else "Usuario",
                "can_access_admin": user.is_staff or user.is_superuser,
                "can_edit_employees": user.has_perm("employees.change_employee"),
                "employee_fields": [
                    ("Codigo de empleado", employee.employee_code or "No registrado"),
                    ("Tipo de documento", employee.document_type or "No registrado"),
                    ("Numero de documento", employee.document_number or "No registrado"),
                    ("Correo electronico", employee.email or "No registrado"),
                    ("Telefono", employee.phone or "No registrado"),
                    ("Cargo", employee.position or "No registrado"),
                    ("Departamento", employee.department or "No registrado"),
                    ("Fecha de ingreso", employee.hire_date.strftime("%d/%m/%Y") if employee.hire_date else "No registrada"),
                    ("Fecha de nacimiento", employee.birth_date.strftime("%d/%m/%Y") if employee.birth_date else "No registrada"),
                    ("Salario", employee.salary or "No registrado"),
                    ("Estado", employee.get_status_display()),
                ],
                "employee_extra_fields": extra_fields,
            }
        )
        return context


class EmployeeUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = "employees/edit.html"
    model = Employee
    form_class = EmployeeUpdateForm
    permission_required = "employees.change_employee"
    raise_exception = True
    success_message = "Los datos del empleado fueron actualizados correctamente."

    def get_success_url(self):
        return reverse("employee-detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update(
            {
                "user_role": "Administrador" if (user.is_staff or user.is_superuser) else "Usuario",
                "can_access_admin": user.is_staff or user.is_superuser,
                "can_edit_employees": user.has_perm("employees.change_employee"),
                "employee": self.object,
            }
        )
        return context
