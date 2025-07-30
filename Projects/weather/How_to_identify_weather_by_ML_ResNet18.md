# 📸 写真から天気を推定するPython with PyTorchプログラムを(ResNet18)作ってみた！

## 🧩 はじめに
前回の記事では、画像の明るさ（Value）、彩度（Saturation）を使って空の写真から天気を判別するプログラムをご紹介しました。今回は、訓練済のResNet18(画像認識に特化した畳み込みニューラルネットワーク（CNN）の一種、ImageNetで学習済)を「晴れ・くもり・雨」の画像で独自の天気分類用ラベルに微調整(ファインチューニング)し、画像を「晴れ・くもり・雨」に分類していきます。また、判定精度をさらに高めるためのヒントを解説していきます！
自分でモデルを学習させることで、よりあなたの用途に合った、高精度な天気判別AIを構築できるようになります。

-----

## ✅ 天気分類用画像データを準備する 🖼️

AIモデルを学習させるためには、大量の画像データが必要です。今回は「晴れ」「くもり」「雨」の3種類の天気画像を準備します。

### 📁 データ構成

PyTorchの`ImageFolder`を使ってデータを読み込むため、以下のようなフォルダ構成で画像を配置します。

```
weather_dataset/
├── sunny/          ← 晴れの画像
│   ├── sunny_1.jpg
│   ├── sunny_2.jpg
│   └── ...
├── cloudy/         ← くもりの画像
│   ├── cloudy_1.jpg
│   ├── cloudy_2.jpg
│   └── ...
└── rainy/          ← 雨の画像
    ├── rainy_1.jpg
    ├── rainy_2.jpg
    └── ...
```

各フォルダに最低でも**30枚以上**の画像を入れるのが理想的です。多ければ多いほど、モデルの学習効果が高まります。

### 🚀 Pixabay API で画像を自動ダウンロード！

手動で画像を集めるのは大変ですよね。ここでは、著作権フリー画像サイトのPixabayのAPIを利用して、自動で画像をダウンロードするPythonスクリプトを紹介します。

