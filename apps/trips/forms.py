from django import forms
from .models import Trip

class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        exclude = ['request_number']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'result_info': forms.Textarea(attrs={'rows': 3}),
            'created_at': forms.DateInput(attrs={'type': 'date'}),
        }

class TripStatusForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['status', 'result_info'] # Users might add results? Spec said "User - changes only status".
        # Let's stick to status only for strict adherence, maybe result_info is for Managers.
        # Spec: "User - изменяет только статус"
        fields = ['status']
