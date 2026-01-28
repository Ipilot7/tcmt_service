from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm, UserChangeForm as BaseUserChangeForm
from .models import User, Role

class UserCreationForm(BaseUserCreationForm):
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Роли"
    )

    class Meta:
        model = User
        fields = ('login', 'fullname', 'psn', 'roles')

    def save(self, commit=True):
        user = super().save(commit=False)
        def save_m2m():
            if self.cleaned_data.get('roles'):
                user.roles.set(self.cleaned_data['roles'])
        self.save_m2m = save_m2m
        if commit:
            user.save()
            save_m2m()
        return user

class UserChangeForm(BaseUserChangeForm):
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Роли"
    )

    class Meta:
        model = User
        fields = ('login', 'fullname', 'psn', 'is_active', 'is_staff', 'is_superuser', 'roles')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['roles'].initial = self.instance.roles.all()

    def save(self, commit=True):
        user = super().save(commit=False)
        def save_m2m():
            if 'roles' in self.cleaned_data:
                user.roles.set(self.cleaned_data['roles'])
        self.save_m2m = save_m2m
        if commit:
            user.save()
            save_m2m()
        return user
