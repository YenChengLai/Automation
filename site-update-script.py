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
view = socrata.views.lookup('r766-qgkx')

with open('SiteAnalytics_AssetAccess_test.csv', 'rb') as my_file:
  (revision, job) = socrata.using_config('SiteAnalytics_AssetAccess_test_05-08-2023_e059', view).csv(my_file)
  # These next 2 lines are optional - once the job is started from the previous line, the
  # script can exit; these next lines just block until the job completes
  job = job.wait_for_finish(progress = lambda job: print('Job progress:', job.attributes['status']))
  sys.exit(0 if job.attributes['status'] == 'successful' else 1)