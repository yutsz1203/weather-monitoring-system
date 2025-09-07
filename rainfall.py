import requests
import pandas as pd
from datetime import datetime
from utils import rich_display_dataframe, countdown


def get_rainfall():
    pd.set_option("display.unicode.east_asian_width", True)
    url = "https://data.weather.gov.hk/weatherAPI/opendata/hourlyRainfall.php"

    # First fetch to initialize variables
    average_rainfall = 0
    max_rainfall = 0
    max_station = ""
    init_df = pd.read_csv("data/rainfall/init_rainfall.csv")

    while True:
        response = requests.get(url, params={"lang": "tc"})
        data = response.json()

        df = pd.DataFrame(data["hourlyRainfall"])
        df.drop(columns=["automaticWeatherStationID", "unit"], inplace=True)
        df.rename(columns={"automaticWeatherStation": "Location"}, inplace=True)
        df["value"] = pd.to_numeric(df["value"], errors='coerce').astype("Int64")
        df["change"] = (df["value"] - init_df["value"]).astype("Int64")
        
        df["yellow"] = 0
        df["red"] = 0
        df["black"] = 0
        df.loc[df["value"] >= 30, "yellow"] = 1
        df.loc[df["value"] >= 50, "red"] = 1
        df.loc[df["value"] >= 70, "black"] = 1

        df.sort_values(by=["value", "change"], ascending=False, inplace=True) 

        minute = (datetime.now().minute // 15)*15
        nearest_time = datetime.now().replace(minute=minute, second=0, microsecond=0)
        print(f"As at {nearest_time}: ")

        latest_average_rainfall = int(df["value"].mean())
        if latest_average_rainfall >= average_rainfall:
            print(f"The average rainfall is: {latest_average_rainfall} mm (+{latest_average_rainfall-average_rainfall})mm") 
        else:
            print(f"The average rainfall is: {latest_average_rainfall} mm (-{average_rainfall-latest_average_rainfall})mm")
        average_rainfall = latest_average_rainfall

        latest_max_rainfall = df["value"].max()
        latest_max_station = df.loc[df["value"].idxmax(), "Location"]    
        if latest_max_rainfall >= max_rainfall:
            print(f"The maximum rainfall is: {latest_max_rainfall} mm (+{latest_max_rainfall-max_rainfall})mm at {latest_max_station}")
        else:
            print(f"The maximum rainfall is: {latest_max_rainfall} mm (-{max_rainfall-latest_max_rainfall})mm at {latest_max_station}")

        max_rainfall = latest_max_rainfall

        if latest_max_station != max_station:
            print(f"The station with the maximum rainfall has changed from {max_station} to {latest_max_station}")
            max_station = latest_max_station
        else:
            print(f"The station with the maximum rainfall remains {max_station}")
        yellow_count = df["yellow"].sum()
        red_count = df["red"].sum()
        black_count = df["black"].sum()
        total = len(df)
        print(f"{yellow_count}/{total}({int(yellow_count/total * 100)}%) of stations satisfy condition for yellow rain warning (>30 mm)")
        print(f"{red_count}/{total}({int(red_count/total * 100)}%) of stations satisfy condition for red rain warning (>50 mm)")
        print(f"{black_count}/{total}({int(black_count/total * 100)}%) of stations satisfy condition for black rain warning (>70 mm)")
        print("*" * 70)

        rich_display_dataframe(df, title=f"Rainfall as at {nearest_time}")
        init_df = df.copy()
        nearest_time = nearest_time.strftime("%H:%M").replace(":", "")
        df.to_csv(f"data/rainfall/latest_rainfall.csv", index=False)
        
        
        countdown(15)

if __name__ == "__main__":
    get_rainfall()