from django.contrib import admin
from django.urls import path, include
from users import views as user_view


app_name = "users"

urlpatterns = [
    path("", user_view.home, name='home'),
    path("accounts/profile/", user_view.afterlogin, name='afterloginpage'),
    path("cards/find_people/", user_view.findPeople, name='find_peoples'),
    path("cards/games/", user_view.games, name='wit_games'),
    path("cards/movies/", user_view.movies, name='wit_movies'),
    path("cards/music/", user_view.music, name='wit_music'),
    path("cards/news/", user_view.news, name='wit_news'),
    path("cards/social/", user_view.social, name='wit_social'),
    path("cards/sports/", user_view.sports, name='wit_sport')
]
