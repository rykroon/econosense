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


    APARTMENT_CHOICES = (
        ('total','Any'),
        ('no','No bedroom'),
        ('one','1 bedroom'),
        ('two','2 bedrooms'),
        ('three','3 bedrooms'),
        ('four','4 bedrooms'),
        ('five','5 or more bedrooms'),
    )

    apartment = forms.ChoiceField(
        choices=APARTMENT_CHOICES,
        initial='total',
        widget=forms.Select(attrs={'class': 'custom-select'})
    )

    # def clear_classes(self):
    #     self.fields['job_category'].widget.attrs['class'] = ''
    #     self.fields['job'].widget.attrs['class'] = ''
    #     self.fields['location_type'].widget.attrs['class'] = ''
    #     self.fields['apartment'].widget.attrs['class'] = ''

    def custom_bootstrap(self):
        self.fields['job_category'].widget.attrs['class'] = 'custom-select'
        self.fields['job'].widget.attrs['class'] = 'custom-select'
        self.fields['location_type'].widget.attrs['class'] = 'custom-control-input'
        self.fields['apartment'].widget.attrs['class'] = 'custom-select'

    # def bootstrap_material_design(self):
    #     self.fields['job_category'].widget.attrs['class'] = 'form-control'
    #     self.fields['job'].widget.attrs['class'] = 'form-control'
    #     #self.fields['location_type'].widget.attrs['class'] = 'custom-control-input'
    #     self.fields['apartment'].widget.attrs['class'] = 'form-control'
    #
    #
    # def material_design(self):
    #     self.fields['job_category'].widget.attrs['class'] = 'mdl-textfield__input'
    #     self.fields['job'].widget.attrs['class'] = 'mdl-textfield__input'
    #     self.fields['location_type'].widget.attrs['class'] = 'mdl-radio__button'
    #     self.fields['apartment'].widget.attrs['class'] = 'mdl-textfield__input'



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


    APARTMENT_CHOICES = (
        ('total','Any'),
        ('no','No bedroom'),
        ('one','1 bedroom'),
        ('two','2 bedrooms'),
        ('three','3 bedrooms'),
        ('four','4 bedrooms'),
        ('five','5 or more Bedrooms'),
    )

    apartment       = forms.ChoiceField(
        choices=APARTMENT_CHOICES,
        initial='total',
        widget=forms.Select(attrs={'class': 'custom-select'})
    )

    def __init__(self, *args, **kwargs):
        super(RentToIncomeRatioForm, self).__init__(*args, **kwargs)

        #custom stuff goes here







#
