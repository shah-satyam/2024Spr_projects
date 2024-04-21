"""
This Module uses the huduser.gov API to fetch Free Market rates
for different zipcodes in all the states in the United States.
"""

from configparser import ConfigParser
import requests
import time
import pandas as pd

config_file = 'API_Config.ini'
config = ConfigParser()
config.read(config_file)
key = config['API_Key']['key']

base_url = 'https://www.huduser.gov/hudapi/public/fmr'
headers = {"Authorization": "Bearer " + key}
state_endpoint = '/listStates'

list_states = requests.get(url=base_url+state_endpoint, headers=headers).json()

state_data_endpoint = '/fmr/statedata/'
years = range(2017, 2025)
metro_endpoint = '/statedata/'
metros = dict()
for state in list_states:
    state_code = '/'+state['state_code']
    data = requests.get(url=base_url+metro_endpoint+state_code, headers=headers).json()
    metros[state['state_name']] = data['data']['metroareas']
    time.sleep(5)

for state in list_states:
    print(metros[state['state_name']])
