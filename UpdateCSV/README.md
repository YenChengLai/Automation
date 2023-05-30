# Python Code Explanation

## **metadataFromAPI.py**

The "MetadataFromAPI" code automates the process of extracting data from an API and generating an Excel file for review. It includes seven functions that return dataframes. Using pandas ExcelWriter, the code combines these dataframes into a single Excel file, simplifying the review process. This automation replaces the manual maintenance of a metadata Excel file created with power query.

## **googleAnalysisUpdate.py**

To execute the code, you will need a *Google Service Account Key* and Google Analytics access with the *service account*. 

Once the key is generated, replace the file path under *credentials_file_path*

Package ‘google.analytics.data_v1beta’ will be used.

Follow these steps:

**1. Generate Google Service Account Key**
* Go to Google Cloud Platform (https://console.cloud.google.com/)
* Select WAOpenData
* Go to “APIs & Services” (https://console.cloud.google.com/apis/) with the selected project
* Click ‘Enable APIs & Services’
* Go to library and search for “Google Analytics Data API”, and enable it
* Go to ‘Credentials’ -> ‘Create Credentials’ -> ‘Service Account’
* Give a name to the service account, then click “Done” (e.g. google-analytics-api)
* A service account is created, copy it as we will need to add it into GA next step
* Then Go to “KEYS” -> “ADD KEY”, choose “JSON” and a JSON Key file will be generated. Saved the file into the working folder (or somewhere you can remember) as it will be read in python code later.

**2. Share GA access with the service account**
* Login to the Google Analytics
* Go to ‘Admin’ -> Account Access Management
* Grant ‘Read’ access to the service account we copied in the previous step (Or ask admin to grant it if you don’t have the right)
* Copy the WAOpenData property ID and paste it to PROPERTY_ID in the code


## **metricsVisualization.py**

The code generates files that are essential for creating visualizations on the open data portal. These visualizations provide a graphical representation of the data, making it easier for users to understand and interpret the information.

By running the code, you will produce the necessary files that contain the processed and formatted data required for the visualization process. These files serve as inputs for creating charts, graphs, maps, or any other visual elements that enhance data presentation on the open data portal.