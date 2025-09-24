import pandas as pd
import numpy as np
from utils import countdown

def track_sea_level(init=False):
    pd.set_option("display.unicode.east_asian_width", True)
    sea_level_data = "https://data.weather.gov.hk/weatherAPI/hko_data/tide/ALL_tc.csv"
    df = pd.read_csv(sea_level_data, encoding="utf-8")
    date = df.iat[0, 1]
    day = date[-2:]
    month = date[5:7]
    year = date[:4]

    time = df.iat[0, 2]
    df.drop(df.columns[[1,2]], axis=1, inplace=True)
    df.columns = ["Location", "Max_Sea_Level(m)"]
    df["Max_Sea_Level_Time"] = f"{day}/{month}/{year} {time}"
    df["Max_Sea_Level(m)"] = np.where(df["Max_Sea_Level(m)"] == "----", "0.0", df["Max_Sea_Level(m)"])

    if init:
        df.to_excel("data/typhoon/tides_record.xlsx", index=False)
        return

    record_df = pd.read_excel("data/typhoon/tides_record.xlsx")
    record_df["Max_Sea_Level(m)"] = record_df["Max_Sea_Level(m)"].where(record_df["Max_Sea_Level(m)"].astype(float) >= df["Max_Sea_Level(m)"].astype(float), df["Max_Sea_Level(m)"])
    record_df["Max_Sea_Level_Time"] = np.where(df["Max_Sea_Level(m)"].astype(float) >= record_df["Max_Sea_Level(m)"].astype(float),df["Max_Sea_Level_Time"],record_df["Max_Sea_Level_Time"])

    record_df.to_excel("data/typhoon/tides_record.xlsx", index=False)

if __name__ == "__main__":
    while True:
        track_sea_level()
        countdown(5)