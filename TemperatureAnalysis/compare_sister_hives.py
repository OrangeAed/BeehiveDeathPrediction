from datetime import datetime
import numpy as np
from scipy.stats import ttest_rel, mannwhitneyu, chi2
from TemperatureAnalysis.collect_data import CollectData
import death_info
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.dates import DateFormatter


def get_sister_dataframes(hives: list[tuple[str, str]], times_of_death, avg_by_day: bool = False,
                          include_rms: bool = False, year: int = 2022) \
        -> list[tuple[pd.DataFrame, pd.DataFrame]]:
    sister_hives = []
    start_and_end_dates = death_info.get_start_and_end_dates(year)
    for surviving_hive, died_hive in hives:
        end_date = times_of_death[died_hive] if died_hive in times_of_death else start_and_end_dates["end"]
        # start_date = max(start_and_end_dates["start"], end_date - pd.Timedelta(days=90))
        start_date = start_and_end_dates["start"]
        surviving_df = cd.get_temp_dataframe(surviving_hive, start_date, end_date, avg_by_day, True)
        died_df = cd.get_temp_dataframe(died_hive, start_date, end_date, avg_by_day, True)
        if include_rms:
            try:
                surviving_rms = cd.get_rms_dataframe(surviving_hive, start_date, end_date, avg_by_day)
                surviving_df = cd.merge_temp_rms(surviving_df, surviving_rms)
            except ValueError:
                print(f"No RMS data found for {surviving_hive}")

            try:
                died_rms = cd.get_rms_dataframe(died_hive, start_date, end_date, avg_by_day)
                died_df = cd.merge_temp_rms(died_df, died_rms)
            except ValueError:
                print(f"No RMS data found for {died_hive}")

        sister_hives.append((surviving_df, died_df))

    return sister_hives


def plot_sister_hives(sister_hives: list[tuple[pd.DataFrame, pd.DataFrame]], hive_names: list[tuple[str, str]]):
    for i in range(len(sister_hives)):
        fig, ax = plt.subplots()
        ax.plot(sister_hives[i][0]['Time'], sister_hives[i][0]['TemperatureDifference'], label="Survived")
        ax.plot(sister_hives[i][1]['Time'], sister_hives[i][1]['TemperatureDifference'], label="Died")
        ax.set_title(f"{hive_names[i][0]} vs {hive_names[i][1]}", fontsize=12)
        ax.set_xlabel("Date")
        ax.set_ylabel("Temperature Difference (°F)")
        ax.legend()
        
        # Set the date format to exclude the year
        date_format = DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(date_format)
        
        plt.show()


def test_difference(survived: pd.DataFrame, died: pd.DataFrame):
    # Drop NA values from both arrays
    survived = survived.dropna(subset=['TemperatureDifference', 'HumidityDifference'])
    died = died.dropna(subset=['TemperatureDifference', 'HumidityDifference'])

    # Ensure both arrays are of equal length by dropping corresponding values
    min_length = min(len(survived), len(died))
    survived = survived.iloc[:min_length]
    died = died.iloc[:min_length]

    # Perform the t-test
    stat_temp, p_value_temp = ttest_rel(survived['TemperatureDifference'], died['TemperatureDifference'])
    stat_humid, p_value_humid = ttest_rel(survived['HumidityDifference'], died['HumidityDifference'])
    stat_rms, p_value_rms = ttest_rel(survived['MedMagSpecRMS'], died['MedMagSpecRMS'])

    return stat_temp, p_value_temp, stat_humid, p_value_humid, stat_rms, p_value_rms


def combine_p_values(p_values):
    # Calculate the test statistic
    chi2_stat = -2 * np.sum(np.log(p_values))
    # Degrees of freedom is twice the number of p-values
    df = 2 * len(p_values)
    # Calculate the combined p-value
    combined_p_value = chi2.sf(chi2_stat, df)
    return combined_p_value


