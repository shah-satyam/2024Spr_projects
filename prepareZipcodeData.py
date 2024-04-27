"""
Reads and processes all the small area FMR files
from the huduser.gov for the past decade.
"""

import pandas as pd
import glob
import re
from datetime import datetime
import math
import os


# def assign_col_names(use_cols: list) -> dict:
#     """
#
#     :param use_cols:
#     :return:
#     """
#     assign_names = dict()
#     for col in range(len(use_cols)):
#         if col == 0:
#             assign_names[use_cols[col]] = 'ZIPCODE'
#         elif col == 1:
#             assign_names[use_cols[col]] = 'Efficiency'
#         elif col == 2:
#             assign_names[use_cols[col]] = 'One-Bedroom'
#         elif col == 3:
#             assign_names[use_cols[col]] = 'Two-Bedroom'
#         elif col == 4:
#             assign_names[use_cols[col]] = 'Three-Bedroom'
#         elif col == 5:
#             assign_names[use_cols[col]] = 'Four-Bedroom'
#     return assign_names


def load_one_fmr_file(filename: str, path: str) -> pd.DataFrame:
    """

    :param filename:
    :param path:
    :return:
    """
    column_variation_1 = ['ZIP\nCode', 'SAFMR\n0BR', 'SAFMR\n1BR', 'SAFMR\n2BR', 'SAFMR\n3BR', 'SAFMR\n4BR']
    column_variation_2 = ['zcta', 'safmr_0br', 'safmr_1br', 'safmr_2br', 'safmr_3br', 'safmr_4br']
    column_variation_3 = ['zip_code', 'area_rent_br0', 'area_rent_br1', 'area_rent_br2', 'area_rent_br3',
                          'area_rent_br4']
    column_variation_4 = ['zipcode', 'area_rent_br0', 'area_rent_br1', 'area_rent_br2', 'area_rent_br3',
                          'area_rent_br4']
    column_variation_5 = ['ZIP', 'area_rent_br0', 'area_rent_br1', 'area_rent_br2', 'area_rent_br3', 'area_rent_br4']
    datatypes = ['str', 'Int16', 'Int16', 'Int16', 'Int16', 'Int16']
    actual_col_names = ['ZIPCODE', 'Efficiency', 'One-Bedroom', 'Two-Bedroom', 'Three-Bedroom', 'Four-Bedroom']
    string = filename.lower()
    year = re.search('fy\d\d\d\d', string=string).group()
    year = int(re.sub('\D', '', year))
    if year >= 2018 and year != 2020:
        use_cols = column_variation_1
        assign_data_type = dict(zip(use_cols, datatypes))
        use_names = dict(zip(use_cols, actual_col_names))
    elif year == 2020:
        use_cols = column_variation_2
        assign_data_type = dict(zip(use_cols, datatypes))
        use_names = dict(zip(use_cols, actual_col_names))
    elif year == 2017 or year == 2016:
        use_cols = column_variation_3
        assign_data_type = dict(zip(use_cols, datatypes))
        use_names = dict(zip(use_cols, actual_col_names))
    elif year == 2015:
        use_cols = column_variation_4
        assign_data_type = dict(zip(use_cols, datatypes))
        use_names = dict(zip(use_cols, actual_col_names))
    elif year <= 2014:
        use_cols = column_variation_5
        assign_data_type = dict(zip(use_cols, datatypes))
        use_names = dict(zip(use_cols, actual_col_names))
    try:
        df = pd.read_excel(path + '/' + filename, usecols=use_cols, dtype=assign_data_type)
    except ValueError:
        print('Column names do not match existing pattern')
    df = df.rename(columns=use_names)
    df = common_zipcode_mean(df)
    df['Date'] = datetime.strptime("10-" + str(year), '%m-%Y')
    return df


def load_all_fmr_files(file_directory='Data/HUD FMR') -> pd.DataFrame:
    """
    Loads all the small area FMR files from a given directory, and merges them
    into a single DataFrame. Based on the merge method, it either merges for all
    the zipcodes (method = 'outer'), or merges only the zipcodes that are
    common in all the files (merge_method = 'inner').
    :param file_directory: The path of the directory containing the small area FMR files.
    :return: A single dataframe containing FMRs for all the small area FMR files.
    """
    fmr_file_name = glob.glob(file_directory + '/*.csv')
    df = pd.DataFrame()
    # for file in range(len(fmr_file_name)):
    #     fmr_file_name[file] = fmr_file_name[file].replace(file_directory, '')
    #     fmr_file_name[file] = fmr_file_name[file].replace('\\', '')
    for file in range(len(fmr_file_name)):
        if df.shape[0] == 0:
            df = load_one_fmr_file(filename=os.path.basename(fmr_file_name[file]), path=file_directory)
            df_zip = pd.DataFrame(df['ZIPCODE'])
        else:
            data = load_one_fmr_file(filename=os.path.basename(fmr_file_name[file]), path=file_directory)
            data_zip = pd.DataFrame(data['ZIPCODE'])
            df = pd.concat([df, data], ignore_index=True)
            df_zip = df_zip.merge(data_zip, how='inner', on='ZIPCODE')
    df_final = (pd.merge(df, df_zip, how='inner', on='ZIPCODE')
                .sort_values(['Date', 'ZIPCODE'], ascending=True).reset_index(drop=True))
    return df_final


def common_zipcode_mean(fmr_data: pd.DataFrame) -> pd.DataFrame:
    """

    :param fmr_data:
    :return:
    """
    cols = list(fmr_data.columns)
    non_unique = fmr_data[[cols[0], cols[1]]].groupby(cols[0]).count()
    zips = list(non_unique[non_unique[cols[1]] > 1].index)
    for zipcode in zips:
        temp = fmr_data[fmr_data[cols[0]] == zipcode]
        mean = temp.mean(numeric_only=True).apply(lambda x: math.ceil(x))
        fmr_data = fmr_data[fmr_data[cols[0]] != zipcode]
        add = {cols[0]: zipcode, cols[1]: mean[cols[1]], cols[2]: mean[cols[2]],
               cols[3]: mean[cols[3]], cols[4]: mean[cols[4]],
               cols[5]: mean[cols[5]]}
        temp = pd.DataFrame(add, index=[0])
        fmr_data = pd.concat([fmr_data, temp], ignore_index=True)
    return fmr_data


if __name__ == '__main__':
    zip_data = load_all_fmr_files(file_directory='Data/HUD FMR')
    zip_data.to_csv('Data/Processed Data/zipcode_fmrs.csv')
    print('Data Processing Complete')
