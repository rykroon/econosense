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


    def skip_job(self,job):
        if self.PARTIAL_DATABASE:
            job_id = str(job.id)

            #do not add jobs where the third digit from the left is greater than one
            if int(job_id[2]) > 1 or job.id >= 300000:
                return True

        return False


    def skip_state(self,state):
        if self.PARTIAL_DATABASE:
            if state.region.id in [2,4]:
                return True

        return False


    def skip_area(self,area):
        if self.PARTIAL_DATABASE:
            area_id = str(area.id)

            #do not add areas where the second digit from the left is greater than zero
            if int(area_id[1]) > 0:
                return True

        return False
