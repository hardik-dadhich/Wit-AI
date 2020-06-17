from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.contrib.auth import logout
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView
from .models import Recording
from .forms import RecordingForm

from configparser import ConfigParser
from gtts import gTTS
import bs4
from bs4 import BeautifulSoup
import json
import os
import requests
import pyaudio
import wave


config = ConfigParser()
config.read('./settings.ini')

# Wit endpoint and API keys:
API_ENDPOINT = config.get("settings", 'API_ENDPOINT')
wit_access_token = config.get("settings", 'WIT_ACCESS_TOKEN')


# Create your views here.

def record_audio(RECORD_SECONDS, WAVE_OUTPUT_FILENAME):
    #--------- SETTING PARAMS FOR OUR AUDIO FILE ------------#
    FORMAT = pyaudio.paInt16    # format of wave
    CHANNELS = 2                # no. of audio channels
    RATE = 44100                # frame rate
    CHUNK = 1024                # frames per audio sample
    #--------------------------------------------------------#

    # creating PyAudio object
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    #----------------- start of recording -------------------#
    print("Listening...")

    # list to save all audio frames
    frames = []

    for i in range(int(RATE / CHUNK * RECORD_SECONDS)):
        # read audio stream from microphone
        data = stream.read(CHUNK)
        # append audio data to frames list
        frames.append(data)

    #------------------ end of recording --------------------#
    print("Finished recording.")

    stream.stop_stream()    # stop the stream object
    stream.close()          # close the stream object
    audio.terminate()       # terminate PortAudio

    #------------------ saving audio ------------------------#

    # create wave file object
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')

    # settings for wave file object
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))

    # closing the wave file object
    waveFile.close()


def read_audio(WAVE_FILENAME):
    # function to read audio(wav) file
    with open(WAVE_FILENAME, 'rb') as f:
        audio = f.read()
    return audio


# def home(request):
#     if request.session.has_key('is_login'):
#         return redirect('users:afterloginpage')
#     else:
#         request.session['is_login'] = True
#         return render(request, "users/login.html", {})
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


# def get_user_type():
#      headers = {'authorization': 'Bearer ' + wit_access_token,
#                'Content-Type': 'audio/wav'}

#     # making an HTTP post request
#     resp = requests.post(API_ENDPOINT, headers=headers,
#                          data=)

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
    if 'users' in data:
        friends_name = [i['name'] for i in data['users']]
        total_friends = len(friends_name)

        # user_desciption = data['description']

        return render(request, "users/meetfriends.html", {'friends_name': friends_name, 'user': username, 'total_friends': total_friends})
    else:
        return render(request, "users/meetfriends.html", {'friends_name': "NO USER FRIEND", 'user': username, 'total_friends': 0})


def RecognizeSpeech(AUDIO_FILENAME, num_seconds=5):

    # reading audio
    record_audio(num_seconds, AUDIO_FILENAME)
    audio = read_audio(AUDIO_FILENAME)
    # defining headers for HTTP request
    headers = {'authorization': 'Bearer ' + wit_access_token,
               'Content-Type': 'audio/wav'}

    # making an HTTP post request
    resp = requests.post(API_ENDPOINT, headers=headers,
                         data=audio)

    # converting response content to JSON format
    data = json.loads(resp.content)
    print("data", data)
    return data


