# 📸 写真から天気を推定するPython with PyTorchプログラム(EfficientNet-B0)を作ってみた！第2弾

## 🧩 はじめに
前回の記事では、PyTorchとResNet18を使って空の画像から天気を分類する基本的な方法を紹介しましたが、実際に空を撮影してデータを使い作成した学習モデルでの判定で晴れを曇りと判定するケースがありました。このため、今回は**判定精度を高める**ための具体的なアプローチとして高性能なモデルの導入と、**学習・推論コードの最適化**について詳しく解説します。
ResNet18は手軽に利用できる優れたモデルですが、より複雑なパターンを学習し、高い精度を出すには限界があります。そこで登場するのが**EfficientNet**です。EfficientNetは、モデルの深さ（depth）、幅（width）、解像度（resolution）の3つの次元を効率的にスケーリングすることで、高い精度と計算効率を両立させたモデル群です。特に画像認識タスクにおいて、その性能の高さが証明されています。今回は、最も軽量なバージョンである **EfficientNet-B0** を用いて、天気分類モデルを構築します。

-----

### 📦 準備：必要なライブラリのインストール

以下のコマンドで必要なライブラリをインストールします。

```bash
pip install torch torchvision tqdm
```

-----

### 📁 データセットの準備

学習には、前回の記事で準備した`weather_dataset`フォルダを使用します。
まだ準備していない場合は、以下の構造で画像を配置してください。各フォルダに晴れ、くもり、雨の画像を分類して格納します。

```
weather_dataset/
├── sunny/
│   ├── sunny_1.jpg
│   ├── sunny_2.jpg
│   └── ...
├── cloudy/
│   ├── cloudy_1.jpg
│   ├── cloudy_2.jpg
│   └── ...
└── rainy/
    ├── rainy_1.jpg
    ├── rainy_2.jpg
    └── ...
```

各クラスには**最低でも30枚以上**の画像を用意することが推奨されますが、より良い精度を目指すなら**100枚以上**あると理想的です。

-----

### 🧪 2. EfficientNet-B0 を使った学習コード

ここからが本題です。以下のPythonスクリプトを実行することで、EfficientNet-B0モデルが事前にImageNetで学習された重みをベースに、天気分類用にファインチューニングされます。

```python
import torch
from torch import nn, optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader, random_split
from tqdm import tqdm
import os

# 学習用設定
data_dir = 'weather_dataset'
batch_size = 16
epochs = 10
model_path = 'efficientnet_weather.pth'
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# データ変換（EfficientNet向け）
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],  # ImageNet基準
        std=[0.229, 0.224, 0.225]
    )
])

# データセット読み込み
dataset = datasets.ImageFolder(data_dir, transform=transform)
num_classes = len(dataset.classes)
print(f"クラスラベル: {dataset.classes}")

# 訓練/検証に分割（8:2）
train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size
train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size)

# EfficientNet-B0 の読み込みと出力層変更
model = models.efficientnet_b0(pretrained=True)
model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
model = model.to(device)

# 損失関数・最適化
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.0003)

# 学習ループ
for epoch in range(epochs):
    model.train()
    train_loss = 0.0
    for images, labels in tqdm(train_loader, desc=f"[{epoch+1}/{epochs}] 学習"):
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        train_loss += loss.item()

    # 検証ループ
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

    accuracy = correct / total * 100
    print(f"Epoch {epoch+1}: Loss={train_loss/len(train_loader):.4f}, Val Acc={accuracy:.2f}%")

# モデル保存
torch.save(model.state_dict(), model_path)
print(f"✅ モデルを保存しました: {model_path}")
```

#### コードのポイント：

  * **データ拡張（Data Augmentation）**: `transforms.RandomHorizontalFlip()`, `transforms.RandomRotation(15)`, `transforms.ColorJitter()` を追加し、画像の多様性を増やすことで汎化性能を高めています。
  * **訓練/検証データの分割**: `random_split` を用いて、データセットを訓練用と検証用に8:2の割合で分割しています。これにより、モデルが未知のデータに対してどれだけ正確に予測できるかを評価し、過学習を防ぐことができます。
  * **EfficientNet-B0の利用**: `models.efficientnet_b0(pretrained=True)` でImageNetで事前学習済みのEfficientNet-B0モデルをロードしています。
  * **出力層の変更**: `model.classifier[1]` を、天気分類の3クラス (`num_classes`) に合わせた全結合層に置き換えています。
  * **学習ループと検証**: 各エポックの終わりに検証データでの精度 (`Val Acc`) を表示することで、学習の進捗とモデルの性能を確認できます。

