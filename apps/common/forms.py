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
    ROLE_GROUP_NAMES = {
        ROLE_USER: "Rol Usuario",
        ROLE_REVIEWER: "Rol Revisor",
        ROLE_ADMIN: "Rol Administrador",
    }

    role = forms.ChoiceField(
        label="Rol de acceso",
        choices=[
            (ROLE_USER, "Usuario"),
            (ROLE_REVIEWER, "Revisor"),
            (ROLE_ADMIN, "Administrador"),
            (ROLE_SUPERADMIN, "Superadministrador"),
        ],
        widget=forms.Select(attrs={"class": "field-input"}),
    )
    can_edit_employees = forms.BooleanField(
        label="Puede editar empleados",
        required=False,
    )

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
            "email": "Correo electrónico",
            "is_active": "Usuario activo",
        }
        help_texts = {
            "username": "Este será el identificador que la persona usará para iniciar sesión.",
            "email": "Se usará para contacto y recuperación futura.",
        }

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop("current_user", None)
        super().__init__(*args, **kwargs)
        instance = self.instance

        if instance.pk:
            self.fields["role"].initial = self.get_role_from_instance(instance)
            self.fields["can_edit_employees"].initial = instance.has_perm("employees.change_employee")

        self.fields["role"].help_text = "Orden de acceso: Superadministrador, Administrador, Revisor y Usuario."

        self.fields["is_active"].help_text = "Si se desactiva, la persona ya no podrá ingresar al portal."

    @classmethod
    def get_role_from_instance(cls, instance):
        if instance.is_superuser:
            return cls.ROLE_SUPERADMIN
        if instance.groups.filter(name=cls.ROLE_GROUP_NAMES[cls.ROLE_ADMIN]).exists():
            return cls.ROLE_ADMIN
        if instance.groups.filter(name=cls.ROLE_GROUP_NAMES[cls.ROLE_REVIEWER]).exists():
            return cls.ROLE_REVIEWER
        if instance.groups.filter(name=cls.ROLE_GROUP_NAMES[cls.ROLE_USER]).exists():
            return cls.ROLE_USER
        if instance.is_staff:
            return cls.ROLE_ADMIN
        return cls.ROLE_USER

    @classmethod
    def get_role_label(cls, role):
        return {
            cls.ROLE_USER: "Usuario",
            cls.ROLE_REVIEWER: "Revisor",
            cls.ROLE_ADMIN: "Administrador",
            cls.ROLE_SUPERADMIN: "Superadministrador",
        }.get(role, "Usuario")

    def apply_role(self, user):
        role = self.cleaned_data["role"]
        user.is_superuser = role == self.ROLE_SUPERADMIN
        user.is_staff = role in {self.ROLE_ADMIN, self.ROLE_SUPERADMIN}
        return user

    def apply_role_groups(self, user, selected_groups=None):
        role_group_names = set(self.ROLE_GROUP_NAMES.values())
        source_groups = list(selected_groups) if selected_groups is not None else list(user.groups.all())
        preserved_groups = [group for group in source_groups if group.name not in role_group_names]
        role = self.cleaned_data["role"]
        if role != self.ROLE_SUPERADMIN:
            role_group, _ = Group.objects.get_or_create(name=self.ROLE_GROUP_NAMES[role])
            preserved_groups.append(role_group)
        user.groups.set(preserved_groups)

    def apply_employee_permission(self, user):
        permission = Permission.objects.get(codename="change_employee")
        if user.is_superuser or self.cleaned_data.get("can_edit_employees"):
            user.user_permissions.add(permission)
        else:
            user.user_permissions.remove(permission)


