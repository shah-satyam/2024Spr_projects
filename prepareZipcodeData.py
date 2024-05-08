"""
Reads and processes all the small area FMR files
from the huduser.gov for the past decade to create
a dataset of FMR rates for all available zipcodes.
"""

import pandas as pd
import glob
import re
from datetime import datetime
import math
import os


def load_one_fmr_file(filename: str, path: str) -> pd.DataFrame:
    """
    This file takes the file name and file path for a small area FMR file as an input to read FMR rates for all
    the zipcodes and return that in the form of a dataframe.

    :param filename: Name of the small area FMR file
    :param path: path to the small area FMR file
    :return: dataframe containing the small area FMR rates for all zipcodes
    """

    # Over the years, the HUD department has reformated the way in which they release the small area data,
    # hence files from different years have different column names and formats. Form my observation, they
    # have stuck to a single from since 2018 (except 2020), so any new file that they would release could
    # also be processed using this function.
    column_variation_1 = ['ZIP\nCode', 'SAFMR\n0BR', 'SAFMR\n1BR', 'SAFMR\n2BR', 'SAFMR\n3BR', 'SAFMR\n4BR']
    column_variation_2 = ['zcta', 'safmr_0br', 'safmr_1br', 'safmr_2br', 'safmr_3br', 'safmr_4br']
    column_variation_3 = ['zip_code', 'area_rent_br0', 'area_rent_br1', 'area_rent_br2', 'area_rent_br3',
                          'area_rent_br4']
    column_variation_4 = ['zipcode', 'area_rent_br0', 'area_rent_br1', 'area_rent_br2', 'area_rent_br3',
                          'area_rent_br4']
    column_variation_5 = ['ZIP', 'area_rent_br0', 'area_rent_br1', 'area_rent_br2', 'area_rent_br3', 'area_rent_br4']
    datatypes = ['str', 'Float32', 'Float32', 'Float32', 'Float32', 'Float32']
    actual_col_names = ['ZIPCODE', 'Efficiency', 'One-Bedroom', 'Two-Bedroom', 'Three-Bedroom', 'Four-Bedroom']

    # extracting the year for which the file was released, using the file name.
    # I noticed that each file has a section contain year in the format - 'fy' followed by the year.
    # using this pattern to figure out the year of the file.
    # https://www.w3schools.com/python/python_regex.asp
    string = filename.lower()
    year = re.search('fy\d{4}', string=string).group()
    year = int(re.sub('\D', '', year))

    # based on the year of the file, using the relevant column names and mapping them to appropriate datatypes.
    if year >= 2018 and year != 2020:
        use_cols = column_variation_1
        assign_data_type = dict(zip(use_cols, datatypes))
        use_names = dict(zip(use_cols, actual_col_names))
    elif year == 2020:
        use_cols = column_variation_2
        assign_data_type = dict(zip(use_cols, datatypes))
        use_names = dict(zip(use_cols, actual_col_names))
    elif 2016 <= year <= 2017:
        use_cols = column_variation_3
        assign_data_type = dict(zip(use_cols, datatypes))
        use_names = dict(zip(use_cols, actual_col_names))
    elif year == 2015:
        use_cols = column_variation_4
        assign_data_type = dict(zip(use_cols, datatypes))
        use_names = dict(zip(use_cols, actual_col_names))
    else:
        use_cols = column_variation_5
        assign_data_type = dict(zip(use_cols, datatypes))
        use_names = dict(zip(use_cols, actual_col_names))

    # Incase there is a file that does not match any of the above pattern, then the function will
    # raise a ValueError with an appropriate error message.
    df = pd.DataFrame()  # defining the dataframe to prevent 'variable may be referred before assignment' warning.
    try:
        df = pd.read_excel(path + '/' + filename, usecols=use_cols, dtype=assign_data_type)
    except ValueError:
        print('Column names do not match existing pattern')
    df = df.rename(columns=use_names)

    # aggregating the FMR values for multiple entries of a single zipcode
    df = common_zipcode_mean(df)

    df['Date'] = datetime.strptime("10-" + str(year), '%m-%Y')  # converting the date column to datetime datatype.

    return df


