from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Teams(models.Model):
    image = models.URLField()
    name = models.CharField(max_length=200)

class Lineup(models.Model):
    name = models.CharField(max_length=20)
    image = models.URLField()
    forwards = models.IntegerField()
    midfielders = models.IntegerField()
    defenders = models.IntegerField()
    goalKeeper = models.IntegerField(default=1)

class Players(models.Model):
    image = models.URLField()
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
    intelligence = models.IntegerField(default=0)
    total = models.IntegerField()
    age_Group = models.CharField(max_length=200)
    school_Year = models.CharField(max_length=200)
    gender = models.CharField(max_length=200)
    role = models.CharField(max_length=200)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

class Futdraft(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    players = models.ManyToManyField(Players, related_name= "draft_players")
    lineup = models.ForeignKey(Lineup, on_delete=models.CASCADE)
