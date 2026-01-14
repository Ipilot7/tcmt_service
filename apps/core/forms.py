from django import forms
from .models import Institution, Region

class InstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ['name', 'region']
