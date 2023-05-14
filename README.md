# Data Pipeline Setup
## _Explanation and Walkthrough_
![Socrata Logo](https://www.drupal.org/files/styles/grid-3-2x/public/project-images/socrata_vertical_thumb.jpg?itok=u9t1pXc7)

This Documentation will guide you on how to set up the automation pipeline to update dataset on [Data.wa](https://data.wa.gov/) utilizing:
- _**GitHub Action**_ as task scheduler
- _**Azure Cloud Storage**_ as data storage solution
- 

## Flow Chart



## Setup

### Credentials

| Name | Value |
| ------ | ------ |
| MY_SOCRATA_USERNAME | the username of the service account |
| MY_SOCRATA_PASSWORD | the password of the service account |
|AZURE_STORAGE_CONNECTION_STRING| the connection string retrieved from Azure service |



# Automation
Purpose: Automatically update data in the csv file to chosen dataset in Data.wa platform
Steps: 
- Set up your secret credentials in the repository
  - Go to ***Settings*** tab in the repo
  - Click ***Secrets and variables*** in the left sidebar
  - Click ***New repository secret*** green button to add new secret
    - put "MY_SOCRATA_USERNAME" in the ***Name*** field and put your username in the ***Secret*** field
    - put "MY_SOCRATA_PASSWORD" in the ***Name*** field and put your password in the ***Secret*** field
  - You can use other name, but make sure they are the same as listed in the ***update-script.py*** file
- Under the .github/workflows directory, you will see a YAML file (.yml) defining the automation parameters
  - on: defining the triggered time
    - workflow_dispatch: allowing the action to be triggered manually
    - schedule: defining the schedule (in UTC time)
  - jobs: you can define different jobs here. All jobs will be triggered in this action.
    - Checkout repository: clone the repository in the runner's environment
    - Set up Python: install specific Python version
    - Install dependencies: install necessary lib, including update Python and install socrata lib
    - Set up Git user: sets the global Git user name and email to be used by subsequent Git commands
    - Run Python script: run the update script provided in the repository
