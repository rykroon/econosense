import sys
import os
from acsapi import AcsApi

#Set up Django Environment
import django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "econosense.settings")
django.setup()

from data.models import Rent,Area,State,Location
from data.build.build import Build

#partialdb = PartialDatabase()

class AcsBuild(Build):

    def __init__(self,year):
        super().__init__(year)
        self.api = AcsApi(year=year)

        self.geographies = {
            'State'     :   'state',
            'CBSA'      :   'metropolitan statistical area/micropolitan statistical area',
            'NECTA'     :   'new england city and town area',
            'METDIV'    :   'metropolitan division',
            'NECTADIV'  :   'necta division',
            'CSA'       :   'combined statistical area',
            'CNECTA'    :   'combined new england city and town area'
        }

        self.median_gross_rent = dict()
        self.median_gross_rent['group'] = 'B25031'
        self.median_gross_rent['variables'] = {
            'total'             : '001E',
            'no_bedroom'        : '002E',
            'one_bedroom'       : '003E',
            'two_bedroom'       : '004E',
            'three_bedroom'     : '005E',
            'four_bedroom'      : '006E',
            'five_plus_bedrooms': '007E'
        }

        self.println('-- Begin ACS Build --',space_before=True,space_after=True)



    def cache_locations(self):
        self.locations = list(Location.objects.filter(year=self.year).values('id','geo_id'))

    def get_location_id_by_geo_id(self,geo_id):
        for loc in self.locations:
            if loc['geo_id'] == geo_id:
                return loc['id']


    def build(self):
        Rent.objects.filter(year=self.year).delete()
        self.cache_locations()

        for geo_key,geo_value in self.geographies.items(): #each geography
            self.build_median_gross_rent(geo_key,geo_value)



    def build_median_gross_rent(self,geo_key,geo_value):
        rents = dict()
        self.println('Building rent data by ' + geo_key)
        for var_key,var_value in self.median_gross_rent['variables'].items(): #each bedroom

            response = self.api.get(self.median_gross_rent['group'],var_value,geo_value)

            if response.status_code == 200:

                result = response.json()

                for row in result[1:]:

                    if geo_key in ['METDIV','NECTADIV']:
                        geo_id = int(row[2])
                    else:
                        geo_id = int(row[1])


                    if int(row[0]) < 0: #If rent is < 0
                        amount = None
                    else:
                        amount = int(row[0])


                    try: #use already existing Rent object
                        rent = rents[geo_id]
                    except: #create new Rent object
                        rent = Rent()
                        rent.year = self.year
                        rent.location_id = self.get_location_id_by_geo_id(geo_id)

                        if self.partialdb.skip_rent(rent):
                            continue


                    if var_key == 'total':                  rent.total = amount
                    elif var_key == 'no_bedroom':           rent.no_bedroom = amount
                    elif var_key == 'one_bedroom':          rent.one_bedroom = amount
                    elif var_key == 'two_bedroom':          rent.two_bedroom = amount
                    elif var_key == 'three_bedroom':        rent.three_bedroom = amount
                    elif var_key == 'four_bedroom':         rent.four_bedroom = amount
                    elif var_key == 'five_plus_bedrooms':   rent.five_bedroom = amount

                    rents[geo_id] = rent #save object to the dict

            else:
                print('There was an issue with URL: ' + response.url)

        rent_list = list(rents.values())
        self.println('Inserting batch of ' + str(len(rent_list)) + ' records',space_after=True)
        Rent.objects.bulk_create(rent_list)



#
