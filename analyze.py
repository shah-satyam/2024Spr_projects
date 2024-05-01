"""
This module contains functions used to analyze the prepared FMR and CPI data.
"""

import pandas as pd
import matplotlib.pyplot as plt

import transformData


def lag_calculator(df: pd.DataFrame, field_to_analyze: str, estimated_lag=2, use_estimate=False) -> None:
    acceptable_values = ['Efficiency', 'One-Bedroom', 'Two-Bedroom', 'Three-Bedroom', 'Four-Bedroom', 'Mean_Rent']
    if field_to_analyze not in acceptable_values:
        raise ValueError(f'Field {field_to_analyze} is not acceptable\n Valid options are {acceptable_values}')
    df = df[[field_to_analyze, 'CPI']]

    def plot_lag(data: pd.DataFrame, time_lag: int) -> None:
        data_s = data.copy()
        data_s['CPI'] = data_s['CPI'].shift(time_lag)
        data_s.rename(columns={'CPI': 'CPI Shifted'}, inplace=True)
        data_s[field_to_analyze].plot.line(figsize=(10, 6), linewidth=1, color='orange', legend=True)
        data_s['CPI Shifted'].plot.line(figsize=(10, 6), linewidth=4, color='green', legend=True)
        data['CPI'].plot.line(figsize=(10, 6), linewidth=1, color='red', linestyle='dashed', legend=True)
        plt.xlabel('Year')
        plt.ylabel('Percentage Change')
        plt.show()

    if use_estimate:
        plot_lag(df, estimated_lag)
    else:
        best_corr = 0
        best_lag = 0
        for lag in range(0, 4):
            shift_data = df.copy()
            shift_data['CPI'] = shift_data['CPI'].shift(lag)
            shift_data = (shift_data - shift_data.mean()) / shift_data.std()
            corr = shift_data.corr().loc[field_to_analyze, 'CPI']
            if corr > best_corr:
                best_corr = corr
                best_lag = lag

        if best_corr < 0.80:
            print("No correlation was found between CPI and FMR for the metro area")
            return None
        print("The lag between the free market rate implemented and the consumer price index is: ", best_lag)
        print(f"The correlation {field_to_analyze} and consumer price index, after a {best_lag} year lag is: "
              f"{round(best_corr, 2)}")
        plot_lag(df, best_lag)

    return None


def zipcodes_trends(df: pd.DataFrame, field_to_analyze: str) -> pd.DataFrame:
    acceptable_values = ['Efficiency', 'One-Bedroom', 'Two-Bedroom', 'Three-Bedroom', 'Four-Bedroom', 'Mean_Rent']
    if field_to_analyze not in acceptable_values:
        raise ValueError(f'Field {field_to_analyze} is not acceptable')

    # list of unique zip codes in the area:
    zips = list(df['ZIPCODE'].unique())
    total_zips = zips.__len__()
    df = df[['ZIPCODE', field_to_analyze, 'Date']]
    df_pivot = df.pivot(columns='ZIPCODE', index='Date', values=field_to_analyze)
    df_pivot['Mean_Rent'] = df_pivot.mean(axis=1)
    df_pivot = df_pivot.pct_change().dropna()
    df_pivot['STD'] = df_pivot.drop(columns=['Mean_Rent']).std(axis=1)
    df_pivot['Upper_Limit'] = df_pivot['Mean_Rent'] + (
            2 * df_pivot['STD'])
    df_pivot['Lower_Limit'] = df_pivot['Mean_Rent'] - (
            2 * df_pivot['STD'])
    deviation = list()
    for z in zips:
        temp = dict()
        upper = df_pivot[z] >= df_pivot['Upper_Limit']
        lower = df_pivot[z] <= df_pivot['Lower_Limit']
        upper_true_count = 0
        lower_true_count = 0
        if upper.value_counts().shape[0] == 2:
            upper_true_count = upper.value_counts().iloc[1]
        if lower.value_counts().shape[0] == 2:
            lower_true_count = lower.value_counts().iloc[1]
        total_count = upper_true_count + lower_true_count
        temp['ZIPCODE'] = z
        temp['Above STD'] = upper_true_count
        temp['Below STD'] = lower_true_count
        temp['Total'] = total_count
        temp['Mean_growth_rate'] = df_pivot[z].mean()
        deviation.append(temp)
    dev = (pd.DataFrame(deviation).
           astype(dtype={'ZIPCODE': 'string', 'Above STD': 'Int8', 'Below STD': 'Int8', 'Total': 'Int8'}))
    return dev.sort_values(['Total', 'Above STD', 'Below STD'], ascending=False).reset_index(drop=True)


def plot_zipcode_trends(df: pd.DataFrame, field_to_analyze: str, zipcode: str,
                        cpi_data_transformed: pd.DataFrame, fmr_implementation_date: int) -> None:
    zip_data = df[df['ZIPCODE'] == zipcode][['Date', field_to_analyze]]
    zip_data = zip_data.set_index('Date')

    cbsa_data_t = df.drop(columns=['ZIPCODE']).groupby(['Date']).mean().reset_index()
    merge_zip = transformData.smooth_and_merge(cpi=cpi_data_transformed, fmr=cbsa_data_t,
                                               start_month=fmr_implementation_date)
    merge_zip = pd.merge(zip_data, merge_zip, left_index=True, right_index=True, how='inner',
                         suffixes=('_zip', '_metro'))
    merge_zip = merge_zip[[field_to_analyze + '_zip', field_to_analyze + '_metro', 'CPI']]

    merge_zip = merge_zip.pct_change()
    merge_zip['CPI'] = merge_zip['CPI'].shift(2)
    merge_zip[field_to_analyze + '_zip'].plot.line(figsize=(10, 6), linewidth=2, color='orange', legend=True)
    merge_zip[field_to_analyze + '_metro'].plot.line(figsize=(10, 6), linewidth=1, color='red', legend=True)
    merge_zip['CPI'].plot.line(figsize=(10, 6), linewidth=3, color='green', legend=True)
    plt.xlabel('Year')
    plt.ylabel('Percentage Change')
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5), fontsize=9)
    plt.show()
