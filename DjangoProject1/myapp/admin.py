from django.contrib import admin
from .models import Teams, Players, Lineup, Profile, Futdraft

admin.site.register(Teams)
admin.site.register(Players)
admin.site.register(Lineup)
admin.site.register(Profile)
admin.site.register(Futdraft)