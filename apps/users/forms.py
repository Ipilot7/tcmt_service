from django import forms
from .models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ['username', 'full_name', 'passport', 'role', 'password', 'is_active']

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        if self.current_user and self.current_user.role == User.Role.MANAGER:
            # Managers can only assign 'user' role
            self.fields['role'].choices = [
                (User.Role.USER, User.Role.USER.label)
            ]
            self.fields['role'].initial = User.Role.USER

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
