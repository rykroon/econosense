import sys
import os
import datetime
import concurrent.futures
import threading

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

    def refresh(self):
        Gross.objects.filter(year=self.year).delete()
        Tax.objects.filter(year=self.year).delete()
        JobLocation.objects.filter(
            year=self.year).update(
                avg_gross=None,
                pct_10_gross=None,
                pct_25_gross=None,
                median_gross=None,
                pct_75_gross=None,
                pct_90_gross=None
            )


    def build(self):
        self.refresh()



        ###!!!!! im a fucking idiot
        #I am not clearing the fields in the job_location table that were populated
        #from previous runs

        states = State.objects.filter(year=self.year).exclude(region__geo_id=9)
        job_locs = JobLocation.objects.filter(year=self.year).filter(location__in=states)
        # job_locs.update(
        #     avg_gross=None,
        #     pct_10_gross=None,
        #     pct_25_gross=None,
        #     median_gross=None,
        #     pct_75_gross=None,
        #     pct_90_gross=None
        # )


        job_loc_length = len(job_locs)

        #print(threading.active_count())

        i = 0
        times = list()

        for job in job_locs:
            i += 1
            state = job.location.state

            #start = datetime.datetime.now()

            if self.use_concurrency:

                amounts = [
                    job.average,
                    job.pct_10,
                    job.pct_25,
                    job.median,
                    job.pct_75,
                    job.pct_90
                ]

                with concurrent.futures.ThreadPoolExecutor(3) as pool:
                    futures = {pool.submit(self.get_gross,state,amount) : amount for amount in amounts}

                    #print(threading.active_count())

                    for future in concurrent.futures.as_completed(futures):

                        try:
                            gross = future.result()
                            gross.save()
                            job.set_gross(gross)

                        except:
                            pass

                        if future.exception() is not None:
                            print(future.exception())

            else:

                job.avg_gross       = self.get_gross(state,job.average)
                job.pct_10_gross    = self.get_gross(state,job.pct_10)
                job.pct_25_gross    = self.get_gross(state,job.pct_25)
                job.median_gross    = self.get_gross(state,job.median)
                job.pct_75_gross    = self.get_gross(state,job.pct_75)
                job.pct_90_gross    = self.get_gross(state,job.pct_90)


            if job.has_null_gross():
                print(str(job.id) + ' ' + str(job) + ' has null gross')

            # end = datetime.datetime.now()
            # times.append(end-start)
            # avg_time = sum(times,datetime.timedelta(0)).total_seconds() / len(times)
            # print(avg_time)

            job.save()
            print(str(i) + ' / ' + str(job_loc_length))



    def get_gross(self,state,pay_rate):
        #Dont bother calculating tax for invalid values
        if pay_rate <= 0 or pay_rate >= 999999:
            return None

        try:
            gross = Gross.objects.get(year=self.year,state=state,amount=pay_rate)
            return gross
        except:
            pass

        gross = Gross()

        gross.year = self.year
        gross.state = state
        gross.amount = pay_rate

        if self.use_concurrency:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:

                futures = {pool.submit(self.get_tax,state,filing_status,pay_rate): filing_status for filing_status in self.filing_statuses}

                #print(threading.active_count())

                for future in concurrent.futures.as_completed(futures):
                    try:
                        tax = future.result()
                        tax.save()
                        gross.set_tax(tax)
                    except:
                        pass

                    #print exception if future had an exception
                    if future.exception() is not None:
                        print(future.exception())

        else:

            gross.single                = self.get_tax(state,'single',pay_rate)
            gross.single.save()

            gross.married               = self.get_tax(state,'married',pay_rate)
            gross.married.save()

            gross.married_separately    = self.get_tax(state,'married_separately',pay_rate)
            gross.married_separately.save()

            gross.head_of_household     = self.get_tax(state,'head_of_household',pay_rate)
            gross.head_of_household.save()

            gross.save()


        if gross.has_null_tax():
            print(str(gross) + ' has null tax')


        return gross


    def get_tax(self,state,filing_status,pay_rate):
        tax = Tax()

        tax.year = self.year
        tax.state = state
        tax.filing_status = filing_status
        tax.amount = pay_rate


        income_tax = self.api.income_tax(self.year,pay_rate,filing_status,state.initials)

        tax.fica_tax = income_tax.fica_tax
        tax.state_tax = income_tax.state_tax
        tax.federal_tax = income_tax.federal_tax

        #tax.save()

        return tax
