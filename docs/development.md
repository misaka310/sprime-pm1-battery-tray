# 開発・検証ガイド

## セットアップ

```powershell
.\scripts\setup.ps1
```

## ソースから実行

```powershell
.\run.ps1
```

## 品質確認

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m ruff check src tests
.\.venv\Scripts\python.exe -m mypy src\sprime_pm1_battery_tray\hid_protocol.py
.\.venv\Scripts\python.exe -m pytest tests
```

CIでは全体の非退行coverageに加え、HID protocolへRuffのimport・modernization・bugbear規則と90%のfocused coverageを要求します。空パス、空応答、異常値、権限エラー、列挙失敗、複合HID endpoint競合をモックで検証します。

## EXEビルド

```powershell
.\scripts\build.ps1
```

生成物:

```text
dist/SPRIME-PM1-Battery-Tray/SPRIME-PM1-Battery-Tray.exe
```

`.github/workflows/build-windows.yml`は`main`へのpush、手動実行、`v*`タグpushでWindows EXEをビルドします。通常のpushと手動実行ではActions artifact、タグpushではGitHub ReleaseへZIPを添付します。

## ユーザー環境へのインストール（任意）

ビルド済みEXE（`dist/SPRIME-PM1-Battery-Tray/`）を`%LOCALAPPDATA%\Programs`配下へ配置し、スタートメニュー登録・スタートアップ起動設定まで行う場合は以下を使います。

```powershell
.\scripts\install_user.ps1 [-EnableStartup]
```

## 実機E2E

```powershell
.\scripts\e2e.ps1
```

この検証はユニットテスト、実機HID読み取り、ビルド、EXE起動確認をまとめて行います。SPRIME PM1を接続していない環境では実機HID確認が失敗します。GitHub Actionsでは実機HIDを読めないため、ユニットテストとビルドだけを実行します。

## 公開前確認

1. GitHub Actionsの`Build Windows EXE`が通る
2. SPRIME PM1接続状態で`scripts\e2e.ps1`が通る
3. 生成されたEXEが起動する
4. 通知領域に残量、`--`、`!`が表示される
5. READMEに確認済み環境と未確認デバイスの範囲が記載されている
6. `dist/`、`.venv/`、ログ、ローカル設定がGitに含まれていない

詳細は[公開前チェックリスト](public-release-checklist.md)を参照してください。

## 技術スタック

- GUI: CustomTkinter、Pystray、Pillow
- HID: hidapi
- アイコン描画: Arial Bold
