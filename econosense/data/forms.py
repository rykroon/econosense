from django import forms
from django.db.models import Q, F
from data.models import Job, Location, State, Area
from dal import autocomplete

class BestPlacesToWorkForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(BestPlacesToWorkForm, self).__init__(*args, **kwargs)


    # job = forms.ModelChoiceField(
    #     queryset=Job.jobs.detailed_jobs(
    #         ).annotate(major_id=F('parent__parent__parent')
    #         ).order_by('title'),
    #     widget=forms.Select(attrs={'class': 'custom-select'})
    # )

    # job = forms.ModelChoiceField(
    #     queryset=Job.jobs.detailed_jobs().order_by('title'),
    #     widget=autocomplete.ModelSelect2(
    #         url='/ajax/job-autocomplete',
    #         attrs={
    #             'class':'custom-select',
    #         }
    #     )
    # )

    #This is the job autocomplete field
    job = forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control'})
    )

    #this is a hidden field that stores the result of the above autocomplete field
    job_value = forms.ModelChoiceField(
        queryset=Job.jobs.detailed_jobs(),
        widget=forms.TextInput(attrs={'hidden':True})
    )


    LOCATION_CHOICES = (
        ('state','State'),
        ('area','Metropolitan Area')
    )

    location_type = forms.ChoiceField(
        choices=LOCATION_CHOICES,
        initial='state',
        widget=forms.RadioSelect(attrs={'class': 'custom-control-input'})
    )


    RENT_CHOICES = (
        ('total','All'),
        ('no','Studio'),
        ('one','1 bedroom'),
        ('two','2 bedrooms'),
        ('three','3 bedrooms'),
        ('four','4 bedrooms'),
        ('five','5 or more bedrooms'),
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

    # location = forms.ModelChoiceField(
    #     queryset = Location.locations.all().order_by('name'),
    #
    #     widget=autocomplete.ModelSelect2(
    #         url='/ajax/location-autocomplete',
    #         attrs={
    #             'class':'custom-select',
    #         },
    #         forward=['location_type'])
    # )

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
        ('no','Studio'),
        ('one','1 bedroom'),
        ('two','2 bedrooms'),
        ('three','3 bedrooms'),
        ('four','4 bedrooms'),
        ('five','5 or more Bedrooms'),
    )

    rent       = forms.ChoiceField(
        choices=RENT_CHOICES,
        initial='total',
        widget=forms.Select(attrs={'class': 'custom-select'})
    )


    def __init__(self, *args, **kwargs):
        super(RentToIncomeRatioForm, self).__init__(*args, **kwargs)

        #custom stuff goes here







#
