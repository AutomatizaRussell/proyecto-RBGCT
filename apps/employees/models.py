from django.db import models

from apps.common.models import TimeStampedModel


class Employee(TimeStampedModel):
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_SUSPENDED = "suspended"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Activo"),
        (STATUS_INACTIVE, "Inactivo"),
        (STATUS_SUSPENDED, "Suspendido"),
    ]

    employee_code = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    document_type = models.CharField(max_length=20, blank=True)
    document_number = models.CharField(max_length=50, unique=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    position = models.CharField(max_length=120, blank=True)
    department = models.CharField(max_length=120, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["employee_code"]),
            models.Index(fields=["document_number"]),
            models.Index(fields=["status"]),
            models.Index(fields=["department"]),
        ]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
