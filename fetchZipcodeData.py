"""
This module fetches top zipcodes from top cities for each state in the United States.
"""

import pandas as pd
import requests

file = 'view-source_https___www.edq.com_resources_glossary_zip-codes-of-major-cities-in-the-united-states_.html'
in_city = False
final_data = list()
with open(file, encoding="utf8") as f:
    for line in f:
        line = line.strip()
        if line.__contains__('span class="NormalTextRun SCXW137986799 BCX0"'):
            line = line.replace('<span class="NormalTextRun SCXW137986799 BCX0">','')
            line = line.replace('</span>','')
            if line.__contains__('heading 2'):
                temp = line.replace('<span class="NormalTextRun SCXW137986799 BCX0" data-ccp-parastyle="heading 2">', '')
                in_city = False
                state = temp.split('data-contrast="auto">')[1].split('<span class')[0]
            if line.__contains__('heading 3'):
                temp = line.replace('<span class="NormalTextRun SCXW137986799 BCX0" data-ccp-parastyle="heading 3">', '')
                in_city = True
                city = temp.split('data-contrast="none">')[1].split('<span class')[0]
            if not (line.__contains__('heading 2')) and not (line.__contains__('heading 3')) and in_city:
                line = line.split('data-contrast="auto">')[1]
                line = line.split(' - ')[0]
                data = dict()
                data['ZIPCODE'] = line
                data['State'] = state
                data['City'] = city
                final_data.append(data)
zipcode_data = pd.DataFrame(final_data)

