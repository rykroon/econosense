import os
import sys
import urllib.request
import requests
import zipfile
from simpledbf import Dbf5
import pandas as pd

#Set up Django Environment
import django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "econosense.settings")
django.setup()

from data.models import Location,Region,Division,State,CombinedArea,Area


#Heroku only allows up to 10,000 rows of data for the free database tier
#limit how much data gets added if in Staging Environment
try:
    PARTIAL_DATABASE = os.environ['PARTIAL_DATABASE']
except:
    PARTIAL_DATABASE = False


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
        return pd.read_csv(os.path.join(working_directory,file_name))

    file_name = file_name[:-4] + '.zip'

    download_url = os.path.join(base_url, directory, file_name)
    zip_file_path = os.path.join(working_directory,file_name)

    #Download
    # !! use requests library instead !!
    urllib.request.urlretrieve(download_url,zip_file_path)

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

    if skip_state(state): return

    state.save()


#Created this because of 10,000 row limit in Heroku Postgres Free Tier
def skip_state(state):
    if PARTIAL_DATABASE:
        if state.region.id in [2,4]:
            return True

    return False


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

    try: area.id = data.METDIVFP
    except:
        try: area.id = data.NCTADVFP
        except: area.id = data.GEOID

    if skip_area(area): return

    area.name = data.NAME
    area.lsad_name = data.NAMELSAD
    area.lsad = data.LSAD
    area.latitude = data.INTPTLAT
    area.longitude = data.INTPTLON

    area.parent = None
    area.combined_area = None


    #Get Parent Area if it exists
    try: parent_id = int(data.CBSAFP)
    except:
        try: parent_id = int(data.NECTAFP)
        except: parent_id = None


    if parent_id is not None and parent_id != area.id:
        #if building a partial database then the parent may not exist
        try: area.parent = Area.objects.get(id=parent_id)
        except: return


    #Get Combined Area if it exists
    try: combined_area_id = int(data.CSAFP)
    except:
        try: combined_area_id = int(data.CNECTAFP)
        except: combined_area_id = None

    if combined_area_id is not None:
        area.combined_area = CombinedArea.objects.get(id=combined_area_id)

    area.save()


#Created this because of 10,000 row limit in Heroku Postgres Free Tier
def skip_area(area):
    if PARTIAL_DATABASE:
        str_id = str(area.id)

        #do not add areas where the second digit from the left is greater than zero
        if int(str_id[1]) > 0:
            return True

    return False


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
