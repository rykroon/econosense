import json
import requests
import os.path
import sys

#Set up Django Environment
import django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "econosense.settings")
django.setup()

from data.models import Rent,Area,State,Location


def build_url(year,group,geo,variable):
    base_url = 'https://api.census.gov/data/' + year + '/acs/acs1'
    #might be an easier way to this with a 'params' variable as part of the request
    #'get' and 'for' would be the parms
    get = '?get=' + group + '_' + variable
    for_ = 'for=' + geo + ':*' # * - all
    get_for = get + '&' + for_
    return os.path.join(base_url,get_for)


def main(year):
    median_gross_rent = 'B25031'

    variables = {'Total':'001E','no_bedroom':'002E','one_bedroom':'003E','two_bedroom':'004E','three_bedroom':'005E','four_bedroom':'006E','five_plus_bedrooms':'007E'}
    geographies = {
        'State'     :   'state',
        'CBSA'      :   'metropolitan%20statistical%20area/micropolitan%20statistical%20area',
        'NECTA'     :   'new%20england%20city%20and%20town%20area',
        'METDIV'    :   'metropolitan%20division',
        'NECTADIV'  :   'necta%20division',
        'CSA'       :   'combined%20statistical%20area',
        'CNECTA'    :   'combined%20new%20england%20city%20and%20town%20area'
    }


    for kgeo,vgeo in geographies.items(): #each geography
        rents = {}

        print('Building rent data by ' + kgeo)
        for kvar,vvar in variables.items(): #each bedroom
            url = build_url(year,median_gross_rent,vgeo,vvar)
            response = requests.get(url)

            if response.status_code == 200:
                #result = json.loads(response.content.decode('UTF8'))
                result = response.json()

                for row in result[1:]:

                    if kgeo in ['METDIV','NECTADIV']:
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

                        #If building a partial database then we might not find the location
                        try: rent.location = Location.objects.get(id=loc_id)
                        except: continue


                    if kvar == 'Total': rent.total = amount
                    elif kvar == 'no_bedroom': rent.no_bedroom = amount
                    elif kvar == 'one_bedroom': rent.one_bedroom = amount
                    elif kvar == 'two_bedroom': rent.two_bedroom = amount
                    elif kvar == 'three_bedroom': rent.three_bedroom = amount
                    elif kvar == 'four_bedroom': rent.four_bedroom = amount
                    elif kvar == 'five_plus_bedrooms': rent.five_bedroom = amount

                    rents[loc_id] = rent #save object to the dict

            else:
                print('There was an issue with URL: ' + url )

        for key,rent in rents.items():
            rent.save()






#
