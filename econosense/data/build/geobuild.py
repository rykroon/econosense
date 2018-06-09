import os
import sys
import requests
import zipfile
from simpledbf import Dbf5
import pandas as pd
from data.build.partialdb import PartialDatabase

from datetime import datetime

#Set up Django Environment
import django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "econosense.settings")
django.setup()

from data.models import Location,Region,Division,State,CombinedArea,Area

partialdb = PartialDatabase()


def get_data(directory,year,raw_data_path):
    base_url = 'https://www2.census.gov/geo/tiger/TIGER' + year

    #Create Working Directory if it doesn't exist.
    if not os.path.isdir(os.path.join(raw_data_path,year)):
        os.mkdir(os.path.join(raw_data_path,year))
        print('Created directory ' + os.path.join(raw_data_path,year))

    if not os.path.isdir(os.path.join(raw_data_path,year,directory)):
        os.mkdir(os.path.join(raw_data_path,year,directory))
        print('Created directory ' + os.path.join(raw_data_path,year,directory))

    working_directory = os.path.join(raw_data_path,year,directory)

    file_name = 'tl_' + year + '_us_' + directory.lower() + '.csv'

    if os.path.exists(os.path.join(working_directory,file_name)):
        print('Loading data from ' + os.path.join(working_directory,file_name))
        return pd.read_csv(os.path.join(working_directory,file_name))

    file_name = file_name[:-4] + '.zip'

    download_url = os.path.join(base_url, directory, file_name)
    zip_file_path = os.path.join(working_directory,file_name)

    #Download
    print('Downloading data from ' + download_url)
    response = requests.get(download_url)
    with open(zip_file_path,'wb') as f:
        f.write(response.content)

    #Extract Zip File
    zip_ref = zipfile.ZipFile(zip_file_path, 'r')
    zip_ref.extractall(working_directory)
    zip_ref.close()

    #Clean up
    files_in_working_directory = os.listdir(working_directory)

    for file in files_in_working_directory:
        file_path = os.path.join(working_directory,file)

        if file_path.endswith('.dbf'):
            dbf = Dbf5(file_path)
            df = dbf.to_dataframe()
            df.to_csv(file_path[:-4] + '.csv',index=False)

        os.remove(file_path)

    return df

def create_state(data):
    state = State()

    state.id            = data.GEOID
    state.name          = data.NAME
    state.lsad_name     = data.NAME
    state.lsad          = 'ST'
    state.latitude      = data.INTPTLAT
    state.longitude     = data.INTPTLON

    state.initials      = data.STUSPS
    #state.region    = Region.objects.get(id=int(data.REGION))
    #state.division  = Division.objects.get(id=int(data.DIVISION))
    state.region_id     = data.REGION
    state.division_id   = data.DIVISION

    if partialdb.skip_state(state): return

    state.save()


def create_combined_area(data):
    csa = CombinedArea()

    csa.id          = data.GEOID
    csa.name        = data.NAME
    csa.lsad_name   = data.NAMELSAD
    csa.lsad        = data.LSAD
    csa.latitude    = data.INTPTLAT
    csa.longitude   = data.INTPTLON

    csa.save()


def create_area(data):
    area = Area()

    try: area.id = data.METDIVFP        #id for Metropolitan Divisions
    except:
        try: area.id = data.NCTADVFP    #id for NECTA Divisions
        except: area.id = data.GEOID    #id for other

    area.name       = data.NAME
    area.lsad_name  = data.NAMELSAD
    area.lsad       = data.LSAD
    area.latitude   = data.INTPTLAT
    area.longitude  = data.INTPTLON

    area.parent         = None
    area.combined_area  = None

    try:
        if data.CBSAFP != area.id:  area.parent_id = data.CBSAFP
    except:
        if data.NECTAFP != area.id: area.parent_id = data.NECTAFP


    try:    area.combined_area_id = int(data.CSAFP)
    except:
        try:    area.combined_area_id = int(data.CNECTAFP)
        except: pass

    if partialdb.status():
        if partialdb.skip_area(area):
            return
        else:
            area.parent_id = None

    area.save()


def create_regions_and_divisons():
    Region.objects.all().delete()
    Division.objects.all().delete()

    regions = list()
    north_east = Region(id=1,name='Northeast')
    #north_east.save()
    regions.append(north_east)

    mid_west = Region(id=2,name='Midwest')
    #mid_west.save()
    regions.append(mid_west)

    south = Region(id=3,name='South')
    #south.save()
    regions.append(south)

    west = Region(id=4,name='West')
    #west.save()
    regions.append(west)

    territory = Region(id=9,name='Territory')
    #territory.save()
    regions.append(territory)

    Region.objects.bulk_create(regions)

    divisions = list()
    territory_div = Division(id=0,name='Territory',region=territory)
    #territory_div.save()
    divisions.append(territory_div)

    new_england = Division(id=1,name='New England',region=north_east)
    #new_england.save()
    divisions.append(new_england)

    mid_atlantic = Division(id=2,name='Mid-Atlantic',region=north_east)
    #mid_atlantic.save()
    divisions.append(mid_atlantic)

    east_north_central = Division(id=3,name='East North Central',region=mid_west)
    #east_north_central.save()
    divisions.append(east_north_central)

    west_north_central = Division(id=4,name='West North Central',region=mid_west)
    #west_north_central.save()
    divisions.append(west_north_central)

    south_atlantic = Division(id=5,name='South Atlantic',region=south)
    #south_atlantic.save()
    divisions.append(south_atlantic)

    east_south_central = Division(id=6,name='East South Central',region=south)
    #east_south_central.save()
    divisions.append(east_south_central)

    west_south_central = Division(id=7,name='West South Central',region=south)
    #west_south_central.save()
    divisions.append(west_south_central)

    mountain = Division(id=8,name='Mountain',region=west)
    #mountain.save()
    divisions.append(mountain)

    pacific = Division(id=9,name='Pacific',region=west)
    #pacific.save()
    divisions.append(pacific)

    Division.objects.bulk_create(divisions)


def main(year,raw_data_path):
    Location.objects.all().delete()

    directories = ['STATE','CSA','CNECTA','CBSA','NECTA','METDIV','NECTADIV']

    data_frames = {}
    print('Getting geo data')
    for directory in directories:
        data_frames[directory] = get_data(directory, year, raw_data_path)

    start = datetime.now()

    print('\n')
    print('Building Regions and Divisions')
    create_regions_and_divisons()

    #for key,value in data_frames.items():
    for key in directories:
        print('Building data from geo directory ' + key)

        value = data_frames[key]
        print('Dataframe ' + key + ' has ' + str(len(value.index)) + ' rows of data')
        for row in value.itertuples():
            if key == 'STATE':
                create_state(row)

            elif key in ['CSA','CNECTA']:
                create_combined_area(row)

            elif key in ['CBSA','NECTA','METDIV','NECTADIV']:
                create_area(row)

        print('\n')

    end = datetime.now()
    print(end-start)
    print(str(len(partialdb.skipped_locations)) + ' locations have been skipped')

            # if key == 'METDIV':         create_area_div(row)
            # if key == 'NECTADIV':       create_necta_div(row)



#stuff
