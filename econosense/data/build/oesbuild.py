import os
import sys

#import requests
#import zipfile
#import pandas as pd

from datetime import datetime


#Set up Django Environment
import django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "econosense.settings")
django.setup()

from django.db.models import Max
from data.models import Job,JobLocation,Area,State,Location

from data.build.build import Build


class OesBuild(Build):

    def __init__(self,year):
        super().__init__(year)

        self.source = 'oes'
        self.download_path = os.path.join(self.download_path,self.source)
        self.create_dir(self.download_path)

        self.download_path = os.path.join(self.download_path,self.year)
        self.create_dir(self.download_path)

        self.base_url = 'https://www.bls.gov/oes/special.requests'

        self.jobs = None
        self.locations = None
        self.last_location = {'id':None,'geo_id':None}

    def get_data(self,table):

        working_directory = self.download_path

        file_name = 'oesm' + self.year[-2:]

        if table == 'National':     file_name += 'nat'
        if table == 'State':        file_name += 'st'
        if table == 'Metropolitan': file_name += 'ma'

        #If directory does not exist then download
        if not os.path.isdir(os.path.join(working_directory,file_name)):

            zip_file = file_name + '.zip'

            download_url = os.path.join(self.base_url,zip_file)
            zip_file_path = os.path.join(working_directory,zip_file)

            self.download(download_url,zip_file_path)
            self.unzip(zip_file_path,working_directory)
            os.remove(zip_file_path)

        working_directory = os.path.join(working_directory,file_name)

        files_in_working_directory = os.listdir(working_directory)

        data_frames = {}

        for file in files_in_working_directory:
            file_path = os.path.join(working_directory,file)


            if file_path.endswith('_dl.xlsx'):
                df = self.load_file(file_path)
                frame_name = file[:file.index('_')]
                data_frames[frame_name] = df

                export_path = os.path.join(working_directory,frame_name + '.csv')
                df.to_csv(export_path,index=False)
                os.remove(file_path)

            elif file_path.endswith('.csv'):
                frame_name = file[:-4]
                df = self.load_file(file_path)
                data_frames[frame_name] = df

        return data_frames


    #only include states, Metro Areas, Metro Divisions, NECTA Areas and NECTA Divisions
    def cache_locations(self):
        self.locations = list(
            Location.objects.filter(
            year=self.year).filter(
            lsad__in=['ST','M1','M3','M5','M7']
            ).values('id','geo_id'))

    def get_location_id_by_geo_id(self,geo_id):
        if self.last_location['geo_id'] == geo_id:
            return self.last_location['id']

        for loc in self.locations:
            if loc['geo_id'] == geo_id:
                self.last_location = loc
                return loc['id']


    def cache_jobs(self):
        self.jobs = list(Job.objects.filter(year=self.year).values('id','code'))

    def get_job_id_by_occ_code(self,occ_code):
        for job in self.jobs:
            if job['code'] == occ_code:
                return job['id']


    def create_job(self,data,parents):
        job = Job()
        job.code = self.occ_code_to_int(data.OCC_CODE)
        job.year = self.year

        job.title = data.OCC_TITLE
        job.group = data.OCC_GROUP

        if job.group == 'minor':       job.parent_id = parents['major']
        if job.group == 'broad':       job.parent_id = parents['minor']
        if job.group == 'detailed':    job.parent_id = parents['broad']

        if self.partialdb.skip_job(job): return

        job.save()
        return job


    def occ_code_to_int(self,occ_code):
        return int(occ_code[:2] + occ_code[3:])


    def create_job_location(self,data):
        job_loc = JobLocation()

        job_loc.year        = self.year
        occ_code            = self.occ_code_to_int(data.OCC_CODE)
        job_loc.job_id      = self.get_job_id_by_occ_code(occ_code)
        job_loc.location_id = self.get_location_id_by_geo_id(data.AREA)

        job_loc.employed    = self.clean_data(data.TOT_EMP)
        job_loc.jobs_1000   = self.clean_data(data.JOBS_1000)
        job_loc.average     = self.clean_data(data.A_MEAN)
        job_loc.median      = self.clean_data(data.A_MEDIAN)
        job_loc.pct_10      = self.clean_data(data.A_PCT10)
        job_loc.pct_25      = self.clean_data(data.A_PCT25)
        job_loc.pct_75      = self.clean_data(data.A_PCT75)
        job_loc.pct_90      = self.clean_data(data.A_PCT90)

        if self.partialdb.skip_job_location(job_loc):
            return None

        return job_loc



    def clean_data(self,data):
        if data in ['*','**']: return -1
        elif data == '#': return 999999.99
        else: return data


    def build(self):
        Job.objects.filter(year=self.year).delete()
        JobLocation.objects.filter(year=self.year).delete()

        tables = ['National','State','Metropolitan']

        data = dict()

        for table in tables:
            data[table] = self.get_data(table)


        print('\n')
        print('Building jobs')
        parents = dict()

        for row in data['National']['national'].itertuples():
            if row.OCC_CODE != '00-0000':
                job = self.create_job(row,parents)
                parents[job.group] = job.id

        print(str(len(self.partialdb.skipped_jobs)) + ' jobs were skipped.')

        print('\n')

        self.cache_jobs()
        self.cache_locations()

        def df_to_db(df,batch_size):

            job_loc_list = list()

            #max = JobLocation.objects.all().aggregate(Max('id'))
            #max = max['id__max']

            #if max is None: pk = 0
            #else: pk = max

            for row in df.itertuples():
                if row.OCC_CODE != '00-0000':

                    job_location = self.create_job_location(row)

                    if job_location is not None:
                        #pk += 1
                        #job_location.id = pk
                        job_loc_list.append(job_location)


                    #batch_size = 20000
                    if len(job_loc_list) >= batch_size:
                        print("Inserting batch of " + str(batch_size) + " records")
                        JobLocation.objects.bulk_create(job_loc_list)
                        job_loc_list.clear()

            print("Inserting batch of " + str(len(job_loc_list)) + " records")
            JobLocation.objects.bulk_create(job_loc_list)



        def create_job_states():
            print('Building job locations by state')
            df_to_db(data['State']['state'],15000)

        self.time_it(create_job_states)

        def create_job_metros():
            print('Building job locations by Metropolitan Area')
            df_to_db(data['Metropolitan']['MSA'],25000)

            #print('Building job locations by Metropolitan Area 2')
            df_to_db(data['Metropolitan']['aMSA'],10000)

        self.time_it(create_job_metros)
