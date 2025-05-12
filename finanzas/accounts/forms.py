from django import forms
from .models import Consulta

class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['consulta']
        widgets = {
            'consulta': forms.Textarea(attrs={'rows': 3}),
        }