---
title: iPhone（Lightning端子）のフルバックアップ方法
cue: |
  - 公式な方法
  - フルバックアップ取得
  - macOS Sequoia15.5とWindows 11を前提
  - 写真・動画の参照可能
  - 外部ディスクへの取得
summary: |
  - 不測の事態を想定し、フルバックアップの取得は必要である
---
-----
### 前提
  - Apple公式サポートのある方法を使う
  - iCloudへの自動バックアップは設定しているが、一部のデータであるためローカル環境でフルバックアップを取得したい
  - フルバックアップに使用する環境は、macOS Sequoia15.5とWindows 11を前提とする(Ubuntuは公式サポートがない)
  - 写真・動画の参照がフルバックアップ先環境で可能とする
  - フルバックアップで使用する環境により、ディスク容量が不測ケースが想定されるため、外部ディスクへ取得するための設定もカバーする
  - OSと使用するツール
    - Windows 11 + iTunes(別途導入が必要)
    - macOS Sequaia15.5 + Finder
  - iPhoneとの接続
  - Lightningケーブルを使用する

-----
### 外部ディスクへバックアップを取得するための設定
  - Windows 11
    - iTunesのバックアップフォルダを外部ディクスに移動する(下記の例は、"E:\iPhoneBackup")
    - 移動後にiTunesのバックアップフォルダを外部ディスクにするためのシンボリックリンクを作成する
      ```
      mklink /J "C:\Users\<ユーザー名>\AppData\Roaming\Apple Computer\MobileSync\Backup" "E:\iPhoneBackup"
      ```
  - macOS Sequaia15.5
    - 最初に一度バックアップを完了させる
    - 以下のコマンドで取得したバックアップを外部ディスクに移動し、Backupディレクトが存在しないことを確認し、シンボリックリンクを作成する
      ```
      mv ~/Library/Application\ Support/MobileSync/Backup /Volumes/ExternalDrive/iPhoneBackup

      ls ~/Library/Application\ Support/MobileSync/

      ln -s /Volumes/ExternalDrive/iPhoneBackup ~/Library/Application\ Support/MobileSync/Backup
      ```

-----
### バックアップ手順
  - Windows 11
    - LightningケーブルでiPhoneを接続
    - iPhone側で「このコンピュータを信頼しますか？」のメッセージに対し「信頼」する
    - iTunesを起動
    - 「iPhoneのバックアップを暗号化」にもチェック
    - 「今すぐバックアップ」をクリック
  - macOS Sequaia15.5
    - LightningケーブルでiPhoneを接続
    - Finderのサイドバーから「iPhone」を選択
    - 「バックアップ」セクションで「このMacにバックアップ」にチェック
    - 「ローカルバックアップを暗号化」にもチェック
    - 「今すぐバックアップ」をクリック

-----
### 写真・動画をバックアップ先で個別閲覧にする手順
  - Windows11
    - エクスプローラーで「Apple iPhone」フォルダーを開く
    - Internal Storage → DCIM フォルダーに移動する
    - 配下のフォルダーを全てを任意のディレクトリにコピーする
  - macOS Sequaia15.5
    - Finderで「iPhone」デバイスを開く
    - 「内臓ストレージ」→ DCIMフォルダーに移動する
    - 配下のフォルダーを全てを任意のフォルダーにコピーする

-----
### リストア手順
  - iPhoneをLightningケーブルで接続する
  - iTunes/Finderから復元方法のリコメンドがある。これに従い復元する
