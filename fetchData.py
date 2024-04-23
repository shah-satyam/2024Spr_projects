"""
This Module uses the huduser.gov API to fetch Free Market rates
 and the BLS API to fetch CPI data, for different metro areas.
"""

from configparser import ConfigParser
import requests
import pandas as pd
import time
import json


def fetch_metro_cpi_bls(api_config: str, series_id: list, start_year: int, end_year: int) -> dict:
    """
    The function fetches monthly CPI data from the Bureau of Labor Statistics
     for the specified metro areas, in the specified years.

    :param api_config: API configuration file path and name
    :param series_id: List of metro codes to fetch
    :param start_year: Starting year
    :param end_year: Ending year
    :return: Dictionary of monthly CPI data
    """
    config_file = api_config
    config = ConfigParser()
    config.read(config_file)
    bls_key = config['API_Key']['BLS_key']

    bls_base_url = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
    bls_headers = {'Content-type': 'application/json', 'Authorization': 'Bearer ' + bls_key}
    bls_metro_data = json.dumps({"seriesid": series_id, "startyear": start_year, "endyear": end_year})
    bls_response = requests.post(url=bls_base_url, data=bls_metro_data, headers=bls_headers).json()['Results']['series']

    return_data = dict()

    for series in bls_response:
        temp = series['data']
        data = pd.DataFrame(temp)
        data.drop(columns=['periodName', 'footnotes'], inplace=True)
        data['period'] = data['period'].apply(lambda x: x.replace('M', ''))
        data.rename(columns={'period': 'Month'}, inplace=True)
        data = data.pivot(columns='Month', index='year', values='value')
        data = data.astype('Float32')
        return_data[series.key()] = data
    return return_data


def get_bls_series_id(metro_code_file='Data/BLS/cu.area.txt',
                      series_id_prefix='CUUR', series_id_suffix='SA0') -> pd.DataFrame:
    """
    The function fetches the area codes for metro areas and creates a series_id for
    each metro area that can be used to fetch CPI data from BLS API.

    :param metro_code_file: Path and name of the metro code file
    :param series_id_prefix: String prefix for series IDs
    :param series_id_suffix: String suffix for series IDs
    :return: DataFrame of series IDs
    """
    code = pd.read_csv(metro_code_file, usecols=['area_code', 'area_name'],
                       dtype={'area_code': 'string', 'area_name': 'string'}, sep='\t', skiprows=list(range(1, 32)))
    code.rename(columns={'area_name': 'old_area_name'}, inplace=True)
    code = code[code['old_area_name'].str.contains('Size Class A') != True]
    code['area_name'] = code['old_area_name'].apply(lambda x: x.split(',')[0])
    code['area_state'] = code['old_area_name'].apply(lambda x: x.split(',')[1] if len(x.split(',')) > 1 else 'NA')
    code.drop(['old_area_name'], axis=1, inplace=True)
    code['area_code'] = series_id_prefix + code['area_code'] + series_id_suffix
    code = code.astype({'area_name': 'string', 'area_state': 'string'})
    return code


def get_metro_codes_hud(api_config: str) -> pd.DataFrame:
    """
    This function uses the HUD API to fetch a list of metro areas
    along with their cbsa code and returns them in a dataframe.
    :param api_config: API configuration file path and name
    :return: DataFrame of metro areas along with their cbsa code
    """
    config_file = api_config
    config = ConfigParser()
    config.read(config_file)
    hud_key = config['API_Key']['HUD_key']

    hud_base_url = 'https://www.huduser.gov/hudapi/public/fmr'
    hud_headers = {"Authorization": "Bearer " + hud_key}
    metro_endpoint = '/listMetroAreas'

    list_metros = requests.get(url=hud_base_url + metro_endpoint, headers=hud_headers).json()

    def state_parser(x: str):
        """

        :param x:
        :return:
        """
        x = x.split(',')
        if len(x) > 1:
            x = x[1].split(' ')
            return x[1]
        else:
            return 'NA'

    metro = pd.DataFrame(list_metros)
    metro.drop(columns=['category'], inplace=True)
    metro.rename(columns={'area_name': 'old_area_name'}, inplace=True)
    metro['area_name'] = metro['old_area_name'].apply(lambda x: x.split(',')[0])
    metro['area_state'] = metro['old_area_name'].apply(lambda x: state_parser(x))
    metro.drop(['old_area_name'], axis=1, inplace=True)
    metro = metro.astype({'area_name': 'string', 'area_state': 'string'})
    return metro


def fetch_metro_fmr_data(api_config: str, metro_code: str, start_year: int, end_year: int) -> pd.DataFrame:
    """
    This function takes a cbsa code for a metro area and
    fetches the fair market rates during the years specified.
    :param api_config: API configuration file path and name
    :param metro_code: CBSA code for metro area
    :param start_year: Starting year
    :param end_year: Ending year
    :return: DataFrame of fair market rates for the metro area.
    """
    config_file = api_config
    config = ConfigParser()
    config.read(config_file)
    hud_key = config['API_Key']['HUD_key']

    hud_base_url = 'https://www.huduser.gov/hudapi/public/fmr'
    hud_headers = {"Authorization": "Bearer " + hud_key}

    year_data = list()
    for year in range(start_year, end_year+1):
        cbsa_code = metro_code
        data_endpoint = '/data/'
        data = requests.get(url=hud_base_url + data_endpoint + cbsa_code + '?year=' + str(year),
                            headers=hud_headers)
        if data.status_code == 200:
            year_data.append(data.json()['data']['basicdata'])
        time.sleep(2)
    metro_data = pd.DataFrame(year_data)
    metro_data = metro_data.astype(
        {'year': 'int16', 'Efficiency': 'Float32', 'One-Bedroom': 'Float32', 'Two-Bedroom': 'Float32',
         'Three-Bedroom': 'Float32', 'Four-Bedroom': 'Float32'})
    metro_data.set_index('year', inplace=True)
    return metro_data

