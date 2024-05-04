# Understanding Housing Rents and Consumer Price Index: A Metropolitan Area-Level Analysis

## API Setup
1. Register on the following government websites to get your API keys:
    1. https://www.huduser.gov/portal/dataset/fmr-api.html
    2. https://www.bls.gov/developers/home.htm
2. Place your API keys in the API_Config_template.ini file and rename it to API_Config.ini
Note:
HUD API has a limit of 60 calls per minute, try not to exceed it
BLS API has a limit of 500 queries daily and request for data of up to 20 years per query

## Instructions
1. The prepareZipcodeData.py needs to be executed first if the 'Data/Processed Data/' directory is empty or if new data is added in the 'Data/HUD FMR/' directory.
2. Sequentially execute the notebook to load data from the APi and select a metro area to analyze.