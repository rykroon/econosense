from django.db import models
#from django.db.models import Q

#from django_pandas.managers import DataFrameManager

from data.querysets import *

# Create your models here.

class Location(models.Model):
    #id          = models.BigIntegerField(primary_key=True)
    geo_id      = models.IntegerField()
    year        = models.IntegerField()
    name        = models.CharField(max_length=100)
    lsad_name   = models.CharField(max_length=100)
    lsad        = models.CharField(max_length=2) #Legal Statistical Area Description
    Longitude   = models.FloatField(null=True)
    Latitude    = models.FloatField(null=True)

    objects = models.Manager()
    locations = LocationQuerySet.as_manager()

    class Meta:
        db_table = 'location'
        unique_together = ('geo_id','year')

    def __str__(self):
        return self.lsad_name

#!! potentially change Region and Division so that they inherit from Location
class Region(models.Model):
    #id      = models.IntegerField(primary_key=True)
    geo_id  = models.IntegerField()
    name    = models.TextField()
    year    = models.IntegerField()

    class Meta:
        db_table = 'region'
        unique_together = ('geo_id','year')

    def __str__(self):
        return self.name


class Division(models.Model):
    #id      = models.IntegerField(primary_key=True)
    geo_id  = models.IntegerField()
    name    = models.TextField()
    year    = models.IntegerField()
    region  = models.ForeignKey('Region',on_delete=models.CASCADE,null=False)

    class Meta:
        db_table = 'division'
        unique_together = ('geo_id','year')

    def __str__(self):
        return self.name


class State(Location):
    initials    = models.CharField(max_length=2)
    region      = models.ForeignKey('Region',on_delete=models.CASCADE,null=False)
    division    = models.ForeignKey('Division',on_delete=models.CASCADE,null=False)

    objects = models.Manager()
    states = StateQuerySet.as_manager()
    locations = LocationQuerySet.as_manager()

    class Meta:
        db_table = 'state'

    def __str__(self):
        return self.name


class CombinedArea(Location):

    objects = models.Manager()
    locations = LocationQuerySet.as_manager()

    class Meta:
        db_table = 'combined_area'

    def __Str__(self):
        return self.name



class Area(Location):
    parent          = models.ForeignKey("self",on_delete=models.CASCADE,null=True)
    combined_area   = models.ForeignKey("CombinedArea",on_delete=models.CASCADE,null=True)

    objects = models.Manager()
    areas = AreaQuerySet.as_manager()
    locations = LocationQuerySet.as_manager()

    class Meta:
        db_table = 'area'

    def __str__(self):
        return self.name



class Job(models.Model):
    code    = models.IntegerField()
    year        = models.IntegerField()
    title       = models.TextField()
    group       = models.TextField()
    parent      = models.ForeignKey("self",on_delete=models.CASCADE,null=True)

    objects = models.Manager()
    jobs = JobQueryset.as_manager()

    class Meta:
        db_table = 'job'
        unique_together = ('code','year')

    def __str__(self):
        return self.title


class JobLocationQuerySet(models.QuerySet):

    #add function that filters out bad median and jobs_1000
    def has_rent(self,rent_type):
        if rent_type == 'total':    return self.has_total_rent()
        elif rent_type == 'no':    return self.has_no_bedroom()
        elif rent_type == 'one':    return self.has_one_bedroom()
        elif rent_type == 'two':    return self.has_two_bedroom()
        elif rent_type == 'three':  return self.has_three_bedroom()
        elif rent_type == 'four':   return self.has_four_bedroom()
        elif rent_type == 'five':   return self.has_five_bedroom()

    def has_total_rent(self):
        return self.filter(location__rent__total__isnull=False)

    def has_no_bedroom(self):
        return self.filter(location__rent__no_bedroom__isnull=False)

    def has_one_bedroom(self):
        return self.filter(location__rent__one_bedroom__isnull=False)

    def has_two_bedroom(self):
        return self.filter(location__rent__two_bedroom__isnull=False)

    def has_three_bedroom(self):
        return self.filter(location__rent__three_bedroom__isnull=False)

    def has_four_bedroom(self):
        return self.filter(location__rent__four_bedroom__isnull=False)

    def has_five_bedroom(self):
        return self.filter(location__rent__five_bedroom__isnull=False)

    def by_state(self,include_puerto_rico=False):
        if include_puerto_rico:
            return self.filter(location__in=State.states.states_and_pr())

        else:
            return self.filter(location__in=State.states.states())

    def by_area(self):  return self.filter(location__in=Area.areas.default())

    def by_location_type(self,location_type,include_puerto_rico=False):
        if location_type == 'state':    return self.by_state(include_puerto_rico)
        elif location_type == 'area':   return self.by_area()

    def major_jobs(self):       return self.filter(job__group='major')
    def minor_jobs(self):       return self.filter(job__group='minor')
    def broad_jobs(self):       return self.filter(job__group='broad')
    def detailed_jobs(self):    return self.filter(job__group='detailed')



