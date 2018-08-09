from django.shortcuts import render, HttpResponseRedirect, redirect
from django.http import HttpResponse,JsonResponse
from django.db.models import F,Q
from django.views import View

from .forms import BestPlacesToWorkForm, RentToIncomeRatioForm
from .models import Job, Location, State, Area

import json


class DataTable(View):
    def process_form(self):
        pass


class BestPlacesToWorkAjax(View):

    def get(self,request):
        form = BestPlacesToWorkForm(request.GET or None)

        if form.is_valid():
            self.process_form()
        else:
            return HttpResponse(status=400)

    def process_form(self,form):
        job             = form.cleaned_data['job_value']
        location_type   = form.cleaned_data['location_type']
        apartment       = form.cleaned_data['rent']
        include_tax     = form.cleaned_data['include_tax']
        include_tax     = include_tax and location_type == 'state'
        filing_status   = form.cleaned_data['filing_status']

        qs = JobLocation.job_locations()







class JQueryAutocomplete(View):

    def get(self,request):
        self.label  = None
        self.value  = None
        self.limit  = None
        self.term   = request.GET.get("term","")
        self.forwarded    = request.GET

        qs      = self.get_queryset()
        if qs is None:
            return HttpResponse(status=400)

        if self.limit is not None:
            qs = qs[:self.limit]

        result  = self.qs_to_json(qs)

        return HttpResponse(result)


    def get_queryset(self):
        pass


    def qs_to_json(self,qs):
        qs      = qs.annotate(label=F(self.label),value=F(self.value))
        result  = list(qs.values('label','value'))
        return json.dumps(result)


class JobAutocomplete(JQueryAutocomplete):

    def get_queryset(self):
        self.label = 'title'
        self.value = 'id'
        self.limit = 25

        print('job autocomplete')
        qs = Job.jobs.detailed_jobs().order_by('title')
        if self.term is not None:
            print(self.term)
            qs = qs.filter(title__icontains=self.term)

        return qs


class LocationAutocomplete(JQueryAutocomplete):

    def get_queryset(self):
        self.label = 'name'
        self.value = 'id'

        location_type = self.forwarded.get('location_type',None)

        if location_type == 'state':
            return self.get_state_qs()
        elif location_type == 'area':
            return self.get_area_qs()
        else:
            return None


    def get_state_qs(self):
        self.limit = 10
        qs = State.states.states_and_pr().order_by('name')

        starts_with = Q(name__istartswith=self.term) | Q(name__icontains=' ' + self.term)
        initials    = None

        if len(self.term) == 2:
            initials = Q(initials__iexact=self.term)

        if initials is None:
            qs = qs.filter(starts_with)
        else:
            qs = qs.filter(starts_with | initials)

        return qs


    def get_area_qs(self):
        self.limit = 25
        qs = Area.areas.default().order_by('name')

        starts_with = Q(name__istartswith=self.term) | Q(name__icontains='-' + self.term)
        initials = None

        if len(self.term) == 2:
            initials = Q(name__contains=self.term.upper())

        if initials is None:
            qs = qs.filter(starts_with)
        else:
            qs = qs.filter(starts_with | initials)

        return qs
