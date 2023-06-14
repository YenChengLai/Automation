import numpy as np
import pandas as pd
import os
from azure.storage.blob import BlobServiceClient

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange
from google.analytics.data_v1beta.types import Dimension
from google.analytics.data_v1beta.types import Metric
from google.analytics.data_v1beta.types import RunReportRequest
from google.analytics.data_v1beta.types import OrderBy

## Set up global variables
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
container_name = os.getenv('CONTAINER_NAME')  # The container where your credentials file is stored

# Create a blob client for your credentials file
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
credentials_blob_client = blob_service_client.get_blob_client(container_name, 'waopendata_api_access_key.json')

# Download the credentials file to a temporary file
with tempfile.NamedTemporaryFile(delete=False) as temp:
    data = credentials_blob_client.download_blob().readall()
    temp.write(data)
    credentials_file_path = temp.name

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file_path
PROPERTY_ID = '331807331'

client = BetaAnalyticsDataClient()

## Format Report - run_report method
def format_report(request):
    response = client.run_report(request)
    
    # Row index
    row_index_names = [header.name for header in response.dimension_headers]
    row_header = []
    for i in range(len(row_index_names)):
        row_header.append([row.dimension_values[i].value for row in response.rows])

    row_index_named = pd.MultiIndex.from_arrays(np.array(row_header), names = np.array(row_index_names))
    # Row flat data
    metric_names = [header.name for header in response.metric_headers]
    data_values = []
    for i in range(len(metric_names)):
        data_values.append([row.metric_values[i].value for row in response.rows])

    output = pd.DataFrame(data = np.transpose(np.array(data_values, dtype = 'f')), 
                          index = row_index_named, columns = metric_names)
    return output


request = RunReportRequest(
        property='properties/'+PROPERTY_ID,
        dimensions=[Dimension(name="month"),
                    Dimension(name="deviceCategory"),
                    Dimension(name="newVsReturning")],
        metrics=[Metric(name="newUsers"),
                 Metric(name="activeUsers"),
                 Metric(name="totalUsers"),
                 Metric(name="userEngagementDuration")],
        order_bys = [OrderBy(dimension = {'dimension_name': 'month'}),
                    OrderBy(dimension = {'dimension_name': 'deviceCategory'}),
                    OrderBy(dimension = {'dimension_name': 'newVsReturning'})],
        date_ranges=[DateRange(start_date="2023-04-01", end_date="today")],
    )

output_df = format_report(request)
output_csv_filename = 'GAUserAndDevice.csv'
output_df.to_csv(output_csv_filename)

# Upload the output CSV file to Azure Blob Storage
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

# Create a blob client using the output CSV file name as the name for the blob
blob_client = blob_service_client.get_blob_client(container_name, output_csv_filename)

# Upload the output CSV file
with open(output_csv_filename, "rb") as data:
    blob_client.upload_blob(data, overwrite=True)

# Remove the local output CSV file
os.remove(output_csv_filename)

# Remove the temporary credentials file
os.remove(credentials_file_path)
