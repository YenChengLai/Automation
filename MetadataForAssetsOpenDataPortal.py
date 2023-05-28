import os
import sys
import json
import requests

# Socrata API credentials
username = os.environ['MY_SOCRATA_USERNAME']
password = os.environ['MY_SOCRATA_PASSWORD']

# Blob storage credentials
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
container_name = os.getenv('CONTAINER_NAME')
blob_name = 'Metric3.csv'

# Download the file locally
local_file_name = 'Metric3.csv'
blob_url = f"{connect_str}/{container_name}/{blob_name}"
response = requests.get(blob_url)
with open(local_file_name, 'wb') as file:
    file.write(response.content)

# This is the unique identifier of the dataset you want to update
uid = '43g5-5aa3'

# Construct the metadata update payload
metadata = {'name': 'Metric3_05-28-2023_2b21'}
action_type = 'update'
permission = 'private'
revision_json = json.dumps({
    'metadata': metadata,
    'action': {
        'type': action_type,
        'permission': permission
    }
})

# Upload the file and update the metadata
url = f'https://data.wa.gov/api/views/{uid}'
with open(local_file_name, 'rb') as file:
    files = {'file': (local_file_name, file)}
    response = requests.post(url, auth=(username, password), files=files, data={'revision': revision_json})

# Remove the local file
os.remove(local_file_name)

# Check the response
if response.status_code == 200:
    print('Metadata update successful')
else:
    print('Metadata update failed')
    sys.exit(1)
