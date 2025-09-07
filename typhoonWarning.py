import json
import urllib.request

from utils import countdown, get_distance_from_lat_lon_km

def typhoonWarning():
    last_lat, last_long, last_speed, last_dist = 0.0, 0.0, 0.0, 0.0
    lat_diff, long_diff, speed_diff, dist_diff = 0.0, 0.0, 0.0, 0.0
    lat_direc, long_direc = "", ""
    speed_sign, dist_sign = "+", "+"

    while True:
        with urllib.request.urlopen("https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warningInfo&lang=tc") as url:
            data = (json.loads(url.read().decode()))["details"]
            for warning in data:
                if warning["warningStatementCode"] == "WTCSGNL":
                    time = warning["updateTime"]
                    content = warning["contents"]
                    text = "".join(content)
                    typhoonInfo = content[3]
                    
                    for i, c in enumerate(typhoonInfo):
                        if c == "北" and typhoonInfo[i+1] == "緯":
                            lat = float(typhoonInfo[i+2:i+6])
                            long = float(typhoonInfo[i+10:i+15])
                            dist = get_distance_from_lat_lon_km(lat, long)
                        
                        if c == "時" and typhoonInfo[i+1] == "速":
                            speed = float(typhoonInfo[i+3 : i+5])
                            pass
                        
            
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
            
            print(f"As at {time}: ")
            print(f"Location: {lat}° N ({lat_diff}{lat_direc}), {long}° E ({long_diff}{long_direc})")
            print(f"Distance to Hong Kong (22.3° N, 114.2° E): {dist:.1f}km ({dist_sign}{dist_diff} km)")
            print(f"Speed: {speed}km/h ({speed_sign}{speed_diff} km/h)\n")
            print("Full warning: ")
            print(text)

            countdown(60, "TCSGNL")


if __name__ == "__main__":
    typhoonWarning()
            
            
            