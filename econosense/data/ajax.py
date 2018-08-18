from django.shortcuts import render, HttpResponseRedirect, redirect
from django.http import HttpResponse,JsonResponse
from django.db.models import F,Q
from django.views import View

from .forms import BestPlacesToWorkForm, RentToIncomeRatioForm
from .models import Job, Location, State, Area, JobLocation

import pandas as pd
from django_pandas.io import read_frame

import json


class DataTable(View):
    def process_form(self):
        pass


class BestPlacesToWorkAjax(View):

    def get(self,request):
        form = BestPlacesToWorkForm(request.GET or None)

        if form.is_valid():
            return HttpResponse(self.process_form(form))
        else:
            return HttpResponse(status=400)

    def process_form(self,form):
        job             = form.cleaned_data['job_value']
        location_type   = form.cleaned_data['location_type']
        rent            = form.cleaned_data['rent']
        include_tax     = form.cleaned_data['include_tax']
        filing_status   = form.cleaned_data['filing_status']

        if not include_tax:
            filing_status = None

        if location_type == 'state':
            location_qs = State.states.states(include_puerto_rico=not include_tax)

        elif location_type == 'area':
            location_qs = Area.areas.default(include_puerto_rico=not include_tax)


        qs = JobLocation.job_locations.filter(job=job
            ).filter(location__in=location_qs
            ).filter(median__gte=0
            ).filter(jobs_1000__gte=0
            ).annotate_salary('median',filing_status
            ).annotate_rent(rent)

        field_names = ['jobs_1000','salary','location','rent']

        df = read_frame(qs,fieldnames=field_names,verbose=True,coerce_float=True)

        df['score'] = 100 * (
            (.3 * self.normalize(df['salary'])) +
            (.4 * self.normalize(df['jobs_1000'])) +
            (.3 * (1 - self.normalize(df['rent']))))

        df = df.sort_values(by='score',ascending=False)
        df.index = pd.Series(range(1,len(df) + 1))
        df['rank'] = df.index

        df = df[['rank','location','jobs_1000','salary','rent','score']]

        df['salary']    = df['salary'].map('${:,.0f}'.format)
        df['rent']      = df['rent'].map('${:,.0f}'.format)
        df['score']     = df['score'].map('{:,.2f}'.format)

        result = json.dumps(df.to_dict(orient='record'))
        return result


    def normalize(self,series):
        return (series - series.min()) / (series.max() - series.min())


class RentToIncomeRatioAjax(View):

    def get(self,request):
        form = RentToIncomeRatioForm(request.GET or None)

        if form.is_valid():
            return HttpResponse(self.process_form(form))
        else:
            return HttpResponse(status=400)


    def process_form(self,form):
        location_type   = form.cleaned_data['location_type']
        location        = form.cleaned_data['location_value']
        rent            = form.cleaned_data['rent']
        include_tax     = form.cleaned_data['include_tax']
        filing_status   = form.cleaned_data['filing_status']

        if not include_tax:
            filing_status = None

        qs = JobLocation.job_locations.filter(location=location
            ).filter(median__gte=0
            ).filter(jobs_1000__gte=0
            ).annotate_salary('median',filing_status
            ).annotate_rent(rent
            ).detailed_jobs()

        field_names = ['job','rent','salary']

        df = read_frame(qs,fieldnames = field_names,verbose=True,coerce_float=True)

        df['ratio'] = (df['rent'] * 12) / df['salary'] * 100

        df = df.sort_values(by='ratio',ascending=True)

        df.index = pd.Series(range(1,len(df) + 1))
        df['rank'] = df.index

        df = df[['rank','job','rent','salary','ratio']]

        df['ratio']     = df['ratio'].map('{:,.2f}'.format)
        df['rent']      = df['rent'].map('${:,.2f}'.format)
        df['salary']    = df['salary'].map('${:,.2f}'.format)

        result = json.dumps(df.to_dict(orient='record'))
        return result







class JQueryAutocomplete(View):

    def get(self,request):
        self.label  = None
        self.value  = None
        self.limit  = None
        self.term   = request.GET.get("term","")
        self.forwarded    = request.GET

        qs = self.get_queryset()
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

        qs = Job.jobs.detailed_jobs().order_by('title')
        if self.term is not None:
            starts_with  = Q(title__istartswith=self.term)
            contains    = Q(title__icontains=' ' + self.term)
            qs = qs.filter(starts_with | contains)

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
        qs = State.states.states(include_puerto_rico=True).order_by('name')

        starts_with = Q(name__istartswith=self.term) | Q(name__icontains=' ' + self.term)
        initials    = None

        if len(self.term) == 2:
            initials = Q(initials__iexact=self.term)
            qs = qs.filter(starts_with | initials)

        else:
            qs = qs.filter(starts_with)

        return qs


    def get_area_qs(self):
        self.limit = 25
        qs = Area.areas.default(include_puerto_rico=True).order_by('name')

        starts_with = Q(name__istartswith=self.term) | Q(name__icontains='-' + self.term)
        initials = None

        if len(self.term) == 2:
            initials = Q(name__contains=self.term.upper())

        if initials is None:
            qs = qs.filter(starts_with)
        else:
            qs = qs.filter(starts_with | initials)

        return qs
