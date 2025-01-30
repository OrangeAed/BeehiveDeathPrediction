from datetime import datetime
from TemperatureAnalysis.collect_data import CollectData


def get_2022_hives(jefferson_hives: bool = True):
    cd = CollectData()
    hives = cd.get_hivenames(include_pop_designator=False)
    jh = get_2022_jefferson_hives()
    hives = [hive for hive in hives if not (len(hive[7:]) == 3 and int(hive[8]) > 2)]
    if not jefferson_hives:
        hives = [hive for hive in hives if hive not in jh]
    return hives


def get_2022_jefferson_hives():
    return [
        "AppMAIS1L",
        "AppMAIS1R",
        "AppMAIS2L",
        "AppMAIS2R"
    ]


def get_2022_deaths_late(jefferson_hives: bool = True):
    deaths = {
        "AppMAIS3L": datetime(2022, 12, 19),
        "AppMAIS3R": datetime(2022, 8, 21),
        "AppMAIS4L": datetime(2023, 3, 10),
        "AppMAIS4R": datetime(2023, 3, 13),
        "AppMAIS5L": datetime(2023, 4, 3),
        "AppMAIS6R": datetime(2023, 2, 3),
        "AppMAIS8L": datetime(2023, 4, 2),
        "AppMAIS9L": datetime(2023, 4, 10),
        "AppMAIS10L": datetime(2022, 9, 13),
        "AppMAIS10R": datetime(2023, 1, 10),
        "AppMAIS11R": datetime(2022, 11, 7),
        "AppMAIS12L": datetime(2023, 1, 11),
    }
    if jefferson_hives:
        deaths["AppMAIS1L"] = datetime(2023, 5, 3)
        deaths["AppMAIS2R"] = datetime(2023, 4, 7)

    return deaths


def get_2022_deaths_early(jefferson_hives: bool = True):
    deaths = {
        "AppMAIS3L": datetime(2022, 10, 26),
        "AppMAIS3R": datetime(2022, 8, 9),
        "AppMAIS4L": datetime(2023, 2, 24),
        "AppMAIS4R": datetime(2023, 2, 15),
        "AppMAIS5L": datetime(2022, 10, 31),
        "AppMAIS6R": datetime(2022, 10, 29),
        "AppMAIS8L": datetime(2023, 2, 17),
        "AppMAIS9L": datetime(2022, 10, 30),
        "AppMAIS10L": datetime(2022, 8, 23),
        "AppMAIS10R": datetime(2022, 11, 9),
        "AppMAIS11R": datetime(2022, 11, 7),
        "AppMAIS12L": datetime(2022, 10, 30),
    }
    if jefferson_hives:
        deaths["AppMAIS1L"] = datetime(2023, 3, 31)
        deaths["AppMAIS2R"] = datetime(2022, 10, 26)

    return deaths


def get_2022_survived(jefferson_hives: bool = True):
    survived = [
        "AppMAIS5R",
        "AppMAIS6L",
        "AppMAIS7L",
        "AppMAIS7R",
        "AppMAIS8R",
        "AppMAIS9R",
        "AppMAIS11L",
        "AppMAIS12R",
    ]
    if jefferson_hives:
        survived.append("AppMAIS1R")
        survived.append("AppMAIS2L")

    return survived

def get_2022_opposing_pairs(jefferson_hives: bool = True) -> list[tuple[str, str]]:
    # the left (first) tuple value will be the hive that survived
    pairs = [
        # ("AppMAIS5R", "AppMAIS5L"),
        ("AppMAIS6L", "AppMAIS6R"),
        ("AppMAIS8R", "AppMAIS8L"),
        ("AppMAIS9R", "AppMAIS9L"),
        ("AppMAIS11L", "AppMAIS11R"),
        ("AppMAIS12R", "AppMAIS12L")
    ]
    if jefferson_hives:
        jefferson_pairs = [("AppMAIS1R", "AppMAIS1L"), ("AppMAIS2L", "AppMAIS2R")]
        pairs = jefferson_pairs + pairs

    return pairs


def get_2022_all_pairs(jefferson_hives: bool = True) -> list[tuple[str, str]]:
    # pairs = get_2022_opposing_pairs(jefferson_hives)
    pairs = []
    if jefferson_hives:
        pairs += [
            ("AppMAIS1R", "AppMAIS1L"),
            ("AppMAIS2L", "AppMAIS2R")
        ]
    pairs += [
        ("AppMAIS3L", "AppMAIS3R"),
        ("AppMAIS4L", "AppMAIS4R"),
        ("AppMAIS5R", "AppMAIS5L"),
        ("AppMAIS6L", "AppMAIS6R"),
        ("AppMAIS7L", "AppMAIS7R"),
        ("AppMAIS8R", "AppMAIS8L"),
        ("AppMAIS9R", "AppMAIS9L"),
        ("AppMAIS10R", "AppMAIS10L"),
        ("AppMAIS11L", "AppMAIS11R"),
        ("AppMAIS12R", "AppMAIS12L")
    ]
    return pairs

