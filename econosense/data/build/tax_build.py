import sys
import os
import decimal

#Set up Django Environment
import django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "econosense.settings")
django.setup()

from data.models import JobLocation,Income,State
from data.taxee_api import TaxeeApi



def main(year):
    tax = TaxeeApi()
    qs = JobLocation.job_locations.by_state().filter(median__gte=0)

    for job_loc in qs:
        for filing_status,filing_status_verbose in Income.FILING_STATUS_CHOICES:
            try:
                income = Income.objects.get(
                    year=year,
                    gross=job_loc.median,
                    filing_status=filing_status,
                    state=job_loc.location
                )
                print('income already exists')
                continue
            except:
                income = Income()
                income.year = year
                income.gross = job_loc.median
                income.filing_status = filing_status
                income.state = job_loc.location.state

                taxes = tax.get_income_taxes(income.year,income.gross,income.filing_status,income.state.initials)
                if taxes == None:
                    print('error')
                else:
                    income.fica = taxes['fica']
                    income.federal_tax = taxes['federal']
                    income.state_tax = taxes['state']
                    income.net = income.gross - decimal.Decimal(income.fica) - decimal.Decimal(income.federal_tax) - decimal.Decimal(income.state_tax)

                    print(income)
                    income.save()
