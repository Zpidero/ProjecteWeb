from django.http import JsonResponse
from django.http import HttpResponse
import random
import json
import urllib.request
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Profile, Lineup, Futdraft, Players

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


@login_required
@require_POST  
def save_draft(request):
    try:
        data = json.loads(request.body)
        name = data.get('name', 'El meu equip')
        formation_name = data.get('formation', '4-3-3')
        player_ids = data.get('players', [])

        parts = formation_name.split('-')
        lineup, _ = Lineup.objects.get_or_create(
            name=formation_name,
            defaults={
                'image': 'https://placeholder.com/1x1.png',  # URLField necessita valor vàlid
                'forwards':    int(parts[2]),
                'midfielders': int(parts[1]),
                'defenders':   int(parts[0]),
                'goalKeeper':  1,
            }
        )

        draft = Futdraft.objects.create(
            name=name,
            user=request.user,
            lineup=lineup,
        )
        draft.players.set(Players.objects.filter(id__in=player_ids))  # Players, no Player

        return JsonResponse({'ok': True, 'id': draft.id})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)
    

@login_required(login_url='login') # Redirects to your login named URL if not logged in
def game_view(request):
    return render(request, "myapp/game.html")

def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST, request.FILES) # Note: request.FILES is for the image
        if form.is_valid():
            user = form.save()
            # Create the profile and save the image
            profile_image = form.cleaned_data.get('image')
            Profile.objects.create(user=user, image=profile_image)
            
            login(request, user)
            return redirect("home")
    else:
        form = UserRegisterForm()
    return render(request, "myapp/register.html", {"register_form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect("home")

        else:
            messages.error(request, "Datos del formulario inválidos.")
    else:
        form = AuthenticationForm()
    
    return render(request, "myapp/login.html", {"login_form": form})