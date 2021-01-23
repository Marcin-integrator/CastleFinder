from django import forms
from .models import Locations

class LocationsModelForm(forms.ModelForm):
    class Meta:
        model = Locations
        fields = ('name', 'state', 'review')

        
    def save(self, user, name, review, state):
        obj = super().save(commit = False)
        obj.user = user
        obj.name = name
        obj.review = review
        obj.state = state
        obj.save()
        return obj