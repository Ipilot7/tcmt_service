from django import forms
from .models import Institution, Equipment

class InstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ['name', 'region', 'sale_date', 'equipments']
        widgets = {
            'sale_date': forms.DateInput(attrs={'type': 'date'}),
            'equipments': forms.CheckboxSelectMultiple(),
        }

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['equipment_type', 'serial_number']
