# AccuWeather APIとPythonで天気予報データを自動取得！

## はじめに

こんにちは！今回は、AccuWeather APIを活用して、Pythonで日々の天気予報（特に1時間ごとの気温）を自動的に取得し、CSV形式で保存する方法についてご紹介します。データの自動収集と可視化に興味がある方には特におすすめです。

## AccuWeather APIとは？

AccuWeatherは、アメリカの民間気象企業が提供する世界的な天気予報サービスです。リアルタイムの気象情報、長期予報、地域別の詳細な予報が特徴です。開発者向けのAPIも提供されており、これを使うことでプログラムから気象データを取得できます。

## APIキーの取得手順

AccuWeather APIを利用するには、まずAPIキーが必要です。以下のステップで取得できます。

1.  **AccuWeather Developer Portalにログイン**: [https://developer.accuweather.com/](https://developer.accuweather.com/) にアクセスし、アカウントにログインします。
2.  **「My Apps」ページへ移動**: メニューから「My Apps」をクリックします。
3.  **新しいアプリを作成**: 「Add a new App」ボタンをクリックし、以下の情報を入力します。
    * **App Name**: 任意の名前 (例: WeatherDataCollector)
    * **App Description**: 簡単な説明
    * **Product**: **Limited Trial** (無料プランで1日50回までAPI呼び出しが可能) を選択します。
4.  **「Create App」ボタンを押す**: アプリ作成後、アプリ一覧に表示されます。
5.  **APIキーを確認**: 作成したアプリ名をクリックすると、API Keyが表示されます。このキーをPythonコードで使用します。

## Pythonプログラムの作成

今回は、指定した都市の`locationKey`を取得し、それを使って12時間分の時間別天気予報（気温、体感温度、湿度など）を取得するPythonスクリプトを作成します。取得したデータはCSVファイルとして出力します。

> **注意点**: AccuWeatherの無料プラン「Limited Trial」では、`24-hour hourly forecast` APIは利用できません。そのため、`12-hour hourly forecast` APIを使用します。

```python
import csv
import requests
import json
from datetime import datetime

API_KEY = "あなたのAPIキー" # ここに取得したAPIキーを設定
CITY = "Setagaya" # 予報を取得したい都市
COUNTRY_CODE = "JP" # 国コード

def get_location_key(api_key, city, country_code):
    """都市名からAccuWeatherのlocationKeyを取得する関数"""
    url = f"[http://dataservice.accuweather.com/locations/v1/cities/](http://dataservice.accuweather.com/locations/v1/cities/){country_code}/search"
    params = {"apikey": api_key, "q": city}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error getting location key: {response.status_code}")
        return None
    data = response.json()
    if not isinstance(data, list) or len(data) == 0:
        print(f"Error: Could not find location key for {city}, {country_code}")
        return None
    return data[0]["Key"]

def get_hourly_forecast(api_key, location_key):
    """指定されたlocationKeyに基づき、12時間分の天気予報を取得する関数"""
    url = f"[http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/](http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/){location_key}"
    params = {"apikey": api_key, "details": "true", "metric": "true"} # metric=trueで摂氏表示
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error getting hourly forecast: {response.status_code}")
        return None
    return response.json()

# プログラム実行時のタイムスタンプを取得し、ファイル名に利用
timestamp = datetime.now().strftime("%Y%m%d-%H%M")
filename = f"/home/kazukif/Documents/Projects/weather/WeatherForecast_{timestamp}.csv" # 絶対パスを指定

# ロケーションキーの取得
location_key = get_location_key(API_KEY, CITY, COUNTRY_CODE)

if location_key:
    # 時間別予報の取得
    forecast = get_hourly_forecast(API_KEY, location_key)

    if forecast:
        # CSVファイルへの書き出し
        with open(filename, mode="w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            # ヘッダー行の書き込み
            writer.writerow(["DateTime", "Condition", "Temperature(°C)", "FeelsLike(°C)", "Humidity(%)"])
            # 各時間のデータを書き込み
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
else:
    print("⚠️ ロケーションキーの取得に失敗しました。")
