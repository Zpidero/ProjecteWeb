from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

def index(request):
    return render (request, "base.html")
def base(request):
    return render(request, "base.html")