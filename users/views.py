from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.contrib.auth import logout
import requests
from configparser import ConfigParser

config = ConfigParser()
config.read('./settings.ini')

# Create your views here.


def home(request):
    request.session['is_login'] = True
    return render(request, "users/login.html", {})


@login_required
def afterlogin(request):

    if request.session.has_key("is_login"):
        return render(request, "users/home.html", {})
    return redirect('/')


def logout_view(request):
    logout(request)
    return redirect('home')


def get_token():

    data = {
        'grant_type': 'client_credentials'
    }
    SOCIAL_AUTH_TWITTER_KEY = config.get("settings", 'SOCIAL_AUTH_TWITTER_KEY')
    SOCIAL_AUTH_TWITTER_SECRET = config.get(
        "settings", 'SOCIAL_AUTH_TWITTER_SECRET')

    response = requests.post('https://api.twitter.com/oauth2/token', data=data, auth=(
        SOCIAL_AUTH_TWITTER_KEY, SOCIAL_AUTH_TWITTER_SECRET))
    key = response.json()['access_token']
    return key


@login_required
def findPeople(request):
    keys = get_token()
    headers = {
        'authorization': f'Bearer {keys}',
    }
    username = request.user.username
    response = requests.get(
        f'https://api.twitter.com/1.1/friends/list.json?cursor=-1&screen_name={username}&skip_status=true&include_user_entities=false', headers=headers)
    data = response.json()
    friends_name = [i['name'] for i in data['users']]
    total_friends = len(friends_name)

    return render(request, "users/meetfriends.html", {'friends_name': friends_name, 'user': username, 'total_friends': total_friends})
