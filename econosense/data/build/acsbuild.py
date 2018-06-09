import sys
import os
import requests
from datetime import datetime
from partialdb import PartialDatabase

#Set up Django Environment
import django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "econosense.settings")
django.setup()

from data.models import Rent,Area,State,Location

partialdb = PartialDatabase()

def main(year):
    Rent.objects.all().delete()
    base_url = 'https://api.census.gov/data/' + year + '/acs/acs1'

    try:
        CENSUS_API_KEY = os.environ['CENSUS_API_KEY']
    except:
        print('API key not found')
        return

    params = dict()
    params['key'] = CENSUS_API_KEY

    median_gross_rent = 'B25031' #group

    variables = {
        'Total'             : '001E',
        'no_bedroom'        : '002E',
        'one_bedroom'       : '003E',
        'two_bedroom'       : '004E',
        'three_bedroom'     : '005E',
        'four_bedroom'      : '006E',
        'five_plus_bedrooms': '007E'
    }

    geographies = {
        'State'     :   'state',
        'CBSA'      :   'metropolitan statistical area/micropolitan statistical area',
        'NECTA'     :   'new england city and town area',
        'METDIV'    :   'metropolitan division',
        'NECTADIV'  :   'necta division',
        'CSA'       :   'combined statistical area',
        'CNECTA'    :   'combined new england city and town area'
    }

    start = datetime.now()
    for geo_key,geo_value in geographies.items(): #each geography
        rents = {}

        print('Building rent data by ' + geo_key)
        for var_key,var_value in variables.items(): #each bedroom
            params['get'] = median_gross_rent + '_' + var_value
            params['for'] = geo_value + ':*'
            response = requests.get(base_url,params=params)

            if response.status_code == 200:
                print('Requesting data from ' + response.url)
                result = response.json()

                for row in result[1:]:

                    if geo_key in ['METDIV','NECTADIV']:
                        loc_id = int(row[2])
                    else:
                        loc_id = int(row[1])


                    if int(row[0]) < 0: #If rent is < 0
                        amount = None
                    else:
                        amount = int(row[0])


                    try: #use already existing Rent object
                        rent = rents[loc_id]
                    except: #create new Rent object
                        rent = Rent()
                        rent.location_id = loc_id

                        if partialdb.skip_rent(rent):
                            continue

                        #If building a partial database then we might not find the location
                        # try:
                        #     rent.location = Location.objects.get(id=loc_id)
                        # except:
                        #     continue


                    if var_key == 'Total': rent.total = amount
                    elif var_key == 'no_bedroom': rent.no_bedroom = amount
                    elif var_key == 'one_bedroom': rent.one_bedroom = amount
                    elif var_key == 'two_bedroom': rent.two_bedroom = amount
                    elif var_key == 'three_bedroom': rent.three_bedroom = amount
                    elif var_key == 'four_bedroom': rent.four_bedroom = amount
                    elif var_key == 'five_plus_bedrooms': rent.five_bedroom = amount

                    rents[loc_id] = rent #save object to the dict

            else:
                print('There was an issue with URL: ' + response.url)

        print('\n')

        rent_list = list(rents.values())
        Rent.objects.bulk_create(rent_list)

        #for key,rent in rents.items():
        #    rent.save()


    end = datetime.now()
    print(end-start)





#
