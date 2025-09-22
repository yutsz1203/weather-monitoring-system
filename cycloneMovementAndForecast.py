import pandas as pd
import requests
import xmltodict
from utils import get_distance_from_lat_lon_km


def process_cyclone_dataframe(df):
    processed_df = df.copy()

    processed_df["MaximumWind"] = processed_df["MaximumWind"].str[:-4].astype(int)
    processed_df["Time"] = (
        processed_df["Time"].str[:10]
        + "HKT"
        + ((processed_df["Time"].str[11:13].astype(int) + 8) % 24)
        .astype(str)
        .str.zfill(2)
        + ":00"
    )
    processed_df["Latitude"] = processed_df["Latitude"].str[:-1].astype(float)
    processed_df["Longitude"] = processed_df["Longitude"].str[:-1].astype(float)

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


def get_cyclone_movement_and_forecast(url, init=False):
    source = requests.get(url)
    data = xmltodict.parse(source.content)["TropicalCycloneTrack"]["WeatherReport"]

    name = data["TropicalCycloneName"]
    curr_information = data["AnalysisInformation"]

    if init:
        past_information = data["PastInformation"]
        for past in past_information:
            del past["Index"]
        past_information.append(curr_information)
        track_df = pd.DataFrame(past_information)
        track_df = process_cyclone_dataframe(track_df)
    else:
        track_df = pd.read_excel("data/typhoon/cyclone_track.xlsx")
        maxwind = int(curr_information["MaximumWind"][:-4])
        curr_hour = str((int(curr_information["Time"][11:13]) + 8) % 24).zfill(2)
        time = f"{curr_information["Time"][:10]}HKT{curr_hour}:00"
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

    print(track_df)
    track_df.to_excel("data/typhoon/cyclone_track.xlsx", index=False)

    print(f"Latest updates for {name}:\n{track_df.iloc[-1]}")

    forecast_information = data["ForecastInformation"]
    for forecast in forecast_information:
        del forecast["Index"]
    forecast_df = pd.DataFrame(forecast_information)
    forecast_df = forecast_df.fillna({"MaximumWind": "0 km/h"})
    # forecast_df = process_cyclone_dataframe(forecast_df)
    forecast_df.to_excel("data/typhoon/cyclone_forecast.xlsx", index=False)


if __name__ == "__main__":
    # get_cyclone_url()
    get_cyclone_movement_and_forecast(
        "http://www.weather.gov.hk/wxinfo/currwx/hko_tctrack_2528.xml"
    )
