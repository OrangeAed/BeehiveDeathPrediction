import os

import pymongo
from pymongo import MongoClient
import csv
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from MongoUtils.mongo_helper import MongoHelper, ClientSessionRefresh


def get_sister_hive(hive_name: str) -> str:
    """
    Simple method to get the sister hive of a given hive name.
    Args:
        hive_name:

    Returns:

    """
    if hive_name[-1] == 'L':
        return hive_name[:-1] + 'R'
    elif hive_name[-1] == 'R':
        return hive_name[:-1] + 'L'
    else:
        raise ValueError("Invalid hive name. Must end in 'L' or 'R'.")


class CollectData:
    def __init__(self, is_on_server: bool = True):
        # Connect to MongoDB
        if not is_on_server:
            self.client = None
        else:
            self.client = MongoClient('mongo-mais.cs.appstate.edu', 27017)

        self.db = self.client['beeDB']
        self.dc = self.client['beeDC']

    def get_hivenames(self, include_pop_designator: bool = False) -> list[str]:
        collection = self.db['Hives']
        cursor = collection.find({}, {"HiveName": 1})

        def include_hivename(name):
            if name == "All_Hives" or name == "No_Hives":
                return False
            if name[-1].lower() == 'b' or name[-1].lower() == 'c':
                return include_pop_designator
            return True

        return [record["HiveName"] for record in cursor if include_hivename(record["HiveName"])]

    def get_temp_dataframe(self, hivename: str, start_date: datetime = None, end_date: datetime = None,
                           averaged_by_day: bool = False, include_humid: bool = False) -> pd.DataFrame:
        # if done locally, use the csv files
        if not self.client:
            if averaged_by_day:
                return self.csv_to_dataframe(f"data/averaged/{hivename}.csv")
            else:
                return self.csv_to_dataframe(f"data/not_averaged/{hivename}.csv")

        # Query TemperatureHumidity collection
        internal_temp = self.db['TemperatureHumidity']
        query = {"HiveName": hivename}
        if start_date and end_date:
            query["TimeStamp"] = {"$lt": end_date, "$gte": start_date}
        elif start_date:
            query["TimeStamp"] = {"$gte": start_date}
        elif end_date:
            query["TimeStamp"] = {"$lt": end_date}
        internal_records = list(internal_temp.find(query))

        # Check if internal_records is empty
        if not internal_records:
            raise ValueError("No records found in TemperatureHumidity collection for the given criteria.")

        # Extract date range from internal records
        dates = [record["TimeStamp"] for record in internal_records]
        oldest_date = min(dates)
        newest_date = max(dates)

        # Query HiveWeather2 collection
        external_temp = self.db['HiveWeather2']
        external_records = list(external_temp.find({
            "TimeStamp": {"$gte": oldest_date, "$lte": newest_date}
        }))
        temp_field_name = "ExternalTemperatureBoone"

        if not external_records or include_humid:
            external_records = list(self.dc['HiveWeather'].find({
                "HiveName": "AppMAIS1L",
                "TimeStamp": {"$gte": oldest_date, "$lte": newest_date}
            }))
            temp_field_name = "Temp"
            if not external_records:
                raise ValueError("No records found in HiveWeather or HiveWeather2 collections for the given criteria.")

        # Create DataFrames
        internal_df = pd.DataFrame(internal_records)
        external_df = pd.DataFrame(external_records)

        # Merge DataFrames on approximate time
        merged_df = pd.merge_asof(
            internal_df.sort_values("TimeStamp"),
            external_df.sort_values("TimeStamp"),
            on="TimeStamp",
            direction="nearest",
            suffixes=("_internal", "_external")
        )

        # Select required columns
        final_df = merged_df.loc[:, ["TimeStamp", "Temperature", temp_field_name, "Humidity_internal", "Humidity_external"]]

        # Rename columns using .loc to avoid SettingWithCopyWarning
        final_df.loc[:, "Time"] = final_df["TimeStamp"]
        final_df.loc[:, "InternalTemperature"] = final_df["Temperature"]
        final_df.loc[:, "ExternalTemperature"] = final_df[temp_field_name]
        final_df.loc[:, "InternalHumidity"] = final_df["Humidity_internal"]
        final_df.loc[:, "ExternalHumidity"] = final_df["Humidity_external"]

        # Calculate the difference
        final_df.loc[:, "TemperatureDifference"] = final_df["InternalTemperature"] - final_df["ExternalTemperature"]
        final_df.loc[:, "ProportionalTemperatureDifference"] = final_df["TemperatureDifference"] / final_df["ExternalTemperature"]
        final_df.loc[:, "HumidityDifference"] = final_df["InternalHumidity"] - final_df["ExternalHumidity"]
        final_df.loc[:, "ProportionalHumidityDifference"] = final_df["HumidityDifference"] / final_df["ExternalHumidity"]

        # Drop the original columns to avoid confusion
        final_df = final_df.drop(columns=["TimeStamp", "Temperature", temp_field_name])

        if averaged_by_day:
            final_df = self.get_temp_dataframe_averaged_by_day(final_df)
        return final_df

    def get_rms_dataframe(self, hivename: str, start_date: datetime = None, end_date: datetime = None,
                          average_by_day: bool = False):
        col = self.db.get_collection("AudioMetrics")
        query = {"HiveName": hivename}
        if start_date and end_date:
            query["TimeStamp"] = {"$lt": end_date, "$gte": start_date}
        elif start_date:
            query["TimeStamp"] = {"$gte": start_date}
        elif end_date:
            query["TimeStamp"] = {"$lt": end_date}

        records = list(col.find(query))
        if not records:
            raise ValueError("No records found in AudioMetrics collection for the given criteria.")

        df = pd.DataFrame(records)
        df = df[['TimeStamp', 'MedMagSpecRMS']]

        if average_by_day:
            df = self.get_temp_dataframe_averaged_by_day(df, False)
        return df

    def merge_temp_rms(self, temp_df: pd.DataFrame, rms_df: pd.DataFrame) -> pd.DataFrame:
        merged_df = pd.merge_asof(
            temp_df.sort_values("Time"),
            rms_df.sort_values("TimeStamp"),
            left_on="Time",
            right_on="TimeStamp",
            direction="nearest"
        )

        # Drop the original columns to avoid confusion
        merged_df = merged_df.drop(columns=["TimeStamp"])

        return merged_df

    def get_temp_dataframe_averaged_by_day(self, df: pd.DataFrame, is_temp: bool = True) -> pd.DataFrame:
        time_var_name = 'Time' if is_temp else 'TimeStamp'
        # Ensure the Time column is a datetime object
        df[time_var_name] = pd.to_datetime(df[time_var_name])

        # Extract the date part from the Time column
        df['Date'] = df[time_var_name].dt.date

        # Group by the Date and calculate the mean for each day
        daily_avg_df = (df.groupby('Date').mean().reset_index())

        return daily_avg_df

    def dataframe_to_csv(self, df: pd.DataFrame, filename: str) -> None:
        df.to_csv(filename, index=False)

    def csv_to_dataframe(self, filepath: str) -> pd.DataFrame:
        df = pd.read_csv(filepath)
        return df

    def dataframe_to_dict(self, df: pd.DataFrame) -> list[dict]:
        return df.to_dict(orient='records')

    def insert_dict_to_db(self, collection: pymongo.collection.Collection, records: list[dict]) -> None:
        collection.insert_many(records)


if __name__ == "__main__":
    cd = CollectData(True)
    # hives = death_info.get_2022_hives(True)
    # print("Current working directory:", os.getcwd())
    # print("Hives to process:", hives)
    #
    # if not os.path.exists("data"):
    #     os.makedirs("data")
    #     print("Created 'data' directory")
    #
    # for hive in hives:
    #     try:
    #         df = cd.get_temp_dataframe(hive)
    #         # df = cd.get_temp_dataframe_averaged_by_day(df)
    #         csv_filename = f"data/{hive}.csv"
    #         cd.dataframe_to_csv(df, csv_filename)
    #         if os.path.exists(csv_filename):
    #             print(f"Created CSV file: {csv_filename}")
    #     except Exception as e:
    #         print(f"Error processing hive {hive}: {e}")
