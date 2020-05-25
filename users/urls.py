from django.contrib import admin
from django.urls import path
from users import views as user_view

app_name = "users"

urlpatterns = [
    path("", user_view.Loginview)
]
