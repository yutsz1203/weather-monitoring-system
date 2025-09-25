import numpy as np
import pandas as pd
import requests
import xmltodict

from utils import countdown, get_distance_from_lat_lon_km

def process_cyclone_dataframe(df, adjust_Time=True):
    processed_df = df.copy()    

    processed_df["MaximumWind"] = processed_df["MaximumWind"].str[:-4].astype(int)
    if adjust_Time:
        processed_df["Time"] = (
            processed_df["Time"].str[:10]
            + "HKT"
            + ((processed_df["Time"].str[11:13].astype(int) + 8) % 24)
            .astype(str)
            .str.zfill(2)
            + ":00"
        )
    processed_df["Latitude"] = processed_df["Latitude"].apply(lambda s: round(float(s[:-1]), 1))
    processed_df["Longitude"] = processed_df["Longitude"].apply(lambda s: round(float(s[:-1]), 1))

    processed_df["DistanceToHK"] = processed_df.apply(
        lambda row: int(
            round(get_distance_from_lat_lon_km(row["Latitude"], row["Longitude"]), -1)
        ),
        axis=1,
    )

    return processed_df


def get_cyclone_url():
    url = "https://www.weather.gov.hk/wxinfo/currwx/tc_list.xml"
    source = requests.get(url)
    data = xmltodict.parse(source.content)

    cyclones = data["TropicalCycloneList"].values()

    for cyclone in cyclones:
        print(cyclone["TropicalCycloneURL"])


def get_cyclone_movement(data, init=False):

    cyclone_name = data["TropicalCycloneName"]
    curr_information = data["AnalysisInformation"]

    if init:
        past_information = data["PastInformation"]
        for past in past_information:
            del past["Index"]
        past_information.append(curr_information)
        track_df = pd.DataFrame(past_information)
        track_df = process_cyclone_dataframe(track_df)
    else:
        track_df = pd.read_excel(f"data/typhoon/{cyclone_name}_track.xlsx")
        maxwind = int(curr_information["MaximumWind"][:-4])
        curr_hour = str((int(curr_information["Time"][11:13]) + 8) % 24).zfill(2)
        time = f'{curr_information["Time"][:10]}HKT{curr_hour}:00'
        lat = float(curr_information["Latitude"][:-1])
        lon = float(curr_information["Longitude"][:-1])
        dist = int(round(get_distance_from_lat_lon_km(lat, lon), -1))
        track_df.loc[len(track_df)] = [
            curr_information["Intensity"],
            maxwind,
            time,
            lat,
            lon,
            dist,
        ]

    print(track_df.tail())
    track_df.to_excel(f"data/typhoon/{cyclone_name}_movement.xlsx", index=False)

    print(f"Latest updates for {cyclone_name}:\n{track_df.iloc[-1]}")

def get_cyclone_forecast(data):

    cyclone_name = data["TropicalCycloneName"]
    curr_information = data["AnalysisInformation"]
    curr_intensity = curr_information["Intensity"]
    curr_maximum_wind = curr_information["MaximumWind"]

    forecast_information = data["ForecastInformation"]
    for forecast in forecast_information:
        if "Index" in forecast:
            del forecast["Index"]
        else:
            print(forecast)
    forecast_df = pd.DataFrame(forecast_information)
    forecast_df["MaximumWind"] = forecast_df["MaximumWind"].ffill().fillna(curr_maximum_wind)
    forecast_df["Intensity"] = forecast_df["Intensity"].ffill().fillna(curr_intensity)


    forecast_df = process_cyclone_dataframe(forecast_df, False)
    time = curr_information["Time"]
    start = pd.to_datetime(time, utc=True).tz_convert("Asia/Hong_Kong") + pd.Timedelta(hours=1)
    timestamps = pd.date_range(start=start, periods=len(forecast_df), freq='h')
    forecast_df["Time"] = timestamps.strftime('%Y-%m-%dHKT%H:%M')
    forecast_df.to_excel(f"data/typhoon/{cyclone_name}_forecast.xlsx", index=False)


if __name__ == "__main__":
    # get_cyclone_url()
    prev_lat, prev_long = 19.42, 120.9
    
    while True:
        url = "http://www.weather.gov.hk/wxinfo/currwx/hko_tctrack_2528.xml"
        source = requests.get(url)
        data = xmltodict.parse(source.content)["TropicalCycloneTrack"]["WeatherReport"]
        curr_information = data["AnalysisInformation"]
        curr_lat = float(curr_information["Latitude"][:-1])
        curr_long = float(curr_information["Longitude"][:-1])

        lat_diff = round(curr_lat - prev_lat, 2)
        long_diff = round(curr_long - prev_long, 2)

        if lat_diff > 0:
            lat_dir = "more north"
        elif lat_diff < 0:
            lat_dir = "more south"
        else:
            lat_dir = "(as forecasted)"
        
        if long_diff > 0:
            long_dir = "more east"
        elif long_diff < 0:
            long_dir = "more west"
        else:
            long_dir = "(as forecasted)"

        print(f"Latitude: {abs(lat_diff)} {lat_dir}; Longitude: {abs(long_diff)}  {long_dir}")
        
        prev_forecast = data["ForecastInformation"][0]
        prev_lat = float(prev_forecast["Latitude"][:-1])
        prev_long = float(prev_forecast["Longitude"][:-1])
        
        get_cyclone_movement(data)
        get_cyclone_forecast(data)
        countdown(60, type="cycloneTracking")
