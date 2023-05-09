from socrata.authorization import Authorization
from socrata import Socrata
from azure.storage.blob import BlobServiceClient
import os
import sys

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
  sys.exit(0 if job.attributes['status'] == 'successful' else 1)

# Upload the processed file back to Azure Blob Storage
with open('SiteAnalytics_AssetAccess_test.csv', 'rb') as data:
    blob_client.upload_blob(data, overwrite=True)
