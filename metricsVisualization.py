import requests
import pandas as pd
import numpy as np
import ast
import os
from azure.storage.blob import BlobServiceClient

def fetchAssetParents(data):
    columns = ['asset_name', 'asset_id', 'publication_date', 'asset_type', 'asset_link', 'asset_parent_id']

    df = pd.DataFrame(columns=columns)

    for i in range(len(data['results'])):
        result_dict = dict(data['results'][i])
        asset_parent_id = result_dict['resource']['parent_fxf']
        if isinstance(asset_parent_id, list) and len(asset_parent_id) > 0:
            # If asset_parent_id is a non-empty list, create a new row in the DataFrame for each element
            for parent_id in asset_parent_id:
                info = {
                    'asset_name': result_dict['resource']['name'],
                    'asset_id': result_dict['resource']['id'],
                    'publication_date': result_dict['resource']['publication_date'],
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
                'publication_date': result_dict['resource']['publication_date'],
                'asset_type': result_dict['resource']['type'],
                'asset_link': result_dict['link'],
                'asset_parent_id': '' if not asset_parent_id else asset_parent_id[0]
            }
            df_new = pd.DataFrame(info, index=[0])
            df = pd.concat([df, df_new], ignore_index=True)

    return df

# function to determine derivative/foundamental
def f_or_d(df):
    if df['asset_type'] == 'dataset':
        return 'Foundational'
    elif (df['asset_type'] == 'href' or df['asset_type'] == 'federated_href'):
        return 'External'
    else:
        return 'Derivative'

def merge_DF(AssetParents, agency):

    merge_AssetParents = pd.merge(AssetParents, agency, how='left', left_on="asset_id", right_on="asset id")
    merge_AssetParents = merge_AssetParents[['asset_name', 'asset_id', 'asset_type', 'asset_link', 'asset_parent_id',
                                             'publication_date', 'asset parent id', 'Parent asset type', 'Asset Agency',
                                             'Parent Agency']]

    merge_AssetParents['publication_date'] = merge_AssetParents['publication_date'].str[:10]
    merge_AssetParents['publication_date'] = pd.to_datetime(merge_AssetParents['publication_date'])
    # Add derivative/foundamental
    merge_AssetParents['FoundationalorNot'] = merge_AssetParents.apply(f_or_d, axis=1)

    return merge_AssetParents

def metric2(merge_AssetParents):
    df_visualization = merge_AssetParents.loc[merge_AssetParents['asset_type'].isin(['chart', 'map'])]
    df_visualization = df_visualization.loc[df_visualization['Parent asset type'].isin(['dataset'])]

    # List of unique parents of visualization
    uni_parent = df_visualization['asset parent id'].unique()

    # Add new column for visualization dataset
    VPlist = merge_AssetParents['asset_id'].isin(uni_parent)
    merge_AssetParents['Vparent'] = VPlist
    merge_AssetParents.replace({False: 0, True: 1}, inplace=True)

    # Add new column for asset mark
    merge_AssetParents['All_Asset'] = 1

    # delete duplicate rows
    merge_AssetParents = merge_AssetParents[merge_AssetParents['asset_parent_id'] == merge_AssetParents['asset parent id']]

    # add asset count column
    merge_AssetParents = merge_AssetParents.sort_values(by='publication_date')
    merge_AssetParents['asset_cnt'] = (merge_AssetParents.reset_index().index) + 1
    merge_AssetParents = merge_AssetParents.fillna('')

    return merge_AssetParents

def metric3(df, merge_AssetParents):
    df_story = df.loc[df['asset_type'].isin(['story'])]
    df_story = df_story.loc[~df_story['Parent asset type'].isin(['', 'parent asset is private or deleted'])]

    mapping = df_story[['asset_parent_id', 'Parent asset type']]
    mapping = mapping.drop_duplicates()
    # Extract non-dataset parent
    merge_story = pd.merge(df, mapping, how='right', left_on="asset_id", right_on="asset_parent_id")
    merge_story_lst = merge_story['asset_parent_id_x'].unique()

    # Extract dataset parent
    merge_story_lst2 = mapping.loc[mapping['Parent asset type'].isin(['dataset'])]['asset_parent_id'].unique()

    # Combine
    merge_story_lst = np.concatenate((merge_story_lst, merge_story_lst2), axis=0)

    # Add new column for story parent dataset
    SPlist = merge_AssetParents['asset_id'].isin(merge_story_lst)
    df['Sparent'] = SPlist
    df.replace({False: 0, True: 1}, inplace=True)

    return df

def metric4(pd_access):
    pd_access_cat = pd_access[['Asset UID', 'Asset', 'categories']]

    # drop null value
    pd_access_cat = pd_access_cat.dropna(subset=['categories'])
    len(pd_access_cat)

    # this will take some time
    # ================ should have a more efficient way to do it =============== #
    pd_access_cat['categories'] = pd_access_cat['categories'].apply(ast.literal_eval)
    pd_access_cat = pd_access_cat.explode('categories')

    return pd_access_cat

def download_blob(blob_client, local_file_name):
    with open(local_file_name, "wb") as file:
        file.write(blob_client.download_blob().readall())
        
def upload_file_to_azure(blob_service_client, container_name, local_file_name, blob_name):
    blob_client = blob_service_client.get_blob_client(container_name, blob_name)
    with open(local_file_name, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

def main():
    agency = pd.read_csv('UserAgencies.csv')
    agency = agency.fillna('')
    url = "http://api.us.socrata.com/api/catalog/v1?domains=data.wa.gov&limit=9000"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
    else:
        raise Exception(f"Failed to retrieve data with status code: {response.status_code}")

    #fetch Asset Parents
    AssetParents = fetchAssetParents(data)

    #Add Agency Data
    merge_AssetParents = merge_DF(AssetParents, agency)

    #Adding variables for metric2: Number of datasets with visualizations
    df_metric2 = metric2(merge_AssetParents)
    
    #Adding variables for metric3: Number of datasets with stories
    #df_metric3 is the final version for the dataset/asset for the first 3 metrics 
    df_metric3 = metric3(df_metric2, merge_AssetParents)
    
    #For the 4th metric, we need to create another asset for "Asset ACcess vs Category"
    
    # Download the AssetAccess file from Azure Blob Storage
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_name = os.getenv('CONTAINER_NAME')  # Get the container name from the environment variable
    asset_access_file_name = 'SiteAnalytics_AssetAccess_test.csv'  # The name of the file in Azure Blob Storage

    blob_client = blob_service_client.get_blob_client(container_name, asset_access_file_name)

    # Download the file locally
    local_file_name = 'AssetAccess.csv'
    download_blob(blob_client, local_file_name)

    # Read the downloaded file using pandas
    pd_access = pd.read_csv(local_file_name)

    # Remove the downloaded file
    os.remove(local_file_name)

    df_metric4 = metric4(pd_access)

    # Write metric3 and metric4 to CSV files
    df_metric3.to_csv('Metric3.csv', index=False)
    df_metric4.to_csv('Metric4.csv', index=False)
            
    # Upload the generated files to Azure Blob Storage
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_name = os.getenv('CONTAINER_NAME')  # Get the container name from the environment variable

    # Upload the Metric3.csv file
    upload_file_to_azure(blob_service_client, container_name, 'Metric3.csv', 'Metric3.csv')

    # Upload the Metric4.csv file
    upload_file_to_azure(blob_service_client, container_name, 'Metric4.csv', 'Metric4.csv')


if __name__ == "__main__":
    main()
