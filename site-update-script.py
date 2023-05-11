from socrata.authorization import Authorization
from socrata import Socrata
from azure.storage.blob import BlobServiceClient
import os
import sys
import json
import requests

# Azure Blob Storage details
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
container_name = 'siteanalysis'
blob_name = 'SiteAnalytics_AssetAccess_test.csv'

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
blob_client = blob_service_client.get_blob_client(container_name, blob_name)

# Download the blob to a local file
with open('SiteAnalytics_AssetAccess_test.csv', 'wb') as download_file:
    download_file.write(blob_client.download_blob().readall())

# Socrata processing
auth = Authorization(
  'data.wa.gov',
  os.environ['MY_SOCRATA_USERNAME'],
  os.environ['MY_SOCRATA_PASSWORD']
)
socrata = Socrata(auth)
view = socrata.views.lookup('y56a-jizm')

with open('SiteAnalytics_AssetAccess_test.csv', 'rb') as my_file:
  (revision, job) = socrata.using_config('SiteAnalytics_AssetAccess_test_05-09-2023_c502', view).csv(my_file)
  job = job.wait_for_finish(progress = lambda job: print('Job progress:', job.attributes['status']))
  # Check if the job was successful
  if job.attributes['status'] != 'successful':
    sys.exit(1)

# Upload the processed file back to Azure Blob Storage
with open('SiteAnalytics_AssetAccess_test.csv', 'rb') as data:
    blob_client.upload_blob(data, overwrite=True)
  
# This is the full path to the metadata API on the domain that you care about
url = 'https://data.wa.gov/api/views/metadata/v1'

# This is the unique identifier of the dataset you care about
uid = 'y56a-jizm'

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