class ManagementUserPermissionForm(BaseManagementUserForm):
    class Meta(BaseManagementUserForm.Meta):
        fields = ["first_name", "last_name", "email", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance
        self.fields.pop("username", None)
        self.fields["role"].choices = [
            (self.ROLE_USER, "Usuario"),
            (self.ROLE_REVIEWER, "Revisor"),
            (self.ROLE_ADMIN, "Administrador"),
        ]

        if instance.is_superuser:
            self.fields["role"].disabled = True
            self.fields["can_edit_employees"].disabled = True
            self.fields["is_active"].disabled = True
            self.fields["role"].help_text = "Los superadministradores conservan su acceso completo."
            self.fields["can_edit_employees"].help_text = "Este acceso ya está habilitado para superadministradores."

        self.fields["role"].help_text = "Orden de acceso: Superadministrador, Administrador, Revisor y Usuario."

        if not custom_groups.exists():
            self.fields.pop("groups")
        else:
            self.fields["groups"].help_text = "Selecciona grupos adicionales solo si ya existen grupos funcionales creados."

        self.fields["role"].help_text = "Orden de acceso: Superadministrador, Administrador, Revisor y Usuario."
        self.fields.pop("groups")
        self.fields.pop("direct_permissions")

        self.fields["role"].help_text = "Orden de acceso: Superadministrador, Administrador, Revisor y Usuario."
        if "groups" in self.fields:
            self.fields.pop("groups")
        if "direct_permissions" in self.fields:
            self.fields.pop("direct_permissions")

    def save(self, commit=True):
        user = super().save(commit=False)
        if not user.is_superuser:
            user.is_staff = self.cleaned_data["role"] == self.ROLE_ADMIN

        if commit:
            user.save()
            if not user.is_superuser:
                self.apply_role_groups(user)
                self.apply_employee_permission(user)
            self.save_m2m()
        return user


class SuperAdminUserPermissionForm(BaseManagementUserForm):
    groups = forms.ModelMultipleChoiceField(
        label="Grupos",
        queryset=Group.objects.order_by("name"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "field-input", "size": 6}),
        help_text="Asigna grupos para heredar permisos de forma organizada.",
    )
    direct_permissions = forms.ModelMultipleChoiceField(
        label="Permisos específicos",
        queryset=Permission.objects.select_related("content_type").order_by("content_type__app_label", "codename"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "field-input", "size": 10}),
        help_text="Úsalo solo cuando necesites una autorización puntual fuera de los grupos.",
    )
    new_password = forms.CharField(
        label="Nueva contraseña temporal",
        required=False,
        widget=forms.PasswordInput(attrs={"class": "field-input", "autocomplete": "new-password"}),
        help_text="Déjalo vacío si no deseas cambiar la contraseña de esta cuenta.",
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
        else:
            self.fields["groups"].help_text = "Selecciona solo grupos funcionales adicionales, si los necesitas."

        if self.current_user and self.current_user.pk == instance.pk:
            self.fields["role"].help_text = "Puedes ajustar tu rol, pero ten cuidado al modificar permisos de tu propia cuenta."

    def clean(self):
        cleaned_data = super().clean()
        if self.current_user and self.instance.pk and self.current_user.pk == self.instance.pk:
            if not cleaned_data.get("is_active", True):
                self.add_error("is_active", "No puedes desactivar tu propia cuenta desde esta pantalla.")
            if cleaned_data.get("role") != self.ROLE_SUPERADMIN:
                self.add_error("role", "No puedes quitarte a ti mismo el rol de superadministrador.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        self.apply_role(user)

        if commit:
            user.save()
            self.apply_role_groups(user, self.cleaned_data["groups"])
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

    role = forms.ChoiceField(
        label="Rol inicial",
        choices=[
            (ROLE_USER, "Usuario"),
            (ROLE_REVIEWER, "Revisor"),
            (ROLE_ADMIN, "Administrador"),
            (ROLE_SUPERADMIN, "Superadministrador"),
        ],
        widget=forms.Select(attrs={"class": "field-input"}),
    )
    email = forms.EmailField(
        label="Correo electrónico",
        required=False,
        widget=forms.EmailInput(attrs={"class": "field-input"}),
    )
    first_name = forms.CharField(
        label="Nombres",
        required=False,
        widget=forms.TextInput(attrs={"class": "field-input"}),
    )
    last_name = forms.CharField(
        label="Apellidos",
        required=False,
        widget=forms.TextInput(attrs={"class": "field-input"}),
    )
    is_active = forms.BooleanField(
        label="Usuario activo",
        required=False,
        initial=True,
    )
    can_edit_employees = forms.BooleanField(
        label="Puede editar empleados",
        required=False,
    )
    groups = forms.ModelMultipleChoiceField(
        label="Grupos",
        queryset=Group.objects.order_by("name"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "field-input", "size": 6}),
    )
    direct_permissions = forms.ModelMultipleChoiceField(
        label="Permisos específicos",
        queryset=Permission.objects.select_related("content_type").order_by("content_type__app_label", "codename"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "field-input", "size": 10}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")
        widgets = {
            "username": forms.TextInput(attrs={"class": "field-input"}),
        }
        help_texts = {
            "username": "Nombre único para ingresar al portal.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["class"] = "field-input"
        self.fields["password1"].widget.attrs["class"] = "field-input"
        self.fields["password2"].widget.attrs["class"] = "field-input"
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Confirmar contraseña"
        self.fields["password1"].help_text = "Usa una contraseña segura para la cuenta inicial."
        self.fields["password2"].help_text = "Debe coincidir con la contraseña anterior."
        self.fields["is_active"].help_text = "Si se desactiva, la persona no podrá iniciar sesión."

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data["role"]
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.is_active = self.cleaned_data["is_active"]
        user.is_superuser = role == self.ROLE_SUPERADMIN
        user.is_staff = role in {self.ROLE_ADMIN, self.ROLE_SUPERADMIN}

        if commit:
            user.save()
            role_group_names = set(BaseManagementUserForm.ROLE_GROUP_NAMES.values())
            preserved_groups = []
            if role != self.ROLE_SUPERADMIN:
                role_group, _ = Group.objects.get_or_create(name=BaseManagementUserForm.ROLE_GROUP_NAMES[role])
                preserved_groups.append(role_group)
            user.groups.set(preserved_groups)
            user.user_permissions.clear()
            permission = Permission.objects.get(codename="change_employee")
            if user.is_superuser or self.cleaned_data["can_edit_employees"]:
                user.user_permissions.add(permission)
            else:
                user.user_permissions.remove(permission)
        return user
