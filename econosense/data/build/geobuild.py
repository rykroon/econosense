import os
import sys
import requests
import zipfile
from simpledbf import Dbf5
import pandas as pd
from data.build.partialdb import PartialDatabase

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

    if not os.path.isdir(os.path.join(raw_data_path,year,directory)):
        os.mkdir(os.path.join(raw_data_path,year,directory))

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
        #extension = file_path[-3:]

        #if extension == 'dbf':
        if file_path.endswith('.dbf'):
            dbf = Dbf5(file_path)
            df = dbf.to_dataframe()
            df.to_csv(file_path[:-4] + '.csv',index=False)

        os.remove(file_path)

    return df

def create_state(data):
    state = State()

    state.id = data.GEOID
    state.name = data.NAME
    state.lsad_name = data.NAME
    state.lsad = 'ST'
    state.latitude = data.INTPTLAT
    state.longitude = data.INTPTLON

    state.initials = data.STUSPS
    state.region = Region.objects.get(id=int(data.REGION))
    state.division = Division.objects.get(id=int(data.DIVISION))

    if partialdb.skip_state(state): return

    state.save()


def create_combined_area(data):
    csa = CombinedArea()

    csa.id = data.GEOID
    csa.name = data.NAME
    csa.lsad_name = data.NAMELSAD
    csa.lsad = data.LSAD
    csa.latitude = data.INTPTLAT
    csa.longitude = data.INTPTLON

    csa.save()


def create_area(data):
    area = Area()

    try: area.id = data.METDIVFP #id for Metropolitan Divisions
    except:
        try: area.id = data.NCTADVFP #id for NECTA Divisions
        except: area.id = data.GEOID #id for other

    area.name = data.NAME
    area.lsad_name = data.NAMELSAD
    area.lsad = data.LSAD
    area.latitude = data.INTPTLAT
    area.longitude = data.INTPTLON

    area.parent = None
    area.combined_area = None


    if partialdb.skip_area(area): return


    #Get Parent Area if it exists
    try: parent_id = int(data.CBSAFP) #parent for metropolitan divisions
    except:
        try: parent_id = int(data.NECTAFP) #parent for NECTA divisions
        except: parent_id = None


    if parent_id is not None and parent_id != area.id:
        #if building a partial database then the parent may not exist
        try:    area.parent = Area.objects.get(id=parent_id)
        except:
            if partialdb.status() == False:
                print('Could not find parent of area ' + area.name)
            else:
                return


    #Get Combined Area if it exists
    try: combined_area_id = int(data.CSAFP) #combined area for metropolitan divisions
    except:
        try: combined_area_id = int(data.CNECTAFP) #combined area for NECTA divisions
        except: combined_area_id = None

    if combined_area_id is not None:
        area.combined_area = CombinedArea.objects.get(id=combined_area_id)

    area.save()


def create_regions_and_divisons():
    north_east = Region(id=1,name='Northeast')
    north_east.save()

    mid_west = Region(id=2,name='Midwest')
    mid_west.save()

    south = Region(id=3,name='South')
    south.save()

    west = Region(id=4,name='West')
    west.save()

    territory = Region(id=9,name='Territory')
    territory.save()

    territory_div = Division(id=0,name='Territory',region=territory)
    territory_div.save()

    new_england = Division(id=1,name='New England',region=north_east)
    new_england.save()

    mid_atlantic = Division(id=2,name='Mid-Atlantic',region=north_east)
    mid_atlantic.save()

    east_north_central = Division(id=3,name='East North Central',region=mid_west)
    east_north_central.save()

    west_north_central = Division(id=4,name='West North Central',region=mid_west)
    west_north_central.save()

    south_atlantic = Division(id=5,name='South Atlantic',region=south)
    south_atlantic.save()

    east_south_central = Division(id=6,name='East South Central',region=south)
    east_south_central.save()

    west_south_central = Division(id=7,name='West South Central',region=south)
    west_south_central.save()

    mountain = Division(id=8,name='Mountain',region=west)
    mountain.save()

    pacific = Division(id=9,name='Pacific',region=west)
    pacific.save()


def main(year,raw_data_path):
    Location.objects.all().delete()

    directories = ['STATE','CSA','CNECTA','CBSA','NECTA','METDIV','NECTADIV']

    data_frames = {}
    print('Getting geo data')
    for directory in directories:
        data_frames[directory] = get_data(directory, year, raw_data_path)

    print('Building Regions and Divisions')
    create_regions_and_divisons()

    #for key,value in data_frames.items():
    for key in directories:
        print('Building data from geo directory ' + key)

        value = data_frames[key]
        for row in value.itertuples():
            if key == 'STATE':
                create_state(row)

            elif key in ['CSA','CNECTA']:
                create_combined_area(row)

            elif key in ['CBSA','NECTA','METDIV','NECTADIV']:
                create_area(row)

            # if key == 'METDIV':         create_area_div(row)
            # if key == 'NECTADIV':       create_necta_div(row)



#stuff