@ login_required
def movies(request):
    if request.method == 'POST':
        # rec = Recording.objects.all()[0]
        rec = Recording.objects.order_by('-pk')[0]
        print("yeh", rec)
        asked_question = RecognizeSpeech(f'media/recordings/{rec}.wav', 4)
        print("final :", asked_question)
        intent = ''
        if 'text' not in asked_question:
            intent = "Not_sure"
        else:
            text = asked_question['text']
            print("\nYou said: {}".format(text))

            if asked_question['intents']:
                intent = asked_question['intents'][0]['name']
            else:
                intent = 'Not_trained'

        print("\nIntent is: {}".format(intent))

        # calling return answer funtion
        answer_dict = {'get_top_hollywood_movies':['The Godfather','The Shawshank Redemption','The Lord of the Rings'],
                    'get_top_bollywood_movies':['3 Idiots','Andhadhun','Dangal'], 
                    'get_marvel_movies':['Avengers Endgame','Captain Marvel', 'Black Panther'],
                    'Not_trained':['We are not trained on this'],'Not_sure': ['Not sure what you want to say']
                        }

        ReturnAnswer(intent, answer_dict)

        form = RecordingForm(request.POST, request.FILES)
        if form.is_valid():
            newrec = Recording(audiofile=request.FILES['recording'])
            newrec.save()
            return HttpResponseRedirect(reverse('users:lists'))
    else:
        form = RecordingForm()

    return render(
        request,
        'users/movies.html',
        {'form': form},
    )



@ login_required
def music(request):
    if request.method == 'POST':
        # rec = Recording.objects.all()[0]
        rec = Recording.objects.order_by('-pk')[0]
        print("yeh", rec)
        asked_question = RecognizeSpeech(f'media/recordings/{rec}.wav', 4)
        print("final :", asked_question)
        intent = ''
        if 'text' not in asked_question:
            intent = "Not_sure"
        else:
            text = asked_question['text']
            print("\nYou said: {}".format(text))

            if asked_question['intents']:
                intent = asked_question['intents'][0]['name']
            else:
                intent = 'Not_trained'

        print("\nIntent is: {}".format(intent))

        # calling return answer funtion
        answer_dict = {'get_top_songs_this_year':['Blinding lights','Dance Monkey'],'get_music_catagories':['Hip Hop','Rock','Pop'],
        'get_pop_singer':['Beyonce','Taylor Swift'],'get_top_indian_artists':['A R Rehman','Lata Mangeshkar'],
        'get_most_liked_music_video':['Despacito'],'Not_trained':['We are not trained on this'],'Not_sure': ['Not sure what you want to say']
            }

        ReturnAnswer(intent, answer_dict)

        form = RecordingForm(request.POST, request.FILES)
        if form.is_valid():
            newrec = Recording(audiofile=request.FILES['recording'])
            newrec.save()
            return HttpResponseRedirect(reverse('users:lists'))
    else:
        form = RecordingForm()

    return render(
        request,
        'users/music.html',
        {'form': form},
    )



@ login_required
def news(request):
    return render(request, "users/news.html", {})


@ login_required
def social(request):
    return render(request, "users/social.html", {})



def sports(request):
    if request.method == 'POST':
        # rec = Recording.objects.all()[0]
        rec = Recording.objects.order_by('-pk')[0]
        print("yeh", rec)
        asked_question = RecognizeSpeech(f'media/recordings/{rec}.wav', 4)
        print("final :", asked_question)
        intent = ''
        if 'text' not in asked_question:
            intent = "Not_sure"
        else:
            text = asked_question['text']
            print("\nYou said: {}".format(text))

            if asked_question['intents']:
                intent = asked_question['intents'][0]['name']
            else:
                intent = 'Not_trained'

        print("\nIntent is: {}".format(intent))

        # calling return answer funtion
        answer_dict = {'get_apple_stock_price':'https://finance.yahoo.com/quote/AAPL?p=AAPL&.tsrc=fin-srch',
                      'get_facebook_stock_price':'https://finance.yahoo.com/quote/FB?p=FB&.tsrc=fin-srch',
                      'get_walmart_stock_price':'https://finance.yahoo.com/quote/WMT?p=WMT&.tsrc=fin-srch',
                      'get_microsoft_stock_price':'https://finance.yahoo.com/quote/MSFT?p=MSFT&.tsrc=fin-srch',
                     'get_twitter_stock_price':'https://finance.yahoo.com/quote/TWTR?p=TWTR&.tsrc=fin-srch',
                      'get_amazon_stock_price':'https://finance.yahoo.com/quote/AMZN?p=AMZN&.tsrc=fin-srch',
                     'Not_trained':'We are not trained on this','Not_sure':'You did not said anything'}
        ReturnStockPrice(intent, answer_dict)

        form = RecordingForm(request.POST, request.FILES)
        if form.is_valid():
            newrec = Recording(audiofile=request.FILES['recording'])
            newrec.save()
            return HttpResponseRedirect(reverse('users:lists'))
    else:
        form = RecordingForm()

    return render(
        request,
        'users/sports.html',
        {'form': form},
    )

