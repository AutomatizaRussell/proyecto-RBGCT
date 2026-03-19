from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, Permission

User = get_user_model()


class BaseManagementUserForm(forms.ModelForm):
    ROLE_USER = "user"
    ROLE_REVIEWER = "reviewer"
    ROLE_ADMIN = "admin"
    ROLE_SUPERADMIN = "superadmin"
    ADDED_ROLE_NONE = "none"
    ROLE_GROUP_NAMES = {
        ROLE_REVIEWER: "Rol Revisor",
        ROLE_ADMIN: "Rol Administrador",
    }

    initial_role = forms.ChoiceField(
        label="Rol inicial",
        choices=[
            (ROLE_USER, "Usuario"),
            (ROLE_SUPERADMIN, "Superadministrador"),
        ],
        widget=forms.Select(attrs={"class": "field-input"}),
    )
    added_role = forms.ChoiceField(
        label="Rol añadido",
        choices=[
            (ADDED_ROLE_NONE, "Sin rol añadido"),
            (ROLE_REVIEWER, "Revisor"),
            (ROLE_ADMIN, "Administrador"),
        ],
        widget=forms.Select(attrs={"class": "field-input"}),
    )
    can_edit_employees = forms.BooleanField(label="Puede editar empleados", required=False)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "field-input"}),
            "first_name": forms.TextInput(attrs={"class": "field-input"}),
            "last_name": forms.TextInput(attrs={"class": "field-input"}),
            "email": forms.EmailInput(attrs={"class": "field-input"}),
            "is_active": forms.CheckboxInput(),
        }
        labels = {
            "username": "Usuario de ingreso",
            "first_name": "Nombres",
            "last_name": "Apellidos",
            "email": "Correo electronico",
            "is_active": "Usuario activo",
        }
        help_texts = {
            "username": "Este sera el identificador que la persona usara para iniciar sesion.",
            "email": "Se usara para contacto y recuperacion futura.",
        }

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop("current_user", None)
        super().__init__(*args, **kwargs)
        instance = self.instance

        if instance.pk:
            self.fields["initial_role"].initial = self.get_initial_role_from_instance(instance)
            self.fields["added_role"].initial = self.get_added_role_from_instance(instance)
            self.fields["can_edit_employees"].initial = instance.has_perm("employees.change_employee")

        self.fields["initial_role"].help_text = "Toda cuenta inicia como Usuario, excepto cuando necesita acceso de Superadministrador."
        self.fields["added_role"].help_text = "Si la persona necesita mas alcance, aqui puedes agregar Revisor o Administrador."
        self.fields["is_active"].help_text = "Si se desactiva, la persona ya no podra ingresar al portal."
        self._sync_added_role_field_state()

    def _sync_added_role_field_state(self):
        initial_role = self.data.get(self.add_prefix("initial_role")) if self.is_bound else self.fields["initial_role"].initial
        if initial_role == self.ROLE_SUPERADMIN:
            self.fields["added_role"].disabled = True
            self.fields["added_role"].help_text = "No aplica. Un superadministrador ya tiene control total del sistema."
        else:
            self.fields["added_role"].disabled = False

    @classmethod
    def get_initial_role_from_instance(cls, instance):
        if instance.is_superuser:
            return cls.ROLE_SUPERADMIN
        return cls.ROLE_USER

    @classmethod
    def get_added_role_from_instance(cls, instance):
        if instance.is_superuser:
            return cls.ADDED_ROLE_NONE
        if instance.groups.filter(name=cls.ROLE_GROUP_NAMES[cls.ROLE_ADMIN]).exists():
            return cls.ROLE_ADMIN
        if instance.groups.filter(name=cls.ROLE_GROUP_NAMES[cls.ROLE_REVIEWER]).exists():
            return cls.ROLE_REVIEWER
        if instance.is_staff:
            return cls.ROLE_ADMIN
        return cls.ADDED_ROLE_NONE

    @classmethod
    def get_role_label(cls, role):
        return {
            cls.ROLE_USER: "Usuario",
            cls.ROLE_REVIEWER: "Revisor",
            cls.ROLE_ADMIN: "Administrador",
            cls.ROLE_SUPERADMIN: "Superadministrador",
        }.get(role, "Usuario")

    @classmethod
    def get_display_role_label(cls, instance):
        initial_role = cls.get_initial_role_from_instance(instance)
        if initial_role == cls.ROLE_SUPERADMIN:
            return cls.get_role_label(cls.ROLE_SUPERADMIN)
        added_role = cls.get_added_role_from_instance(instance)
        if added_role != cls.ADDED_ROLE_NONE:
            return f"Usuario con rol {cls.get_role_label(added_role)}"
        return cls.get_role_label(cls.ROLE_USER)

    def apply_role(self, user):
        initial_role = self.cleaned_data["initial_role"]
        added_role = self.cleaned_data.get("added_role", self.ADDED_ROLE_NONE)
        user.is_superuser = initial_role == self.ROLE_SUPERADMIN
        user.is_staff = user.is_superuser or added_role == self.ROLE_ADMIN
        return user

    def apply_role_groups(self, user, selected_groups=None):
        role_group_names = set(self.ROLE_GROUP_NAMES.values())
        source_groups = list(selected_groups) if selected_groups is not None else list(user.groups.all())
        preserved_groups = [group for group in source_groups if group.name not in role_group_names]
        initial_role = self.cleaned_data["initial_role"]
        added_role = self.cleaned_data.get("added_role", self.ADDED_ROLE_NONE)
        if initial_role != self.ROLE_SUPERADMIN and added_role in self.ROLE_GROUP_NAMES:
            role_group, _ = Group.objects.get_or_create(name=self.ROLE_GROUP_NAMES[added_role])
            preserved_groups.append(role_group)
        user.groups.set(preserved_groups)

    def apply_employee_permission(self, user):
        permission = Permission.objects.get(codename="change_employee")
        if user.is_superuser or self.cleaned_data.get("can_edit_employees"):
            user.user_permissions.add(permission)
        else:
            user.user_permissions.remove(permission)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("initial_role") == self.ROLE_SUPERADMIN:
            cleaned_data["added_role"] = self.ADDED_ROLE_NONE
        return cleaned_data


