from django import forms
from .models import Request

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        exclude = ['request_number']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'created_at': forms.DateInput(attrs={'type': 'date'}),
        }

class RequestStatusForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['status']
