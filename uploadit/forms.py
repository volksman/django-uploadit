from django import forms

class FileForm(forms.Form):
    filename = forms.CharField()
    id = forms.CharField()
