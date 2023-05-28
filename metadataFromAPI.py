import os
import requests
import pandas as pd
from azure.storage.blob import BlobServiceClient

def columnMetadata(data):
    columns = ['id', 'name', 'ColumnName', 'ColumnDescription', 'DataType', 'DatasetURL', 'Last Update Date']
    df = pd.DataFrame(columns = columns)

    for i in range(len(data['results'])):
        result_dict = dict(data['results'][i])
        info = {
            'id': result_dict['resource']['id'],
            'name': result_dict['resource']['name'],
            'ColumnName': result_dict['resource']['columns_name'],
            'ColumnDescription': result_dict['resource']['columns_description'],
            'DataType': result_dict['resource']['columns_datatype'],
            'DatasetURL': result_dict['link'],
            'Last Update Date': result_dict['resource']['updatedAt']
        }
        
        df_new = pd.DataFrame(info)
        df = pd.concat([df, df_new])

    return df

def datasetMetadata(data):
    columns = ['id', 'name', 'description', 'attribution','attribution_link', 'contact_email',
                'updatedAt','createdAt','metadata_updated_at','data_updated_at', 'download_count',
                'publication_date', 'link','OwnerID','OwnerName']
    df = pd.DataFrame(columns = columns)

    for i in range(len(data['results'])):
        result_dict = dict(data['results'][i])
        info = {
            'id': result_dict['resource']['id'],
            'name': result_dict['resource']['name'],
            'description': result_dict['resource']['description'], 
            'attribution': result_dict['resource']['attribution'],
            'attribution_link': result_dict['resource']['attribution_link'], 
            'contact_email': result_dict['resource']['contact_email'],
            'updatedAt': result_dict['resource']['updatedAt'],
            'createdAt': result_dict['resource']['createdAt'],
            'metadata_updated_at': result_dict['resource']['metadata_updated_at'],
            'data_updated_at': result_dict['resource']['data_updated_at'],
            'download_count': result_dict['resource']['download_count'],
            'publication_date': result_dict['resource']['publication_date'], 
            'link': result_dict['link'],
            'OwnerID': result_dict['owner']['id'],
            'OwnerName': result_dict['owner']['display_name']
        }
    
        df_new = pd.DataFrame(info, index=[0])
        df = pd.concat([df, df_new])

    df = df.sort_values(by=['id'])
    df = df.reset_index(drop=True)

    return df

def pageViews(data): # diff url
    columns = ['id', 'name', 'type', 'page_views_last_week','page_views_last_month', 'page_views_total',
                'page_views_last_week_log','page_views_last_month_log','page_views_total_log']
    df = pd.DataFrame(columns = columns)

    for i in range(len(data['results'])):
        result_dict = dict(data['results'][i])
        info = {
            'id': result_dict['resource']['id'],
            'name': result_dict['resource']['name'],
            'type': result_dict['resource']['type'], 
            'page_views_last_week': result_dict['resource']['page_views']['page_views_last_week'],
            'page_views_last_month': result_dict['resource']['page_views']['page_views_last_month'], 
            'page_views_total': result_dict['resource']['page_views']['page_views_total'], 
            'page_views_last_week_log': result_dict['resource']['page_views']['page_views_last_week_log'],
            'page_views_last_month_log': result_dict['resource']['page_views']['page_views_last_month_log'],
            'page_views_total_log': result_dict['resource']['page_views']['page_views_total_log']
        }
        
        df_new = pd.DataFrame(info, index=[0])
        df = pd.concat([df, df_new])

    return df

def datasetMetadata_License(data):
    columns = ['id', 'license']
    df = pd.DataFrame(columns = columns)

    for i in range(len(data['results'])):
        result_dict = dict(data['results'][i])
        info = {
            'id': result_dict['resource']['id'],
            'license': result_dict['metadata'].get('license', "")
        }

        df_new = pd.DataFrame(info, index=[0])
        df = pd.concat([df, df_new])

    return df

def datasetMetadata_Temporal(data):
    columns = ['id', 'Notes_1.-', 'Notes_2.-', 'Notes_3.-','Temporal_Posting-Frequency', 'Temporal_Period-of-Time',
           'Notes_4.-','Notes_5.-','Notes_6.-','Identification_Originator',
           'Identification_Metadata-Language','Metadata_Data-Definition','Metadata_Data-Frequency',
           'Metadata_Data-Source','Metadata_Target-Rationale','Metadata_Level-of-Influence']

    df = pd.DataFrame(columns = columns)

    for i in range(len(data['results'])):
        result_dict = dict(data['results'][i])
        info = {}
        # extract the keys from the list of dictionaries and store them in a new dictionary 'd' using a loop
        for d in result_dict['classification']['domain_metadata']:
            info[d['key']] = d['value']
            
        result = {
            'id': result_dict['resource']['id'],
            'Notes_1.-': info.get('Notes_1.-', None),
            'Notes_2.-': info.get('Notes_2.-', None), 
            'Notes_3.-': info.get('Notes_3.-', None),
            'Temporal_Posting-Frequency': info.get('Temporal_Posting-Frequency', None),
            'Temporal_Period-of-Time': info.get('Temporal_Period-of-Time', None),
            'Notes_4.-': info.get('Notes_4.-', None),
            'Notes_5.-': info.get('Notes_5.-', None),
            'Identification_Originator': info.get('Identification_Originator', None),
            'Identification_Metadata-Language': info.get('Identification_Metadata-Language', None),
            'Metadata_Data-Definition': info.get('Metadata_Data-Definition', None),
            'Metadata_Data-Frequency': info.get('Metadata_Data-Frequency', None),
            'Metadata_Data-Source': info.get('Metadata_Data-Source', None),
            'Metadata_Target-Rationale': info.get('Metadata_Target-Rationale', None),
            'Metadata_Level-of-Influence': info.get('Metadata_Level-of-Influence', None),
        }
        
        df_new = pd.DataFrame(result, index=[0])
        df = pd.concat([df, df_new])
    
    df = df.sort_values(by=['id'])
    df = df.reset_index(drop=True)
    # dropna() method along with the `how` parameter set to 'all'. This will remove any row that contains all missing values (NaN or None).
    # exclude the first column from the dropna operation by specifying the subset parameter
    df = df.dropna(how='all', subset=df.columns[1:])

    return df

