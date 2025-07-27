# 📸 写真から天気を推定するPythonプログラムを作ってみた！

## 🧩 はじめに
日々の天気を記録する方法として、気象庁の情報を確認する以外にも、「写真から自動で天気を推定する」というユニークな手法があります。  
ここでは、**PythonとOpenCVを使って、空の写真から天気を簡易的に判別する方法**をご紹介します。

---

## ✅ 必要な環境

本プロジェクトでは以下のツールとライブラリを使います。

- Python 3.x
- OpenCV (`cv2`)
- NumPy
- 空の画像ファイル（例：`sky.jpg`）またはWebカメラ

ライブラリのインストール:

```bash
pip install opencv-python numpy
```

---

## 🧠 天気の分類ルール（簡易）

天気の分類は、画像の**明るさ（Value）**、**彩度（Saturation）**、**色相（Hue）**の平均値を用いて簡易的に判定します。

| 写真の特徴             | 推定される天気 |
|------------------------|----------------|
| 明るく青みが強い       | 晴れ           |
| 明るくて白っぽい       | くもり         |
| 暗く、青・白が少ない   | 雨または嵐     |

---

## 🧪 画像ファイルから天気を判定するコード

```python
import cv2
import numpy as np

def classify_weather(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print("画像が見つかりません")
        return

    img = cv2.resize(img, (100, 100))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    brightness = np.mean(hsv[:, :, 2])
    saturation = np.mean(hsv[:, :, 1])
    hue = np.mean(hsv[:, :, 0])

    if brightness > 170 and saturation > 60 and (90 < hue < 140):
        weather = "晴れ"
    elif brightness > 120:
        weather = "くもり"
    else:
        weather = "雨・曇り"

    print(f"推定天気: {weather}")
    print(f"明るさ: {brightness:.2f}, 彩度: {saturation:.2f}, 色相: {hue:.2f}")

# 使用例
classify_weather("sky.jpg")
```

---

## 📷 Webカメラからリアルタイムで天気を推定する

空の写真を撮ってすぐに天気を推定したい場合は、Webカメラから直接画像を取得する方法が便利です。

```python
def capture_and_classify():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("カメラが見つかりません")
        return

    print("カメラを起動中... スペースキーで撮影、ESCで終了")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow('Webカメラ', frame)
        key = cv2.waitKey(1)

        if key == 27:  # ESCキーで終了
            break
        elif key == 32:  # スペースキーで撮影＆判定
            cv2.imwrite("sky.jpg", frame)
            classify_weather("sky.jpg")

    cap.release()
    cv2.destroyAllWindows()

# 実行
capture_and_classify()
```
---

## 📝 まとめ

今回は、**空の画像から天気を推定するシンプルな仕組み**を紹介しました。  
難しいAI技術を使わなくても、OpenCVとPythonだけで意外と面白い天気推定が可能です。  
ぜひ自分の住む場所や旅先の空で試してみてください。

