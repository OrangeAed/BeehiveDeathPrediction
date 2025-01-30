from datetime import datetime
from typing import Dict

import pandas as pd
from matplotlib import pyplot as plt

from TemperatureAnalysis.collect_data import CollectData

class CreatePlot:
    def __init__(self):
        # Initialize CollectData object
        self.collect_data = CollectData()


    def get_dataframe(self, hivename: str, start_date: datetime = None, end_date: datetime = None) -> pd.DataFrame:
        # Get the data
        df = self.collect_data.get_temp_dataframe(hivename, start_date, end_date)

        return df


    def get_dataframe_avg_by_day(self, df: pd.DataFrame) -> pd.DataFrame:
        # Wrapper function to average the data by day
        df = self.collect_data.get_temp_dataframe_averaged_by_day(df)

        return df


    def plot_internal_vs_external_temperature(self, df: pd.DataFrame, survived: bool = False, hivename: str = '') -> None:
        # Plot the data
        plt.figure(figsize=(10, 6))
        plt.plot(df["Time"], df["InternalTemperature"], label="Internal Temperature")
        plt.plot(df["Time"], df["ExternalTemperature"], label="External Temperature")
        plt.plot(df["Time"], df["TemperatureDifference"], label="Temperature Difference")
        plt.axhline(y=0, color='gray', linestyle='--')  # Add a dotted line at the x-axis
        plt.xlabel("Time")
        plt.ylabel("Temperature")
        plt.title(f"{hivename} Temperature Comparison {'(Survived)' if survived else ''}")
        plt.legend()
        plt.show()


    def plot_temperature_differental_ratio(self, df: pd.DataFrame, survived: bool = False, hivename: str = '') -> None:
        # Plot the data
        plt.figure(figsize=(10, 6))
        plt.plot(df["Time"], df["ProportionalTemperatureDifference"],
                 label="Temperature Difference / External Temperature")
        plt.axhline(y=0, color='gray', linestyle='--')  # Add a dotted line at the x-axis
        plt.xlabel("Time")
        plt.ylabel("Temperature Difference Ratio (%)")
        plt.title(f"{hivename} Temperature Difference Ratio Over Time {'(Survived)' if survived else ''}")
        plt.legend()
        plt.show()


    def make_plots(self, data: Dict[str, any], raw_difference: bool = False,
                   proportional_difference: bool = False, avg_by_day: bool = False) -> None:
        """
        Make plots from the requested hives/times in bulk.
        Args:
            data: should be in the form {<hivename>: {
             "start_date": Optional[datetime],
             "end_date": Optional[datetime]},
             "survived": Optional[bool] - whether the hive survived or not
             }
            raw_difference: Optional[bool] - whether to plot the raw temperature difference
            proportional_difference: Optional[bool] - whether to plot the proportional temperature difference
            avg_by_day: Optional[bool] - whether to average the data by day before plotting

        Returns: None

        """
        for hive in data:
            hivename = hive
            start_date = data[hive].get("start_date", None)
            end_date = data[hive].get("end_date", None)
            df = self.get_dataframe(hivename, start_date, end_date)
            if avg_by_day:
                df = self.get_dataframe_avg_by_day(df)
            if raw_difference:
                self.plot_internal_vs_external_temperature(df,
                                                           survived=data[hive].get("survived", False),
                                                           hivename=hive)
            if proportional_difference:
                self.plot_temperature_differental_ratio(df,
                                                        survived=data[hive].get("survived", False),
                                                        hivename=hive)


if __name__ == "__main__":
    # Initialize CollectData object
    plotter = CreatePlot()

    data = {
        "AppMAIS3L":
            {
                "end_date": datetime(2022, 12, 20),
                "survived": False
            },
        "AppMAIS3R":
            {
                "end_date": datetime(2022, 8, 21),
                "survived": False
            },
        "AppMAIS4L":
            {
                "end_date": datetime(2023, 3, 10),
                "survived": False
            },
        "AppMAIS4R":
            {
                "end_date": datetime(2023, 2, 15),
                "survived": False
            }

    }

    plotter.make_plots(data, raw_difference=True, proportional_difference=True, avg_by_day=True)
