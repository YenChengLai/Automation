from socrata.authorization import Authorization
from socrata import Socrata
import os
import sys
import json
import requests

auth = Authorization(
  'data.wa.gov',
  os.environ['MY_SOCRATA_USERNAME'],
  os.environ['MY_SOCRATA_PASSWORD']
)

socrata = Socrata(auth)
view = socrata.views.lookup('hndz-vqe9')

# These are the fields you want to update
dataset_name = 'Asset_Type_by_AgencyV4_05-06-2023_a1a2'
metadata = { 'name': dataset_name }
action_type = 'update'
permission = 'private'

revision_json = json.dumps({ 
    'metadata': metadata, 
    'action': { 
        'type': action_type, 
        'permission': permission 
    } 
})

with open('Asset_Type_by_AgencyV4.csv', 'rb') as my_file:
  # Here, we're adding the revision_json to the .csv() method call
  (revision, job) = socrata.using_config('Asset_Type_by_AgencyV4_05-06-2023_a1a2', view).csv(my_file, revision_json)
  
  job = job.wait_for_finish(progress = lambda job: print('Job progress:', job.attributes['status']))
  
  # Check if the job was successful
  if job.attributes['status'] != 'successful':
    sys.exit(1)

# This is the full path to the metadata API on the domain that you care about
url = 'https://data.wa.gov/api/views/metadata/v1'

# This is the unique identifier of the dataset you care about
uid = 'hndz-vqe9'

# And this is your login information
username = os.environ['MY_SOCRATA_USERNAME']
password = os.environ['MY_SOCRATA_PASSWORD']

headers = {'Content-Type': 'application/json'}

# These are the fields you want to update
data = {'private': True}

response = requests.patch('{}/{}'.format(url, uid),
                          auth=(username, password),
                          headers=headers,
                          # the data has to be passed as a string
                          data=json.dumps(data))

print(response.json())
print(response.headers)