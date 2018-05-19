#add partial database logic in here
#Keep it in here to separate it from other logic

#Heroku only allows up to 10,000 rows of data for the free database tier
#limit how much data gets added if in Staging Environment
import os

class PartialDatabase():
    PARTIAL_DATABASE = None

    def __init__(self):
        try:
            self.PARTIAL_DATABASE = os.environ['PARTIAL_DATABASE']
        except:
            self.PARTIAL_DATABASE = False

        self.skip_count = 0

    def status(self):
        return self.PARTIAL_DATABASE


    def skip_job(self,job):
        if self.PARTIAL_DATABASE:
            job_id = str(job.id)

            #do not add jobs where the third digit from the left is greater than one
            if int(job_id[2]) > 1 or job.id >= 300000:
                self.skip_count += 1
                return True

        return False


    def skip_state(self,state):
        if self.PARTIAL_DATABASE:
            if state.division.id not in [1,2,5]: #only keep east coast states
                self.skip_count += 1
                return True

        return False


    def skip_area(self,area):
        if self.PARTIAL_DATABASE:
            area_id = str(area.id)

            #do not add areas where the second digit from the left is greater than zero
            if int(area_id[1]) > 0:
                self.skip_count += 1
                return True

            #do not include Micropolitan areas
            if area.lsad in ['M2','M6']:
                self.skip_count += 1
                return True

        return False
