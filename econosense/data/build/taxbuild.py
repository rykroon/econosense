import sys
import os
import datetime
from datetime import datetime as dt
import concurrent.futures

#Set up Django Environment
import django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "econosense.settings")
django.setup()

from data.models import JobLocation,State,Gross,Tax

from data.build.build import Build
from taxee import Taxee


class TaxBuild(Build):
    def __init__(self,year):
        super().__init__(year)
        self.api = Taxee()

        self.filing_statuses = [
            'single',
            'married',
            'married_separately',
            'head_of_household'
        ]

        self.use_concurrency = True
        self.println('-- Begin Tax Build --',space_before=True,space_after=True)

    def refresh(self):

        #I believe everytime I delete Gross/Tax objects then if there are any JobLocation
        #objects that reference those deleted objects then those JobLocations also get deleted
        JobLocation.objects.filter(
            year=self.year).update(
                avg_gross=None,
                pct_10_gross=None,
                pct_25_gross=None,
                median_gross=None,
                pct_75_gross=None,
                pct_90_gross=None
            )

        Gross.objects.filter(year=self.year).delete()
        Tax.objects.filter(year=self.year).delete()


    #This will first create gross and tax objects w/o associating them to a JobLocation
    def build(self):
        self.refresh()

        states = State.objects.filter(year=self.year).exclude(region__geo_id=9)
        qs = JobLocation.objects.filter(year=self.year).filter(location_id__in=states).filter(median__gt=0).filter(median__lt=999999)

        qs = qs.values('year','location','location__state__initials','median').distinct()
        qs_len = len(qs)
        self.println(str(qs_len) + ' gross objects will be created')

        gross_list = list()

        start = dt.now()

        batch_size = 5000
        count = 0
        #
        futures = list()

        if self.use_concurrency:

            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
                futures = {pool.submit(self.build_helper,row): row for row in qs}

                for future in concurrent.futures.as_completed(futures):
                    try:
                        gross = future.result()
                    except:
                        print(future.exception())

                    gross_list.append(gross)

                    if len(gross_list) >= batch_size:
                        end = dt.now()
                        print(end-start)
                        self.println("Inserting batch of {} Gross objects".format(len(gross_list)),space_after=True)

                        Gross.objects.bulk_create(gross_list)
                        gross_list.clear()

                if len(gross_list) > 0:
                    end = dt.now()
                    print(end-start)
                    self.println("Inserting batch of {} Gross objects".format(len(gross_list)),space_after=True)

                    Gross.objects.bulk_create(gross_list)

                with django.db.connection.cursor() as cursor:
                    sql = "update job_location set median_gross_id = gross.id from gross where job_location.year=gross.year and job_location.location_id=gross.state_id and job_location.median=gross.amount;"
                    cursor.execute(sql)

        else:
            for row in qs:
                count += 1

                state = {
                    'id'        : row['location'],
                    'initials'  : row['location__state__initials']
                }

                gross = self.get_gross(state,row['median'])

                if gross.has_null_tax():
                    print(str(gross) + ' has null tax')

                gross_list.append(gross)

                #print(str(count) + ' / ' + str(qs_len))

                if len(gross_list) >= batch_size:
                    end = dt.now()
                    print(end-start)
                    print("Inserting batch of {} Gross objects".format(batch_size))
                    print('\n')

                    Gross.objects.bulk_create(gross_list)
                    gross_list.clear()


    def build_helper(self,row):
        state = {
            'id'        : row['location'],
            'initials'  : row['location__state__initials']
        }

        gross = self.get_gross(state,row['median'])
        if gross.has_null_tax():
            print(str(gross) + ' has null tax')

        return gross



    def get_gross(self,state,pay_rate):
        gross = Gross()

        gross.year      = self.year
        gross.state_id  = state['id']
        gross.amount    = pay_rate


        tax_list = list()

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:

            futures = {pool.submit(self.get_tax,state,filing_status,pay_rate): filing_status for filing_status in self.filing_statuses}

            for future in concurrent.futures.as_completed(futures):
                try:
                    tax = future.result()
                except:
                    print(future.exception())

                if tax is not None:
                    tax_list.append(tax)
                    #gross.set_tax(tax)

        Tax.objects.bulk_create(tax_list)
        for tax in tax_list:
            gross.set_tax(tax)

        return gross


    def get_tax(self,state,filing_status,pay_rate):
        tax = Tax()

        tax.year            = self.year
        tax.state_id        = state['id']
        tax.filing_status   = filing_status
        tax.amount          = pay_rate

        income_tax          = self.api.income_tax(self.year,pay_rate,filing_status,state['initials'])

        tax.fica_tax        = income_tax.fica_tax
        tax.state_tax       = income_tax.state_tax
        tax.federal_tax     = income_tax.federal_tax

        if tax.is_missing_info():
            print('tax is missing info')

        return tax
