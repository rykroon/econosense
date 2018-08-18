from django import forms
from django.db.models import Q, F
from data.models import Job, Location, State, Area

class BestPlacesToWorkForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(BestPlacesToWorkForm, self).__init__(*args, **kwargs)

    #This is the job autocomplete field
    job = forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control'})
    )

    #this is a hidden field that stores the result of the above autocomplete field
    job_value = forms.ModelChoiceField(
        queryset=Job.jobs.detailed_jobs(),
        widget=forms.TextInput(attrs={'hidden':True})
    )

    LOCATION_TYPE_CHOICES = (
        ('state','State'),
        ('area','Metropolitan Area')
    )

    location_type = forms.ChoiceField(
        choices=LOCATION_TYPE_CHOICES,
        initial='state',
        widget=forms.RadioSelect(attrs={'class': 'custom-control-input'})
    )

    RENT_CHOICES = (
        ('total','All'),
        ('no_bedroom','Studio'),
        ('one_bedroom','1 bedroom'),
        ('two_bedroom','2 bedrooms'),
        ('three_bedroom','3 bedrooms'),
        ('four_bedroom','4 bedrooms'),
        ('five_bedroom','5 or more bedrooms'),
    )

    rent = forms.ChoiceField(
        choices=RENT_CHOICES,
        initial='total',
        widget=forms.Select(attrs={'class': 'custom-select'})
    )

    include_tax = forms.BooleanField(
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={'class':'custom-control-input'})
    )

    FILING_STATUS_CHOICES = (
        ('single','Single'),
        ('married','Married'),
        ('married_separately','Married Separately'),
        ('head_of_household','Head of Household')
    )

    filing_status = forms.ChoiceField(
        choices=FILING_STATUS_CHOICES,
        initial='single',
        required=False,
        widget=forms.Select(attrs={'class':'custom-select disabled','disabled':True})
    )


class RentToIncomeRatioForm(forms.Form):
    LOCATION_TYPE_CHOICES = (
        ('state','State'),
        ('area','Metropolitan Area')
    )

    location_type = forms.ChoiceField(
        choices=LOCATION_TYPE_CHOICES,
        initial='state',
        widget=forms.RadioSelect(attrs={'class':'custom-control-input'})
    )

    location = forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control'})
    )

    #this is a hidden field that stores the result of the above autocomplete field
    location_value = forms.ModelChoiceField(
        queryset=Location.locations.all(),
        widget=forms.TextInput(attrs={'hidden':True})
    )


    RENT_CHOICES = (
        ('total','All'),
        ('no_bedroom','Studio'),
        ('one_bedroom','1 bedroom'),
        ('two_bedroom','2 bedrooms'),
        ('three_bedroom','3 bedrooms'),
        ('four_bedroom','4 bedrooms'),
        ('five_bedroom','5 or more Bedrooms'),
    )

    rent       = forms.ChoiceField(
        choices=RENT_CHOICES,
        initial='total',
        widget=forms.Select(attrs={'class': 'custom-select'})
    )

    include_tax = forms.BooleanField(
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={'class':'custom-control-input'})
    )

    FILING_STATUS_CHOICES = (
        ('single','Single'),
        ('married','Married'),
        ('married_separately','Married Separately'),
        ('head_of_household','Head of Household')
    )

    filing_status = forms.ChoiceField(
        choices=FILING_STATUS_CHOICES,
        initial='single',
        required=False,
        widget=forms.Select(attrs={'class':'custom-select disabled','disabled':True})
    )


    def __init__(self, *args, **kwargs):
        super(RentToIncomeRatioForm, self).__init__(*args, **kwargs)

        #custom stuff goes here







#
