"""
This module contains functions that transform existing dataframes
into new dataframes, which are better suitable for analysis.
"""

import pandas as pd
from datetime import datetime


def transform_cpi_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms the existing CPI dataframe into a single column
    dataframe with a column called 'CPI' and Date as the index.

    :param df: CPI dataframe as fetched from BLS API
    :return: CPI dataframe with a column called 'CPI'

    >>> test_data = pd.read_pickle('Data/Test Data/cpi_test_data')  # https://stackoverflow.com/questions/17098654/how-to-reversibly-store-and-load-a-pandas-dataframe-to-from-disk
    >>> test_data_t = transform_cpi_data(test_data)
    >>> print(list(test_data_t.index)) # doctest: +ELLIPSIS
    [Timestamp('2017-11-01 00:00:00'), ..., Timestamp('2021-03-01 00:00:00'), ..., Timestamp('2023-11-01 00:00:00')]
    >>> print(len(list(test_data_t.index)))
    37
    >>> print(test_data_t.shape)
    (37, 1)
    """
    years = df.index
    df_t = pd.DataFrame()

    # Transforming all rows into a single column
    for year in range(len(years)):
        y = pd.DataFrame(df.loc[years[year]])
        y.reset_index(inplace=True)
        # Computing date using year and month
        y['Date'] = y['Month'].apply(lambda x: datetime.strptime(years[year] + ' ' + x, '%Y %m'))
        y = y.drop(columns=['Month']).set_index('Date').rename(columns={years[year]: 'CPI'})
        if year == 0:
            df_t = y.copy()
        else:
            df_t = pd.concat([df_t, y], axis=0).dropna()

    return df_t


def smooth_and_merge(cpi: pd.DataFrame, fmr: pd.DataFrame, start_month: int) -> pd.DataFrame:
    """
    Smoothing the CPI dataframe to make it yearly based on FMR implementation date, and merging it
    with metro area FMR dates dataframe based on date.

    :param cpi: Transformed CPI dataframe
    :param fmr: Metro area FMR dataframe
    :param start_month: FMR rates implementation month (int)
    :return: Dataframe with FMR data and its corresponding CPI

    >>> test_cpi_t = transform_cpi_data(pd.read_pickle('Data/Test Data/cpi_test_data'))
    >>> test_cbsa = pd.read_pickle('Data/Test Data/cbsa_data_dec_test')
    >>> merge = smooth_and_merge(test_cpi_t, test_cbsa, start_month=10)
    >>> print(list(merge.index)) # doctest: +ELLIPSIS
    [Timestamp('2017-10-01 00:00:00'), ..., Timestamp('2023-10-01 00:00:00')]
    >>> test_cbsa = pd.read_pickle('Data/Test Data/cbsa_data_jun_test')
    >>> merge = smooth_and_merge(test_cpi_t, test_cbsa, start_month=6)
    >>> print(list(merge.index)) # doctest: +ELLIPSIS
    [Timestamp('2017-06-01 00:00:00'), ..., Timestamp('2023-06-01 00:00:00')]
    >>> merge = smooth_and_merge(test_cpi_t, test_cbsa, start_month=13) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError: start_month must be between 1 and 12
    """

    if not (1 <= start_month <= 12):
        raise ValueError('start_month must be between 1 and 12')

    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
    month_map = {1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR', 5: 'MAY', 6: 'JUN',
                 7: 'JUL', 8: 'AUG', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'}
    month = month_map[start_month]
    freq = 'YS-'+month

    # https://www.youtube.com/watch?v=PFQme5QfpaI
    cpi = cpi.groupby(pd.Grouper(freq=freq)).mean()
    combined = pd.merge(fmr.set_index('Date'), cpi, how='inner', left_index=True, right_index=True)

    # computing mean rent for the area
    combined['Mean_Rent'] = combined[['Efficiency', 'One-Bedroom',
                                      'Two-Bedroom', 'Three-Bedroom', 'Four-Bedroom', 'CPI']].mean(axis=1)

    return combined[['Efficiency', 'One-Bedroom', 'Two-Bedroom', 'Three-Bedroom', 'Four-Bedroom', 'Mean_Rent', 'CPI']]


if __name__ == '__main__':
    pass