def get_2023_hives(jefferson_hives: bool = True):
    cd = CollectData()
    hives = cd.get_hivenames(include_pop_designator=False)
    jh = get_2022_jefferson_hives()
    hives = [hive for hive in hives if not (len(hive[7:]) == 3 and int(hive[8]) > 6)]
    if not jefferson_hives:
        hives = [hive for hive in hives if hive not in jh]
    return hives


def get_2023_jefferson_hives():
    get_2022_jefferson_hives()


def get_2023_belgium_hives():
    return [
        'AppMAIS14L',
        'AppMAIS14R',
        'AppMAIS15L'
    ]


def get_2023_survived(jefferson_hives: bool = True, belgium_hives: bool = False):
    survived = [

        "AppMAIS3LB",
        "AppMAIS3RB",
        "AppMAIS4LB",
        "AppMAIS5LB",
        "AppMAIS6L",
        "AppMAIS6RC",
        "AppMAIS8R",
        "AppMAIS10LB",
        "AppMAIS10R",
        "AppMAIS11L",
        "AppMAIS12L",
        "AppMAIS12R",
        "AppMAIS16LB",
        "AppMAIS16R"
    ]
    if jefferson_hives:
        survived += [
            "AppMAIS1LB",
            "AppMAIS2R",
            "AppMAIS2RC"
        ]
    if belgium_hives:
        survived += [
            "AppMAIS14L",
            "AppMAIS14R"
        ]
    return survived


def get_2023_deaths_early(jefferson_hives: bool = True, belgium_hives: bool = False):
    deaths = get_2023_deaths_late(jefferson_hives, belgium_hives)
    if jefferson_hives:
        deaths["AppMAIS1R"] = datetime(2023, 10, 20)
    deaths["AppMAIS5R"] = datetime(2023, 10, 20)
    deaths["AppMAIS7L"] = datetime(2023, 11, 17)
    deaths["AppMAIS7R"] = datetime(2023, 10, 15)
    deaths["AppMAIS9LB"] = datetime(2023, 11, 14)
    deaths["AppMAIS13L"] = datetime(2023, 11, 3)
    if belgium_hives:
        deaths["AppMAIS15R"] = datetime(2023, 11, 15)


def get_2023_deaths_late(jefferson_hives: bool = True, belgium_hives: bool = False):
    deaths = {
        "AppMAIS4RB": datetime(2024, 5, 21),
        "AppMAIS5R": datetime(2023, 11, 15),
        "AppMAIS7L": datetime(2023, 11, 20),
        "AppMAIS7R": datetime(2023, 10, 20),
        "AppMAIS8LB": datetime(2024, 5, 21),
        "AppMAIS9LB": datetime(2023, 11, 15),
        # "AppMAIS9R": datetime(), removing this one because we do not have a good idea of when it died
        # "AppMAIS11RB": datetime(), ^^ same here
        "AppMAIS13L": datetime(2024, 1, 2),
    }
    if jefferson_hives:
        deaths["AppMAIS1R"] = datetime(2023, 10, 30)
    if belgium_hives:
        deaths["AppMAIS14L"] = datetime(2023, 4, 3)
        deaths["AppMAIS15R"] = datetime(2024, 1, 2)
    return deaths


def get_2023_opposing_pairs(jefferson_hives: bool = True, belgium_hives: bool = False) -> list[tuple[str, str]]:
    pairs = [
        ("AppMAIS5LB", "AppMAIS5R"),
        ("AppMAIS8R", "AppMAIS8LB"),
        ("AppMAIS13R", "AppMAIS13L")
    ]
    if jefferson_hives:
        pairs += [
            ("AppMAIS1LB", "AppMAIS1R")
        ]
    return pairs


def get_start_and_end_dates(year: int):
    if year == 2022:
        return {
            "start": datetime(2022, 4, 10),
            "end": datetime(2023, 4, 20)
        }
    elif year == 2023:
        return {
            "start": datetime(2023, 4, 22),
            "end": datetime(2024, 4, 6)
        }
    else:
        raise ValueError("Year must be 2022 or 2023")