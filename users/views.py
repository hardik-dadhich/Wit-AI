from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import FormView
# from . import forms
# Create your views here.


def Loginview(requests):
    return render(requests, "users/login.html", {})

# class Loginview(FormView):
#     template_name = "users/login.html"
    # form_class = forms.LoginForm
    # success_url = reverse_lazy("/")

    # def form_valid(self, form):
    #     email = form.cleaned_data.get("email")
    #     password = form.cleaned_data.get("password")
    #     user = authenticate(self.request, username=email, password=password)
    #     if user is not None:
    #         login(self.request, user)
    # return super().form_valid(form)
