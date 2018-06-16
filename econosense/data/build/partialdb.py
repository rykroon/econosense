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
# import django stuff
# instead of keeping a list of skipped jobs and skipped_locations...
# do a query to get the ids of available jobs and locations

class PartialDatabase():
    PARTIAL_DATABASE = None

    def __init__(self):
        try:
            self.PARTIAL_DATABASE = os.environ['PARTIAL_DATABASE'] == 'True'
        except:
            self.PARTIAL_DATABASE = False

        self.jobs = None
        self.locations = None

        if self.PARTIAL_DATABASE:
            self.jobs = list(Job.jobs.values_list('id',flat=True))
            self.locations = list(Location.locations.values_list('id',flat=True))

        self.skip_count = 0
        self.skipped_locations = list()
        self.skipped_jobs = list()

    def status(self):
        return self.PARTIAL_DATABASE


    def skip_job(self,job):
        if self.PARTIAL_DATABASE:
            job_id = str(job.occ_code)

            #do not add jobs where the third digit from the left is greater than one
            if int(job_id[2]) > 1 or job.occ_code >= 300000:
                self.skip_count += 1
                self.skipped_jobs.append(job.occ_code)
                return True

        return False


    def skip_state(self,state):
        if self.PARTIAL_DATABASE:
            if state.division.id not in [1,2,5]: #only keep east coast states
                self.skipped_locations.append(state.geo_id)
                return True

        return False


    def skip_area(self,area):
        if self.PARTIAL_DATABASE:
            if area.parent_id is None:
                self.skipped_locations.append(area.geo_id)
                return True

            #do not include Micropolitan areas
            if area.lsad in ['M2','M6']:
                self.skipped_locations.append(area.geo_id)
                return True

        return False

    def skip_job_location(self,job_loc):
        if self.PARTIAL_DATABASE:
            if job_loc.job_id not in self.jobs:
                return True

            if job_loc.location_id not in self.locations:
                return True

        return False


    def skip_rent(self,rent):
        if self.PARTIAL_DATABASE:
            if rent.location_id not in self.locations:
                return True


        return False
