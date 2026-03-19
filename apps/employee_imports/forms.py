from django import forms


class EmployeeImportUploadForm(forms.Form):
    file = forms.FileField(
        label="Archivo Excel",
        help_text="Archivo .xlsx. Puedes usar columnas en español como codigo_empleado, nombres, apellidos, documento, correo, cargo y departamento.",
        widget=forms.ClearableFileInput(attrs={"class": "field-input"}),
    )

    def clean_file(self):
        file = self.cleaned_data["file"]
        if not file.name.lower().endswith(".xlsx"):
            raise forms.ValidationError("Solo se permiten archivos Excel con extension .xlsx.")
        return file
