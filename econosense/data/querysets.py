from django.db import models
from django.db.models import Q

from data.models import *

#Can be used for any model that may be considered a "Location"
#Ex: State, County, City,Town, Area
class LocationQuerySet(models.QuerySet):
    def states(self):
        return self.filter(lsad='ST')



    def has_rent(self,apartment_type):
        if apartment_type == 'total':   return self.has_total_rent()
        elif apartment_type == 'one':   return self.has_one_bedroom()
        elif apartment_type == 'two':   return self.has_two_bedroom()
        elif apartment_type == 'three': return self.has_three_bedroom()
        elif apartment_type == 'four':  return self.has_four_bedroom()
        elif apartment_type == 'five':  return self.has_five_bedroom()

    def has_total_rent(self):       return self.filter(rent__total__isnull=False)
    def has_one_bedroom(self):      return self.filter(rent__one_bedroom__isnull=False)
    def has_two_bedroom(self):      return self.filter(rent__two_bedroom__isnull=False)
    def has_three_bedroom(self):    return self.filter(rent__three_bedroom__isnull=False)
    def has_four_bedroom(self):     return self.filter(rent__four_bedroom__isnull=False)
    def has_five_bedroom(self):     return self.filter(rent__five_bedroom__isnull=False)


class StateQuerySet(models.QuerySet):
    def territories(self):      return self.filter(region_id=9)
    def states(self):           return self.filter(region_id__in=[1,2,3,4])
    def states_and_pr(self):    return self.filter(Q(id=72) | Q(region_id__in=[1,2,3,4]))
    def north_east(self):       return self.filter(region_id=1)
    def mid_west(self):         return self.filter(region_id=2)
    def south(self):            return self.filter(region_id=3)
    def west(self):             return self.filter(region_id=4)



class AreaQuerySet(models.QuerySet):
    def default(self):
        return self.ex_new_england_areas().ex_parents().ex_micros()
        #return self.exclude_divisions()

    def ex_parents(self):
        parents =  self.filter(parent__isnull=False).values('parent').distinct()
        return self.exclude(id__in=parents)

    #All New England Areas should exclusively be NECTA's (New England City and Town Areas)
    #Exclude New England Areas that are NOT NECTA's
    def ex_new_england_areas(self):
        ne_areas = self.filter(
            Q(name__contains='CT') | Q(name__contains='MA') |
            Q(name__contains='ME') | Q(name__contains='NH') |
            Q(name__contains='RI') | Q(name__contains='VT')
        ).filter(lsad__in=['M1','M2','M3'])
        return self.exclude(id__in=ne_areas)


    def ex_micros(self):        return self.exclude(lsad__in=['M2','M6'])

    def ex_divisions(self):     return self.exclude(lsad__in=['M3','M7'])
    def divisions(self):        return self.filter(lsad__in=['M3','M7'])

    def metro_areas(self):      return self.filter(lsad='M1')
    def micro_areas(self):      return self.filter(lsad='M2')
    def metro_divisions(self):  return self.filter(lsad='M3')

    def metro_nectas(self):     return self.filter(lsad='M5')
    def micro_nectas(self):     return self.filter(lsad='M6')
    def necta_divisions(self):  return self.filter(lsad='M7')



class JobQueryset(models.QuerySet):
    def major_jobs(self): return self.filter(group='major')
    def minor_jobs(self): return self.filter(group='minor')
    def broad_jobs(self): return self.filter(group='broad')
    def detailed_jobs(self): return self.filter(group='detailed')



# class JobLocationQuerySet(models.QuerySet):
#     #add function that filters out bad median and jobs_1000
#     def has_rent(self,rent_type):
#         if rent_type == 'total':    return self.has_total_rent()
#         elif rent_type == 'no':    return self.has_no_bedroom()
#         elif rent_type == 'one':    return self.has_one_bedroom()
#         elif rent_type == 'two':    return self.has_two_bedroom()
#         elif rent_type == 'three':  return self.has_three_bedroom()
#         elif rent_type == 'four':   return self.has_four_bedroom()
#         elif rent_type == 'five':   return self.has_five_bedroom()
#
#     def has_total_rent(self):
#         return self.filter(location__rent__total__isnull=False)
#
#     def has_no_bedroom(self):
#         return self.filter(location__rent__no_bedroom__isnull=False)
#
#     def has_one_bedroom(self):
#         return self.filter(location__rent__one_bedroom__isnull=False)
#
#     def has_two_bedroom(self):
#         return self.filter(location__rent__two_bedroom__isnull=False)
#
#     def has_three_bedroom(self):
#         return self.filter(location__rent__three_bedroom__isnull=False)
#
#     def has_four_bedroom(self):
#         return self.filter(location__rent__four_bedroom__isnull=False)
#
#     def has_five_bedroom(self):
#         return self.filter(location__rent__five_bedroom__isnull=False)
#
#     def by_state(self,include_puerto_rico=False):
#         if include_puerto_rico:
#             return self.filter(location__in=State.states.states_and_pr())
#
#         else:
#             return self.filter(location__in=State.states.states())
#
#     def by_area(self):  return self.filter(location__in=Area.areas.default())
#
#     def by_location_type(self,location_type,include_puerto_rico=False):
#         if location_type == 'state':    return self.by_state(include_puerto_rico)
#         elif location_type == 'area':   return self.by_area()
#
#     def major_jobs(self):       return self.filter(job__group='major')
#     def minor_jobs(self):       return self.filter(job__group='minor')
#     def broad_jobs(self):       return self.filter(job__group='broad')
#     def detailed_jobs(self):    return self.filter(job__group='detailed')



class RentQuerySet(models.QuerySet):
    def apartment(self,apartment_type):
        if apartment_type == 'total':   return self.total()
        elif apartment_type == 'no':   return self.no_bedroom()
        elif apartment_type == 'one':   return self.one_bedroom()
        elif apartment_type == 'two':   return self.two_bedroom()
        elif apartment_type == 'three': return self.three_bedroom()
        elif apartment_type == 'four':  return self.four_bedroom()
        elif apartment_type == 'five':  return self.five_bedroom()

    def total(self):            return self.filter(total__isnull=False)
    def no_bedroom(self):       return self.filter(no_bedroom__isnull=False)
    def one_bedroom(self):      return self.filter(one_bedroom__isnull=False)
    def two_bedroom(self):      return self.filter(two_bedroom__isnull=False)
    def three_bedroom(self):    return self.filter(three_bedroom__isnull=False)
    def four_bedroom(self):     return self.filter(four_bedroom__isnull=False)
    def five_bedroom(self):     return self.filter(five_bedroom__isnull=False)
