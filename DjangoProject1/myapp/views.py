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
from .models import Profile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

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

