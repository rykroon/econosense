from django.shortcuts import render
from django.http import HttpResponseRedirect

# Create your views here.
def home(request):
    template ='home.html'
    context = {}

    return render(request,template,context)


def about(request):
    template ='about.html'
    context = {}

    return render(request,template,context)


def contact(request):
    template ='contact.html'
    context = {}

    return render(request,template,context)
