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
        1: (925, 930),
        2: (931, 945),
        3: (946, 960),
        4: (961, 999)
    }
    position = request.GET.get("position", "")
    interval_n = random.randint(1, 4)
    min_avg = ranges[interval_n][0]
    max_avg = ranges[interval_n][1]

    with urllib.request.urlopen('http://api:5000/all') as response:
        data = json.loads(response.read().decode())

    all_players = list(data.values())
    filtered_players = [
        p for p in all_players
        if (
                p.get("Position") == position and
                min_avg <= int(p.get("Total", 0)) <= max_avg
        )
    ]

    num_to_take = min(5, len(filtered_players))
    random_players = random.sample(filtered_players, num_to_take) if num_to_take > 0 else []
    for p in random_players:
        p["Category"] = interval_n
    return JsonResponse(random_players, safe=False)

def game_view(request):
    return render(request, 'myapp/game.html')