**【重要】Pixabay APIキーの取得**
このスクリプトを使うには、[PixabayのAPIドキュメントページ](https://pixabay.com/api/docs/)で無料登録を行い、APIキーを取得する必要があります。取得したAPIキーを以下のコードの`YOUR_PIXABAY_API_KEY`の部分に置き換えてください。

#### 🧪 Pythonスクリプト（3クラスの画像をまとめてダウンロード）

```python
import requests
import os
import time

API_KEY = 'YOUR_PIXABAY_API_KEY'  # ⭐あなたのPixabay APIキーに置き換えてください
NUM_IMAGES = 30 # 各クラス30枚の画像をダウンロード
BASE_DIR = 'weather_dataset' # 画像を保存するルートディレクトリ

# 天気カテゴリと検索キーワードの対応表
weather_classes = {
    'sunny': 'clear sky', # 晴れ
    'cloudy': 'cloudy sky', # くもり
    'rainy': 'rainy sky' # 雨
}

# ディレクトリ作成
for label in weather_classes:
    os.makedirs(os.path.join(BASE_DIR, label), exist_ok=True)

# 画像をダウンロードする関数
def download_images():
    for label, query in weather_classes.items():
        print(f"\n▶ {label} の画像を取得中...")
        url = f'https://pixabay.com/api/?key={API_KEY}&q={query}&image_type=photo&per_page={NUM_IMAGES}&orientation=horizontal'
        response = requests.get(url)
        data = response.json()

        if 'hits' not in data:
            print(f"{label} 画像の取得に失敗しました")
            continue

        for i, hit in enumerate(data['hits']):
            img_url = hit['webformatURL']
            img_data = requests.get(img_url).content
            save_path = os.path.join(BASE_DIR, label, f"{label}_{i+1}.jpg")
            with open(save_path, 'wb') as f:
                f.write(img_data)
            print(f"{i+1}枚目: {img_url}")
            time.sleep(0.5)  # 負荷軽減のため少し待機

        print(f"✅ {label} の画像を保存しました → {os.path.join(BASE_DIR, label)}")

# スクリプト実行
if __name__ == '__main__':
    download_images()
```

このスクリプトを実行すると、`weather_dataset`フォルダ内に`sunny/`、`cloudy/`、`rainy/`の各フォルダが作成され、それぞれに30枚の画像がダウンロードされます。

-----

## 🧪 AIモデルを学習させる！ 🧠

画像データが準備できたら、いよいよモデルの学習です。ここでは、`ResNet18`という訓練済みモデルを「ファインチューニング」して、天気分類に特化させます。ファインチューニングとは、既に大量のデータで学習済みのモデルを、新しいタスクに合わせて微調整する手法です。

#### 📦 必要ライブラリ

学習を開始する前に、必要なライブラリをインストールしておきましょう。

```bash
pip install torch torchvision tqdm scikit-learn
```

#### 🧪 Python学習コード（ResNet18をFine-tune）

以下のコードを`train.py`などのファイル名で保存し、実行してください。

```python
import os
import torch
from torch import nn, optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from torch.utils.data import Subset # Subsetを追加

# データパス
data_dir = 'weather_dataset'
model_path = 'model.pth'

# GPUがあれば使用
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 前処理とデータ拡張
transform = transforms.Compose([
    transforms.RandomHorizontalFlip(), # 左右反転
    transforms.RandomRotation(15),     # 15度まで回転
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2), # 色調調整
    transforms.Resize((224, 224)), # 画像サイズを224x224にリサイズ
    transforms.ToTensor(), # PyTorchテンソルに変換
    transforms.Normalize([0.485, 0.456, 0.406], # ImageNetの平均値で正規化
                         [0.229, 0.224, 0.225])   # ImageNetの標準偏差で正規化
])

# データセットとローダー
full_dataset = datasets.ImageFolder(data_dir, transform=transform) # データセット全体を読み込み

# データを訓練用と検証用に分割
train_size = int(0.8 * len(full_dataset))
val_size = len(full_dataset) - train_size
train_dataset, val_dataset = torch.utils.data.random_split(full_dataset, [train_size, val_size])

# データローダーの作成
train_dataloader = DataLoader(train_dataset, batch_size=16, shuffle=True)
val_dataloader = DataLoader(val_dataset, batch_size=16, shuffle=False) # 検証用はシャッフル不要

# ラベル数
num_classes = len(full_dataset.classes)
print("クラス:", full_dataset.classes)

# モデル準備（ResNet18）
model = models.resnet18(pretrained=True) # 訓練済みモデルをロード

# 最後の全結合層を新しいタスク（天気分類）用に変更
model.fc = nn.Linear(model.fc.in_features, num_classes)
model = model.to(device)

# 損失関数と最適化
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.0003) # 学習率を調整

# 学習ループ
epochs = 20 # エポック数を増やす
model.train() # モデルを訓練モードに設定
for epoch in range(epochs):
    running_loss = 0.0
    for images, labels in tqdm(train_dataloader, desc=f"Epoch {epoch+1}/{epochs}"):
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
    print(f"訓練損失: {running_loss/len(train_dataloader):.4f}")

    # 検証フェーズ
    model.eval() # モデルを評価モードに設定
    val_loss = 0.0
    correct = 0
    total = 0
    with torch.no_grad(): # 勾配計算を無効化
        for images, labels in val_dataloader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            val_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    print(f"検証損失: {val_loss/len(val_dataloader):.4f}, 検証精度: {100 * correct / total:.2f}%")
    model.train() # モデルを訓練モードに戻す

# モデル保存
torch.save(model.state_dict(), model_path)
print(f"✅ モデルを保存しました → {model_path}")
```

このスクリプトを実行すると、`model.pth`というファイルが作成されます。これが学習済みモデルのデータです。

-----

## ✅ 学習済みモデルで天気を判別する！ ☀️

`model.pth`が作成されたら、以下のコードを`classify.py`などのファイル名で保存し、実行してください。`model.pth`を読み込み、画像の前処理を行い、天気を出力します。	
	```python
	import torch
	import torchvision.transforms as transforms
	from torchvision import models
	from PIL import Image
	
	# クラスラベル
	classes = ['晴れ', 'くもり', '雨']
	
	# モデル読み込み
	def load_model(model_path):
	    model = models.resnet18(pretrained=False)
	    num_ftrs = model.fc.in_features
	    model.fc = torch.nn.Linear(num_ftrs, len(classes))  # 晴れ・くもり・雨
	    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
	    model.eval()
	    return model
	
	# 前処理（ResNetの要求仕様）
	def preprocess_image(image_path):
	    transform = transforms.Compose([
	        transforms.Resize((224, 224)),
	        transforms.ToTensor(),
	        transforms.Normalize(mean=[0.485, 0.456, 0.406],  # ImageNetの平均
	                             std=[0.229, 0.224, 0.225])   # ImageNetの標準偏差
	    ])
	    image = Image.open(image_path).convert('RGB')
	    return transform(image).unsqueeze(0)  # バッチ次元を追加
	
	# 推論処理
	def predict(model, image_tensor):
	    with torch.no_grad():
	        outputs = model(image_tensor)
	        _, predicted = torch.max(outputs, 1)
	        return classes[predicted.item()]
	
	# 実行部
	if __name__ == '__main__':
	    image_path = 'test.jpg'
	    model_path = 'model.pth'
	
	    model = load_model(model_path)
	    image_tensor = preprocess_image(image_path)
	    weather = predict(model, image_tensor)
	
	    print(f"この空の天気は: {weather}")
	```
	
-----

## 🚀 判定精度をさらに上げるには？

せっかく学習させるなら、できるだけ高い精度で天気を判別したいですよね。ここでは、モデルの判定精度を向上させるための重要なポイントをいくつか紹介します。

### 1\. データの質と量を増やす 📈

最も効果的なのは、**高品質で多様な画像データ**を増やすことです。

  * **各クラス（晴れ・くもり・雨）に最低100枚以上**の画像を用意しましょう。多ければ多いほど、モデルは様々なパターンを学習できます。
  * 同じ天気でも、**時間帯、アングル、季節が異なる画像**を含めることで、モデルの汎化能力が高まります。
  * 天気の区別が**曖昧な画像は学習から除外**しましょう。曖昧なデータはモデルの学習を妨げることがあります。
  * **データ拡張 (Data Augmentation)** を積極的に利用しましょう。これは、既存の画像を加工して多様性を増やす手法で、上記の学習コードにも`RandomHorizontalFlip`や`RandomRotation`などの例が含まれています。

### 2\. より高性能なモデルを使う 🧠

`ResNet18`は手軽ですが、より複雑な画像を扱うには表現力が不足することもあります。

  * **ResNet50**: ResNet18よりも深いネットワークで、より高い精度が期待できますが、計算コストも増加します。
  * **EfficientNet**: 軽量でありながら高精度を実現するモデルファミリーです。特にモバイル環境などでの利用に適しています。
  * **Vision Transformer (ViT)**: 大量のデータがある場合に非常に高い性能を発揮しますが、学習には多くの計算リソースが必要となることがあります。

### 3\. ファインチューニング戦略の最適化 ⚙️

モデルのすべての層を学習させるのではなく、一部の層だけを学習させることで、効率的に精度を向上させられる場合があります。

  * **例：最後の数層だけ学習させる**
    ```python
    for param in model.parameters():
        param.requires_grad = False # 全てのパラメータの勾配計算をオフ
    for param in model.fc.parameters():
        param.requires_grad = True # 最後の全結合層のパラメータの勾配計算をオン
    ```
    これにより、モデルの基本的な特徴抽出能力は維持しつつ、新しいタスクに特化した部分だけを学習させることができます。

### 4\. 学習パラメータのチューニング 🧪

学習の進行を左右するパラメータ（ハイパーパラメータ）を調整することで、精度が変わることがあります。

  * **epoch数**: モデルがデータセット全体を学習する回数です。5回から**20回以上**に増やすことで、より深く学習させることができます。ただし、増やしすぎると過学習のリスクもあります。
  * **学習率 (Learning Rate)**: モデルが一度に学習する度合いを示す値です。`0.0003`のような小さな値に調整することで、より安定した学習が可能です。
  * **最適化手法**: `Adam`以外にも`SGD + momentum`など、様々な最適化手法があります。タスクやデータセットによって最適なものが異なりますので、いくつか試してみるのも良いでしょう。

### 5\. バリデーションとテストを正しく行う 📊

学習中のモデルの性能を適切に評価し、\*\*過学習（学習データに過剰に適合し、未知のデータへの汎化性能が落ちる現象）\*\*を防ぐために、データセットを3つに分割して管理します。

  * **訓練(Train)データ**: モデルの学習に使うデータです。
  * **検証(Validation)データ**: 学習中にモデルの性能を評価し、ハイパーパラメータの調整などに使います。
  * **テスト(Test)データ**: 学習と調整が完了したモデルの最終的な性能を評価するために使います。このデータは学習や調整には一切使ってはいけません。

上記の学習コードには、データの分割（訓練データと検証データ）が組み込まれています。

### 6\. 評価指標を工夫する 🎯

単に「正解率 (Accuracy)」だけでなく、他の評価指標も確認することで、モデルの得意な部分や苦手な部分を詳細に把握できます。

  * **混同行列 (Confusion Matrix)**: 各クラスの正解・不正解の内訳を視覚的に確認できます。
  * **Precision (適合率)** / **Recall (再現率)** / **F1-score**: クラスごとの性能を詳しく評価できます。例えば、「雨」の画像を「晴れ」と誤判別するのを避けたい場合など、特定のクラスの性能を重視する際に役立ちます。

<!-- end list -->

```python
from sklearn.metrics import classification_report, confusion_matrix

# 以下は学習後の評価コード例です。
# 実際にはテストデータを用いて推論を行い、true_labelsとpredicted_labelsを準備します。
# print(confusion_matrix(true_labels, predicted_labels))
# print(classification_report(true_labels, predicted_labels))
```

-----

## 🔚 まとめ：精度向上の鍵

| 項目 | 対策例 |
| :--- | :--- |
| **データ** | 量を増やす、多様性を持たせる、ノイズを除去する、データ拡張 |
| **モデル構造** | より深いモデル（ResNet50）、軽量高精度モデル（EfficientNet）、大規模モデル（ViT）を検討 |
| **訓練戦略** | ファインチューニングの対象層を調整（例：最終層のみ）、学習率のスケジューリング |
| **評価** | 適切なデータ分割（訓練/検証/テスト）、混同行列やF1-scoreなどの多角的な指標確認 |
| **過学習対策** | EarlyStopping、Dropout、正則化（Weight Decayなど）の導入 |

これらのポイントを参考に、ぜひあなただけの高精度な天気判別AIを構築してみてください！