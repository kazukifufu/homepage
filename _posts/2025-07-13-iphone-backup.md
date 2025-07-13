---
title: iPhone（Lightning端子）のフルバックアップ方法
cue: |
  - Apple公式サポートのある方法を使う
  - iCloudへの自動バックアップは設定しているが、一部のデータであるためローカル環境でフルバックアップを取得したい
  - フルバックアップに使用する環境は、macOS Sequoia15.5とWindows 11を前提とする(Ubuntuは公式サポートがない)
  - 写真・動画の参照がフルバックアップ先環境で可能とする
  - フルバックアップで使用する環境により、ディスク容量が不測ケースが想定されるため、外部ディスクへ取得するための設定もカバーする
summary: |
  - 不測の事態を想定し、フルバックアップの取得は必要である
---

-----
### 前提
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
-----

### ステップ1：iTunesを使ったバックアップ手順
xxxここに記事を書く

### ステップ2：iCloudを使ったバックアップ手順
xxx

### 注意点
xxx