def datasetMetadata_Catstags(data):
    columns = ['id', 'categories', 'domain_category', 'domain_tags']
    df = pd.DataFrame(columns = columns)

    for i in range(len(data['results'])):
        result_dict = dict(data['results'][i])
        info = {
            'id': result_dict['resource']['id'],
            'categories': result_dict['classification'].get('categories', None),
            'domain_category': result_dict['classification'].get('domain_category', None), 
            'domain_tags': result_dict['classification'].get('domain_tags', None)
        }
        df_new = pd.DataFrame.from_dict(info, orient='index').transpose()
        df = pd.concat([df, df_new], ignore_index=True)

    return df

def assetParents(data): # diff url
    columns = ['asset_name', 'asset_id', 'asset_type', 'asset_link', 'asset_parent_id']

    df = pd.DataFrame(columns = columns)

    for i in range(len(data['results'])):
        result_dict = dict(data['results'][i])
        asset_parent_id = result_dict['resource']['parent_fxf']
        if isinstance(asset_parent_id, list) and len(asset_parent_id) > 0:
            # If asset_parent_id is a non-empty list, create a new row in the DataFrame for each element
            for parent_id in asset_parent_id:
                info = {
                    'asset_name': result_dict['resource']['name'],
                    'asset_id': result_dict['resource']['id'],
                    'asset_type': result_dict['resource']['type'], 
                    'asset_link': result_dict['link'],
                    'asset_parent_id': parent_id
                }
                df_new = pd.DataFrame(info, index=[0])
                df = pd.concat([df, df_new], ignore_index=True)
        else:
            # If asset_parent_id is an empty list or not a list, create a single row in the DataFrame
            info = {
                'asset_name': result_dict['resource']['name'],
                'asset_id': result_dict['resource']['id'],
                'asset_type': result_dict['resource']['type'], 
                'asset_link': result_dict['link'],
                'asset_parent_id': '' if not asset_parent_id else asset_parent_id[0]
            }
            df_new = pd.DataFrame(info, index=[0])
            df = pd.concat([df, df_new], ignore_index=True)

    return df

# entry point of the program
def main():
    url = "http://api.us.socrata.com/api/catalog/v1?only=datasets&domains=data.wa.gov&limit=9000"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
    else:
        raise Exception(f"Failed to retrieve data with status code: {response.status_code}")

    # only used by pageViews
    url2 = "http://api.us.socrata.com/api/catalog/v1?domains=data.wa.gov&limit=9000"
    response2 = requests.get(url2)
    
    if response2.status_code == 200:
        data2 = response2.json()
    else:
        print("Failed to retrieve data2")


    # each function will return a dataframe
    df_columnMetadata = columnMetadata(data)
    df_datasetMetadata = datasetMetadata(data)
    df_pageViews = pageViews(data2)
    df_datasetMetadata_License = datasetMetadata_License(data)
    df_datasetMetadata_Temporal = datasetMetadata_Temporal(data)
    df_datasetMetadata_Catstags = datasetMetadata_Catstags(data)
    df_assetParents = assetParents(data2)

    # using Pandas ExcelWriter function to combine every dataframe into one excel file
    with pd.ExcelWriter('MetadataFromAPI_py.xlsx', engine='xlsxwriter') as writer:
        df_columnMetadata.to_excel(writer, sheet_name='columnMetadata', index=False)
        df_datasetMetadata.to_excel(writer, sheet_name='datasetMetadata', index=False)
        df_pageViews.to_excel(writer, sheet_name='pageViews', index=False)
        df_datasetMetadata_License.to_excel(writer, sheet_name='datasetMetadata_License', index=False)
        df_datasetMetadata_Temporal.to_excel(writer, sheet_name='datasetMetadata_Temporal', index=False)
        df_datasetMetadata_Catstags.to_excel(writer, sheet_name='datasetMetadata_Catstags', index=False)
        df_assetParents.to_excel(writer, sheet_name='assetParents', index=False)
    
    # Now we want to upload this to Azure Blob Storage
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_name = os.getenv('CONTAINER_NAME')  # Get the container name from the environment variable
    
    # Choose a local file name
    local_file_name = 'MetadataFromAPI_py.xlsx'
    
    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container_name, local_file_name)

    # Upload the created file
    with open(local_file_name, "rb") as data:
        blob_client.upload_blob(data, overWrite = True)

if __name__ == "__main__":
    main()
