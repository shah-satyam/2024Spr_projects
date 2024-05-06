# Understanding Housing Rents and Consumer Price Index: A Metropolitan Area-Level Analysis

## API Setup
1. Register on the following government websites to get your API keys:
    1. https://www.huduser.gov/portal/dataset/fmr-api.html
    2. https://www.bls.gov/developers/home.htm
2. Place your API keys in the API_Config_template.ini file and rename it to API_Config.ini
Note:
   1. *Note: HUD API has a limit of 60 calls per minute* 
   2. *Note: BLS API has a limit of 500 queries daily. Additionally, we can only request for up to 20 years of data at a time.*

## Environment Setup
Execute the following command to install the requirements:\
_Note: Open the terminal with your python environment in the project directory containing the 'requirements.txt' file.\
If you are using Pycharm, then it will prompt to install all the missing requirements._\
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

