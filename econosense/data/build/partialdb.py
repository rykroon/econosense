#add partial database logic in here
#Keep it in here to separate it from other logic

#Heroku only allows up to 10,000 rows of data for the free database tier
#limit how much data gets added if in Staging Environment
class PartialDatabase():

    def __init__(self):
        try:
            PARTIAL_DATABASE = os.environ['PARTIAL_DATABASE']
        except:
            PARTIAL_DATABASE = False


    def skip_job(job):
        if self.PARTIAL_DATABASE:
            str_id = str(job.id)

            #do not add jobs where the third digit from the left is greater than one
            if int(str_id[2]) > 1 or job.id >= 300000:
                return True

        return False


    def skip_state(state):
        if self.PARTIAL_DATABASE:
            if state.region.id in [2,4]:
                return True

        return False


    def skip_area(area):
        if self.PARTIAL_DATABASE:
            str_id = str(area.id)

            #do not add areas where the second digit from the left is greater than zero
            if int(str_id[1]) > 0:
                return True

        return False
