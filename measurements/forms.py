from django import forms
from .models import Locations

class LocationsModelForm(forms.ModelForm):
    class Meta:
        model = Locations
        fields= ('name', 'state', 'review',)