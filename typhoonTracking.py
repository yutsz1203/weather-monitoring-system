import pandas as pd
import numpy as np
from datetime import datetime
from utils import rich_display_dataframe, countdown

def get_wind_scale(speed):
    if speed >= 118:
        return 12
    if speed >= 104:
        return 11
    if speed >= 88:
        return 10
    if speed >= 76:
        return 9
    if speed >= 63:
        return 8
    if speed >= 52:
        return 7
    if speed >= 41:
        return 6
    if speed >= 31:
        return 5
    if speed >= 20:
        return 4
    if speed >= 13:
        return 3
    if speed >= 7:
        return 2
    if speed >= 2:
        return 1
    return 0

def pad_chinese_string(s, target_width):
    if pd.isna(s):
        s = ""  
    current_width = sum(2 if '\u4e00' <= char <= '\u9fff' else 1 for char in str(s))
    padding_needed = target_width - current_width
    if padding_needed < 0:
        return s
    return s + ' ' * padding_needed

def typhoon_tracking():
    pd.set_option("display.unicode.east_asian_width", True)
    wind_data = "https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_10min_wind_uc.csv"
    pressure_data = "https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_1min_pressure_uc.csv"

    while True:
        wind_df = pd.read_csv(wind_data, encoding="utf-8")
        current_time = str(wind_df.iloc[0]["日期時間"])
        date_time = f"{current_time[0:4]}/{current_time[4:6]}/{current_time[6:8]} {current_time[8:10]}:{current_time[10:]}"

        wind_df.drop(wind_df.columns[0], axis=1, inplace=True)
        wind_df.columns = [
            "Location",
            "Mean_Wind_Direction",
            "Mean_Speed(km/h)",
            "Max_Gust(km/h)",
        ]

        # print(wind_df)
        
        direction_counts = wind_df.value_counts("Mean_Wind_Direction")
        max_count = direction_counts.max()
        wind_directions = direction_counts[direction_counts==max_count].index.tolist()

        # generating lists of stations based on wind scale
        hurricane_mean_speed, hurricane_max_gust = [], []
        storm_mean_speed, storm_max_gust = [], []
        gale_mean_speed, gale_max_gust = [], []
        strong_mean_speed, strong_max_gust = [], []

        for station, direction, mean_speed, max_gust in wind_df.itertuples(index=False):
            if mean_speed >= 118:
                hurricane_mean_speed.append(station)
            elif mean_speed >= 88:
                storm_mean_speed.append(station)
            elif mean_speed >= 63:
                gale_mean_speed.append(station)
            elif mean_speed >= 41:
                strong_mean_speed.append(station)
            
            if max_gust >= 118:
                hurricane_max_gust.append(station)
            elif max_gust >= 88:
                storm_max_gust.append(station)
            elif max_gust >= 63:
                gale_max_gust.append(station)
            elif max_gust >= 41:
                strong_max_gust.append(station)
    
        # Output
        print(f"{date_time}\n")
        print(f"平均風向: {'、'.join(wind_directions)}")

        qualified_station = hurricane_mean_speed + hurricane_max_gust + storm_mean_speed + storm_max_gust + gale_mean_speed + gale_max_gust + strong_mean_speed + strong_max_gust
        qualified_station_set = set(qualified_station)

        qualified_df = wind_df[wind_df["Location"].isin(qualified_station_set)]
        qualified_df = qualified_df.sort_values(by="Mean_Speed(km/h)", ascending=False)

        for location, wind_direction, mean_speed, max_gust in qualified_df.itertuples(index=False):
            mean_speed_wind_scale = get_wind_scale(mean_speed)
            max_gust_wind_scale = get_wind_scale(max_gust)
            padded_location = pad_chinese_string(location, 12)
            padded_wind_dir = pad_chinese_string(wind_direction, 8)
            print(f"{padded_location} {padded_wind_dir} {int(mean_speed)}(F{mean_speed_wind_scale}) | {int(max_gust)}(F{max_gust_wind_scale})")

        print("")
        if len(hurricane_mean_speed) >= 1:
            print(f"颶風({len(hurricane_mean_speed)}): {'、'.join(hurricane_mean_speed)}")
        
        if len(hurricane_max_gust) >= 1:
            print(f"颶陣({len(hurricane_max_gust)}): {'、'.join(hurricane_max_gust)}")

        if len(storm_mean_speed) >= 1:
            print(f"暴風({len(storm_mean_speed)}): {'、'.join(storm_mean_speed)}")
        
        if len(storm_max_gust) >= 1:
            print(f"暴陣({len(storm_max_gust)}): {'、'.join(storm_max_gust)}")
        
        if len(gale_mean_speed) >= 1:
            print(f"烈風({len(gale_mean_speed)}): {'、'.join(gale_mean_speed)}")
        
        if len(gale_max_gust) >= 1:
            print(f"烈陣({len(gale_max_gust)}): {'、'.join(gale_max_gust)}")
        
        if len(strong_mean_speed) >= 1:
            print(f"強風({len(strong_mean_speed)}): {'、'.join(strong_mean_speed)}")
        
        if len(strong_max_gust) >= 1:
            print(f"強陣({len(strong_max_gust)}): {'、'.join(strong_max_gust)}")
        
        pressure_df = pd.read_csv(pressure_data, encoding="utf-8")
        pressure_df.drop(pressure_df.columns[0], axis=1, inplace=True)
        pressure_df.columns = [
            "Location",
            "Mean_Sea_Level_Pressure(hPa)"
        ]
        max_pressure = pressure_df["Mean_Sea_Level_Pressure(hPa)"].max()
        max_pressure_stations_df = pressure_df[pressure_df["Mean_Sea_Level_Pressure(hPa)"] == max_pressure]

        min_pressure = pressure_df["Mean_Sea_Level_Pressure(hPa)"].min()
        min_pressure_stations_df = pressure_df[pressure_df["Mean_Sea_Level_Pressure(hPa)"] == min_pressure]

        max_pressure_stations, min_pressure_stations = [], []

        for row in max_pressure_stations_df.itertuples(index=False):
            max_pressure_stations.append(row.Location)
        
        for row in min_pressure_stations_df.itertuples(index=False):
            min_pressure_stations.append(row.Location)

        print("")
        print(f"最低氣壓: {min_pressure} ({'、'.join(min_pressure_stations)})")
        print(f"最高氣壓: {max_pressure} ({'、'.join(max_pressure_stations)})")
        print("")
        print("24小時八站記錄:")

        countdown(10)
        print("")

if __name__ == "__main__":
    typhoon_tracking()