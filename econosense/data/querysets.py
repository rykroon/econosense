import os
from django.db import models
from django.db.models import Q,F

from data.models import *

#Can be used for any model that may be considered a "Location"
#Ex: State, County, City,Town, Area
class LocationQuerySet(models.QuerySet):

    def year(self):
        try:    year = os.environ['YEAR']
        except: year = None
        return self.filter(year=year)

    def states(self):
        return self.year().filter(lsad='ST')


    def rent_is_not_null(self,apartment_type):
        rent_field = 'rent__{}'.format(apartment_type)
        qs = self.year().annotate(rent_field=F(rent_field))
        return qs.filter(rent_field__isnull=False)


class StateQuerySet(models.QuerySet):

    def year(self):
        try:    year = os.environ['YEAR']
        except: year = None
        return self.filter(year=year)

    def territories(self):
        return self.year().filter(region__geo_id=9)

    def states(self,include_puerto_rico=False):
        states = Q(region__geo_id__in=[1,2,3,4])

        if include_puerto_rico:
            puerto_rico = Q(initials='PR')
            return self.year().filter(states | puerto_rico)

        return self.year().filter(states)


    def north_east(self):   return self.year().filter(region__geo_id=1)
    def mid_west(self):     return self.year().filter(region__geo_id=2)
    def south(self):        return self.year().filter(region__geo_id=3)
    def west(self):         return self.year().filter(region__geo_id=4)



class AreaQuerySet(models.QuerySet):

    def year(self):
        try:    year = os.environ['YEAR']
        except: year = None
        return self.filter(year=year)

    def default(self,include_puerto_rico=False):
        qs = self.year().ex_new_england_areas().ex_parents().ex_micros()

        if not include_puerto_rico:
            qs = qs.exclude(primary_state__initials='PR')

        return qs


    #exclude Metro areas and NECTAs that have divisions
    def ex_parents(self):
        parents =  self.year().filter(parent__isnull=False).values('parent').distinct()
        return self.year().exclude(id__in=parents)

    #All New England Areas should exclusively be NECTA's (New England City and Town Areas)
    #Exclude New England Areas that are NOT NECTA's
    def ex_new_england_areas(self):
        # ne_areas = self.year().filter(
        #     Q(name__contains='CT') | Q(name__contains='MA') |
        #     Q(name__contains='ME') | Q(name__contains='NH') |
        #     Q(name__contains='RI') | Q(name__contains='VT')
        # ).filter(lsad__in=['M1','M2','M3'])

        new_england_areas = self.year(
            ).filter(primary_state__initials__in=['CT','MA','ME','NH','RI','VT']
            ).filter(lsad__in=['M1','M2','M3'])
        return self.year().exclude(id__in=new_england_areas)


    def ex_micros(self):        return self.year().exclude(lsad__in=['M2','M6'])

    def ex_divisions(self):     return self.year().exclude(lsad__in=['M3','M7'])
    def divisions(self):        return self.year().filter(lsad__in=['M3','M7'])

    def metro_areas(self):      return self.year().filter(lsad='M1')
    def micro_areas(self):      return self.year().filter(lsad='M2')
    def metro_divisions(self):  return self.year().filter(lsad='M3')

    def metro_nectas(self):     return self.year().filter(lsad='M5')
    def micro_nectas(self):     return self.year().filter(lsad='M6')
    def necta_divisions(self):  return self.year().filter(lsad='M7')



class JobQuerySet(models.QuerySet):

    def year(self):
        try:    year = os.environ['YEAR']
        except: year = None
        return self.filter(year=year)

    def major_jobs(self):       return self.year().filter(group='major')
    def minor_jobs(self):       return self.year().filter(group='minor')
    def broad_jobs(self):       return self.year().filter(group='broad')
    def detailed_jobs(self):    return self.year().filter(group='detailed')


class JobLocationQuerySet2(models.QuerySet):

    def year(self):
        try:    year = os.environ['YEAR']
        except: year = None
        return self.filter(year=year)

    # add function that filters out bad median and jobs_1000

    #Filters outs locations with null rent
    def rent_is_not_null(self,rent_type):
        rent_field = 'location__rent__{}'.format(rent_type)
        qs = self.year().annotate(rent_field=F(rent_field))
        return qs.filter(rent_field__isnull=False)


    #This function creates a "salary" column
    def annotate_salary(self,salary,filing_status=None):
        if filing_status is not None:
            federal = '{}_gross__{}__federal_tax'.format(salary,filing_status)
            fica    = '{}_gross__{}__fica_tax'.format(salary,filing_status)
            state   = '{}_gross__{}__state_tax'.format(salary,filing_status)

            return self.annotate(salary=F(salary) - F(federal) - F(fica) - F(state))

        return self.annotate(salary=F(salary))


    def by_state(self,include_puerto_rico=False):
        states = Q(location__state__region__geo_id__in=[1,2,3,4])

        if include_puerto_rico:
            puerto_rico = Q(location__geo_id=72)
            return self.year().filter(states | puerto_rico)

        return self.year().filter(states)


    def by_area(self):
        pass
        #return self.filter(location__in=Area.areas.default())

    def by_location_type(self,location_type,include_puerto_rico=False):
        if location_type == 'state':    return self.by_state(include_puerto_rico)
        elif location_type == 'area':   return self.by_area()


    def major_jobs(self):       return self.filter(job__group='major')
    def minor_jobs(self):       return self.filter(job__group='minor')
    def broad_jobs(self):       return self.filter(job__group='broad')
    def detailed_jobs(self):    return self.filter(job__group='detailed')



class RentQuerySet(models.QuerySet):

    def year(self):
        try:    year = os.environ['YEAR']
        except: year = None
        return self.filter(year=year)

    def rent_is_not_null(self,apartment_type):
        qs = self.year().annotate(rent_field=F(apartment_type))
        return qs.filter(rent_field__isnull=False)
