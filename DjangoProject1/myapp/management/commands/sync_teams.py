import json
import urllib.request
import urllib.parse
from django.core.management.base import BaseCommand
from myapp.models import Teams


class Command(BaseCommand):
    help = 'Sync all teams from the Inazuma Eleven API into the database'

    def handle(self, *args, **kwargs):
        url = "https://inazumaeleven-api.onrender.com/teams"
        self.stdout.write("Fetching team list...")

        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                team_names = data if isinstance(data, list) else data.get("", [])
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching team list: {e}"))
            return

        self.stdout.write(f"Found {len(team_names)} teams. Syncing...")
        ok, errors = 0, 0

        for name in team_names:
            safe_name = urllib.parse.quote(name)
            detail_url = f"https://inazumaeleven-api.onrender.com/teams/{safe_name}"
            try:
                with urllib.request.urlopen(detail_url) as resp:
                    detail = json.loads(resp.read().decode())
                image = detail.get("Image") or "https://placeholder.com/1x1.png"
                Teams.objects.update_or_create(
                    name=name,
                    defaults={"image": image}
                )
                ok += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  Skipped '{name}': {e}"))
                errors += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done! {ok} teams synced, {errors} skipped."
        ))