学習が完了すると、`efficientnet_weather.pth`という名前で学習済みのモデルが保存されます。

-----

### ✅ 3. 推論用コード：EfficientNetモデルで天気を判定する

学習済みの`efficientnet_weather.pth`モデルを使用して、新しい画像の天気を判定するコードです。

```python
import torch
from torchvision import transforms, models
from PIL import Image
import os

# 使用デバイスの指定（CPU or GPU）
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# クラス名は学習時と一致させてください（ImageFolderのディレクトリ順によって変わります）
# 例: {'cloudy': 0, 'rainy': 1, 'sunny': 2} と表示された場合、['cloudy', 'rainy', 'sunny'] に設定
classes = ['cloudy', 'rainy', 'sunny'] 

# モデル構築と重み読み込み
def load_model(model_path):
    model = models.efficientnet_b0(pretrained=False) # pretrained=Falseでモデルの構造のみを読み込む
    model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, len(classes))
    model.load_state_dict(torch.load(model_path, map_location=device)) # 学習済み重みをロード
    model.to(device)
    model.eval() # 評価モードに設定
    return model

# 推論処理
def predict(image_path, model_path='efficientnet_weather.pth'):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    image = Image.open(image_path).convert('RGB')
    image_tensor = transform(image).unsqueeze(0).to(device)

    model = load_model(model_path) # モデルを読み込む

    with torch.no_grad(): # 勾配計算を無効化
        output = model(image_tensor)
        _, pred = torch.max(output, 1) # 最大値のインデックスを取得

    print(f"判定結果: {classes[pred.item()]}")

# 使用例:
# predict("test.jpg", "efficientnet_weather.pth")
```

#### 重要な注意点：

  * **`device` の定義**: 推論コードでも`device`が定義されている必要があります。これにより、CPUまたはGPUが正しく選択されます。
  * **`classes` の順序**: `classes` リストの要素の順序は、学習時に `datasets.ImageFolder` が認識したクラスのインデックス順（通常はアルファベット順）と**完全に一致している必要があります**。学習スクリプトの `print(f"クラスラベル: {dataset.classes}")` の出力で確認できます。

-----

### 🔚 精度をさらに向上させるためのヒント

今回のEfficientNet-B0の導入とデータ拡張は、精度向上のための大きな一歩です。さらに精度を高めたい場合は、以下の点を検討してみてください。

| 項目 | 対策例 |
| :-- | :-- |
| **データ** | **量を増やす**：各クラスの画像をさらに増やす（数百〜数千枚）。\<br\>**多様性を持たせる**：様々な時間帯、季節、アングル、光の条件下で撮影された画像を収集する。|
| **モデル構造** | **より深いモデル**：EfficientNet-B1, B2, B3など、より大規模なEfficientNetモデルを試す（GPUメモリに注意）。|
| **訓練戦略** | **epoch数を増やす**：学習ループの `epochs` を10から20〜30、あるいはそれ以上に増やす。\<br\>**学習率の調整**：`lr=0.0003` から `1e-4` や `1e-5` のように微調整する。\<br\>**EarlyStopping**：検証損失が改善しなくなった時点で学習を停止する仕組みを導入し、過学習を防ぐ。|
| **評価** | **テストセットの用意**：訓練・検証データとは完全に異なる「テストデータ」を別途用意し、モデルの真の汎化性能を評価する。\<br\>**詳細な評価指標**：単なる正解率だけでなく、`classification_report`（Precision, Recall, F1-score）や `confusion_matrix` を使って、各クラスの分類性能を詳細に分析する。|
| **過学習対策** | **Dropout**：モデルの層にDropoutを追加して、ニューロンの共適応を防ぐ。\<br\>**正則化（Weight Decay）**：最適化関数に`weight_decay`パラメータを設定し、モデルの重みが大きくなりすぎるのを防ぐ。|

これらの施策を段階的に導入することで、あなたの天気分類モデルはさらに賢くなるでしょう。