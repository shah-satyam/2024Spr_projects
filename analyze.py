"""
This module contains functions used to analyze the prepared FMR and CPI data.
"""

import pandas as pd
import matplotlib.pyplot as plt
import transformData


def lag_calculator(df: pd.DataFrame, field_to_analyze: str, estimated_lag=2, use_estimate=False) -> None:
    """
    This function calculates the time lag in the impact of CPI on the fair market rates
    for a metropolitan area. It is calculated based on correlation between the two variables.

    :param df: The Dataframe contains the year-on-year percentage change in fair market rates and consumer price
     index for a metropolitan area.
    :param field_to_analyze: Choose from either ['Efficiency', 'One-Bedroom', 'Two-Bedroom', 'Three-Bedroom',
    'Four-Bedroom', 'Mean_Rent']
    :param estimated_lag: Provide an estimated lag for the fair market rates.
    :param use_estimate: 'Ture' if you want to plot lag using the estimated lag.
    :return: No return value. Plots a graph showing the time lagged impact of CPI on the fair market rates.
    """

    # Checking if the provided field is acceptable
    acceptable_values = ['Efficiency', 'One-Bedroom', 'Two-Bedroom', 'Three-Bedroom', 'Four-Bedroom', 'Mean_Rent']
    if field_to_analyze not in acceptable_values:
        raise ValueError(f'Field {field_to_analyze} is not acceptable\n Valid options are {acceptable_values}')
    df = df[[field_to_analyze, 'CPI']]

    def plot_lag(data: pd.DataFrame, time_lag: int) -> None:
        """
        Inner function to plot the time lagged impact of CPI on the fair market rates.

        :param data: FMR and CPI data.
        :param time_lag: Time lag.
        """
        data_s = data.copy()
        data_s['CPI'] = data_s['CPI'].shift(time_lag)
        data_s.rename(columns={'CPI': 'CPI Shifted'}, inplace=True)
        data_s[field_to_analyze].plot.line(figsize=(10, 6), linewidth=1, color='orange', legend=True)
        data_s['CPI Shifted'].plot.line(figsize=(10, 6), linewidth=4, color='green', legend=True)
        data['CPI'].plot.line(figsize=(10, 6), linewidth=1, color='red', linestyle='dashed', legend=True)
        plt.xlabel('Year')
        plt.ylabel('Percentage Change')
        plt.show()

    # If an estimated lag value is provided, skip the calculation and plot the graph
    if use_estimate:
        plot_lag(df, estimated_lag)

    else:
        best_corr = 0
        best_lag = 0
        for lag in range(0, 4):
            shift_data = df.copy()
            shift_data['CPI'] = shift_data['CPI'].shift(lag)

            # There might be a correlation between percentage change in FMR and CPI, but it might not necessarily be
            # linear in nature.
            # Which means that even if the shape of the graph may have similar shape, it would not
            # be close or overlapping on the graph.
            # To better visualize the correlation in trends, normalizing the data to bring it on the same scale.
            shift_data = (shift_data - shift_data.mean()) / shift_data.std()
            corr = shift_data.corr().loc[field_to_analyze, 'CPI']
            if corr > best_corr:
                best_corr = corr
                best_lag = lag

        # Setting a threshold of corr =0.80.
        # If the best time lagged correlation is below this value,
        # Then there is no significant correlation between fair market rates and consumer price index.
        if best_corr < 0.80:
            print("No correlation was found between CPI and FMR for the metro area")
            return None

        print("The lag between the free market rate implemented and the consumer price index is: ", best_lag)
        print(f"The correlation {field_to_analyze} and consumer price index, after a {best_lag} year lag is: "
              f"{round(best_corr, 2)}")

        plot_lag(df, best_lag)

    return None


def zipcodes_trends(df: pd.DataFrame, field_to_analyze: str) -> pd.DataFrame:
    """
    This function uses standard deviation to identify zipcodes for which the percentage change in fair market rates
    was less than or greater than two standard deviations, as compared to all the zipcodes for that particular area.
    For the given time period in the data, the function returns the number of years for which a zipcode was
    less than 2 std, greater than 2 std, and the total number of years when it was marked as an anomaly.

    :param df: Dataframe containing FMR for all zipcodes in the metro area.
    :param field_to_analyze: Choose from either ['Efficiency', 'One-Bedroom', 'Two-Bedroom', 'Three-Bedroom',
    'Four-Bedroom', 'Mean_Rent']
    :return: The number of years for which a zipcode was less than 2 std, greater than 2 std,
    and the total number of years when it was marked as an anomaly.
    """
    acceptable_values = ['Efficiency', 'One-Bedroom', 'Two-Bedroom', 'Three-Bedroom', 'Four-Bedroom', 'Mean_Rent']
    if field_to_analyze not in acceptable_values:
        raise ValueError(f'Field {field_to_analyze} is not acceptable')

    # list of unique zip codes in the area:
    zips = list(df['ZIPCODE'].unique())
    total_zips = zips.__len__()

    # Getting the data to be analyzed.
    df = df[['ZIPCODE', field_to_analyze, 'Date']]

    # Pivoting the dataframe to make zipcodes as the columns and date as the index, with FMR data as the values.
    df_pivot = df.pivot(columns='ZIPCODE', index='Date', values=field_to_analyze)
    df_pivot['Mean_Rent'] = df_pivot.mean(axis=1)  # calculating the mean rent for the metro area for every year
    df_pivot = df_pivot.pct_change().dropna()   # calculating the percentage change in FMR
    # calculating the standard deviation in FMR value for each year
    df_pivot['STD'] = df_pivot.drop(columns=['Mean_Rent']).std(axis=1)
    df_pivot['Upper_Limit'] = df_pivot['Mean_Rent'] + (
            2 * df_pivot['STD'])
    df_pivot['Lower_Limit'] = df_pivot['Mean_Rent'] - (
            2 * df_pivot['STD'])
    deviation = list()

    # Identifying anomalies
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
    """
    Plotting the percentage change in FMR for a zipcode and the metro area that it belongs to,
    along with the time lagged percentage change in CPI for that metro area.

    :param df: Dataframe containing FMR for all zipcodes in the metro area.
    :param field_to_analyze: Choose from either ['Efficiency', 'One-Bedroom', 'Two-Bedroom', 'Three-Bedroom',
    'Four-Bedroom', 'Mean_Rent']
    :param zipcode: Zipcode that needs to be analyzed.
    :param cpi_data_transformed: CPI data with date as its index.
    :param fmr_implementation_date: Month (int) in which FMR rates are implemented.
    """
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
