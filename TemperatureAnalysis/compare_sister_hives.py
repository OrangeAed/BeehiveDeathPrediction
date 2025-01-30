#%%

from datetime import datetime

import numpy as np
from scipy.stats import ttest_rel, mannwhitneyu, chi2
from TemperatureAnalysis.collect_data import CollectData
import death_info
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.dates import DateFormatter
#%%
def get_sister_dataframes(hives: list[tuple[str, str]], times_of_death, avg_by_day: bool = False) -> list[tuple[pd.DataFrame, pd.DataFrame]]:
    sister_hives = []
    for surviving_hive, died_hive in hives:
        end_date = times_of_death[died_hive] if died_hive in times_of_death else datetime(2023, 4, 20)
        start_date = max(datetime(2022, 4, 10), end_date - pd.Timedelta(days=90))
        surviving_df = cd.get_temp_dataframe(surviving_hive, start_date, end_date, avg_by_day, True)
        died_df = cd.get_temp_dataframe(died_hive, start_date, end_date, avg_by_day, True)
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

# sister_hives = death_info.get_2022_opposing_pairs()
sister_hives = death_info.get_2022_all_pairs()
times_of_death = death_info.get_2022_deaths_early()

cd = CollectData()
sister_hives_dfs = get_sister_dataframes(sister_hives, times_of_death, True)

#%%
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

    return stat_temp, p_value_temp, stat_humid, p_value_humid

def combine_p_values(p_values):
    # Calculate the test statistic
    chi2_stat = -2 * np.sum(np.log(p_values))
    # Degrees of freedom is twice the number of p-values
    df = 2 * len(p_values)
    # Calculate the combined p-value
    combined_p_value = chi2.sf(chi2_stat, df)
    return combined_p_value

results = []
print ("\nT-Test Results\n")
for i in range(len(sister_hives_dfs)):
    # print(f"Test for {sister_hives[i][0]} vs {sister_hives[i][1]}")
    # sister_hives_dfs[i][0].dropna(inplace=True)
    # sister_hives_dfs[i][1].dropna(inplace=True)
    # if len(sister_hives_dfs[i][0]) != len(sister_hives_dfs[i][1]):
    #     print(f"{sister_hives[i][0]} and {sister_hives[i][1]} have different lengths")
    #     continue

    sister_hives_dfs[i][0]['TemperatureDifference'] = sister_hives_dfs[i][0]['TemperatureDifference'].abs()
    sister_hives_dfs[i][1]['TemperatureDifference'] = sister_hives_dfs[i][1]['TemperatureDifference'].abs()
    stat_temp, p_value_temp, stat_humid, p_value_humid = test_difference(sister_hives_dfs[i][0], sister_hives_dfs[i][1])
    combined_p_value = combine_p_values([p_value_temp, p_value_humid])

    results.append({
        "Surviving Hive": sister_hives[i][0],
        "Died Hive": sister_hives[i][1],
        "Temperature Statistic": stat_temp,
        "Temperature p-value": p_value_temp,
        "Humidity Statistic": stat_humid,
        "Humidity p-value": p_value_humid,
        "Combined p-value": combined_p_value
    })

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Print the DataFrame in a tabular format
print(results_df.to_string(index=False))
#%%
# plot_sister_hives(sister_hives_dfs, sister_hives)

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

plot_temperature_and_humidity_difference(sister_hives_dfs, sister_hives)
#%%
def normalize_days(sister_hives: list[tuple[pd.DataFrame, pd.DataFrame]], times_of_death: list[pd.Timestamp]):
    normalized_hives = []
    for i, (surviving_df, died_df) in enumerate(sister_hives):
        end_date = times_of_death[i]
        start_date = end_date - pd.Timedelta(days=60)

        surviving_df = surviving_df[(surviving_df['Time'] >= start_date) & (surviving_df['Time'] <= end_date)]
        died_df = died_df[(died_df['Time'] >= start_date) & (died_df['Time'] <= end_date)]

        normalized_hives.append((surviving_df, died_df))

    return normalized_hives

# Example usage
# normalized_sister_hives = normalize_days(sister_hives_dfs, times_of_death)
# plot_temperature_difference(normalized_sister_hives, sister_hives)
#%%
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
        results.append((stat_temp, p_value_temp, stat_humid, p_value_humid))

    return results



results = []
print("\nMann-Whitney U Test Results\n")
for i, (stat_temp, p_value_temp, stat_humid, p_value_humid) in enumerate(perform_mann_whitney_test(sister_hives_dfs)):
    combined_p_value = combine_p_values([p_value_temp, p_value_humid])
    results.append({
        "Surviving Hive": sister_hives[i][0],
        "Died Hive": sister_hives[i][1],
        "Temperature Statistic": stat_temp,
        "Temperature p-value": p_value_temp,
        "Humidity Statistic": stat_humid,
        "Humidity p-value": p_value_humid,
        "Combined p-value": combined_p_value
    })

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Print the DataFrame in a tabular format
print(results_df.to_string(index=False))