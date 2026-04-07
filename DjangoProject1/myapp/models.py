from django.db import models

# Create your models here.

class Teams(models.Model):
    image = models.CharField()
    name = models.CharField(max_length=200)

class Lineup(models.Model):
    name = models.CharField(max_length=200)
    imatge = models.CharField()
    forwards = models.IntegerField()
    midfielders = models.IntegerField()
    defenders = models.IntegerField()
    goalKeeper = models.IntegerField()

class Players(models.Model):
    image = models.CharField()
    name = models.CharField(max_length=200)
    nickname = models.CharField(max_length=200)
    game = models.CharField(max_length=200)
    archetype = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    element = models.CharField(max_length=200)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    power = models.IntegerField()
    control = models.IntegerField()
    technique = models.IntegerField()
    physical = models.IntegerField()
    agility = models.IntegerField()
    age_Group = models.CharField(max_length=200)
    school_Year = models.IntegerField()
    gender = models.IntegerField()
    #role = models.IntegerField()

class AppUser(models.Model):
    name = models.CharField(max_length=200)
    mail = models.CharField(max_length=200)
    creation_date = models.CharField(max_length=200)\

class Futdraft(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    date = models.CharField(max_length=200)

    players = models.ManyToManyField(Players, related_name= "draft_players")
    lineup = models.ForeignKey(Lineup, on_delete=models.CASCADE)
