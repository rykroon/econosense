import requests
import os

class AcsApi():

    def __init__(self,api_key=None,year=None):
        if api_key is not None:
            self.API_KEY = api_key
        else:
            try:
                self.API_KEY = os.environ['CENSUS_API_KEY']
            except:
                self.API_KEY = None

        self.year = year

        self.params = dict()
        self.params['key'] = self.API_KEY

        self.base_url = 'https://api.census.gov/data/' #+ year + '/acs/acs1'

        self.session = requests.Session()
        self.adapter = requests.adapters.HTTPAdapter(max_retries=5)
        self.session.mount(self.base_url,self.adapter)

        self.geographies = {
            'State'     :   'state',
            'CBSA'      :   'metropolitan statistical area/micropolitan statistical area',
            'NECTA'     :   'new england city and town area',
            'METDIV'    :   'metropolitan division',
            'NECTADIV'  :   'necta division',
            'CSA'       :   'combined statistical area',
            'CNECTA'    :   'combined new england city and town area'
        }


    def get(self,group,variable,geography,year=None):
        if year is None:
            year = self.year

        url = self.base_url + str(year) + '/acs/acs1'

        if type(variable) == str:

            self.params['get'] = group + '_' + variable
            self.params['for'] = geography + ':*'

            #return requests.get(url,params=self.params)
            return self.session.get(url,params=self.params)

        # elif type(variable) == dict:
        #     result = dict()
        #
        #     for key,value in variable.items():
        #         self.params['get'] = group + '_' + var
        #         self.params['for'] = geography + ':*'
        #
        #         #result[key] = requests.get(url,params=self.params)
        #         result[key] = self.session.get(url,params=self.params)
        #
        #     return result

    #Median Gross Rent
    def get_median_gross_rent(self,geography,num_of_bedrooms=None,year=None):
        group = 'B25031'

        variables = {
            None    : '001E', #Total
            0       : '002E', #No Bedroom
            1       : '003E', #1 Bedroom
            2       : '004E', #2 Bedroom
            3       : '005E', #3 Bedroom
            4       : '006E', #4 Bedroom
            5       : '007E' #5 or More Bedrooms
        }

        var = variables[num_of_bedrooms]
        geo = self.geographies[geography]

        if year is None:
            year = self.year

        return self.get(group,var,geo,year)
