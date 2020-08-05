from django import forms
from scheduling.models import Perawat
class PerawatForm(forms.ModelForm):
    class Meta:
        model = Perawat
        fields = "__all__"