from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.contrib.auth import logout
# from social_auth.utils import dsa_urlopen
# from . import forms
# Create your views here.


def home(request):
    request.session['is_login'] = True
    return render(request, "users/login.html", {})


@login_required
def afterlogin(request):

    if request.session.has_key("is_login"):
        return render(request, "users/home.html", {})
    return redirect('login')


def logout_view(request):
    logout(request)
    return redirect('home')


def SignUpView(request):
    return render(request, "users/signup.html", {})

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
