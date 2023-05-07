from socrata.authorization import Authorization
from socrata import Socrata
import os
import sys

auth = Authorization(
  'data.wa.gov',
  os.environ['MY_SOCRATA_USERNAME'],
  os.environ['MY_SOCRATA_PASSWORD']
)

socrata = Socrata(auth)
view = socrata.views.lookup('hndz-vqe9')

with open('Asset_Type_by_AgencyV4.csv', 'rb') as my_file:
  (revision, job) = socrata.using_config('Asset_Type_by_AgencyV4_05-06-2023_a1a2', view).csv(my_file)
  # These next 2 lines are optional - once the job is started from the previous line, the
  # script can exit; these next lines just block until the job completes
  job = job.wait_for_finish(progress = lambda job: print('Job progress:', job.attributes['status']))
  sys.exit(0 if job.attributes['status'] == 'successful' else 1)