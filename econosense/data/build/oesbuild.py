import os
import sys
#import urllib.request
import requests
import zipfile
import pandas as pd
from data.build.partialdb import PartialDatabase
from datetime import datetime


#Set up Django Environment
import django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "econosense.settings")
django.setup()

from django.db.models import Max
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

        if file_path.endswith('_dl.xlsx'):
            frame_name = file[:file.index('_')]
            df = pd.read_excel(file_path)
            data_frames[frame_name] = df
            df.to_csv(os.path.join(working_directory,frame_name + '.csv'),index=False)
            os.remove(file_path)

        elif file_path.endswith('.csv'):
            print('Loading data from ' + working_directory)
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

    if parent is not None:
        job.parent_id = occ_code_to_int(parent)

    if partialdb.skip_job(job): return

    job.save()


def occ_code_to_int(occ_code):
    return int(occ_code[:2] + occ_code[3:])



def create_job_location(data):
    job_loc = JobLocation()

    job_loc.job_id = occ_code_to_int(data.OCC_CODE)
    job_loc.location_id = data.AREA

    job_loc.employed = clean_data(data.TOT_EMP)
    job_loc.jobs_1000 = clean_data(data.JOBS_1000)
    job_loc.average = clean_data(data.A_MEAN)
    job_loc.median = clean_data(data.A_MEDIAN)
    job_loc.pct_10 = clean_data(data.A_PCT10)
    job_loc.pct_25 = clean_data(data.A_PCT25)
    job_loc.pct_75 = clean_data(data.A_PCT75)
    job_loc.pct_90 = clean_data(data.A_PCT90)

    if partialdb.skip_job_location(job_loc):
        return None

    return job_loc



def clean_data(data):
    if data in ['*','**']: return -1
    elif data == '#': return 999999.99
    else: return data


def main(year,raw_data_path):
    Job.objects.all().delete()
    JobLocation.objects.all().delete()

    tables = ['National','State','Metropolitan']

    data = {}

    print('Getting OES data')
    for table in tables:
        data[table] = get_data(table, year, raw_data_path)


    print('\n')
    print('Building jobs')
    parents = {}

    for row in data['National']['national'].itertuples():
        if row.OCC_CODE != '00-0000':
            parents[row.OCC_GROUP] = row.OCC_CODE
            create_job(row,parents)

    print(str(len(partialdb.skipped_jobs)) + ' jobs were skipped.')

    print('\n')

    def df_to_db(df):

        job_loc_list = list()

        max = JobLocation.objects.all().aggregate(Max('id'))
        max = max['id__max']

        if max is None: pk = 0
        else: pk = max

        for row in df.itertuples():
            if row.OCC_CODE != '00-0000':

                job_location = create_job_location(row)

                if job_location is not None:
                    pk += 1
                    job_location.id = pk
                    job_loc_list.append(job_location)


                batch_size = 20000
                if len(job_loc_list) >= batch_size:
                    print("Inserting batch of " + str(batch_size) + " records")
                    JobLocation.objects.bulk_create(job_loc_list)
                    job_loc_list.clear()

        print("Inserting batch of " + str(len(job_loc_list)) + " records")
        JobLocation.objects.bulk_create(job_loc_list)


    print('Building job locations by state')
    df_to_db(data['State']['state'])

    print('Building job locations by Metropolitan Area')
    df_to_db(data['Metropolitan']['MSA'])

    print('Building job locations by Metropolitan Area 2')
    df_to_db(data['Metropolitan']['aMSA'])
