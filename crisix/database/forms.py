import os
from django import forms
from django.conf import settings

class UploadFileForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={
        'style': 'visibility:hidden;',
        'onchange': 'document.getElementById("pretty").value = getFileName(this);'}))
    merge = forms.BooleanField(initial=True, required=False)
