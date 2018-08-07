from django.shortcuts import render, HttpResponseRedirect, redirect
from django.http import HttpResponse,JsonResponse
from django.db.models import F,Q
from django.views import View

from .models import Job, Location, State, Area

import json

from dal import autocomplete

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






def jobs(request):
    try:
        term = request.GET['term']
    except:
        return HttpResponse(status=400)

    qs = Job.jobs.detailed_jobs().order_by('title')

    print(request.is_ajax())

    qs = qs.filter(title__icontains=term)
    qs = qs[:10]

    return HttpResponse(qs_to_json('title','id',qs))


def locations(request):
    try:
        term            = request.GET['term']
        location_type   = request.GET['location_type']
    except:
        return HttpResponse(status=400)

    if location_type == 'state':
        qs = State.states.states_and_pr()

    elif location_type == 'area':
        qs = Area.areas.default()

    qs = qs.filter(name__icontains=term)
    qs = qs.order_by('name')
    qs = qs[:10]

    return HttpResponse(qs_to_json('name','id',qs))


def qs_to_json(label,value,qs):
    qs = qs.annotate(label=F(label),value=F(value))
    result = list(qs.values('label','value'))
    return json.dumps(result)


# class JobAutocomplete(autocomplete.Select2QuerySetView):
#
#     def get_queryset(self):
#         # Don't forget to filter out results depending on the visitor !
#         # if not self.request.user.is_authenticated:
#         #     return Job.objects.none()
#
#         qs = Job.jobs.detailed_jobs().order_by('title')
#
#         if self.q:
#             qs = qs.filter(title__icontains=self.q)
#
#         return qs


# class LocationAutocomplete(autocomplete.Select2QuerySetView):
#
#     def get_queryset(self):
#         # Don't forget to filter out results depending on the visitor !
#         # if not self.request.user.is_authenticated:
#         #     return Job.objects.none()
#
#         qs = Location.locations.all()
#
#         location_type = self.forwarded.get('location_type',None)
#
#         if location_type == 'state':
#             qs = State.states.states_and_pr().order_by('name')
#
#             #if there are only 2 characters in the query then check if there is
#             # a match on the intiials
#             if self.q:
#                 starts_with = Q(name__istartswith=self.q) | Q(name__icontains=' ' + self.q)
#                 initials = None
#
#                 if len(self.q) == 2:
#                     initials = Q(initials__iexact=self.q)
#
#                 if initials is None:
#                     qs = qs.filter(starts_with)
#                 else:
#                     qs = qs.filter(starts_with | initials)
#
#
#         elif location_type == 'area':
#             qs = Area.areas.default().order_by('name')
#
#             if self.q:
#                 starts_with = Q(name__istartswith=self.q) | Q(name__icontains='-' + self.q)
#                 initials = None
#
#                 if len(self.q) == 2:
#                     initials = Q(name__contains=self.q.upper())
#
#                 if initials is None:
#                     qs = qs.filter(starts_with)
#                 else:
#                     qs = qs.filter(starts_with | initials)
#
#         return qs
#
#
# class RentAutocompleteFromList(autocomplete.Select2ListView):
#
#     mappings =  {
#         'total':'All',
#         'no':'Studio',
#         'one':'1 bedroom',
#         'two':'2 bedrooms',
#         'three':'3 bedrooms',
#         'four':'4 bedrooms',
#         'five':'5 or more Bedrooms',
#     }
#
#     def get_list(self):
#         return ['All','Studio','1 bedroom','2 bedroom','3 bedroom','4 bedroom','5 or more bedrooms']
#         #return ['total','no','one','two','three','four','five']
#
#     def get_result_label(self, item):
#         return item
#
#     def get_selected_result_label(self, item):
#         return self.mappings[item]
