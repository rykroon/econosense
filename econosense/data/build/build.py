import sys
import os

import requests
import zipfile
import pandas as pd
from datetime import datetime

from partialdb import PartialDatabase

class Build(object):

    def __init__(self,year):
        self.year = year
        self.download_path = 'data/build/downloads'
        self.partialdb = PartialDatabase()

        if not os.path.isdir(self.download_path):
            self.create_dir(self.download_path)

    def time_it(self,some_function):
        start = datetime.now()
        some_function()
        end = datetime.now()

        print(end-start)


    def create_dir(self,directory):
        try:
            os.mkdir(directory)
            print('Created directory ' + directory)
            print('\n')
        except:
            pass

    def download(self,url,save_path):
        print('Downloading data from ' + url + ' to ' + save_path)
        print('\n')

        response = requests.get(url)
        with open(save_path,'wb') as f:
            f.write(response.content)


    def unzip(self,zip_file,extract_to_path):
        print('Extracting zip file ' + zip_file + ' to ' + extract_to_path)
        print('\n')

        zip_ref = zipfile.ZipFile(zip_file, 'r')
        zip_ref.extractall(extract_to_path)
        zip_ref.close()

    def load_file(self,file):
        print('Loading data from ' + file)
        print('\n')

        if file.endswith('.csv'):
            return pd.read_csv(file)

        elif file.endswith('.xlsx'):
            return pd.read_excel(file)




if __name__ == '__main__':

    from acsbuild import AcsBuild
    from oesbuild import OesBuild
    from geobuild import GeoBuild

    try:
        year = sys.argv[1]
        try:
            int(year)
        except:
            print('Year must be numeric')
            sys.exit(0)

    except:
        print("Must specify a year")
        sys.exit(0)


    try:
        source = sys.argv[2]
        data_sources = list()
        data_sources.append(source)

    except:
        data_sources = ['geo','oes','acs']


    for source in data_sources:

        if source == 'geo':
            geo = GeoBuild(year)
            geo.build()

        if source == 'oes':
            oes = OesBuild(year)
            oes.build()

        if source == 'acs':
            acs = AcsBuild(year)
            acs.build()





#
