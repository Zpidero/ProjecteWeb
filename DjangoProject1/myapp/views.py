from django.shortcuts import render
from django.http import JsonResponse
import random
import json
import urllib.request


# Funció auxiliar per no repetir codi de l'API
def fetch_api_data():
    url = "http://api:5000/all"
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
    url_all_teams = "http://api:5000/teams/"
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
        url_detail = f"http://api:5000/teams/{safe_name}"

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
    url_team = f"http://api:5000/teams/{safe_name}"

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