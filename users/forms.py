# class LoginForm(forms.Form):
#     email = forms.EmailField()
#     password = forms.CharField(max_length=length, ${blank=True, null=True})

#     def clean(self):
#         email = self.cleaned_data.get("email")
#         password = self.cleaned_data("password")
#         try:
#             print("User exits")
#         else:
#             print("user faild")

from django import forms
from django.forms import ModelForm


class RecordingForm(forms.Form):
    audiofile = forms.FileField(label='Select a file')
