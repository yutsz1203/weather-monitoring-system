import json
import time
import re
import urllib.request

from utils import countdown, get_distance_from_lat_lon_km


def typhoonWarning():
    last_lat, last_long, last_speed, last_dist, last_update_hour = (
        0.0,
        0.0,
        0.0,
        0.0,
        "0",
    )
    lat_diff, long_diff, speed_diff, dist_diff = 0.0, 0.0, 0.0, 0.0
    lat_direc, long_direc = "", ""
    speed_sign, dist_sign = "+", "+"

    while True:
        skip_rest = False
        with urllib.request.urlopen(
            "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warningInfo&lang=tc"
        ) as url:
            data = (json.loads(url.read().decode()))["details"]
            for warning in data:
                if warning["warningStatementCode"] == "WTCSGNL":
                    updateTime = warning["updateTime"]
                    content = warning["contents"]
                    text = "".join(content)
                    typhoon_info = content[3]
                    print(typhoon_info)
                    hour_pattern = re.compile(r"\d+")
                    update_hour = (re.search(hour_pattern, typhoon_info)).group()
                    if update_hour == last_update_hour:
                        print(
                            "Not updated yet. Waiting for 5 seconds before next fetch."
                        )
                        time.sleep(5)
                        skip_rest = True
                        break
                    last_update_hour = update_hour
                    am_pm = "AM" if typhoon_info[1:3] == "上午" else "PM"
                    print(f"Last update hour: {last_update_hour} {am_pm}")
                    for i, c in enumerate(typhoon_info):
                        if c == "北" and typhoon_info[i + 1] == "緯":
                            lat = float(typhoon_info[i + 2 : i + 6])
                            long = float(typhoon_info[i + 10 : i + 15])
                            dist = get_distance_from_lat_lon_km(lat, long)

                        if c == "時" and typhoon_info[i + 1] == "速":
                            speed = float(typhoon_info[i + 3 : i + 5])
                            pass

            if skip_rest:
                continue

            if last_lat == 0.0:
                last_lat = lat
                last_long = long
                last_speed = speed
                last_dist = dist
            else:
                lat_diff = round(lat - last_lat, 1)
                long_diff = round(long - last_long, 1)
                speed_diff = round(speed - last_speed, 1)
                dist_diff = round(dist - last_dist, 1)

            if lat_diff > 0:
                lat_direc = "N"
            elif lat_diff < 0:
                lat_diff = -lat_diff
                lat_direc = "S"
            else:
                lat_direc = ""

            if long_diff > 0:
                long_direc = "E"
            elif long_diff < 0:
                long_diff = -long_diff
                long_direc = "W"
            else:
                long_direc = ""

            speed_sign = "+" if speed_diff >= 0 else ""
            dist_sign = "+" if dist_diff >= 0 else ""

            print(f"As at {updateTime}: ")
            print(
                f"Location: {lat}° N ({lat_diff}{lat_direc}), {long}° E ({long_diff}{long_direc})"
            )
            print(
                f"Distance to Hong Kong (22.3° N, 114.2° E): {dist:.1f}km ({dist_sign}{dist_diff} km)"
            )
            print(f"Speed: {speed}km/h ({speed_sign}{speed_diff} km/h)\n")
            print("Full warning: ")
            print(text)

            countdown(60, "TCSGNL")


if __name__ == "__main__":
    typhoonWarning()
