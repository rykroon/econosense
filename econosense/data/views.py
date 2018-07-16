from django.shortcuts import render, HttpResponseRedirect, redirect
from django.views import View
from django.views.generic.edit import FormView
from django.db.models import Q
#from django.db.models import F,FloatField,DecimalField,ExpressionWrapper

from audit.models import *
from .forms import BestPlacesToWorkForm, RentToIncomeRatioForm
from .models import JobLocation, Job, Location, State, Area

import pandas as pd
from django_pandas.io import read_frame

from dal import autocomplete


# Create your views here.
class BestPlacesToWorkView(FormView):

    http_method_names = ['get']
    template_name = 'best_places_to_work.html'
    success_url = '/best-places-to-work/'



    def get(self, request, *args, **kwargs):
        audit = RequestAudit()
        audit.populate_fields(request)
        audit.save()

        form = BestPlacesToWorkForm(request.GET or None)
        context = dict()
        context['form'] = form

        if form.is_valid():
            context['table'] = self.calculate_best_place_to_work(form)

        return self.render_to_response(context)


    def calculate_best_place_to_work(self,form):
        job = form.cleaned_data['job']
        location_type = form.cleaned_data['location_type']
        apartment = form.cleaned_data['rent']

        for choice in form.fields['location_type'].choices:
            if choice[0] == location_type: location_name = choice[1]

        #
        ## Filter Data
        #

        qs = JobLocation.job_locations.filter(
            job=job).by_location_type(
            location_type,include_puerto_rico=True).has_rent(
            apartment).filter(
            median__gte=0).filter(
            jobs_1000__gte=0)

        #
        ## Convert Queryset into a Dataframe
        #

        rent_col_name = 'location__rent__' + apartment
        if apartment != 'total': rent_col_name += '_bedroom'

        field_names = ['jobs_1000','median','location__name',rent_col_name]
        if location_type == 'state':
            field_names.append('location__state__initials')


        df = read_frame(
            qs,
            fieldnames=field_names,
            verbose=True,
            coerce_float=True)

        #Calculate Net income
        # tax = TaxApi()
        # def apply_net(row):
        #     gross = row['median']
        #     state = row['location__state__initials']
        #     return tax.get_net_income(2016,gross,'single',state)
        #
        # if location_type == 'state' and False:
        #     df['median'] = df.apply(apply_net,axis=1)


        #Calculate score
        df['score'] = 100 * (
            (.25 * self.normalize(df['median'])) +
            (.5 * self.normalize(df['jobs_1000'])) +
            (.25 * (1 - self.normalize(df[rent_col_name]))))

        # df['score'] = ((.5 * df['jobs_1000']) * (.25 * (df['median'] / df[rent_col_name])))
        # df['score'] = self.normalize(df['score']) * 100


        #Sort by Score and add indexes
        df = df.sort_values(by='score',ascending=False)
        df.index = pd.Series(range(1,len(df) + 1))
        df['rank'] = df.index

        #Re-order columns
        df = df[['rank','location__name','jobs_1000','median',rent_col_name,'score']]

        #Rename columns
        df = df.rename(
            columns={
                'rank'              : 'Rank',
                'median'            : 'Salary',
                rent_col_name       : 'Rent',
                'jobs_1000'         : 'Employment per 1000 jobs',
                'location__name'    : location_name,
                'score'             : 'Score'
            }
        )

        #tool tooltips
        tool_tips = {
            'Rank'                      :   "Rank",
            'Salary'                    :   'Median annual salary',
            'Rent'                      :   'Median gross monthly rent',
            'Employment per 1000 jobs'  :   'The number of jobs in the given occupation per 1,000 jobs in the given area.',
            location_name               :   location_name,
            'Score'                     :   'Employment per 1000 jobs is 50%, Salary is 25%, and Rent is 25%'
        }

        #align text right for numeric data types and align text left for text
        table_header = list()

        for col in df.columns:
            if df[col].dtype in [int,float]:
                table_header.append([col,'text-right',tool_tips[col]])
            else:
                table_header.append([col,'text-left',tool_tips[col]])


        #Format output
        df['Salary']    = df['Salary'].map('${:,.0f}'.format)
        df['Rent']      = df['Rent'].map('${:,.0f}'.format)
        df['Score']     = df['Score'].map('{:,.2f}'.format)

        table = {
            'title'     :   'Best Places to Work',
            'header'    :   table_header,
            'data'      :   df
        }

        return table


    def normalize(self,series):
        return (series - series.min()) / (series.max() - series.min())



