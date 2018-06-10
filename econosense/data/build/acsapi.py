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


    def get(self,group,variable,geography,year=None):
        if year is None:
            year = self.year

        url = self.base_url + str(year) + '/acs/acs1'

        if type(variable) == str:

            self.params['get'] = group + '_' + variable
            self.params['for'] = geography + ':*'

            return requests.get(url,params=self.params)

        elif type(variable) == dict:
            result = dict()

            for key,value in variable.items():
                self.params['get'] = group + '_' + var
                self.params['for'] = geography + ':*'

                result[key] = requests.get(url,params=self.params)

            return result
