from socrata.authorization import Authorization
from socrata import Socrata
import os
import sys
import json
import requests
from azure.storage.blob import BlobServiceClient

auth = Authorization(
    'data.wa.gov',
    os.environ['MY_SOCRATA_USERNAME'],
    os.environ['MY_SOCRATA_PASSWORD']
)

socrata = Socrata(auth)
view = socrata.views.lookup('43g5-5aa3')

# These are the fields you want to update
dataset_name = 'Metric3_05-28-2023_2b21'
metadata = {'name': dataset_name}
action_type = 'update'
permission = 'private'

revision_json = json.dumps({
    'metadata': metadata,
    'action': {
        'type': action_type,
        'permission': permission
    }
})

# Connection string for Azure Blob Storage
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

# Blob container name
container_name = os.getenv('CONTAINER_NAME')

# Blob file name
blob_name = 'Metric3.csv'

# Create a BlobServiceClient instance
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

# Get the BlobClient for the file
blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

# Download the file locally
local_file_name = 'GAUserAndDevice.csv'
with open(local_file_name, 'wb') as file:
    file.write(blob_client.download_blob().readall())

with open(local_file_name, 'rb') as my_file:
    # Here, we're adding the revision_json to the .csv() method call
    (revision, job) = socrata.using_config(dataset_name, view).csv(my_file, revision_json)

    job = job.wait_for_finish(progress=lambda job: print('Job progress:', job.attributes['status']))

    # Check if the job was successful
    if job.attributes['status'] != 'successful':
        sys.exit(1)

# Remove the local file
os.remove(local_file_name)

# This is the full path to the metadata API on the domain that you care about
url = 'https://data.wa.gov/api/views/metadata/v1'

# This is the unique identifier of the dataset you care about
uid = '43g5-5aa3'

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
