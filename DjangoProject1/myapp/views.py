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
    ranges = {
        1: (925, 930), #Canviar ja que no hi ha jugadors en aquest rang per certs roles s'ha de primer mirar quina posició es i despres mirar els 4 tipos de rang en aquella posició BUG A solicionar
        2: (931, 945),
        3: (946, 960),
        4: (961, 999)
    }
    position = request.GET.get("position", "")

    with urllib.request.urlopen('https://inazumaeleven-api.onrender.com/all') as response:
        data = json.loads(response.read().decode())

    all_players = list(data.values())

    # Prova categories en ordre aleatori fins trobar jugadors amplia categories basicament
    categories = list(range(1, 5))
    random.shuffle(categories)
    
    random_players = []
    interval_n = 1

    for cat in categories:
        min_avg, max_avg = ranges[cat]
        filtered = [
            p for p in all_players
            if p.get("Position") == position and min_avg <= int(p.get("Total", 0)) <= max_avg
        ]
        if len(filtered) >= 5:
            interval_n = cat
            random_players = random.sample(filtered, 5)
            break
        elif len(filtered) > 0:
            interval_n = cat
            random_players = filtered  # agafa els que hi hagi
            break

    for p in random_players:
        p["Category"] = interval_n

    return JsonResponse(random_players, safe=False)

def game_view(request):
    return render(request, 'myapp/game.html')

