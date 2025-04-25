import pymongo
from pymongo import MongoClient
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

class FeedingDifference:
    def __init__(self):
        self.client = MongoClient('mongo-mais.cs.appstate.edu', 27017)
        self.db = self.client['beeDB']
        self.collection = self.db['Scale']

    def get_scale_data(self, hivename: str, start_date: datetime, end_date: datetime):
        """
        Get the scale data for a given hive name and date range.
        Args:
            hivename: The name of the hive.
            start_date: The start date for the data collection.
            end_date: The end date for the data collection.

        Returns:
            A pandas DataFrame containing the scale data.
        """
        query = {
            "HiveName": hivename,
            "TimeStamp": {
                "$gte": start_date,
                "$lt": end_date
            }
        }

        projection = {
            "_id": 0,
            "TimeStamp": 1,
            "Scale": 1
        }

        cursor = self.collection.find(query, projection)
        df = pd.DataFrame(list(cursor))

        return df

    def normalize_dates(self, df: pd.DataFrame):
        """
        Normalize the dates in the DataFrame to a common year (e.g., 2000).
        Args:
            df: The DataFrame containing the scale data.

        Returns:
            A DataFrame with normalized dates.
        """
        df['NormalizedDate'] = df['TimeStamp'].apply(lambda x: x.replace(year=2000))
        return df

    def plot_comparison(self, df1: pd.DataFrame, df2: pd.DataFrame, hivename: str, year1: int, year2: int):
        """
        Plot the scale data for two years on the same graph with normalized dates.
        Args:
            df1: The DataFrame containing the scale data for the first year.
            df2: The DataFrame containing the scale data for the second year.
            hivename: The name of the hive.
            year1: The first year.
            year2: The second year.

        Returns:
            A matplotlib figure containing the plot.
        """
        plt.figure(figsize=(10, 5))
        plt.plot(df1['NormalizedDate'], df1['Scale'], label=f"{hivename} {year1}")
        plt.plot(df2['NormalizedDate'], df2['Scale'], label=f"{hivename} {year2}")
        plt.title(f"Scale Data Comparison for {hivename}: {year1} vs {year2}")
        plt.xlabel("Date (Normalized to Year 2000)")
        plt.ylabel("Weight (kg)")
        plt.legend()
        plt.grid()

        return plt


if __name__ == "__main__":
    feeding_diff = FeedingDifference()

    hives = [
        "AppMAIS1LB",
        "AppMAIS1R",
        "AppMAIS5R",
        "AppMAIS7L",
        "AppMAIS7R",
        "AppMAIS9LB",
        "AppMAIS13L",
        "AppMAIS15R",
    ]
    dfs_2023 = []
    dfs_2024 = []

    for hivename in hives:
        # Data for 2023
        start_2023 = datetime(2023, 4, 22)
        end_2023 = datetime(2023, 7, 15)
        df_2023 = feeding_diff.get_scale_data(hivename, start_2023, end_2023)
        df_2023 = feeding_diff.normalize_dates(df_2023)
        df_2023 = df_2023[df_2023['Scale'] < 200]
        dfs_2023.append(df_2023)


        # Data for 2024
        start_2024 = datetime(2024, 4, 6)
        end_2024 = datetime(2024, 7, 15)
        df_2024 = feeding_diff.get_scale_data(hivename, start_2024, end_2024)
        df_2024 = feeding_diff.normalize_dates(df_2024)
        df_2023 = df_2023[df_2023['Scale'] < 200]
        dfs_2024.append(df_2024)

        # Plot comparison
        plt = feeding_diff.plot_comparison(df_2023, df_2024, hivename, 2023, 2024)
        plt.show()

    # Average Scale results from 2023 and 2024

    avg_scale_2023 = pd.concat(dfs_2023).groupby('NormalizedDate').mean().reset_index()
    avg_scale_2024 = pd.concat(dfs_2024).groupby('NormalizedDate').mean().reset_index()
    plt.figure(figsize=(10, 5))
    plt.plot(avg_scale_2023['NormalizedDate'], avg_scale_2023['Scale'], label="Average 2023")
    plt.plot(avg_scale_2024['NormalizedDate'], avg_scale_2024['Scale'], label="Average 2024")