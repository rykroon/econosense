import os
import sys
#import urllib.request
import requests
import zipfile
import pandas as pd
from data.build.partialdb import PartialDatabase


#Set up Django Environment
import django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "econosense.settings")
django.setup()

from data.models import Job,JobLocation,Area,State,Location

partialdb = PartialDatabase()

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

        print('Downloading data from ' + download_url)

        #Download
        response = requests.get(download_url)
        with open(zip_file_path,'wb') as f:
            f.write(response.content)

        #Extract Zip File
        zip_ref = zipfile.ZipFile(zip_file_path, 'r')
        zip_ref.extractall(working_directory)
        zip_ref.close()

        os.remove(zip_file_path)
        file_name = file_name[:-4]

    working_directory = os.path.join(working_directory,file_name)

    files_in_working_directory = os.listdir(working_directory)

    data_frames = {}

    for file in files_in_working_directory:
        file_path = os.path.join(working_directory,file)

        #if file_path[-8:] == '_dl.xlsx':
        if file_path.endswith('_dl.xlsx'):
            frame_name = file[:file.index('_')]
            df = pd.read_excel(file_path)
            data_frames[frame_name] = df
            df.to_csv(os.path.join(working_directory,frame_name + '.csv'),index=False)
            os.remove(file_path)


        #elif file_path[-4:] == '.csv':
        elif file_path.endswith('.csv'):
            frame_name = file[:file.index('.')]
            df = pd.read_csv(file_path)
            data_frames[frame_name] = df

    return data_frames


def create_job(data,parents):
    job = Job()
    job.id = occ_code_to_int(data.OCC_CODE)


    if partialdb.skip_job(job): return


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


#Created this because of 10,000 row limit in Heroku Postgres Free Tier
# def skip_job(job):
#     if PARTIAL_DATABASE:
#         str_id = str(job.id)
#
#         #do not add jobs where the third digit from the left is greater than one
#         if int(str_id[2]) > 1 or job.id >= 300000:
#             return True
#
#     return False



#def create_job_location(data,location_type):
def create_job_location(data):
    job_loc = JobLocation()

    #If only building a partial database then sometimes the job_id might not exist
    try: job_loc.job = Job.objects.get(id=occ_code_to_int(data.OCC_CODE))
    except: return

    #If only building a partial database then sometimes the location_id might not exist
    try: job_loc.location = Location.objects.get(id=data.AREA)
    except: return

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
    Job.objects.all().delete()
    JobLocation.objects.all().delete()

    tables = ['National','State','Metropolitan']
    #raw_data_path = 'oes/rawData'

    data = {}

    print('Getting OES data')
    for table in tables:
        data[table] = get_data(table, year, raw_data_path)

    parents = {}
    print('Building jobs')
    for row in data['National']['national'].itertuples():
        if row.OCC_CODE != '00-0000':
            parents[row.OCC_GROUP] = row.OCC_CODE
            create_job(row,parents)

    print('Building job locations by state')
    for row in data['State']['state'].itertuples():
        if row.OCC_CODE != '00-0000':
            # create_job_location(row,'state')
            create_job_location(row)

    print('Building job locations by Metropolitan Area')
    df =  data['Metropolitan']['MSA']
    df.apply(create_job_location_fast,axis=1)

    df =  data['Metropolitan']['aMSA']
    df.apply(create_job_location_fast,axis=1)

# ^^^ Took over an hour to process, might need to just use pd.to_sql()
#Disgregard the above ^^^








#stuff
