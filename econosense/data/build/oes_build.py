import os
import sys
import urllib.request
import zipfile
import pandas as pd

#Set up Django Environment
import django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobproject.settings")
django.setup()

from appdata.models import Job,JobLocation,Area,State,Location


def get_data(table,year,raw_data_path):
    base_url = 'https://www.bls.gov/oes/special.requests'

    #Create Working Directory if it doesn't exist.
    if not os.path.isdir(os.path.join(raw_data_path,year)):
        os.mkdir(os.path.join(raw_data_path,year))

    working_directory = os.path.join(raw_data_path,year)

    file_name = 'oesm' + year[-2:]

    if table == 'National': file_name += 'nat'
    if table == 'State': file_name += 'st'
    if table == 'Metropolitan': file_name += 'ma'

    #Download and Unzip file if doesnt already exist
    if not os.path.isdir(os.path.join(working_directory,file_name)):

        file_name += '.zip'

        download_url = os.path.join(base_url,file_name)
        zip_file_path = os.path.join(working_directory,file_name)

        #Download
        urllib.request.urlretrieve(download_url,zip_file_path)

        #Extract Zip File
        zip_ref = zipfile.ZipFile(zip_file_path, 'r')
        zip_ref.extractall(working_directory)
        zip_ref.close()

        os.remove(zip_file_path)
        file_name = file_name[:-4]

    working_directory = os.path.join(working_directory,file_name)

    files = os.listdir(working_directory)

    data_frames = {}

    for file in files:
        file_path = os.path.join(working_directory,file)

        if file_path[-8:] == '_dl.xlsx':
            frame_name = file[:file.index('_')]
            df = pd.read_excel(file_path)
            data_frames[frame_name] = df
            df.to_csv(os.path.join(working_directory,frame_name + '.csv'),index=False)
            os.remove(file_path)

        elif file_path[-4:] == '.csv':
            frame_name = file[:file.index('.')]
            df = pd.read_csv(file_path)
            data_frames[frame_name] = df

    return data_frames


def create_job(data,parents):
    job = Job()
    job.id = occ_code_to_int(data.OCC_CODE)
    job.title = data.OCC_TITLE
    job.group = data.OCC_GROUP

    parent = None
    if data.OCC_GROUP == 'minor': parent = parents['major']
    if data.OCC_GROUP == 'broad': parent = parents['minor']
    if data.OCC_GROUP == 'detailed': parent = parents['broad']

    if parent is None: job.parent = None
    else: job.parent = Job.objects.get(id=occ_code_to_int(parent))

    job.save()

def occ_code_to_int(occ_code):
    return int(occ_code[:2] + occ_code[3:])


#def create_job_location(data,location_type):
def create_job_location(data):
    job_loc = JobLocation()
    job_loc.job = Job.objects.get(id=occ_code_to_int(data.OCC_CODE))
    #if location_type == 'state': job_loc.state = State.objects.get(id=data.AREA)
    #if location_type == 'area': job_loc.area = Area.objects.get(id=data.AREA)
    job_loc.location = Location.objects.get(id=data.AREA)

    job_loc.employed = clean_data(data.TOT_EMP)
    job_loc.jobs_1000 = clean_data(data.JOBS_1000)
    job_loc.average = clean_data(data.A_MEAN)
    job_loc.median = clean_data(data.A_MEDIAN)
    job_loc.pct_10 = clean_data(data.A_PCT10)
    job_loc.pct_25 = clean_data(data.A_PCT25)
    job_loc.pct_75 = clean_data(data.A_PCT75)
    job_loc.pct_90 = clean_data(data.A_PCT90)

    job_loc.save()

def create_job_location_fast(data):
    if data.OCC_CODE != "00-0000":
        create_job_location(data)
        # if data.AREA > 100:
        #     #if str(data.AREA)[-1:] != '4': #Do not include Divisions
        #     create_job_location(data,'area')
        # else:
        #     create_job_location(data,'state')

    return None


def clean_data(data):
    if data in ['*','**']: return -1
    elif data == '#': return 999999.99
    else: return data


def main(year,raw_data_path):
    tables = ['National','State','Metropolitan']
    #raw_data_path = 'oes/rawData'

    data = {}

    for table in tables:
        data[table] = get_data(table, year, raw_data_path)

    parents = {}
    for row in data['National']['national'].itertuples():
        if row.OCC_CODE != '00-0000':
            parents[row.OCC_GROUP] = row.OCC_CODE
            create_job(row,parents)


    for row in data['State']['state'].itertuples():
        if row.OCC_CODE != '00-0000':
            # create_job_location(row,'state')
            create_job_location(row)

    df =  data['Metropolitan']['MSA']
    df.apply(create_job_location_fast,axis=1)

    df =  data['Metropolitan']['aMSA']
    df.apply(create_job_location_fast,axis=1)

# ^^^ Took over an hour to process, might need to just use pd.to_sql()
#Disgregard the above ^^^








#stuff