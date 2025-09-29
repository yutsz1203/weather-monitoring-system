import threading

import pandas as pd
import requests
import xmltodict

from utils import countdown, get_distance_from_lat_lon_km


def get_data(url):
    try:
        source = requests.get(url)
        data = xmltodict.parse(source.content)["TropicalCycloneTrack"]["WeatherReport"]
        return data
    except requests.RequestException:
        return None


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
    processed_df["Latitude"] = processed_df["Latitude"].apply(
        lambda s: round(float(s[:-1]), 1)
    )
    processed_df["Longitude"] = processed_df["Longitude"].apply(
        lambda s: round(float(s[:-1]), 1)
    )

    processed_df["DistanceToHK"] = processed_df.apply(
        lambda row: int(
            round(get_distance_from_lat_lon_km(row["Latitude"], row["Longitude"]), -1)
        ),
        axis=1,
    )

    return processed_df


def get_cyclones():
    url = "https://www.weather.gov.hk/wxinfo/currwx/tc_list.xml"
    source = requests.get(url)
    data = xmltodict.parse(source.content)

    cyclones = data["TropicalCycloneList"]["TropicalCyclone"]
    cyclone_list = []
    if isinstance(cyclones, list):
        for cyclone in cyclones:
            cyclone_list.append(cyclone["TropicalCycloneURL"])

    elif isinstance(cyclones, dict):
        return [cyclones["TropicalCycloneURL"]]

    return cyclone_list


def get_cyclone_movement(data, issued_signal):
    cyclone_name = data["TropicalCycloneName"]
    curr_information = data["AnalysisInformation"]

    if not issued_signal:
        past_information = data["PastInformation"]
        for past in past_information:
            del past["Index"]
        past_information.append(curr_information)
        track_df = pd.DataFrame(past_information)
        track_df = process_cyclone_dataframe(track_df)
    else:
        track_df = pd.read_excel(
            f"data/tropicalCyclones/{cyclone_name}/{cyclone_name}_track.xlsx"
        )
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
    track_df.to_excel(
        f"data/tropicalCyclones/{cyclone_name}/{cyclone_name}_track.xlsx", index=False
    )

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
    forecast_df["MaximumWind"] = (
        forecast_df["MaximumWind"].ffill().fillna(curr_maximum_wind)
    )
    forecast_df["Intensity"] = forecast_df["Intensity"].ffill().fillna(curr_intensity)

    forecast_df = process_cyclone_dataframe(forecast_df, False)
    time = curr_information["Time"]
    start = pd.to_datetime(time, utc=True).tz_convert("Asia/Hong_Kong") + pd.Timedelta(
        hours=1
    )
    timestamps = pd.date_range(start=start, periods=len(forecast_df), freq="h")
    forecast_df["Time"] = timestamps.strftime("%Y-%m-%dHKT%H:%M")
    forecast_df.to_excel(
        f"data/tropicalCyclones/{cyclone_name}/{cyclone_name}_forecast.xlsx", index=False
    )


def get_cyclone_info(url, issued_signal):
    while True:
        data = get_data(url)
        if data:
            cyclone_name = data["TropicalCycloneName"]
            curr_information = data["AnalysisInformation"]
            curr_lat = float(curr_information["Latitude"][:-1])
            curr_long = float(curr_information["Longitude"][:-1])

            prev_lat, prev_long = 0.0, 0.0

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

            print(
                f"Latitude: {abs(lat_diff)} {lat_dir}; Longitude: {abs(long_diff)}  {long_dir}"
            )

            prev_forecast = data["ForecastInformation"][0]
            prev_lat = float(prev_forecast["Latitude"][:-1])
            prev_long = float(prev_forecast["Longitude"][:-1])

            get_cyclone_movement(data, issued_signal)
            get_cyclone_forecast(data)

            if issued_signal:
                countdown(60, "cycloneTracking")
            else:
                break
        else:
            print(f"{cyclone_name} no longer exists.")
            break


if __name__ == "__main__":
    cyclones = get_cyclones()

    if len(cyclones) > 1:
        thread_list = []
        issued_signal = []
        for cyclone in cyclones:
            data = get_data(cyclone)
            if data:
                cyclone_name = data["TropicalCycloneName"]
                issued = input(
                    f"Is Tropical Cyclone Warning Signal No. 1 or above in force for {cyclone_name}? (y/n): "
                ).lower()
                while True:
                    if issued == "y":
                        issued_signal.append(True)
                        break
                    elif issued == "n":
                        issued_signal.append(False)
                        break
                    else:
                        print("Invalid input. Please enter y or n.")

        for idx, cyclone in enumerate(cyclones):
            print(cyclone)
            t = threading.Thread(
                target=get_cyclone_info, args=(cyclone, issued_signal[idx])
            )
            thread_list.append(t)
            t.start()

        for thread in thread_list:
            thread.join()

    else:
        cyclone = cyclones[0]
        data = get_data(cyclone)
        if data:
            cyclone_name = data["TropicalCycloneName"]
            issued = input(
                f"Is Tropical Cyclone Warning Signal No. 1 or above in force for {cyclone_name}? (y/n): "
            ).lower()
            while True:
                if issued == "y":
                    issued_signal = True
                    break
                elif issued == "n":
                    issued_signal = False
                    break
                else:
                    print("Invalid input. Please enter y or n.")

            get_cyclone_info(cyclone, issued_signal)
