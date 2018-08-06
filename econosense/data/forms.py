from django import forms
from django.db.models import Q, F
from data.models import Job, Location, State, Area
from dal import autocomplete

class BestPlacesToWorkForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(BestPlacesToWorkForm, self).__init__(*args, **kwargs)
        #self.custom_bootstrap()


    # job_category = forms.ModelChoiceField(
    #     queryset=Job.jobs.major_jobs().order_by('title'),
    #     required=False,
    #     widget=forms.Select(attrs={'class': 'custom-select'})
    # )


    # job = forms.ModelChoiceField(
    #     queryset=Job.jobs.detailed_jobs(
    #         ).annotate(major_id=F('parent__parent__parent')
    #         ).order_by('title'),
    #     widget=forms.Select(attrs={'class': 'custom-select'})
    # )

    job = forms.ModelChoiceField(
        queryset=Job.jobs.detailed_jobs().order_by('title'),
        widget=autocomplete.ModelSelect2(
            url='ajax/job-autocomplete',
            attrs={
                'class':'custom-select',
                #'data-container-css-class':'custom-select',
            }
        )
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

    location = forms.ModelChoiceField(
        queryset = Location.locations.all().order_by('name'),

        widget=autocomplete.ModelSelect2(
            url='ajax/location-autocomplete',
            attrs={
                'class':'custom-select',
                #'data-container-css-class':'custom-select',
            },
            forward=['location_type'])
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

    # rent = autocomplete.Select2ListChoiceField(
    #     #choice_list=get_choice_list,
    #
    #     widget=autocomplete.ListSelect2(
    #         url='rent-autocomplete',
    #         attrs={'data-html':True}
    #     )
    # )


    def __init__(self, *args, **kwargs):
        super(RentToIncomeRatioForm, self).__init__(*args, **kwargs)

        #custom stuff goes here







#
