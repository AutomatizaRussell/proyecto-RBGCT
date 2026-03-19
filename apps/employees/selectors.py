from .models import Employee


def list_employees():
    return Employee.objects.all()