def load_all_fmr_files(file_directory='Data/HUD FMR') -> pd.DataFrame:
    """
    This function loads all the small area FMR files from a given directory, and merges them into a single DataFrame.
    It also maps each zipcode with the cbsa_code for that metro area to which it belongs.

    :param file_directory: The path of the directory containing the small area FMR files.
    :return: A single dataframe containing FMRs for all the small area FMR files.
    """

    # reads the file name of all the files present in the given directory
    fmr_file_name = glob.glob(file_directory + '/*.csv')

    # defining the dataframe used in the 'for loop' below to prevent 'variable may be referred before assignment'
    # warning.
    df = pd.DataFrame()
    df_zip = pd.DataFrame()

    # calling the 'load_one_fmr_file' function to load each file in the directory and concat it with the 'df' dataframe.
    for file in range(len(fmr_file_name)):

        # For the very first file, instead of using concat, we can simply copy the contents loaded file.
        # All files don't have the same number of zipcodes; hence it is possible that some zipcodes have
        # missing data for certain years. To have consistent data for analysis, on zipcodes that have data
        # for all the years is considered. This is achieved by having a separate dataframe (df_zip) only for
        # zipcodes, and merging carrying out inner join on zipcodes for every year. Doing this will ensure that
        # only the zipcodes that are common for every year will be present in the final dataset.
        if df.shape[0] == 0:
            df = load_one_fmr_file(filename=os.path.basename(fmr_file_name[file]), path=file_directory)
            df_zip = pd.DataFrame(df['ZIPCODE'])
        else:
            data = load_one_fmr_file(filename=os.path.basename(fmr_file_name[file]), path=file_directory)
            data_zip = pd.DataFrame(data['ZIPCODE'])
            df = pd.concat([df, data], ignore_index=True)
            df_zip = df_zip.merge(data_zip, how='inner', on='ZIPCODE')

    # Doing inner joint on the two dataframes on 'zipcode' column to get only the common zipcodes over the years.
    df_final = (pd.merge(df, df_zip, how='inner', on='ZIPCODE')
                .sort_values(['Date', 'ZIPCODE'], ascending=True).reset_index(drop=True))

    # adding cbsa_code for each zipcode to map the zipcodes to their metro areas.
    df_final = merge_area_code_zipcode(df_final, file_directory)

    return df_final


def common_zipcode_mean(fmr_data: pd.DataFrame) -> pd.DataFrame:
    """
    In the small area dataset, there are some zipcodes that span over multiple counties, hence there are multiple
    entries for that zipcodes containing county wise FMR data, but as we oly need to carry out zipcode level analysis,
    this function averages the FMR value for all the duplicate zipcodes to get a single row for each zipcode.

    :param fmr_data: dataframe containing FMR data for a single-year.
    :return: FMR dataset for each year contains only one entry for each zipcode.

    >>> test_data = pd.read_csv('Data/Test Data/common_zip_data_test.csv', dtype={'ZIPCODE':'string', 'Date':'string'})
    >>> test_data['Date'] = pd.to_datetime(test_data['Date'])
    >>> print(test_data['ZIPCODE'].duplicated().sum())
    2495
    >>> test_data = common_zipcode_mean(test_data)
    >>> print(test_data['ZIPCODE'].duplicated().sum())
    0
    >>>
    """

    # Note: Column index number is used as this is processed dataframe whose layout does not depend on the downloaded
    # data
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


def merge_area_code_zipcode(fmr_data: pd.DataFrame, file_directory='Data/HUD FMR') -> pd.DataFrame:
    """
    This function maps each zipcode with the cbsa_code for that metro area to which it belongs.
    It used the most recent small area fmr file to get the most accurate cbsa_codes for the zipcodes.

    :param fmr_data: Dataframe containing zipcode level FMR rates for all the years.
    :param file_directory: Path of the directory containing the small area FMR files.
    :return: Dataframe with cbsa_codes mapped for all the zipcodes.
    """
    max_year = 0
    fmr_file_name = glob.glob(file_directory + '/*.csv')
    map_year = dict()

    # Identifying the most recent file
    for file in range(len(fmr_file_name)):
        string = os.path.basename(fmr_file_name[file])
        string = string.lower()
        year = re.search('fy\d{4}', string=string).group()
        year = int(re.sub('\D', '', year))
        map_year[year] = fmr_file_name[file]
        if year > max_year:
            max_year = year

    # Loading the most recent file
    path = map_year[max_year]
    codes = pd.read_excel(path, usecols=['ZIP\nCode', 'HUD Area Code'], dtype='string').rename(
        columns={'ZIP\nCode': 'ZIPCODE', 'HUD Area Code': 'Metro_Codes'})

    # mapping zipcodes with their respective metro areas.
    df = pd.merge(fmr_data, codes, how='left', on='ZIPCODE')

    return df


if __name__ == '__main__':
    zip_data = load_all_fmr_files(file_directory='Data/HUD FMR')
    zip_data.to_csv('Data/Processed Data/zipcode_fmrs.csv', index=False)
    print('Data Processing Complete')
