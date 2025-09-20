import json
import time
import urllib.request


def weatherReport():
    existing_special_weather_tips, existing_typhoon_info, existing_warning_messages = [], [], []
    announced_no_special_weather_tips = False

    while True:
        with urllib.request.urlopen(
            "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=tc"
        ) as url:
            now = time.localtime()
            now = time.strftime("%H:%M", now)
            content = json.loads(url.read().decode())
            if "warningMessage" in content:
                current_warning_message = content["warningMessage"]
                if current_warning_message:
                    for warning in existing_warning_messages:
                        if warning not in current_warning_message:
                            existing_warning_messages.remove(warning)
                            print(f"[{now}] Removed a warning message.")
                    for warning in current_warning_message:
                        if warning not in existing_warning_messages:
                            existing_warning_messages.append(warning)
                            print(f"[{now}] 以下是一則新的天氣警告。\n[{now}] {warning}\n")
            if "specialWxTips" in content:
                announced_no_special_weather_tips = False
                current_special_weather_tips = content["specialWxTips"]
                if current_special_weather_tips:
                    for tip in existing_special_weather_tips:
                        if tip not in current_special_weather_tips:
                            existing_special_weather_tips.remove(tip)
                            print(f"[{now}] Removed special weather tip.")
                    for tip in current_special_weather_tips:
                        if tip not in existing_special_weather_tips:
                            existing_special_weather_tips.append(tip)
                            print(f"[{now}] 以下是一則新的特別天氣提示。\n[{now}] {tip}\n")
            else:
                if not announced_no_special_weather_tips:
                    print(f"[{now}] No existing special weather tips.")
                    announced_no_special_weather_tips = True
                    existing_special_weather_tips = []
            if "tcmessage" in content:
                current_typhoon_info = content["tcmessage"]
                if current_typhoon_info:
                    for tip in existing_typhoon_info:
                        if tip not in current_typhoon_info:
                            existing_typhoon_info.remove(tip)
                    for tip in current_typhoon_info:
                        if tip not in existing_typhoon_info:
                            existing_typhoon_info.append(tip)
                            print(f"[{now}] {tip}")
            else:
                # print(f"[{now}] No existing tropical cyclone.")
                existing_typhoon_info = []

        time.sleep(60*30)


if __name__ == "__main__":
    weatherReport()
