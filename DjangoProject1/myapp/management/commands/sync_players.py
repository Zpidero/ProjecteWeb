import json
import urllib.request
from django.core.management.base import BaseCommand
from myapp.models import Players, Teams

ARCHETYPE_TRANSLATIONS = {
    'Afinidad':    'Bond',
    'Contraataque': 'Counter-attack',
    'Justicia':    'Justice',
    'Juego Sucio': 'Rough Play',
    'Tension':     'Tension',
    'Brecha':      'Breach',
}


class Command(BaseCommand):
    help = 'Sync all players from the Inazuma Eleven API into the database'

    def handle(self, *args, **kwargs):
        url = "https://inazumaeleven-api.onrender.com/all"
        self.stdout.write("Fetching players from API...")

        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())

        all_players = list(data.values()) if isinstance(data, dict) else data
        self.stdout.write(f"Found {len(all_players)} players. Syncing...")

        def safe_int(val, default=0):
            try:
                return int(val) if val else default
            except (ValueError, TypeError):
                return default

        for p in all_players:
            team_name = p.get('Team', 'Unknown')
            team_obj, _ = Teams.objects.get_or_create(
                name=team_name,
                defaults={'image': 'https://placeholder.com/1x1.png'}
            )
            Players.objects.update_or_create(
                id=p.get('ID'),
                defaults={
                    'image':        p.get('Image', ''),
                    'name':         p.get('Name', ''),
                    'nickname':     p.get('Nickname', ''),
                    'game':         p.get('Game', ''),
                    'archetype':    p.get('Archetype', ''),
                    'position':     p.get('Position', ''),
                    'element':      p.get('Element', ''),
                    'power':        safe_int(p.get('Power')),
                    'control':      safe_int(p.get('Control')),
                    'technique':    safe_int(p.get('Technique')),
                    'pressure':     safe_int(p.get('Pressure')),
                    'physical':     safe_int(p.get('Physical')),
                    'agility':      safe_int(p.get('Agility')),
                    'intelligence': safe_int(p.get('Intelligence')),
                    'total':        safe_int(p.get('Total')),
                    'age_group':    p.get('Age group', ''),
                    'school_year':  p.get('School year', ''),
                    'gender':       p.get('Gender', ''),
                    'role':         p.get('Role', ''),
                    'team':         team_obj,
                    'archetype': ARCHETYPE_TRANSLATIONS.get(p.get('Archetype', ''), p.get('Archetype', '')),
                }

                
            )


        self.stdout.write(self.style.SUCCESS(f"Done! {len(all_players)} players synced."))