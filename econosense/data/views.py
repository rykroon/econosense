from django.shortcuts import render, HttpResponseRedirect, redirect
from django.views import View
from django.views.generic.edit import FormView

from audit.models import *
from .forms import BestPlacesToWorkForm, RentToIncomeRatioForm
from .models import JobLocation, Job, Location, State, Area

import pandas as pd
from django_pandas.io import read_frame

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
        job             = form.cleaned_data['job_value']
        location_type   = form.cleaned_data['location_type']
        rent            = form.cleaned_data['rent']
        include_tax     = form.cleaned_data['include_tax']
        filing_status   = form.cleaned_data['filing_status']


        if not include_tax:
            filing_status=None

        #
        ## Filter Data
        #

        if location_type == 'state':
            location_qs = State.states.states(include_puerto_rico=not include_tax)

        elif location_type == 'area':
            location_qs = Area.areas.default(include_puerto_rico=not include_tax)


        qs = JobLocation.job_locations.filter(job=job
            ).filter(location__in=location_qs
            ).filter(median__gte=0
            ).filter(jobs_1000__gte=0
            ).annotate_salary('median',filing_status
            ).annotate_rent(rent)

        #
        ## Convert Queryset into a Dataframe
        #

        field_names = ['jobs_1000','salary','location__name','rent']

        df = read_frame(
            qs,
            fieldnames=field_names,
            verbose=True,
            coerce_float=True)

        #Calculate score
        df['score'] = 100 * (
            (.3 * self.normalize(df['salary'])) +
            (.4 * self.normalize(df['jobs_1000'])) +
            (.3 * (1 - self.normalize(df['rent']))))


        #Sort by Score and add indexes
        df = df.sort_values(by='score',ascending=False)
        df.index = pd.Series(range(1,len(df) + 1))
        df['rank'] = df.index

        #Re-order columns
        df = df[['rank','location__name','jobs_1000','salary','rent','score']]

        #Get the verbose location type ("State" or "Metropolitan Area")
        for choice in form.fields['location_type'].choices:
            if choice[0] == location_type:
                location_name = choice[1]

        #Rename columns
        df = df.rename(
            columns={
                'rank'              : 'Rank',
                'salary'            : 'Salary',
                'rent'              : 'Rent',
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
            'Score'                     :   'Employment per 1000 jobs is 40%, Salary is 30%, and Rent is 30%'
        }

        #align text right for numeric data types and align text left for text
        table_header = list()

        for col in df.columns:
            if df[col].dtype in [int,float]:
                table_header.append([col,'text-right',tool_tips[col]])
            else:
                table_header.append([col,'text-left',tool_tips[col]])


        #Format output
        print(df['Salary'])
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
        location_type   = form.cleaned_data['location_type']
        location        = form.cleaned_data['location_value']
        rent            = form.cleaned_data['rent']

        #rent_column_name = 'rent_field'
        #rent_column_name = 'location__rent__' + apartment
        #if apartment != 'total':
        #    rent_column_name = 'location__rent__' + apartment + '_bedroom'


        qs = JobLocation.job_locations.filter(
            location=location).filter(
            median__gte=0).filter(
            jobs_1000__gte=0).annotate_rent(
            rent).detailed_jobs()

        field_names = ['job__title','rent','median']

        #if location_type == 'state':
        #    field_names.append('location__state__initials')


        df = read_frame(
            qs,
            fieldnames = field_names,
            verbose=False,
            coerce_float=True)

        df['ratio'] = (df['rent'] * 12) / df['median'] * 100

        good_jobs = df
        good_jobs = good_jobs.sort_values(by='ratio',ascending=True)



        def format_df(df,title):
            df.index = pd.Series(range(1,len(df) + 1))
            df['rank'] = df.index

            df = df[['rank','job__title','rent','median','ratio']]

            new_column_names = {
                'rank'              :   'Rank',
                'job__title'        :   'Job',
                'rent'    :   'Rent',
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

            df['Ratio']     = df['Ratio'].map('{:,.2f}'.format)
            df['Rent']      = df['Rent'].map('${:,.2f}'.format)
            df['Salary']    = df['Salary'].map('${:,.2f}'.format)

            return {'title':title,'header':table_header,'data':df}

        bad_jobs = None#format_df(bad_jobs,"Jobs that can't afford rent")
        good_jobs = format_df(good_jobs,"Jobs that can afford rent")

        return {'good_jobs':good_jobs,'bad_jobs':bad_jobs}
