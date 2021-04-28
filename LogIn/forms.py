from django import forms

class UploadCityFile(forms.Form):
    city_file = forms.FileField()