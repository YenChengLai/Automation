from azure.storage.blob import BlobServiceClient
import os
import requests
import json

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

# Get the URL of the blob
blob_url = blob_client.url

# Print the blob URL (for verification)
print("Blob URL:", blob_url)

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

# Fetch the blob file
response = requests.get(blob_url)

# Check if the request was successful
if response.status_code == 200:
    # Download the file locally
    local_file_name = 'Metric3.csv'
    with open(local_file_name, 'wb') as file:
        file.write(response.content)

    with open(local_file_name, 'rb') as my_file:
        # Here, you can perform your desired actions with the file
        # For example, you can update the metadata using the Socrata library
        from socrata.authorization import Authorization
        from socrata import Socrata

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

        (revision, job) = socrata.using_config(dataset_name, view).csv(my_file, revision_json)

        job = job.wait_for_finish(progress=lambda job: print('Job progress:', job.attributes['status']))

        # Check if the job was successful
        if job.attributes['status'] != 'successful':
            sys.exit(1)

    # Remove the local file
    os.remove(local_file_name)

    # Update the metadata
    response = requests.patch('{}/{}'.format(url, uid),
                              auth=(username, password),
                              headers=headers,
                              data=json.dumps(data))

    print(response.json())
else:
    print("Failed to fetch the blob file:", response.status_code)