def ReturnStockPrice(converted_text_intent, stored_result_dict):

    if converted_text_intent == 'Not_trained':
        text = stored_result_dict[converted_text_intent]
    
    elif converted_text_intent == 'Not_sure':
        text = stored_result_dict[converted_text_intent]

    else:
        url = stored_result_dict[converted_text_intent]
        response = requests.get(url)
        #print("\nWit Response is: {}".format(response[0]))

        soup = bs4.BeautifulSoup(response.text,"lxml")

        text = soup.find_all('div',{'class': "My(6px) Pos(r) smartphone_Mt(6px)"})[0].find('span').text

    language = 'en'

    myobj = gTTS(text=text, lang=language, slow=False)

    myobj.save("sample.mp3")

    # Playing the converted file
    os.system("mpg321 sample.mp3")
    


def list_to_Save(request):
    if request.method == 'POST':
        form = RecordingForm(request.POST, request.FILES)
        if form.is_valid():
            print(form)
            newrec = Recording(audiofile=request.FILES['audiofile'])
            newrec.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('users:lists'))
    else:
        form = RecordingForm()  # An empty, unbound form

        # Load documents for the list page
    recordings = Recording.objects.all()

    # Render list page with the documents and the form
    return render(
        request,
        'users/list.html',
        {'recordings': recordings, 'form': form},
    )


def games(request):
    if request.method == 'POST':
        # rec = Recording.objects.all()[0]
        rec = Recording.objects.order_by('-pk')[0]
        print("yeh", rec)
        asked_question = RecognizeSpeech(f'media/recordings/{rec}.wav', 4)
        print("final :", asked_question)
        intent = ''
        if 'text' not in asked_question:
            intent = "Not_sure"
        else:
            text = asked_question['text']
            print("\nYou said: {}".format(text))

            if asked_question['intents']:
                intent = asked_question['intents'][0]['name']
            else:
                intent = 'Not_trained'

        print("\nIntent is: {}".format(intent))

        # calling return answer funtion
        answer_dict = {'get_cricket_player_india': ['Sachin'], 'get_best_batsman_world': ['Steve Smith'], 'get_football_player': ['Lionel Messi', 'Cristiano Ronaldo'], 'get_football_clubs': [
            'Football Club Barcelona', 'Real Madrid', 'Liverpool'], 'get_football_teams': ['Belgium', 'France', 'Brazil'], 'get_top_sports_world': ['Soccer/Football', 'Cricket', 'Basketball'], 'Not_trained': ['We are not trained on this'], 'Not_sure': ['Not sure what you want to say']}
        ReturnAnswer(intent, answer_dict)

        form = RecordingForm(request.POST, request.FILES)
        if form.is_valid():
            newrec = Recording(audiofile=request.FILES['recording'])
            newrec.save()
            return HttpResponseRedirect(reverse('users:lists'))
    else:
        form = RecordingForm()

    return render(
        request,
        'users/games.html',
        {'form': form},
    )


def ReturnAnswer(converted_text_intent, stored_result_dict):

    response = stored_result_dict[converted_text_intent]

    print("\nWit Response is: {}".format(response[0]))

    text = response[0]
    language = 'en'

    myobj = gTTS(text=text, lang=language, slow=False)

    myobj.save("sample.mp3")

    # Playing the converted file
    os.system("mpg321 sample.mp3")