class ManagementUserPermissionForm(BaseManagementUserForm):
    class Meta(BaseManagementUserForm.Meta):
        fields = ["first_name", "last_name", "email", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance
        self.fields.pop("username", None)
        self.fields["initial_role"].choices = [(self.ROLE_USER, "Usuario")]

        if instance.is_superuser:
            self.fields["initial_role"].disabled = True
            self.fields["added_role"].disabled = True
            self.fields["can_edit_employees"].disabled = True
            self.fields["is_active"].disabled = True
            self.fields["initial_role"].help_text = "Los superadministradores conservan su acceso completo."
            self.fields["added_role"].help_text = "Los superadministradores no necesitan un rol añadido."
            self.fields["can_edit_employees"].help_text = "Este acceso ya esta habilitado para superadministradores."

    def save(self, commit=True):
        user = super().save(commit=False)
        if not user.is_superuser:
            user.is_staff = self.cleaned_data["added_role"] == self.ROLE_ADMIN

        if commit:
            user.save()
            if not user.is_superuser:
                self.apply_role_groups(user)
                self.apply_employee_permission(user)
            self.save_m2m()
        return user


class SuperAdminUserPermissionForm(BaseManagementUserForm):
    groups = forms.ModelMultipleChoiceField(
        label="Grupos adicionales",
        queryset=Group.objects.order_by("name"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "field-input", "size": 6}),
        help_text="Usalo solo si ya existen grupos funcionales definidos para la operacion.",
    )
    direct_permissions = forms.ModelMultipleChoiceField(
        label="Permisos avanzados",
        queryset=Permission.objects.select_related("content_type").order_by("content_type__app_label", "codename"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "field-input", "size": 10}),
        help_text="Se recomienda usarlo solo para administracion avanzada.",
    )
    new_password = forms.CharField(
        label="Nueva contrasena temporal",
        required=False,
        widget=forms.PasswordInput(attrs={"class": "field-input", "autocomplete": "new-password"}),
        help_text="Dejalo vacio si no deseas cambiar la contrasena de esta cuenta.",
    )

    class Meta(BaseManagementUserForm.Meta):
        fields = ["username", "first_name", "last_name", "email", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance
        custom_groups = Group.objects.exclude(name__in=self.ROLE_GROUP_NAMES.values()).order_by("name")
        self.fields["groups"].queryset = custom_groups

        if instance.pk:
            self.fields["groups"].initial = instance.groups.exclude(name__in=self.ROLE_GROUP_NAMES.values())
            self.fields["direct_permissions"].initial = instance.user_permissions.all()

        if not custom_groups.exists():
            self.fields.pop("groups")

        if self.current_user and self.current_user.pk == instance.pk:
            self.fields["initial_role"].help_text = "Puedes ajustar tu rol inicial, pero ten cuidado al modificar permisos de tu propia cuenta."

    def clean(self):
        cleaned_data = super().clean()
        if self.current_user and self.instance.pk and self.current_user.pk == self.instance.pk:
            if not cleaned_data.get("is_active", True):
                self.add_error("is_active", "No puedes desactivar tu propia cuenta desde esta pantalla.")
            if cleaned_data.get("initial_role") != self.ROLE_SUPERADMIN:
                self.add_error("initial_role", "No puedes quitarte a ti mismo el rol de superadministrador.")
        if cleaned_data.get("initial_role") == self.ROLE_SUPERADMIN:
            cleaned_data["added_role"] = self.ADDED_ROLE_NONE
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        self.apply_role(user)

        if commit:
            user.save()
            selected_groups = self.cleaned_data.get("groups", [])
            self.apply_role_groups(user, selected_groups)
            user.user_permissions.set(self.cleaned_data["direct_permissions"])
            self.apply_employee_permission(user)
            new_password = self.cleaned_data.get("new_password")
            if new_password:
                user.set_password(new_password)
                user.save(update_fields=["password"])
            self.save_m2m()
        return user


class ManagementUserCreateForm(UserCreationForm):
    ROLE_USER = BaseManagementUserForm.ROLE_USER
    ROLE_REVIEWER = BaseManagementUserForm.ROLE_REVIEWER
    ROLE_ADMIN = BaseManagementUserForm.ROLE_ADMIN
    ROLE_SUPERADMIN = BaseManagementUserForm.ROLE_SUPERADMIN

    initial_role = forms.ChoiceField(
        label="Rol inicial",
        choices=[
            (ROLE_USER, "Usuario"),
            (ROLE_SUPERADMIN, "Superadministrador"),
        ],
        widget=forms.Select(attrs={"class": "field-input"}),
    )
    added_role = forms.ChoiceField(
        label="Rol añadido",
        choices=[
            (BaseManagementUserForm.ADDED_ROLE_NONE, "Sin rol añadido"),
            (ROLE_REVIEWER, "Revisor"),
            (ROLE_ADMIN, "Administrador"),
        ],
        widget=forms.Select(attrs={"class": "field-input"}),
    )
    email = forms.EmailField(label="Correo electronico", required=False, widget=forms.EmailInput(attrs={"class": "field-input"}))
    first_name = forms.CharField(label="Nombres", required=False, widget=forms.TextInput(attrs={"class": "field-input"}))
    last_name = forms.CharField(label="Apellidos", required=False, widget=forms.TextInput(attrs={"class": "field-input"}))
    is_active = forms.BooleanField(label="Usuario activo", required=False, initial=True)
    can_edit_employees = forms.BooleanField(label="Puede editar empleados", required=False)
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.none(), required=False)
    direct_permissions = forms.ModelMultipleChoiceField(queryset=Permission.objects.none(), required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")
        widgets = {
            "username": forms.TextInput(attrs={"class": "field-input"}),
        }
        help_texts = {
            "username": "Nombre unico para ingresar al portal.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["class"] = "field-input"
        self.fields["password1"].widget.attrs["class"] = "field-input"
        self.fields["password2"].widget.attrs["class"] = "field-input"
        self.fields["password1"].label = "Contrasena"
        self.fields["password2"].label = "Confirmar contrasena"
        self.fields["password1"].help_text = "Usa una contrasena segura para la cuenta inicial."
        self.fields["password2"].help_text = "Debe coincidir con la contrasena anterior."
        self.fields["is_active"].help_text = "Si se desactiva, la persona no podra iniciar sesion."
        self.fields["initial_role"].help_text = "Selecciona Usuario para cuentas normales o Superadministrador para acceso total."
        self.fields["added_role"].help_text = "Si la persona necesita mas alcance, aqui puedes agregar Revisor o Administrador."
        self.fields.pop("groups", None)
        self.fields.pop("direct_permissions", None)

    def save(self, commit=True):
        user = super().save(commit=False)
        initial_role = self.cleaned_data["initial_role"]
        added_role = self.cleaned_data["added_role"]
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.is_active = self.cleaned_data["is_active"]
        user.is_superuser = initial_role == self.ROLE_SUPERADMIN
        user.is_staff = user.is_superuser or added_role == self.ROLE_ADMIN

        if commit:
            user.save()
            preserved_groups = []
            if initial_role != self.ROLE_SUPERADMIN and added_role in BaseManagementUserForm.ROLE_GROUP_NAMES:
                role_group, _ = Group.objects.get_or_create(name=BaseManagementUserForm.ROLE_GROUP_NAMES[added_role])
                preserved_groups.append(role_group)
            user.groups.set(preserved_groups)
            user.user_permissions.clear()
            permission = Permission.objects.get(codename="change_employee")
            if user.is_superuser or self.cleaned_data["can_edit_employees"]:
                user.user_permissions.add(permission)
            else:
                user.user_permissions.remove(permission)
        return user
