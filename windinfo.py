import pandas as pd
import numpy as np
from datetime import datetime
from utils import rich_display_dataframe, countdown


def get_windinfo():
    pd.set_option("display.unicode.east_asian_width", True)
    url = "https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_10min_wind_uc.csv"
    init_df = pd.read_csv("data/windinfo/init_windinfo.csv")

    while True:
        df = pd.read_csv(url, encoding="utf-8")
        df.drop(df.columns[0], axis=1, inplace=True)
        df.columns = [
            "Location",
            "Mean Wind Direction",
            "Mean Speed(km/h)",
            "Max Gust(km/h)",
        ]

        last_mean_mean_speed = round(init_df["Mean Speed(km/h)"].mean(), 2)
        last_mean_max_gust = round(init_df["Max Gust(km/h)"].mean(), 2)
        last_max_mean_speed = init_df["Mean Speed(km/h)"].max()
        last_max_max_gust = init_df["Max Gust(km/h)"].max()
        last_max_mean_speed_station = init_df.loc[
            init_df["Mean Speed(km/h)"].idxmax(), "Location"
        ]
        last_max_max_gust_station = init_df.loc[
            init_df["Max Gust(km/h)"].idxmax(), "Location"
        ]

        now_mean_mean_speed = round(df["Mean Speed(km/h)"].mean(), 2)
        now_mean_max_gust = round(df["Max Gust(km/h)"].mean(), 2)
        now_max_mean_speed = df["Mean Speed(km/h)"].max()
        now_max_max_gust = df["Max Gust(km/h)"].max()
        now_max_mean_speed_station = df.loc[df["Mean Speed(km/h)"].idxmax(), "Location"]
        now_max_max_gust_station = df.loc[df["Max Gust(km/h)"].idxmax(), "Location"]

        minute = (datetime.now().minute // 10) * 10
        nearest_time = datetime.now().replace(minute=minute, second=0, microsecond=0)
        print(f"As at {nearest_time}: ")
        print(df.value_counts("Mean Wind Direction"))
        print("*" * 70)
        if now_mean_mean_speed >= last_mean_mean_speed:
            print(
                f"The average mean speed is: {now_mean_mean_speed} km/h (+{round(now_mean_mean_speed-last_mean_mean_speed,2)} km/h)"
            )
        else:
            print(
                f"The average mean speed is: {now_mean_mean_speed} km/h (-{round(last_mean_mean_speed-now_mean_mean_speed,2)} km/h)"
            )
        if now_max_mean_speed >= last_max_mean_speed:
            print(
                f"The maximum mean speed is: {now_max_mean_speed} km/h (+{round(now_max_mean_speed - last_max_mean_speed,2)} km/h) at {now_max_mean_speed_station}"
            )
        else:
            print(
                f"The maximum mean speed is: {now_max_mean_speed} km/h (-{round(last_max_mean_speed - now_max_mean_speed,2)} km/h) at {now_max_mean_speed_station}"
            )
        if now_max_mean_speed_station != last_max_mean_speed_station:
            print(
                f"The station with the maximum mean speed has changed from {last_max_mean_speed_station} to {now_max_mean_speed_station}"
            )
        else:
            print(
                f"The station with the maximum rainfall remains {now_max_mean_speed_station}"
            )
        print("*" * 70)

        if now_mean_max_gust >= last_mean_max_gust:
            print(
                f"The average max gust is: {now_mean_max_gust} km/h (+{round(now_mean_max_gust-last_mean_max_gust,2)} km/h)"
            )
        else:
            print(
                f"The average max gust is: {now_mean_max_gust} km/h (-{round(last_mean_max_gust-now_mean_max_gust,2)} km/h)"
            )
        if now_max_max_gust >= last_max_max_gust:
            print(
                f"The maximum max gust is: {now_max_max_gust} km/h (+{round(now_max_max_gust - last_max_max_gust,2)} km/h) at {now_max_max_gust_station}"
            )
        else:
            print(
                f"The maximum max gust is: {now_max_max_gust} km/h (-{round(last_max_max_gust - now_max_max_gust,2)} km/h) at {now_max_max_gust_station}"
            )
        if now_max_max_gust_station != last_max_max_gust_station:
            print(
                f"The station with the maximum max gust has changed from {last_max_max_gust_station} to {now_max_max_gust_station}"
            )
        else:
            print(
                f"The station with the maximum max gust remains {now_max_max_gust_station}"
            )
        print("*" * 70)

        valid_mean_speed_stations = df["Mean Speed(km/h)"].count()
        valid_max_gust_stations = df["Max Gust(km/h)"].count()
        mean_speed_3 = len(df[df["Mean Speed(km/h)"] >= 41])
        max_gust_3 = len(df[df["Max Gust(km/h)"] > 110])
        mean_speed_8 = len(df[df["Mean Speed(km/h)"] >= 63])
        max_gust_8 = len(df[df["Max Gust(km/h)"] >= 180])
        mean_speed_10 = len(df[df["Mean Speed(km/h)"] > 118])
        max_gust_10 = len(df[df["Max Gust(km/h)"] > 220])

        print(
            f"{mean_speed_3}/{valid_mean_speed_stations}({int(mean_speed_3/valid_mean_speed_stations * 100)}%) of stations satisfy condition for No.3 signal (Mean speed 41-62)"
        )
        print(
            f"{max_gust_3}/{valid_mean_speed_stations}({int(max_gust_3/valid_max_gust_stations * 100)}%) of stations satisfy condition for No.3 signal (Max gust > 110)"
        )
        print(
            f"{mean_speed_8}/{valid_mean_speed_stations}({int(mean_speed_8/valid_mean_speed_stations * 100)}%) of stations satisfy condition for No.8 signal (Mean speed 63-117)"
        )
        print(
            f"{max_gust_8}/{valid_mean_speed_stations}({int(max_gust_3/valid_max_gust_stations * 100)}%) of stations satisfy condition for No.8 signal (Max gust > 180)"
        )
        print(
            f"{mean_speed_10}/{valid_mean_speed_stations}({int(mean_speed_10/valid_mean_speed_stations * 100)}%) of stations satisfy condition for No.10 signal (Mean speed >=118)"
        )
        print(
            f"{max_gust_10}/{valid_mean_speed_stations}({int(max_gust_10/valid_max_gust_stations * 100)}%) of stations satisfy condition for No.10 signal (Max gust > 220)"
        )

        print("*" * 70)

        df["Mean Speed Change(km/h)"] = (
            df["Mean Speed(km/h)"] - init_df["Mean Speed(km/h)"]
        )
        df["Max Gust Change(km/h)"] = df["Max Gust(km/h)"] - init_df["Max Gust(km/h)"]

        df["Mean Speed(km/h)"] = df["Mean Speed(km/h)"].astype("Int64")
        df["Max Gust(km/h)"] = df["Max Gust(km/h)"].astype("Int64")
        df["Mean Speed Change(km/h)"] = df["Mean Speed Change(km/h)"].astype("Int64")
        df["Max Gust Change(km/h)"] = df["Max Gust Change(km/h)"].astype("Int64")

        df = df.replace(np.nan, pd.NA)

        df = df.reindex(
            columns=[
                "Location",
                "Mean Wind Direction",
                "Mean Speed(km/h)",
                "Mean Speed Change(km/h)",
                "Max Gust(km/h)",
                "Max Gust Change(km/h)",
            ]
        )
        df.sort_values(
            by=["Mean Speed(km/h)", "Max Gust(km/h)"], ascending=False, inplace=True
        )
        rich_display_dataframe(df, title=f"Wind info as at {nearest_time}")

        df["Mean Speed(km/h)"] = df["Mean Speed(km/h)"].replace(pd.NA, 0)
        df["Max Gust(km/h)"] = df["Max Gust(km/h)"].replace(pd.NA, 0)
        init_df = df.copy()
        df.to_csv("data/windinfo/latest_windinfo.csv", index=False)

        eight_stations = [
            "長洲",
            "赤鱲角",
            "青衣",
            "流浮山",
            "啟德",
            "沙田",
            "西貢",
            "打鼓嶺",
        ]
        eight_stations_df = df[df["Location"].isin(eight_stations)]

        rich_display_dataframe(
            eight_stations_df, title=f"Eight Stations wind info as at {nearest_time}"
        )
        countdown(10)


if __name__ == "__main__":
    get_windinfo()
