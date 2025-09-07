import pandas as pd

pd.set_option("display.unicode.east_asian_width", True)
url = "https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_10min_wind_uc.csv"
df = pd.read_csv(url, encoding="utf-8")
df.drop(df.columns[0], axis=1, inplace=True)
df.columns = ["Location", "Mean Wind Direction", "Mean Speed(km/h)", "Max Gust(km/h)"]
df["Mean Speed(km/h)"] = 0
df["Max Gust(km/h)"] = 0
df.to_csv("data/windinfo/init_windinfo.csv")