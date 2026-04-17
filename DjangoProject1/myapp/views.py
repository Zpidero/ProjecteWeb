from django.http import JsonResponse
from django.http import HttpResponse
import random
import json
import urllib.request


# Funció auxiliar per no repetir codi de l'API
def fetch_api_data():
    url = "https://inazumaeleven-api.onrender.com/all"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            # Si l'API retorna un diccionari, agafem només els valors (els jugadors)
            if isinstance(data, dict):
                return list(data.values())
            return data
    except Exception as e:
        print(f"Error connectant a l'API: {e}")
        return []

from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Profile, Lineup, Futdraft, Players, Teams
import traceback

def index(request):
    return render(request, "base.html")


def home(request):
    return render(request, "myapp/home.html")


def game_view(request):
    return render(request, 'myapp/game.html')


# --- DRAFT LOGIC ---
def get_random_players(request):
    position = request.GET.get("position", "").upper()
    all_players = fetch_api_data()

    if position:
        filtered_players = [p for p in all_players if p.get("Position", "").upper() == position]
    else:
        filtered_players = all_players

    num_to_take = min(5, len(filtered_players))
    random_players = random.sample(filtered_players, num_to_take) if num_to_take > 0 else []
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


def players_list(request):
    players = fetch_api_data()  # La teva funció que crida a http://api:5000/players

    # 1. Recollida de paràmetres del formulari
    search = request.GET.get('search', '').strip().lower()
    pos = request.GET.get('position', '')
    element = request.GET.get('element', '')
    archetype = request.GET.get('archetype', '')
    gender = request.GET.get('gender', '')
    role = request.GET.get('role', '')
    age_group = request.GET.get('age_group', '')
    school_year = request.GET.get('school_year', '')

    # El filtre de total
    min_total = request.GET.get('min_total', '0')

    # 2. Aplicació de filtres (només si l'usuari ha seleccionat alguna cosa)
    if search:
        players = [p for p in players if search in p.get('Name', '').lower() or search in p.get('Nickname', '').lower()]

    if pos:
        players = [p for p in players if p.get('Position') == pos]

    if element:
        players = [p for p in players if p.get('Element') == element]

    if archetype:
        players = [p for p in players if p.get('Archetype') == archetype]

    if gender:
        players = [p for p in players if p.get('Gender') == gender]

    if role:
        players = [p for p in players if p.get('Role') == role]

    if age_group:
        players = [p for p in players if p.get('Age group') == age_group]

    if school_year:
        players = [p for p in players if p.get('School year') == school_year]

    # 3. Filtre per Total d'estadístiques
    if min_total.isdigit() and int(min_total) > 0:
        players = [p for p in players if int(p.get('Total', 0)) >= int(min_total)]

    return render(request, 'myapp/players.html', {
        'players': players,
    })

def teams_list(request):
    url_all_teams = "https://inazumaeleven-api.onrender.com/teams"
    teams_info = []

    try:
        with urllib.request.urlopen(url_all_teams) as response:
            data = json.loads(response.read().decode())
            team_names = data.get("", []) if isinstance(data, dict) else data
    except Exception as e:
        print(f"Error llegint llista d'equips: {e}")
        team_names = []

    search_query = request.GET.get('search', '').lower()
    if search_query:
        team_names = [n for n in team_names if search_query in n.lower()]

    for name in team_names[:20]:
        safe_name = urllib.parse.quote(name)
        url_detail = f"https://inazumaeleven-api.onrender.com/teams/{safe_name}"

        try:
            with urllib.request.urlopen(url_detail) as resp:
                detail = json.loads(resp.read().decode())
                # CAMBIA ESTO: Quita el guion bajo del principio
                detail['original_name'] = name
                teams_info.append(detail)
        except Exception as e:
            print(f"Error en detall d'equip {name}: {e}")
            # CAMBIA ESTO TAMBIÉN: Quita el guion bajo
            teams_info.append({"Team": name, "original_name": name, "Image": None})

    return render(request, 'myapp/teams.html', {'teams': teams_info})


def player_detail(request, player_id):
    all_players = fetch_api_data()

    # Busquem el jugador que coincideixi amb l'ID
    player = next((p for p in all_players if int(p.get('ID')) == int(player_id)), None)

    if not player:
        # Si no el troba, pots fer un 404 o redirigir a la llista
        return render(request, 'myapp/404.html', status=404)

    # MAPEJAT DE CLAUS PER A DJANGO TEMPLATES
    # Com que el JSON té claus amb espais ("Age group"), les passem a
    # claus amb guió baix ("Age_group") perquè el template les detecti.
    player['Age_group'] = player.get('Age group')
    player['School_year'] = player.get('School year')

    return render(request, 'myapp/player_detail.html', {'p': player})


def team_detail(request, team_name):
    team_name = urllib.parse.unquote(team_name)

    safe_name = urllib.parse.quote(team_name)
    url_team = f"https://inazumaeleven-api.onrender.com/teams/{safe_name}"

    try:
        with urllib.request.urlopen(url_team) as response:
            team_data = json.loads(response.read().decode())

        all_players = fetch_api_data()

        team_players_with_info = [
            p for p in all_players
            if p.get('Team', '').lower() == team_name.lower()  # 👈 única canvi
        ]

    except Exception as e:
        print(f"Error carregant detall d'equip: {e}")
        team_data = None
        team_players_with_info = []

    return render(request, 'myapp/team_detail.html', {
        'team': team_data,
        'team_players': team_players_with_info
    })

@login_required
@require_POST  
def save_draft(request):
    try:
        data = json.loads(request.body)
        name = data.get('name', 'El meu equip')
        formation_name = data.get('formation', '4-3-3')
        player_ids = data.get('players', [])

        all_players = fetch_api_data()
        selected_api_players = [p for p in all_players if str(p.get('ID')) in map(str, player_ids)]

        def safe_int(val, default=0):
            try:
                return int(val) if val else default
            except (ValueError, TypeError):
                return default

        saved_players = []
        for p in selected_api_players:
            team_name = p.get('Team', 'Desconegut')
            team_obj, _ = Teams.objects.get_or_create(
                name=team_name,
                defaults={'image': 'https://placeholder.com/1x1.png'}
            )
            
            player_obj, _ = Players.objects.update_or_create(
                id=p.get('ID'),
                defaults={
                    'image': p.get('Image', ''),
                    'name': p.get('Name', ''),
                    'nickname': p.get('Nickname', ''),
                    'game': p.get('Game', ''),
                    'archetype': p.get('Archetype', ''),
                    'position': p.get('Position', ''),
                    'element': p.get('Element', ''),
                    'power': safe_int(p.get('Power')),
                    'control': safe_int(p.get('Control')),
                    'technique': safe_int(p.get('Technique')),
                    'physical': safe_int(p.get('Physical')),
                    'agility': safe_int(p.get('Agility')),
                    'intelligence': safe_int(p.get('Intelligence')),
                    'total': safe_int(p.get('Total')),
                    'age_Group': p.get('Age group', ''),
                    'school_Year': p.get('School year', ''),
                    'gender': p.get('Gender', ''),
                    'role': p.get('Role', ''),
                    'team': team_obj,
                }
            )
            saved_players.append(player_obj)

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
        draft.players.set(saved_players)

        return JsonResponse({'ok': True, 'id': draft.id})
    except Exception as e:
        traceback.print_exc()
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
