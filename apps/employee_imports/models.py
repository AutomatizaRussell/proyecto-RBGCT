from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel
from apps.employees.models import Employee


class EmployeeImport(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_PARTIAL = "partial"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
        (STATUS_PARTIAL, "Partial"),
    ]

    file = models.FileField(upload_to="imports/employees/%Y/%m/%d/")
    original_filename = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="employee_imports",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    total_rows = models.PositiveIntegerField(default=0)
    processed_rows = models.PositiveIntegerField(default=0)
    success_rows = models.PositiveIntegerField(default=0)
    error_rows = models.PositiveIntegerField(default=0)
    summary = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Employee import #{self.pk} - {self.status}"


class EmployeeImportRow(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_SUCCESS = "success"
    STATUS_ERROR = "error"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_ERROR, "Error"),
    ]

    import_batch = models.ForeignKey(EmployeeImport, related_name="rows", on_delete=models.CASCADE)
    row_number = models.PositiveIntegerField()
    raw_data = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    error_detail = models.JSONField(default=dict, blank=True)
    employee = models.ForeignKey(Employee, related_name="import_rows", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["row_number"]
        constraints = [
            models.UniqueConstraint(fields=["import_batch", "row_number"], name="unique_import_row_number"),
        ]
