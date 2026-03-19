from django import forms

from .models import Employee


class EmployeeUpdateForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "employee_code",
            "first_name",
            "last_name",
            "document_type",
            "document_number",
            "email",
            "phone",
            "position",
            "department",
            "hire_date",
            "birth_date",
            "salary",
            "status",
        ]
        widgets = {
            "employee_code": forms.TextInput(attrs={"class": "field-input"}),
            "first_name": forms.TextInput(attrs={"class": "field-input"}),
            "last_name": forms.TextInput(attrs={"class": "field-input"}),
            "document_type": forms.TextInput(attrs={"class": "field-input"}),
            "document_number": forms.TextInput(attrs={"class": "field-input"}),
            "email": forms.EmailInput(attrs={"class": "field-input"}),
            "phone": forms.TextInput(attrs={"class": "field-input"}),
            "position": forms.TextInput(attrs={"class": "field-input"}),
            "department": forms.TextInput(attrs={"class": "field-input"}),
            "hire_date": forms.DateInput(attrs={"class": "field-input", "type": "date"}),
            "birth_date": forms.DateInput(attrs={"class": "field-input", "type": "date"}),
            "salary": forms.NumberInput(attrs={"class": "field-input", "step": "0.01"}),
            "status": forms.Select(attrs={"class": "field-input"}),
        }
        labels = {
            "employee_code": "C\u00f3digo de empleado",
            "first_name": "Nombres",
            "last_name": "Apellidos",
            "document_type": "Tipo de documento",
            "document_number": "N\u00famero de documento",
            "email": "Correo electr\u00f3nico",
            "phone": "Tel\u00e9fono",
            "position": "Cargo",
            "department": "Departamento",
            "hire_date": "Fecha de ingreso",
            "birth_date": "Fecha de nacimiento",
            "salary": "Salario",
            "status": "Estado",
        }

    def clean_document_number(self):
        value = self.cleaned_data["document_number"]
        queryset = Employee.objects.filter(document_number=value).exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("Ya existe un empleado con ese n\u00famero de documento.")
        return value

    def clean_employee_code(self):
        value = self.cleaned_data["employee_code"]
        queryset = Employee.objects.filter(employee_code=value).exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("Ya existe un empleado con ese c\u00f3digo.")
        return value
