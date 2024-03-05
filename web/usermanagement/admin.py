# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserRegistrationForm, CustomUserEditForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserRegistrationForm
    form = CustomUserEditForm
    model = CustomUser
    list_display = ("username", "email", "organization", "is_staff")
    list_filter = ("username", "email", "organization", "is_staff")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Permissions", {"fields": ("is_staff", "role")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "is_staff"),
            },
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)
