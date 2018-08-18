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

        for geo_key,geo_value in self.api.geographies.items(): #each geography
            self.build_median_gross_rent(geo_key,geo_value)



    def build_median_gross_rent(self,geo_key,geo_value):
        rents = dict()
        self.println('Building rent data by ' + geo_key)

        for num_of_bedrooms in [None,0,1,2,3,4,5]:

            response = self.api.get_median_gross_rent(geo_key,num_of_bedrooms)
            print(response.url)

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

                    if num_of_bedrooms == None: rent.total          = amount
                    elif num_of_bedrooms == 0:  rent.no_bedroom     = amount
                    elif num_of_bedrooms == 1:  rent.one_bedroom    = amount
                    elif num_of_bedrooms == 2:  rent.two_bedroom    = amount
                    elif num_of_bedrooms == 3:  rent.three_bedroom  = amount
                    elif num_of_bedrooms == 4:  rent.four_bedroom   = amount
                    elif num_of_bedrooms == 5:  rent.five_bedroom   = amount

                    rents[geo_id] = rent #save object to the dict

            else:
                print('There was an issue with URL: ' + response.url)

        rent_list = list(rents.values())
        self.println('Inserting batch of ' + str(len(rent_list)) + ' records',space_after=True)
        Rent.objects.bulk_create(rent_list)



#