def plot_temperature_and_humidity_difference(sister_hives: list[tuple[pd.DataFrame, pd.DataFrame]], hive_names: list[tuple[str, str]]):
    for i in range(len(sister_hives)):
        fig, ax = plt.subplots(2, 1, figsize=(10, 8))

        # Plot Temperature Difference for survived and died hives
        ax[0].plot(sister_hives[i][0]['Time'], sister_hives[i][0]['TemperatureDifference'], label=f"{hive_names[i][0]} (Survived)")
        ax[0].plot(sister_hives[i][1]['Time'], sister_hives[i][1]['TemperatureDifference'], label=f"{hive_names[i][1]} (Died)")
        ax[0].set_title(f"Temperature Difference: {hive_names[i][0]} vs {hive_names[i][1]}")
        ax[0].set_xlabel("Date")
        ax[0].set_ylabel("Temperature Difference (°F)")
        ax[0].legend()

        # Plot Humidity Difference for survived and died hives
        ax[1].plot(sister_hives[i][0]['Time'], sister_hives[i][0]['HumidityDifference'], label=f"{hive_names[i][0]} (Survived)")
        ax[1].plot(sister_hives[i][1]['Time'], sister_hives[i][1]['HumidityDifference'], label=f"{hive_names[i][1]} (Died)")
        ax[1].set_title(f"Humidity Difference: {hive_names[i][0]} vs {hive_names[i][1]}")
        ax[1].set_xlabel("Date")
        ax[1].set_ylabel("Humidity Difference (%)")
        ax[1].legend()

        # Set the date format to exclude the year
        date_format = DateFormatter("%m-%d")
        ax[0].xaxis.set_major_formatter(date_format)
        ax[1].xaxis.set_major_formatter(date_format)

        plt.tight_layout()
        plt.show()


def normalize_days(sister_hives: list[tuple[pd.DataFrame, pd.DataFrame]], times_of_death: list[pd.Timestamp]):
    normalized_hives = []
    for i, (surviving_df, died_df) in enumerate(sister_hives):
        end_date = times_of_death[i]
        start_date = end_date - pd.Timedelta(days=60)

        surviving_df = surviving_df[(surviving_df['Time'] >= start_date) & (surviving_df['Time'] <= end_date)]
        died_df = died_df[(died_df['Time'] >= start_date) & (died_df['Time'] <= end_date)]

        normalized_hives.append((surviving_df, died_df))

    return normalized_hives


def perform_mann_whitney_test(sister_hives: list[tuple[pd.DataFrame, pd.DataFrame]]):
    results = []
    for surviving_df, died_df in sister_hives:
        # Convert TemperatureDifference to numeric, coercing errors to NaN
        surviving_df['TemperatureDifference'] = pd.to_numeric(surviving_df['TemperatureDifference'], errors='coerce')
        died_df['TemperatureDifference'] = pd.to_numeric(died_df['TemperatureDifference'], errors='coerce')

        survived_temp_diff = surviving_df['TemperatureDifference'].dropna().values
        died_temp_diff = died_df['TemperatureDifference'].dropna().values

        # Perform the Mann-Whitney U test
        stat_temp, p_value_temp = mannwhitneyu(survived_temp_diff, died_temp_diff, alternative='greater')

        surviving_df['HumidityDifference'] = pd.to_numeric(surviving_df['HumidityDifference'], errors='coerce')
        died_df['HumidityDifference'] = pd.to_numeric(died_df['HumidityDifference'], errors='coerce')

        survived_humid_diff = surviving_df['HumidityDifference'].dropna().values
        died_humid_diff = died_df['HumidityDifference'].dropna().values

        stat_humid, p_value_humid = mannwhitneyu(survived_humid_diff, died_humid_diff, alternative='greater')

        stat_rms, p_value_rms = mannwhitneyu(surviving_df['MedMagSpecRMS'], died_df['MedMagSpecRMS'], alternative='greater')

        results.append((stat_temp, p_value_temp, stat_humid, p_value_humid, stat_rms, p_value_rms))

    return results


