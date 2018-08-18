#add partial database logic in here
#Keep it in here to separate it from other logic

#Heroku only allows up to 10,000 rows of data for the free database tier
#limit how much data gets added if in Staging Environment
import os
import sys

import django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "econosense.settings")
django.setup()

from data.models import Job, Location


class PartialDatabase():
    PARTIAL_DATABASE = None

    def __init__(self):
        try:
            self.PARTIAL_DATABASE = os.environ['PARTIAL_DATABASE'] == 'True'
        except:
            self.PARTIAL_DATABASE = False

        #self.jobs = None
        self.locations = None

        if self.PARTIAL_DATABASE:
            #self.jobs = list(Job.jobs.values_list('id',flat=True))
            self.locations = list(Location.locations.values_list('id',flat=True))

        self.skip_count = 0
        self.skipped_locations = list()
        self.skipped_jobs = list()

    def status(self):
        return self.PARTIAL_DATABASE


    def skip_job(self,job):
        if self.PARTIAL_DATABASE:
            job_id = str(job.code)

            #do not add jobs where the third digit from the left is greater than one
            if int(job_id[2]) > 1 or job.code >= 300000:
                self.skip_count += 1
                self.skipped_jobs.append(job.code)
                return True

        return False


    def skip_state(self,state):
        if self.PARTIAL_DATABASE:
            #only keep mid-atlantic states and puerto rico
            if state.division.geo_id not in [2] and state.initials != 'PR':
                self.skipped_locations.append(state.id)
                return True

        return False


    def skip_area(self,area):
        if self.PARTIAL_DATABASE:
            if area.lsad not in ['M1','M3','M7'] or area.primary_state_id in self.skipped_locations:
                self.skipped_locations.append(area.id)
                return True

        return False

    def skip_job_location(self,job_loc):
        if self.PARTIAL_DATABASE:

            if job_loc.job_id == None:
                return True

            if job_loc.location_id == None:
                return True

        return False


    def skip_rent(self,rent):
        if self.PARTIAL_DATABASE:
            if rent.location_id == None:
                return True


        return False
