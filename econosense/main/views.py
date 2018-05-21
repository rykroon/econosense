from django.shortcuts import render
from django.http import HttpResponseRedirect

from audit.models import *
# Create your views here.
def home(request):
    template ='home.html'
    context = {}

    audit = RequestAudit()
    audit.populate_fields(request)
    audit.save()


    return render(request,template,context)


def about(request):
    template ='about.html'
    context = {}

    return render(request,template,context)


def contact(request):
    template ='contact.html'
    context = {}

    return render(request,template,context)