if __name__ == "__main__":
    # sister_hives = death_info.get_2022_all_pairs(jefferson_hives=True)
    sister_hives = death_info.get_2022_opposing_pairs()
    # sister_hives = death_info.get_2023_opposing_pairs()
    times_of_death = death_info.get_2022_deaths_early(jefferson_hives=False)

    cd = CollectData()
    sister_hives_dfs = get_sister_dataframes(sister_hives, times_of_death, True, True, year=2022)

    results = []
    print("\nT-Test Results\n")
    for i in range(len(sister_hives_dfs)):
        # print(f"Test for {sister_hives[i][0]} vs {sister_hives[i][1]}")
        # sister_hives_dfs[i][0].dropna(inplace=True)
        # sister_hives_dfs[i][1].dropna(inplace=True)
        # if len(sister_hives_dfs[i][0]) != len(sister_hives_dfs[i][1]):
        #     print(f"{sister_hives[i][0]} and {sister_hives[i][1]} have different lengths")
        #     continue

        sister_hives_dfs[i][0]['TemperatureDifference'] = sister_hives_dfs[i][0]['TemperatureDifference']
        sister_hives_dfs[i][1]['TemperatureDifference'] = sister_hives_dfs[i][1]['TemperatureDifference']
        stat_temp, p_value_temp, stat_humid, p_value_humid, stat_rms, p_value_rms = test_difference(sister_hives_dfs[i][0],
                                                                             sister_hives_dfs[i][1])
        combined_p_value = combine_p_values([p_value_temp, p_value_humid])

        survived_std = sister_hives_dfs[i][0]['InternalTemperature'].std()
        died_std = sister_hives_dfs[i][1]['InternalTemperature'].std()

        survived_mean = sister_hives_dfs[i][0]['InternalTemperature'].mean()
        died_mean = sister_hives_dfs[i][1]['InternalTemperature'].mean()

        results.append({
            "Surviving Hive": sister_hives[i][0],
            "Died Hive": sister_hives[i][1],
            "Temperature Statistic": stat_temp,
            "Temperature p-value": p_value_temp,
            "Humidity Statistic": stat_humid,
            "Humidity p-value": p_value_humid,
            "RMS Statistic": stat_rms,
            "RMS p-value": p_value_rms,
            "Combined p-value": combined_p_value,
            "Std Temp diff": survived_std - died_std,
            "Mean Temp diff": survived_mean - died_mean
        })
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    # Print the DataFrame in a tabular format
    print(results_df.to_string(index=False))


    plot_temperature_and_humidity_difference(sister_hives_dfs, sister_hives)

    results = []
    print("\nMann-Whitney U Test Results\n")
    for i, (stat_temp, p_value_temp, stat_humid, p_value_humid, stat_rms, p_value_rms) in enumerate(
            perform_mann_whitney_test(sister_hives_dfs)):
        combined_p_value = combine_p_values([p_value_temp, p_value_humid])

        survived_std = sister_hives_dfs[i][0]['InternalHumidity'].std()
        died_std = sister_hives_dfs[i][1]['InternalHumidity'].std()

        survived_mean = sister_hives_dfs[i][0]['InternalHumidity'].mean()
        died_mean = sister_hives_dfs[i][1]['InternalHumidity'].mean()

        results.append({
            "Surviving Hive": sister_hives[i][0],
            "Died Hive": sister_hives[i][1],
            "Temperature Statistic": stat_temp,
            "Temperature p-value": p_value_temp,
            "Humidity Statistic": stat_humid,
            "Humidity p-value": p_value_humid,
            "RMS Statistic": stat_rms,
            "RMS p-value": p_value_rms,
            "Combined p-value": combined_p_value,
            "Std Humid diff": survived_std - died_std,
            "Mean Humid diff": survived_mean - died_mean
        })

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)

    # Print the DataFrame in a tabular format
    print(results_df.to_string(index=False))
