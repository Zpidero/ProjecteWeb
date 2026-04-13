from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
import random
import json
import urllib.request
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

def index(request):
    return render (request, "base.html")
def home(request):
    return render(request, "myapp/home.html")

def get_random_players(request):
    position = request.GET.get("position", "")

    with urllib.request.urlopen('http://api:5000/all') as response:
        data = json.loads(response.read().decode())

    all_players = list(data.values())
    if position:
        filtered_players = [p for p in all_players if p.get("Position", "").upper() == position]
    else:
        filtered_players = all_players

    num_to_take = min(5, len(filtered_players))
    random_players = random.sample(filtered_players, num_to_take) if num_to_take > 0 else []
    return JsonResponse(random_players, safe=False)

def game_view(request):
    return render(request, 'myapp/game.html')

def register_view(request):
    if request.method == 'GET':
        return render(request, 'myapp/register.html', {'form': UserCreationForm})
    else:
        if request.POST['password1'] == request.POST['password2']:
            #register the user
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], 
                    password=request.POST['password1']
                )
                user.save()
                return HttpResponse("User created successfully")
            
            except:
                return render(request, 'myapp/register.html', {
                    'form': UserCreationForm,
                    'error': 'Username already exists'
                })
            
        return render(request, 'myapp/register.html', {
            'form': UserCreationForm,
            'error': 'Passwords do not match'
        })