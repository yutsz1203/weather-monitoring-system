import pandas as pd
import numpy as np
from utils import countdown
from const import eight_stations

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

def typhoon_tracking(refresh, init=False):
    pd.set_option("display.unicode.east_asian_width", True)
    wind_data = "https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_10min_wind_uc.csv"
    pressure_data = "https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_1min_pressure_uc.csv"

    while True:
        wind_df = pd.read_csv(wind_data, encoding="utf-8")
        current_time = str(wind_df.iloc[0]["日期時間"])
        year = current_time[0:4]
        month = current_time[4:6]
        date = current_time[6:8]
        hour = current_time[8:10]
        minute = current_time[10:]
        date_time = f"{date}/{month}/{year} {hour}:{minute}"

        wind_df.drop(wind_df.columns[0], axis=1, inplace=True)
        wind_df.columns = [
            "Location",
            "Mean_Wind_Direction",
            "Mean_Speed(km/h)",
            "Max_Gust(km/h)",
        ]

        wind_df = wind_df.sort_values(by="Mean_Speed(km/h)", ascending=False)

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
        
        qualified_station = hurricane_mean_speed + hurricane_max_gust + storm_mean_speed + storm_max_gust + gale_mean_speed + gale_max_gust + strong_mean_speed + strong_max_gust
        qualified_station_set = set(qualified_station)

        qualified_df = wind_df[wind_df["Location"].isin(qualified_station_set)]
        
        # Getting max and min pressure
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

        if refresh:
            eight_station_df = wind_df[wind_df["Location"].isin(eight_stations)].copy()
            eight_station_df.loc[:,"Mean_Speed_time"] = f"{hour}:{minute}"
            eight_station_df.loc[:,"Max_Gust_time"] = f"{hour}:{minute}"
            new_order = ["Location", 
                         "Mean_Wind_Direction",
                         "Mean_Speed(km/h)",
                         "Mean_Speed_time",
                         "Max_Gust(km/h)",
                         "Max_Gust_time"
                         ]
            eight_station_df = eight_station_df.reindex(columns=new_order)
            refresh = False
            # print(eight_station_df)
            
        else:
            eight_station_df = pd.read_csv("data/windinfo/eight_station_record.csv")
            latest_eight_station_df = wind_df[wind_df["Location"].isin(eight_stations)].copy()
            latest_eight_station_df.loc[:,"Mean_Speed_time"] = f"{hour}:{minute}"
            latest_eight_station_df.loc[:,"Max_Gust_time"] = f"{hour}:{minute}"

            for station in latest_eight_station_df["Location"]:
                latest_station = latest_eight_station_df.loc[latest_eight_station_df["Location"] == station]
                current_station = eight_station_df.loc[eight_station_df["Location"] == station]
                
                latest_mean_speed = latest_station["Mean_Speed(km/h)"].iloc[0]
                curr_max_mean_speed = current_station["Mean_Speed(km/h)"].iloc[0]
                if latest_mean_speed > curr_max_mean_speed:
                    eight_station_df.loc[eight_station_df["Location"] == station, "Mean_Speed(km/h)"] = latest_mean_speed
                    eight_station_df.loc[eight_station_df["Location"] == station, "Mean_Speed_time"] = f"{hour}:{minute}"
                
                latest_max_gust = latest_station["Max_Gust(km/h)"].iloc[0]
                curr_max_max_gust = current_station["Max_Gust(km/h)"].iloc[0]
                if latest_max_gust > curr_max_max_gust:
                    eight_station_df.loc[eight_station_df["Location"] == station, "Max_Gust(km/h)"] = latest_max_gust
                    eight_station_df.loc[eight_station_df["Location"] == station, "Max_Gust_time"] = f"{hour}:{minute}"

        eight_station_df.sort_values(by="Mean_Speed(km/h)", inplace=True, ascending=False)
        eight_station_hurricane_mean_speed, eight_station_storm_mean_speed, eight_station_gale_mean_speed, eight_station_strong_mean_speed = [], [], [], []
        for station, _, mean_speed, _, _, _ in eight_station_df.itertuples(index=False):
            if mean_speed >= 118:
                eight_station_hurricane_mean_speed.append(station)
                eight_station_storm_mean_speed.append(station)
                eight_station_gale_mean_speed.append(station)
                eight_station_strong_mean_speed.append(station)
            elif mean_speed >= 88:
                eight_station_storm_mean_speed.append(station)
                eight_station_gale_mean_speed.append(station)
                eight_station_strong_mean_speed.append(station)
            elif mean_speed >= 63:
                eight_station_gale_mean_speed.append(station)
                eight_station_strong_mean_speed.append(station)
            elif mean_speed >= 41:
                eight_station_strong_mean_speed.append(station)
            
        # print(eight_station_df)
        eight_station_df.to_csv("data/windinfo/eight_station_record.csv", index=False)
        # Output
        print(f"{date_time}\n")
        print(f"平均風向: {'、'.join(wind_directions)}")
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

        print("")
        print(f"最低氣壓: {min_pressure} ({'、'.join(min_pressure_stations)})")
        print(f"最高氣壓: {max_pressure} ({'、'.join(max_pressure_stations)})\n")
        
        eight_station_status = []
        if len(eight_station_hurricane_mean_speed) >= 1:
            eight_station_status.append(f"颶風8中{len(eight_station_hurricane_mean_speed)}")
        if len(eight_station_storm_mean_speed) >= 1:
            eight_station_status.append(f"暴風8中{len(eight_station_storm_mean_speed)}")
        if len(eight_station_gale_mean_speed) >= 1:
            eight_station_status.append(f"烈風8中{len(eight_station_gale_mean_speed)}")
        if len(eight_station_strong_mean_speed) >= 1:
            eight_station_status.append(f"強風8中{len(eight_station_strong_mean_speed)}")

        print(f"24小時八站記錄: {'、'.join(eight_station_status)}")
        for location, _, mean_speed, mean_speed_time, max_gust, max_gust_time in eight_station_df.itertuples(index=False):
            padded_location = pad_chinese_string(location, 6)
            print(f"{padded_location} {int(mean_speed):3} ({mean_speed_time}) | {int(max_gust):3} ({max_gust_time})")


        if init:
            wind_record_df = wind_df.copy()
            wind_record_df.columns = ["Location", "Max_10_Min_Mean_Wind_Direction", "Max_10_Min_Mean_Speed(km/h)", "Max_Gust(km/h)"]
            wind_record_df["Max_10_Min_Mean_Speed_Time"] = date_time
            wind_record_df["Max_Gust_Direction"] = wind_record_df["Max_10_Min_Mean_Wind_Direction"]
            wind_record_df["Max_Gust_Time"] = date_time
            wind_record_df["Max_60_Min_Mean_Wind_Direction"] = wind_record_df["Max_10_Min_Mean_Wind_Direction"]
            wind_record_df["Max_60_Min_Mean_Speed(km/h)"] = round(wind_record_df["Max_10_Min_Mean_Speed(km/h)"] * 0.95)
            wind_record_df["Max_60_Min_Mean_Speed_Time"] = wind_record_df["Max_10_Min_Mean_Speed_Time"]
            new_order = ["Location", "Max_60_Min_Mean_Wind_Direction", "Max_60_Min_Mean_Speed(km/h)", "Max_60_Min_Mean_Speed_Time", "Max_Gust_Direction", "Max_Gust(km/h)", "Max_Gust_Time", "Max_10_Min_Mean_Wind_Direction", "Max_10_Min_Mean_Speed(km/h)", "Max_10_Min_Mean_Speed_Time"]
            wind_record_df = wind_record_df.reindex(columns=new_order)
            wind_record_df.to_excel("data/typhoon/wind_record.xlsx", index=False)

            pressure_record_df = pressure_df.copy()
            pressure_record_df["Time"] = date_time
            pressure_record_df.rename(columns={"Mean_Sea_Level_Pressure(hPa)" : "Min_Pressure(hPa)"}, inplace=True)
            pressure_record_df.to_excel("data/typhoon/sea_level_pressure_record.xlsx", index=False)

            init = False
        else:
            wind_record_df = pd.read_excel("data/typhoon/wind_record.xlsx")
            wind_record_df.sort_values(by="Location",inplace=True)
            wind_df.sort_values(by="Location",inplace=True)
            wind_record_df.reset_index(inplace=True, drop=True)
            wind_df.reset_index(inplace=True, drop=True)
            # print(wind_record_df.head())
            # print(wind_df.head())
            wind_df.columns = ["Location", "Mean_Wind_Direction", "10_Min_Mean_Speed(km/h)", "Max_Gust(km/h)"]
            wind_df["Mean_Speed_Time"] = date_time
            wind_df["60_Min_Mean_Wind_Direction"] = wind_df["Mean_Wind_Direction"]
            wind_df["60_Min_Mean_Speed(km/h)"] = round(wind_df["10_Min_Mean_Speed(km/h)"] * 0.95)
            wind_df["60_Min_Mean_Speed_Time"] = date_time
            wind_df["Max_Gust_Direction"] = wind_df["Mean_Wind_Direction"]
            wind_df["Max_Gust_Time"] = date_time

            wind_record_df["Max_60_Min_Mean_Wind_Direction"] = np.where(wind_df["60_Min_Mean_Speed(km/h)"] > wind_record_df["Max_60_Min_Mean_Speed(km/h)"], wind_df["60_Min_Mean_Wind_Direction"], wind_record_df["Max_60_Min_Mean_Wind_Direction"])
            wind_record_df["Max_60_Min_Mean_Speed_Time"] = np.where(wind_df["60_Min_Mean_Speed(km/h)"] > wind_record_df["Max_60_Min_Mean_Speed(km/h)"], wind_df["60_Min_Mean_Speed_Time"], wind_record_df["Max_60_Min_Mean_Speed_Time"])
            wind_record_df["Max_60_Min_Mean_Speed(km/h)"] = np.where(wind_df["60_Min_Mean_Speed(km/h)"] > wind_record_df["Max_60_Min_Mean_Speed(km/h)"], wind_df["60_Min_Mean_Speed(km/h)"], wind_record_df["Max_60_Min_Mean_Speed(km/h)"])
            

            wind_record_df["Max_Gust_Direction"] = np.where(wind_df["Max_Gust(km/h)"] > wind_record_df["Max_Gust(km/h)"], wind_df["Max_Gust_Direction"], wind_record_df["Max_Gust_Direction"])
            wind_record_df["Max_Gust_Time"] = np.where(wind_df["Max_Gust(km/h)"] > wind_record_df["Max_Gust(km/h)"], wind_df["Max_Gust_Time"], wind_record_df["Max_Gust_Time"])
            wind_record_df["Max_Gust(km/h)"] = np.where(wind_df["Max_Gust(km/h)"] > wind_record_df["Max_Gust(km/h)"], wind_df["Max_Gust(km/h)"], wind_record_df["Max_Gust(km/h)"])

            wind_record_df["Max_10_Min_Mean_Wind_Direction"] = np.where(wind_df["10_Min_Mean_Speed(km/h)"] > wind_record_df["Max_10_Min_Mean_Speed(km/h)"], wind_df["Mean_Wind_Direction"], wind_record_df["Max_10_Min_Mean_Wind_Direction"])
            wind_record_df["Max_10_Min_Mean_Speed_Time"] = np.where(wind_df["10_Min_Mean_Speed(km/h)"] > wind_record_df["Max_10_Min_Mean_Speed(km/h)"], wind_df["Mean_Speed_Time"], wind_record_df["Max_10_Min_Mean_Speed_Time"])
            wind_record_df["Max_10_Min_Mean_Speed(km/h)"] = np.where(wind_df["10_Min_Mean_Speed(km/h)"] > wind_record_df["Max_10_Min_Mean_Speed(km/h)"], wind_df["10_Min_Mean_Speed(km/h)"], wind_record_df["Max_10_Min_Mean_Speed(km/h)"])

            wind_record_df.to_excel("data/typhoon/wind_record.xlsx", index=False)

            pressure_record_df = pd.read_excel("data/typhoon/sea_level_pressure_record.xlsx")
            # print(pressure_record_df.head())
            # print(pressure_df.head())
            pressure_df["Time"] = date_time
            
            pressure_record_df["Time"] = np.where(pressure_df["Mean_Sea_Level_Pressure(hPa)"] < pressure_record_df["Min_Pressure(hPa)"], pressure_df["Time"], pressure_record_df["Time"])
            pressure_record_df["Min_Pressure(hPa)"] = np.where(pressure_df["Mean_Sea_Level_Pressure(hPa)"] < pressure_record_df["Min_Pressure(hPa)"], pressure_df["Mean_Sea_Level_Pressure(hPa)"], pressure_record_df["Min_Pressure(hPa)"])
            
            
            pressure_record_df.to_excel("data/typhoon/sea_level_pressure_record.xlsx", index=False)

        countdown(10)
        print("")

if __name__ == "__main__":
    while True:
        action = input("Refresh eight station wind record? (Y/N): ").lower()
        if action == "y":
            refresh = True
            break
        elif action == "n":
            refresh = False
            break
        else:
            print("Invalid input. Please enter Y or N.")

    typhoon_tracking(refresh)