class JobLocation(models.Model):
    job         = models.ForeignKey('Job',on_delete=models.CASCADE,null=False)
    location    = models.ForeignKey('Location',on_delete=models.CASCADE,null=False)
    year        = models.IntegerField()
    employed    = models.IntegerField()
    jobs_1000   = models.FloatField()
    average     = models.DecimalField(max_digits=8, decimal_places=2)
    pct_10      = models.DecimalField(max_digits=8, decimal_places=2)
    pct_25      = models.DecimalField(max_digits=8, decimal_places=2)
    median      = models.DecimalField(max_digits=8, decimal_places=2)
    pct_75      = models.DecimalField(max_digits=8, decimal_places=2)
    pct_90      = models.DecimalField(max_digits=8, decimal_places=2)

    objects = models.Manager()
    job_locations = JobLocationQuerySet.as_manager()

    class Meta:
        unique_together = ('job','location','year')
        db_table = 'job_location'

    def __str__(self):
        return str(self.location) + ' - ' + str(self.job)


class Rent(models.Model):
    location        = models.OneToOneField('Location',on_delete=models.CASCADE)
    year            = models.IntegerField()
    total           = models.IntegerField(null=True)
    no_bedroom      = models.IntegerField(null=True)
    one_bedroom     = models.IntegerField(null=True)
    two_bedroom     = models.IntegerField(null=True)
    three_bedroom   = models.IntegerField(null=True)
    four_bedroom    = models.IntegerField(null=True)
    five_bedroom    = models.IntegerField(null=True)

    objects = models.Manager()
    apartments = RentQuerySet.as_manager()

    class Meta:
        db_table = 'rent'
        unique_together = ('location','year')

    def __str__(self):
        return self.location.lsad_name + ' Rent'


# class Income(models.Model):
#     #id              = models.IntegerField(primary_key=True)
#     year            = models.IntegerField()
#     gross           = models.DecimalField(max_digits=8, decimal_places=2)
#
#     FILING_STATUS_CHOICES = (
#         ('single','Single'),
#         ('married','Married'),
#         ('married_separately','Married seperately'),
#         ('head_of_household','Head of household')
#     )
#
#     filing_status   = models.CharField(max_length=20,choices=FILING_STATUS_CHOICES)
#
#     state           = models.ForeignKey('State',on_delete=models.CASCADE,null=False)
#     fica            = models.DecimalField(max_digits=8, decimal_places=2)
#     federal_tax     = models.DecimalField(max_digits=8, decimal_places=2)
#     state_tax       = models.DecimalField(max_digits=8, decimal_places=2)
#     net             = models.DecimalField(max_digits=8, decimal_places=2)
#
#
#     class Meta:
#         unique_together = ('year','filing_status','gross','state')
#         db_table = 'income'
#
#     def __str__(self):
#         return 'Filing as ' + self.filing_status + ' in ' + self.state.name + ' for the ' + str(self.year) + ' Tax year.'
#
#
# class Gross(models.Model):
#     amount              = models.DecimalField(max_digits=8,decimal_places=2)
#     state               = models.ForeignKey('State',on_delete=models.CASCADE,null=False)
#     year                = models.IntegerField()
#
#     single              = models.ForeignKey('Tax',on_delete=models.CASCADE,related_name='single',null=True)
#     married             = models.ForeignKey('Tax',on_delete=models.CASCADE,related_name='married',null=True)
#     married_separately  = models.ForeignKey('Tax',on_delete=models.CASCADE,related_name='married_separately',null=True)
#     head_of_household   = models.ForeignKey('Tax',on_delete=models.CASCADE,related_name='head_of_household',null=True)
#
#     class Meta:
#         unique_together = ('year','amount','state')
#         db_table = 'gross'
#
#     def __str__(self):
#         pass
#
#
#
# class Tax(models.Model):
#     state       = models.ForeignKey('State',on_delete=models.CASCADE,null=False)
#     year        = models.IntegerField()
#
#     fica_tax    = models.DecimalField(max_digits=8, decimal_places=2)
#     federal_tax = models.DecimalField(max_digits=8, decimal_places=2)
#     state_tax   = models.DecimalField(max_digits=8, decimal_places=2)
#
#     FILING_STATUS_CHOICES = (
#         ('single','Single'),
#         ('married','Married'),
#         ('married_separately','Married seperately'),
#         ('head_of_household','Head of household')
#     )
#
#     filing_status   = models.CharField(max_length=20,choices=FILING_STATUS_CHOICES)
#
#     class Meta:
#         unique_together = ('year','state','filing_status')
#         db_table = 'tax'
