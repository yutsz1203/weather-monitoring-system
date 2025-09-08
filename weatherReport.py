import json
import time
import urllib.request


def weatherReport():
    existing_special_weather_tips = []
    existing_typhoon_info = []

    while True:
        with urllib.request.urlopen(
            "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=tc"
        ) as url:
            now = time.localtime()
            now = time.strftime("%H:%M", now)
            content = json.loads(url.read().decode())
            current_special_weather_tips = content["specialWxTips"]
            if current_special_weather_tips:
                for tip in existing_special_weather_tips:
                    if tip not in current_special_weather_tips:
                        existing_special_weather_tips.remove(tip)
                        print(f"[{now}] Removed special weather tip.")
                for tip in current_special_weather_tips:
                    if tip not in existing_special_weather_tips:
                        existing_special_weather_tips.append(tip)
                        print(f"[{now}] New special weather tip.\n[{now}] {tip}\n")
            current_typhoon_info = content["tcmessage"]
            if current_typhoon_info:
                for tip in existing_typhoon_info:
                    if tip not in current_typhoon_info:
                        existing_typhoon_info.remove(tip)
                for tip in current_typhoon_info:
                    if tip not in existing_typhoon_info:
                        existing_typhoon_info.append(tip)
                        print(f"[{now}] {tip}")

        time.sleep(60)


if __name__ == "__main__":
    weatherReport()
