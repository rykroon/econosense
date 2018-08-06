from django.shortcuts import render, HttpResponseRedirect, redirect
from django.http import HttpResponse,JsonResponse

from .models import Job, Location, State, Area

import json

from dal import autocomplete

def test(request):
    py_dict = {'k1':'v1','k2':5,'k3':True,'k4':[1,2,3,4,5]}
    py_list = [1,2,3,4,5,6,7,8,9,0]

    qs = Job.jobs.all()

    try:    year = request.GET['year']
    except: year = None

    if year is not None: qs = qs.filter(year=year)

    try:    group = request.GET['group']
    except: group = None

    if group is not None: qs = qs.filter(group=group)

    qs_list = list(qs.values())

    return JsonResponse(qs_list,safe=False)


class JobAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated:
        #     return Job.objects.none()

        qs = Job.jobs.detailed_jobs().order_by('title')

        if self.q:
            qs = qs.filter(title__icontains=self.q)

        return qs


class LocationAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated:
        #     return Job.objects.none()

        qs = Location.locations.all()

        location_type = self.forwarded.get('location_type',None)

        if location_type == 'state':
            qs = State.states.states_and_pr().order_by('name')

            #if there are only 2 characters in the query then check if there is
            # a match on the intiials
            if self.q:
                starts_with = Q(name__istartswith=self.q) | Q(name__icontains=' ' + self.q)
                initials = None

                if len(self.q) == 2:
                    initials = Q(initials__iexact=self.q)

                if initials is None:
                    qs = qs.filter(starts_with)
                else:
                    qs = qs.filter(starts_with | initials)


        elif location_type == 'area':
            qs = Area.areas.default().order_by('name')

            if self.q:
                starts_with = Q(name__istartswith=self.q) | Q(name__icontains='-' + self.q)
                initials = None

                if len(self.q) == 2:
                    initials = Q(name__contains=self.q.upper())

                if initials is None:
                    qs = qs.filter(starts_with)
                else:
                    qs = qs.filter(starts_with | initials)

        return qs


class RentAutocompleteFromList(autocomplete.Select2ListView):

    mappings =  {
        'total':'All',
        'no':'Studio',
        'one':'1 bedroom',
        'two':'2 bedrooms',
        'three':'3 bedrooms',
        'four':'4 bedrooms',
        'five':'5 or more Bedrooms',
    }

    def get_list(self):
        return ['All','Studio','1 bedroom','2 bedroom','3 bedroom','4 bedroom','5 or more bedrooms']
        #return ['total','no','one','two','three','four','five']

    def get_result_label(self, item):
        return item

    def get_selected_result_label(self, item):
        return self.mappings[item]
