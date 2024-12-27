from TemperatureAnalysis import create_plot
from datetime import datetime

if __name__ == "__main__":
    # Initialize CreatePlot object
    create_plotter = create_plot.CreatePlot()

    hives = create_plotter.collect_data.get_hivenames(include_pop_designator=False)

    hives_that_survived = [
        "AppMAIS1R",
        "AppMAIS2L",
        "AppMAIS5R",
        "AppMAIS6L",
        "AppMAIS7L",
        "AppMAIS7R",
        "AppMAIS8R",
        "AppMAIS9R",
        "AppMAIS11L",
        "AppMAIS12R",
    ]

    jefferson_hives = [
        "AppMAIS1L",
        "AppMAIS1R",
        "AppMAIS2L",
        "AppMAIS2R"
    ]

    data = {}
    for hive in hives:
        # gets just appmais 1-12
        if len(hive[7:]) == 3 and int(hive[8]) > 2:
            continue
        if hive in jefferson_hives:
            continue

        data[hive] = {
            "end_date": datetime(2023, 4, 21),
            "survived": hive in hives_that_survived
        }

    # Make plots
    create_plotter.make_plots(
        data=data,
        raw_difference=True,
        proportional_difference=True,
        avg_by_day=True
    )