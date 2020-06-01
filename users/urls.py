from django.contrib import admin
from django.urls import path, include
from users import views as user_view


app_name = "users"

urlpatterns = [
    path("", user_view.home, name='home'),
    path("accounts/profile/", user_view.afterlogin, name='afterloginpage'),
    path("cards/find_people/", user_view.findPeople, name='find_peoples')
]
