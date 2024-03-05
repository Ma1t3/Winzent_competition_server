from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser


class CustomUserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "organization",
            "password1",
            "password2",
        )


class CustomUserEditForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("email",)
