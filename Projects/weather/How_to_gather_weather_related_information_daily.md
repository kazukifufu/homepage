
# 🌤 PythonでAccuWeather APIを使って時間別天気を自動取得してみた！

## 🧩 はじめに

「天気予報を自動で取得して可視化したい」そんな思いから、**AccuWeather API**を使って東京都世田谷区の**1時間ごとの天気と気温、湿度**を取得し、**CSV形式で保存するPythonスクリプト**を作成しました。

さらにこのスクリプトを、**Ubuntuのcron**で**毎日午前6時と午後6時に自動実行**するところまでやってみました！

---

## 🔑 AccuWeather APIとは？

AccuWeatherは、アメリカの民間気象企業が提供する天気情報サービスで、**短期予報の精度が高い**のが特徴です。開発者登録をすれば、以下のようなAPIを無料で使えます：

- 地名からLocation Keyを取得するAPI
- 各地域の時間別天気予報を取得するAPI（12時間版は無料）

🌐 [AccuWeather Developer Portal](https://developer.accuweather.com/)

---

## ⚙️ Pythonで実装したこと

以下の手順で、Pythonスクリプト（`weather_export.py`）を作成しました。

1. **Location Keyの取得**：
    ```python
    def get_location_key(api_key, city, country_code):
        ...
    ```
2. **12時間分の天気データ取得**：
    ```python
    def get_hourly_forecast(api_key, location_key):
        ...
    ```
3. **CSV形式で出力**：
    ```python
    with open(filename, mode="w", newline='', encoding="utf-8") as file:
        ...
    ```

> cronなどからも安全に呼び出せるよう、**ファイルパスを絶対パスで指定**しています。

---

## ⏰ cronで自動実行

Ubuntu 24.04上で、次のようにcronに登録しました（仮想環境のPythonを使用）：

```cron
0 6 * * * /home/user/projects/weather/venv/bin/python /home/user/projects/weather/weather_export.py
0 18 * * * /home/user/projects/weather/venv/bin/python /home/user/projects/weather/weather_export.py
```

> ログファイルも追記することで、動作確認もバッチリです。

---

## 📊 出力結果（例）

| 時刻              | 天気           | 気温（℃） | 体感温度（℃） | 湿度（%） |
|------------------|----------------|-----------|----------------|------------|
| 2025-07-27 06:00 | Intermittent clouds | 27.5     | 31.8           | 78         |
| 2025-07-27 07:00 | Partly sunny   | 29.1      | 34.3           | 72         |
| 2025-07-27 08:00 | Partly sunny   | 30.7      | 36.7           | 66         |
| 2025-07-27 09:00 | Partly sunny   | 32.2      | 38.7           | 60         |

---

## 💡 おわりに

この仕組みをベースに、以下のような拡張も可能です：

- 天気データの**グラフ化（matplotlib）**
- **LINE通知**や**メール送信**
- 複数都市への拡張

APIの力を使えば、日々の生活がどんどん便利になりますね！

---

## 🐍 最終的なPythonスクリプト（weather_export.py）

```python
import csv
import requests
import json
from datetime import datetime

API_KEY = "あなたのAPIキー"
CITY = "あなたの都市"
COUNTRY_CODE = "JP"

def get_location_key(api_key, city, country_code):
    url = f"http://dataservice.accuweather.com/locations/v1/cities/{country_code}/search"
    params = {"apikey": api_key, "q": city}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return None
    data = response.json()
    if not isinstance(data, list) or len(data) == 0:
        print("都市が見つかりません")
        return None
    return data[0]["Key"]

def get_hourly_forecast(api_key, location_key):
    url = f"http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{location_key}"
    params = {"apikey": api_key, "details": "true", "metric": "true"}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return None
    return response.json()

# 現在日時を取得してフォーマット
timestamp = datetime.now().strftime("%Y%m%d-%H%M")
filename = f"/home/user/projects/weather/WeatherForecast_{timestamp}.csv"

location_key = get_location_key(API_KEY, CITY, COUNTRY_CODE)
forecast = get_hourly_forecast(API_KEY, location_key)

if forecast:
    with open(filename, mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["DateTime", "Condition", "Temperature(°C)", "FeelsLike(°C)", "Humidity(%)"])
        for hour in forecast:
            writer.writerow([
                hour["DateTime"],
                hour["IconPhrase"],
                hour["Temperature"]["Value"],
                hour["RealFeelTemperature"]["Value"],
                hour["RelativeHumidity"]
            ])
    print(f"✅ CSV出力完了：{filename}")
else:
    print("⚠️ 予報取得に失敗しました。")
```
