from django import forms
from django.db.models import Q, F
from data.models import Job, Location, State, Area

class BestPlacesToWorkForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(BestPlacesToWorkForm, self).__init__(*args, **kwargs)
        #self.custom_bootstrap()


    job_category = forms.ModelChoiceField(
        queryset=Job.jobs.major_jobs().order_by('title'),
        required=False,
        widget=forms.Select(attrs={'class': 'custom-select'})
    )


    job = forms.ModelChoiceField(
        queryset=Job.jobs.detailed_jobs(
            ).annotate(major_id=F('parent__parent__parent')
            ).order_by('title'),
        widget=forms.Select(attrs={'class': 'custom-select'})
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

    def custom_bootstrap(self):
        self.fields['job_category'].widget.attrs['class'] = 'custom-select'
        self.fields['job'].widget.attrs['class'] = 'custom-select'
        self.fields['location_type'].widget.attrs['class'] = 'custom-control-input'
        self.fields['rent'].widget.attrs['class'] = 'custom-select'




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

    area_qs = Area.areas.default().order_by('name')

    state_qs = State.states.states_and_pr()

    #def get_area_qs(self): return self.area_qs
    #def get_state_qs(self): return self.state_qs

    location = forms.ModelChoiceField(
        queryset = Location.locations.
            filter(
                Q(id__in=state_qs) |
                Q(id__in=area_qs)
            ).order_by('name'),
        widget=forms.Select(attrs={'class':'custom-select'})
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
