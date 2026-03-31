from django.shortcuts import render
from django.http import JsonResponse
import random
import json
import urllib.request

def index(request):
    return render (request, "base.html")
def home(request):
    return render(request, "myapp/home.html")

def get_random_players(request):
    with urllib.request.urlopen('http://api:5000/all') as response:
        data = json.loads(response.read().decode())
    all_players = list(data.values())
    random_players = random.sample(all_players, 5)
    return JsonResponse(random_players, safe=False)  # devuelve solo los 5 jugadores como JSON

def game_view(request):
    return render(request, 'myapp/game.html')