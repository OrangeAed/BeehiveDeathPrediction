from TemperatureAnalysis.collect_data import CollectData
import death_info
import matplotlib.pyplot as plt
import pandas as pd


sister_hives = death_info.get_2022_opposing_pairs()

cd = CollectData()

def get_sister_dataframes(hives: list[tuple[str, str]]):
    sister_hives = []
    for surviving_hive, died_hive in hives:
        surviving_df = cd.get_temp_dataframe(surviving_hive)
        surviving_df = cd.get_temp_dataframe_averaged_by_day(surviving_df)
        diff_mean = surviving_df['TemperatureDifference'].mean()
        diff_std = surviving_df['TemperatureDifference'].std()
        surviving_df = surviving_df[(surviving_df['TemperatureDifference'] > diff_mean - 3*diff_std) & (surviving_df['TemperatureDifference'] < diff_mean + 3*diff_std)]

        died_df = cd.get_temp_dataframe(died_hive)
        died_df = cd.get_temp_dataframe_averaged_by_day(died_df)
        diff_mean = died_df['TemperatureDifference'].mean()
        diff_std = died_df['TemperatureDifference'].std()
        died_df = died_df[(died_df['TemperatureDifference'] > diff_mean - 3*diff_std) & (died_df['TemperatureDifference'] < diff_mean + 3*diff_std)]
        sister_hives.append((surviving_df, died_df))


    return sister_hives


def plot_sister_hives(sister_hives: list[tuple[pd.DataFrame, pd.DataFrame]], hive_names: list[tuple[str, str]]):
    for i, (surviving_df, died_df) in enumerate(sister_hives):
        fig, ax = plt.subplots()
        ax.plot(surviving_df['Time'], surviving_df['TemperatureDifference'], label="Survived")
        ax.plot(died_df['Time'], died_df['TemperatureDifference'], label="Died")
        ax.set_title(f"{hive_names[i][0]} vs {hive_names[i][1]}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Temperature Difference")
        ax.legend()
        plt.show()


if __name__ == "__main__":

    sister_hives_df = get_sister_dataframes(sister_hives)
    plot_sister_hives(sister_hives_df, sister_hives)
