# Understanding Housing Rents and Consumer Price Index: A Metropolitan Area-Level Analysis

## API Setup
1. Register on the following government websites to get your API keys:
    1. https://www.huduser.gov/portal/dataset/fmr-api.html
    2. https://www.bls.gov/developers/home.htm
2. Place your API keys in the 'API_Config_template.ini' file and rename it to 'API_Config.ini'.\
\
_Note:_
   1. *HUD API has a limit of 60 calls per minute* 
   2. *BLS API has a limit of 500 queries daily. Additionally, we can only request for up to 20 years of data at a time.*

## Environment Setup
Execute the following command to install the requirements:

_Note: Open the terminal with your python environment in the project directory containing the 'requirements.txt' file.\
If you are using Pycharm, then it will prompt to install all the missing requirements._

`pip install -r requirements.txt`

## Project Overview
This project aims to develop a comprehensive tool for metropolitan area-level analysis of 'fair market rates'
(FMR) in housing rents and understand its relationship with the economic indicators such as consumer price index (CPI).
It leverages data analytics and visualization techniques
to provide valuable insights in the government housing program.

_Note: For a deeper understanding about the project topic and analysis, please refer to the 'IS_597_Presentation.pptx'
 file._

## Hypotheses
_Hypothesis 1:_ There is a correlation between FMR and CPI where the CPI is independent and influences the FMR. There is a time lag between these two parameters.

_Hypothesis 2:_ Areas of anomalies in the FMR prices can be detected by studying FMR and CPI, indicating any regulatory interventions to control housing rents.


## Instructions
1. The 'prepareZipcodeData.py' needs to be executed only once, during the very first analysis. Before the first analysis, the 'Data/Processed Data/' will be empty. As I have synced my project directory, if you clone this repository, this directory won't be empty, and you can skip this step.
   * _Note: In future if you wish to add the latest zipcode data, add it to '/Data/HUD FMR' directory and execute this module._ 
2. Sequentially execute the notebook to load data from the API and select a metro area to carry out metropolitan-area level analysis.
3. After metropolitan-area level analysis, provide a zipcode to carry out a deeper analysis for that zipcode.




## References
1. Data Sources:
   1. Metropolitan area FMR: https://www.huduser.gov/portal/dataset/fmr-api.html
   2. Small Area FMR (zipcode data): https://www.huduser.gov/portal/datasets/fmr/smallarea/index.html
   3. List of all metro areas available in the HUD database: https://www.huduser.gov/portal/dataset/fmr-api.html
   4. List of all metro areas available in the BLS database: https://download.bls.gov/pub/time.series/mw/mw.area
   5. Metropolitan area Consumer Price Index (CPI): https://www.bls.gov/developers/home.htm
2. References in Program:
   1. Using BLS API to fetch CPI data: https://www.bls.gov/developers/api_python.htm#python2
   2. Series ID format: https://www.bls.gov/help/hlpforma.htm#CU
   3. Making API request with an API key: https://stackoverflow.com/questions/29931671/making-an-api-call-in-python-with-an-api-that-requires-a-bearer-token
   4. Smoothing timeseries data: https://www.youtube.com/watch?v=PFQme5QfpaI
   5. Using time offsets with pandas Grouper: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
   6. Using Config files for API keys: https://www.youtube.com/watch?v=Gdw0-QGq-z0
3. FMR implementation date: https://www.huduser.gov/periodicals/ushmc/winter98/summary-2.html
4. HUD API limitations: https://www.huduser.gov/portal/dataset/api-terms-of-service.html
5. BLS API Limitations: https://www.bls.gov/bls/api_features.htm
6. Understanding concepts and formating text for presentation and documentation: https://chatgpt.com/
   * Prompt 1: Explain the free market rate from the Department of Housing and Urban Development in simple terms. What is it? How is it calculated? why is it calculated?
   * Prompt 2: Explain the concept of the consumer price index calculated by the bureau of labor statistics in simple terms. What is it? How is it calculated? What is its significance?
