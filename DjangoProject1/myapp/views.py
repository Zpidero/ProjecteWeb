from django.http import JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import UserRegisterForm
from .models import Profile, Lineup, Futdraft, Players, Teams
import random
import json
import traceback


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_int(val, default=0):
    try:
        return int(val) if val else default
    except (ValueError, TypeError):
        return default


# ---------------------------------------------------------------------------
# General
# ---------------------------------------------------------------------------

def index(request):
    return render(request, "base.html")


def home(request):
    return render(request, "myapp/home.html")


# ---------------------------------------------------------------------------
# Players Navas
# ---------------------------------------------------------------------------

def players_list(request):
    players = Players.objects.select_related('team').all()

    search      = request.GET.get('search', '').strip()
    pos         = request.GET.get('position', '')
    element     = request.GET.get('element', '')
    archetype   = request.GET.get('archetype', '')
    gender      = request.GET.get('gender', '')
    role        = request.GET.get('role', '')
    age_group   = request.GET.get('age_group', '')
    school_year = request.GET.get('school_year', '')
    min_total   = request.GET.get('min_total', '0')

    if search:
        players = players.filter(
            Q(name__icontains=search) | Q(nickname__icontains=search)
        )
    if pos:         players = players.filter(position=pos)
    if element:     players = players.filter(element=element)
    if archetype:   players = players.filter(archetype=archetype)
    if gender:      players = players.filter(gender=gender)
    if role:        players = players.filter(role=role)
    if age_group:   players = players.filter(age_Group=age_group)
    if school_year: players = players.filter(school_Year=school_year)
    if min_total.isdigit() and int(min_total) > 0:
        players = players.filter(total__gte=int(min_total))

    paginator = Paginator(players, 20)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'myapp/players.html', {'players': page_obj})


def player_detail(request, player_id):
    try:
        player = Players.objects.select_related('team').get(id=player_id)
    except Players.DoesNotExist:
        return render(request, 'myapp/404.html', status=404)

    stats = [
        ('Power',        player.power),
        ('Control',      player.control),
        ('Technique',    player.technique),
        ('Pressure',     player.pressure),
        ('Physical',     player.physical),
        ('Agility',      player.agility),
        ('Intelligence', player.intelligence),
    ]

    return render(request, 'myapp/player_detail.html', {'p': player, 'stats': stats})


# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------

def teams_list(request):
    teams = Teams.objects.annotate(player_count=Count('players')).order_by('name')

    search_query = request.GET.get('search', '').strip()
    if search_query:
        teams = teams.filter(name__icontains=search_query)

    paginator = Paginator(teams, 20)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'myapp/teams.html', {'teams': page_obj})


def team_detail(request, team_name):
    try:
        team         = Teams.objects.get(name__iexact=team_name)
        team_players = Players.objects.filter(team=team).select_related('team')
    except Teams.DoesNotExist:
        team         = None
        team_players = []

    return render(request, 'myapp/team_detail.html', {
        'team':         team,
        'team_players': team_players,
    })


# ---------------------------------------------------------------------------
# Game Players edu
# ---------------------------------------------------------------------------

def get_random_players(request):
    position = request.GET.get("position", "")

    ranges = {
        1: (925, 930),
        2: (931, 945),
        3: (946, 960),
        4: (961, 999),
    }

    categories = list(range(1, 5))
    random.shuffle(categories)

    qs         = []
    interval_n = 1

    for cat in categories:
        min_avg, max_avg = ranges[cat]
        candidates = Players.objects.filter(
            position=position,
            total__gte=min_avg,
            total__lte=max_avg,
        ).select_related('team')
        count = candidates.count()
        if count >= 5:
            interval_n = cat
            qs = random.sample(list(candidates), 5)
            break
        elif count > 0:
            interval_n = cat
            qs = list(candidates)
            break

    random_players = [
        {
            "ID":           p.id,
            "Name":         p.name,
            "Nickname":     p.nickname,
            "Position":     p.position,
            "Image":        p.image,
            "Element":      p.element,
            "Team":         p.team.name if p.team else "",
            "Team_image":   p.team.image if p.team else "",
            "Total":        p.total,
            "Power":        p.power,
            "Control":      p.control,
            "Technique":    p.technique,
            "Physical":     p.physical,
            "Agility":      p.agility,
            "Intelligence": p.intelligence,
            "Pressure":     p.pressure,
            "Category":     interval_n,
        }
        for p in qs
    ]

    return JsonResponse(random_players, safe=False)


@login_required(login_url='login')
def game_view(request):
    return render(request, "myapp/game.html")


# ---------------------------------------------------------------------------
# Drafts Players Gerard
# ---------------------------------------------------------------------------

@login_required
@require_POST
def save_draft(request):
    try:
        data           = json.loads(request.body)
        name           = data.get('name', 'El meu equip')
        formation_name = data.get('formation', '4-3-3')
        player_ids     = data.get('players', [])

        saved_players = list(Players.objects.filter(id__in=player_ids))

        parts = formation_name.split('-')
        lineup, _ = Lineup.objects.get_or_create(
            name=formation_name,
            defaults={
                'image':       'https://placeholder.com/1x1.png',
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
            player_order=player_ids,
        )
        draft.players.set(saved_players)

        return JsonResponse({'ok': True, 'id': draft.id})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@login_required(login_url='login')
def my_drafts(request):
    user_drafts = Futdraft.objects.filter(
        user=request.user
    ).order_by('-date').prefetch_related('players__team', 'lineup')

    for draft in user_drafts:
        player_dict  = {str(p.id): p for p in draft.players.all()}
        ordered_list = (
            [player_dict[str(pid)] for pid in draft.player_order if str(pid) in player_dict]
            if draft.player_order
            else list(draft.players.all())
        )

        draft.js_data = json.dumps([{

            "ID":           p.id,
            "Name":         p.name,
            "Nickname":     p.nickname,
            "Position":     p.position,
            "Image":        p.image,
            "Element":      p.element,
            "Team":         p.team.name if p.team else "",
            "Team_image":   p.team.image if p.team else "",
            "Total":        p.total,
            "Power":        p.power,
            "Control":      p.control,
            "Technique":    p.technique,
            "Physical":     p.physical,
            "Agility":      p.agility,
            "Intelligence": p.intelligence,
            "Pressure":     p.pressure,

            }
            
            for p in ordered_list
        ])

    return render(request, 'myapp/my_drafts.html', {'drafts': user_drafts})


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(
                user=user,
                image=form.cleaned_data.get('image')
            )
            login(request, user)
            return redirect("home")
    else:
        form = UserRegisterForm()
    return render(request, "myapp/register.html", {"register_form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(request.GET.get('next') or 'home')
        messages.error(request, "Datos del formulario inválidos.")
    else:
        form = AuthenticationForm()
    return render(request, "myapp/login.html", {"login_form": form})