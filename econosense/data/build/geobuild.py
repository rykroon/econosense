import os
import sys
import requests
import zipfile
from simpledbf import Dbf5
import pandas as pd
from datetime import datetime

#Set up Django Environment
import django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "econosense.settings")
django.setup()

from data.models import Location,Region,Division,State,CombinedArea,Area
from data.build.build import Build

class GeoBuild(Build):

    def __init__(self,year):
        super().__init__()

        self.source = 'geo'
        self.download_path = os.path.join(self.download_path,self.source)
        self.create_dir(self.download_path)

        self.year = year
        self.download_path = os.path.join(self.download_path,self.year)
        self.create_dir(self.download_path)

        self.base_url = 'https://www2.census.gov/geo/tiger/TIGER' + self.year
        self.geographies = ['STATE','CSA','CNECTA','CBSA','NECTA','METDIV','NECTADIV']

        self.areas = None
        self.combined_areas = None


    def cache_area_ids(self):
        self.areas = list(Area.objects.filter(year=self.year).values('id','geo_id'))

    def get_area_id_by_geo_id(self,geo_id):
        for area in self.areas:
            if area['geo_id'] == geo_id:
                return area['id']

    def cache_combined_area_ids(self):
        self.combined_areas = list(CombinedArea.objects.filter(year=self.year).values('id','geo_id'))

    def get_combined_area_id_by_geo_id(self,geo_id):
        for area in self.combined_areas:
            if area['geo_id'] == geo_id:

                return area['id']


    def get_data(self,geo_type):

        working_directory = os.path.join(self.download_path,geo_type)

        if not os.path.isdir(working_directory):
            self.create_dir(working_directory)

        if os.path.isdir(working_directory):
            file_path = os.path.join(working_directory,geo_type.lower() + '.csv')

            if os.path.exists(file_path):
                return self.load_file(file_path)

        zip_file = file_name = 'tl_' + self.year + '_us_' + geo_type.lower() + '.zip'

        download_url = os.path.join(self.base_url, geo_type, zip_file)
        zip_file_path = os.path.join(working_directory,zip_file)

        #Download and unzip
        self.download(download_url,zip_file_path)
        self.unzip(zip_file_path,working_directory)

        #Clean up
        files_in_working_directory = os.listdir(working_directory)

        for file in files_in_working_directory:
            file_path = os.path.join(working_directory,file)

            if file_path.endswith('.dbf'):
                df = Dbf5(file_path).to_dataframe()
                csv_file = geo_type.lower() + '.csv'
                csv_file_path = os.path.join(working_directory,csv_file)
                df.to_csv(csv_file_path,index=False)
                print('Exported file ' + csv_file_path)

            os.remove(file_path)
            print('Removed file ' + file_path)

        return df


    def create_state(self,data):
        state = State()

        state.geo_id        = data.GEOID
        state.year          = self.year
        state.name          = data.NAME
        state.lsad_name     = data.NAME
        state.lsad          = 'ST'
        state.latitude      = data.INTPTLAT
        state.longitude     = data.INTPTLON

        state.initials      = data.STUSPS
        state.region_id     = data.REGION
        state.division_id   = data.DIVISION

        if self.partialdb.skip_state(state): return

        state.save()


    def create_combined_area(self,data):
        csa = CombinedArea()

        csa.geo_id      = data.GEOID
        csa.year        = self.year
        csa.name        = data.NAME
        csa.lsad_name   = data.NAMELSAD
        csa.lsad        = data.LSAD
        csa.latitude    = data.INTPTLAT
        csa.longitude   = data.INTPTLON

        csa.save()


    def create_area(self,data):
        area = Area()

        try: area.geo_id = data.METDIVFP        #id for Metropolitan Divisions
        except:
            try: area.geo_id = data.NCTADVFP    #id for NECTA Divisions
            except: area.geo_id = data.GEOID    #id for other

        area.year       = self.year
        area.name       = data.NAME
        area.lsad_name  = data.NAMELSAD
        area.lsad       = data.LSAD
        area.latitude   = data.INTPTLAT
        area.longitude  = data.INTPTLON

        area.parent         = None
        area.combined_area  = None

        try:
            if data.CBSAFP != area.geo_id:
                area.parent_id = self.get_area_id_by_geo_id(data.CBSAFP)
        except:
            if data.NECTAFP != area.geo_id:
                 area.parent_id = self.get_area_id_by_geo_id(data.NECTAFP)


        try:
            area.combined_area_id = self.get_combined_area_id_by_geo_id(int(data.CSAFP))
        except:
            try:
                 area.combined_area_id = self.get_combined_area_id_by_geo_id(int(data.CNECTAFP))
            except: pass

        if self.partialdb.status():
            if self.partialdb.skip_area(area):
                return
            else:
                area.parent_id = None

        area.save()


    def create_regions_and_divisons(self):
        Region.objects.all().delete()
        Division.objects.all().delete()

        regions = list()
        north_east = Region(id=1,name='Northeast')
        regions.append(north_east)

        mid_west = Region(id=2,name='Midwest')
        regions.append(mid_west)

        south = Region(id=3,name='South')
        regions.append(south)

        west = Region(id=4,name='West')
        regions.append(west)

        territory = Region(id=9,name='Territory')
        regions.append(territory)

        Region.objects.bulk_create(regions)

        divisions = list()
        territory_div = Division(id=0,name='Territory',region=territory)
        divisions.append(territory_div)

        new_england = Division(id=1,name='New England',region=north_east)
        divisions.append(new_england)

        mid_atlantic = Division(id=2,name='Mid-Atlantic',region=north_east)
        divisions.append(mid_atlantic)

        east_north_central = Division(id=3,name='East North Central',region=mid_west)
        divisions.append(east_north_central)

        west_north_central = Division(id=4,name='West North Central',region=mid_west)
        divisions.append(west_north_central)

        south_atlantic = Division(id=5,name='South Atlantic',region=south)
        divisions.append(south_atlantic)

        east_south_central = Division(id=6,name='East South Central',region=south)
        divisions.append(east_south_central)

        west_south_central = Division(id=7,name='West South Central',region=south)
        divisions.append(west_south_central)

        mountain = Division(id=8,name='Mountain',region=west)
        divisions.append(mountain)

        pacific = Division(id=9,name='Pacific',region=west)
        divisions.append(pacific)

        Division.objects.bulk_create(divisions)


    def build(self):
        Location.objects.filter(year=self.year).delete()

        data_frames = {}
        for geo in self.geographies:
            data_frames[geo] = self.get_data(geo)

        print('\n')
        print('Building Regions and Divisions')
        self.create_regions_and_divisons()

        for geo in self.geographies:
            print('Building data from geo directory ' + geo)

            geo_frame = data_frames[geo]
            print('Dataframe ' + geo + ' has ' + str(len(geo_frame.index)) + ' rows of data')


            if geo in ['CBSA','NECTA'] and self.combined_areas == None:
                self.cache_combined_area_ids()

            elif geo in ['METDIV','NECTADIV'] and self.areas == None:
                self.cache_area_ids()


            for row in geo_frame.itertuples():
                if geo == 'STATE':
                    self.create_state(row)

                elif geo in ['CSA','CNECTA']:
                    self.create_combined_area(row)

                elif geo in ['CBSA','NECTA','METDIV','NECTADIV']:
                    self.create_area(row)

            print('\n')

        print(str(len(self.partialdb.skipped_locations)) + ' locations have been skipped')



#stuff