class RentToIncomeRatioView(FormView):
    http_method_names = ['get']
    template_name = 'rent_to_income_ratio.html'
    success_url = '/rent-to-income-ratio/'

    def get(self, request, *args, **kwargs):
        audit = RequestAudit()
        audit.populate_fields(request)
        audit.save()

        form = RentToIncomeRatioForm(request.GET or None)
        context = dict()
        context['form'] = form

        if form.is_valid():
            result = self.calculate_rent_to_income_ratio(form)
            context['table_one'] = result['good_jobs']
            #context['table_two'] = result['bad_jobs']

        return self.render_to_response(context)



    def calculate_rent_to_income_ratio(self,form):
        location_type = form.cleaned_data['location_type']
        location = form.cleaned_data['location']
        apartment = form.cleaned_data['rent']

        rent_column_name = 'location__rent__' + apartment
        if apartment != 'total':
            rent_column_name = 'location__rent__' + apartment + '_bedroom'


        qs = JobLocation.job_locations.filter(
            location=location).filter(
            median__gte=0).filter(
            jobs_1000__gte=0).has_rent(
            apartment).detailed_jobs()#.annotate(ratio=ExpressionWrapper(F(rent_column_name) * 12 / F('median') * 100, output_field=FloatField())).order_by('ratio')


        field_names = ['job__title',rent_column_name,'median']
        #field_names = ['job__title',rent_column_name,'median','ratio']
        if location_type == 'state':
            field_names.append('location__state__initials')


        df = read_frame(
            qs,
            fieldnames = field_names,
            verbose=False,
            coerce_float=True)

        #Calculate Net income
        # tax = TaxApi()
        # def apply_net(row):
        #     gross = row['median']
        #     state = row['location__state__initials']
        #     return tax.get_net_income(2016,gross,'single',state)
        #
        # if location_type == 'state' and False:
        #     df['median'] = df.apply(apply_net,axis=1)



        df['ratio'] = (df[rent_column_name] * 12) / df['median'] * 100

        #bad_jobs = df[df['ratio'] > 30]
        #good_jobs = df[df['ratio'] <= 30]
        good_jobs = df

        #bad_jobs = bad_jobs.sort_values(by='ratio',ascending=False)
        good_jobs = good_jobs.sort_values(by='ratio',ascending=True)



        def format_df(df,title):
            df.index = pd.Series(range(1,len(df) + 1))
            df['rank'] = df.index

            df = df[['rank','job__title',rent_column_name,'median','ratio']]

            new_column_names = {
                'rank'              :   'Rank',
                'job__title'        :   'Job',
                rent_column_name    :   'Rent',
                'median'            :   'Salary',
                'ratio'             :   'Ratio'
            }

            df = df.rename(columns=new_column_names)

            #align text right for numeric data types and align text left for text
            table_header = list()

            tool_tips = {
                'Rank'      :   'Rank',
                'Job'       :   'Job title',
                'Rent'      :   'Median gross monthly rent',
                'Salary'    :   'Median annual salary',
                'Ratio'     :   'The monthly rent x 12 / annual salary'
            }

            for col in df.columns:
                if df[col].dtype in [int,float]:
                    table_header.append([col,'text-right',tool_tips[col]])
                else:
                    table_header.append([col,'text-left',tool_tips[col]])

            df['Ratio']      = df['Ratio'].map('{:,.2f}'.format)
            df['Rent']      = df['Rent'].map('${:,.2f}'.format)
            df['Salary']    = df['Salary'].map('${:,.2f}'.format)

            return {'title':title,'header':table_header,'data':df}



        bad_jobs = None#format_df(bad_jobs,"Jobs that can't afford rent")
        good_jobs = format_df(good_jobs,"Jobs that can afford rent")

        return {'good_jobs':good_jobs,'bad_jobs':bad_jobs}


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
