#add partial database logic in here
#Keep it in here to separate it from other logic

#Heroku only allows up to 10,000 rows of data for the free database tier
#limit how much data gets added if in Staging Environment
import os

class PartialDatabase():
    PARTIAL_DATABASE = None

    def __init__(self):
        try:
            self.PARTIAL_DATABASE = os.environ['PARTIAL_DATABASE'] == 'True'
        except:
            self.PARTIAL_DATABASE = False

        self.skip_count = 0
        self.skipped_locations = list()
        self.skipped_jobs = list()

    def status(self):
        return self.PARTIAL_DATABASE


    def skip_job(self,job):
        if self.PARTIAL_DATABASE:
            job_id = str(job.id)

            #do not add jobs where the third digit from the left is greater than one
            if int(job_id[2]) > 1 or job.id >= 300000:
                self.skip_count += 1
                self.skipped_jobs.append(job.id)
                return True

        return False


    def skip_state(self,state):
        if self.PARTIAL_DATABASE:
            if state.division.id not in [1,2,5]: #only keep east coast states
                self.skipped_locations.append(state.id)
                return True

        return False


    def skip_area(self,area):
        if self.PARTIAL_DATABASE:
            #do not include areas w/o a combined area
            # if area.combined_area_id is None:
            #     self.skipped_locations.append(area.id)
            #     return True

            if area.parent_id is None:
                self.skipped_locations.append(area.id)
                return True


            #do not include Micropolitan areas
            if area.lsad in ['M2','M6']:
                self.skipped_locations.append(area.id)
                return True

        return False

    def skip_job_location(self,job_loc):
        if self.PARTIAL_DATABASE:
            if job_loc.job_id in self.skipped_jobs:
                return True

            if job_loc.location_id in self.skipped_locations:
                return True
        else:
            return False


    def skip_rent(self,rent):
        if self.PARTIAL_DATABASE:
            if rent.location_id in self.skipped_locations:
                return True
        else:
            return False
