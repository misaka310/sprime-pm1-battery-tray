# SPRIME PM1 Battery Tray

[![Build Windows EXE](https://github.com/misaka310/sprime-pm1-battery-tray/actions/workflows/build-windows.yml/badge.svg)](https://github.com/misaka310/sprime-pm1-battery-tray/actions/workflows/build-windows.yml)

WindowsのタスクトレイにSPRIME PM1系ワイヤレスマウスのバッテリー残量を常駐表示する、プレミアムなダークUIツールです。

> **非公式ツールについて**
> 本ツールは独立して開発された非公式ツールであり、SPRIMEまたは関連企業による公式製品、提携製品、承認製品ではありません。製品名および商標は各権利者に帰属します。

## 重要な設計思想
本ツールは、**「タスクトレイを見るだけでバッテリー残量が分かる」**ことを最優先に設計されています。
従来の「フローティングバッジ（画面上の小窓）」はユーザー体験を妨げるため**完全に廃止**され、すべての情報がトレイアイコンに集約されました。

1. **巨大なトレイ数字アイコン**: 通知領域（タスクトレイ）のアイコン面積を最大限に活用し、バッテリー残量を太く大きな数字で直接描画します。
2. **直感的な視認性**: 他のシステムアイコンと並んでも見劣りしないサイズ感と、状態に応じた背景色の変化により、一目で状況を把握できます。

## ダウンロード

通常利用者は、GitHub Releases から `SPRIME-PM1-Battery-Tray-*.zip` をダウンロードして展開し、`SPRIME-PM1-Battery-Tray.exe` を実行してください。

開発者以外がローカルでビルドする必要はありません。

## 特徴
- **視認性抜群のトレイアイコン**: 32x32ピクセル内に太字で数字を表示。無駄な余白を排除し、視覚的な占有面積を拡大しました。
- **一目で分かる状態表示**:
  - `96`: 接続中・残量96%
  - `99+`: 100%（または満充電に近い状態）
  - `--`: 未接続 / スリープ中
  - `!`: 通信エラー
- **動的なカラーフィードバック**:
  - **通常**: 黒〜濃いグレー背景
  - **充電中**: 鮮やかな緑背景
  - **低残量**: 警告の赤背景
- **安定したバックグラウンド動作**: UIスレッドとHID通信スレッドを分離したイベント駆動設計により、低負荷で安定した動作を実現。
- **HID読み取りの排他制御**: 定期更新と手動更新が重なっても、同時にHID feature reportを叩かないようにしています。
- **自動起動サポート**: 設定画面から簡単にWindows起動時の自動実行を有効化できます（管理者権限不要）。

## 対応環境
- Windows 10 / 11 (64bit)
- SPRIME PM1 Wireless Mouse
- Python 3.11以上（開発・ビルド用）

## 確認済み環境

| 項目 | 内容 |
|---|---|
| OS | Windows 11 |
| デバイス | SPRIME PM1 Wireless Mouse |
| 接続 | 2.4GHz USBレシーバー接続を想定 |
| HID識別子 | VID `0x1915`, PID `0xAC1C` |
| HID取得方式 | `hidapi` で feature report `0x05` を問い合わせ |

## 互換性の注意

このツールは実機で確認したSPRIME PM1のHID応答を前提にしています。

- 同じPM1系でも、別ファームウェア・別レシーバー・別ロットでは動作しない可能性があります。
- PM1以外のSPRIME製品は未確認です。
- マウスがスリープ中、切断中、またはOS側でHIDデバイスを開けない場合は `--` や `!` 表示になります。
- 他環境でうまく読めない場合は、まず `scripts\probe.ps1` と `scripts\e2e.ps1` でHID検出結果を確認してください。

## 使い方

### 通常実行

Releases からダウンロードしたZIPを展開し、次のEXEを起動します。

```text
SPRIME-PM1-Battery-Tray.exe
```

### 操作
- **設定を開く**: トレイアイコンを右クリックして「Show settings」。
- **手動更新**: 設定画面の「Refresh Now」またはトレイメニューの「Refresh now」。
- **ログ確認**: 設定画面の「Open Logs」から、実行ログ用フォルダにアクセスできます。

## 開発者向け

### セットアップ

```powershell
.\scripts\setup.ps1
```

### ソースから実行

```powershell
.\run.ps1
```

### 品質確認

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m ruff check src tests
.\.venv\Scripts\python.exe -m mypy src\sprime_pm1_battery_tray\hid_protocol.py
.\.venv\Scripts\python.exe -m pytest tests
```

CIでは全体の非退行coverageに加え、HID protocolへRuffのimport・modernization・bugbear規則と90%のfocused coverageを要求します。空パス、空応答、異常値、権限エラー、列挙失敗、複合HID endpoint競合をモックで検証します。

### ビルド (EXE生成)
単一のWindows用EXEフォルダ（コンソールなし）を生成します。
```powershell
.\scripts\build.ps1
```
生成物: `dist/SPRIME-PM1-Battery-Tray/SPRIME-PM1-Battery-Tray.exe`

### GitHub Actionsでの配布ビルド

`.github/workflows/build-windows.yml` により、`main` へのpush、手動実行、`v*` タグpushでWindows EXEを自動ビルドします。

- `main` push / 手動実行: Actions artifact としてZIPを保存
- `v*` タグpush: GitHub Releaseを作成し、ZIPを添付

### E2Eテスト
ユニットテスト、実機HID読み取り、ビルド、EXE起動確認を一括で行います。
```powershell
.\scripts\e2e.ps1
```

`e2e.ps1` は実機HID読み取りを含むため、SPRIME PM1を接続していない環境では失敗します。
GitHub Actionsでは実機HIDを読めないため、ユニットテストとビルドのみ実行します。

## 公開前チェック

公開前に最低限、次を確認してください。

1. GitHub Actions の `Build Windows EXE` が通る
2. SPRIME PM1を接続した状態でローカルの `scripts\e2e.ps1` が通る
3. 生成された `SPRIME-PM1-Battery-Tray.exe` が起動する
4. タスクトレイに残量、`--`、`!` の状態表示が出る
5. READMEに確認済み環境と未確認デバイスの範囲を明記している
6. `dist/`、`.venv/`、ログ、ローカル設定がGitに含まれていない

詳細は `docs/public-release-checklist.md` を参照してください。

## トラブルシューティング
- **バッテリーが `--` になる**: マウスがスリープしているか、切断されています。マウスを動かすか、設定画面で「Refresh Now」を試してください。
- **表示が `!` になる**: HID読み取りでエラーが発生しています。PM1が接続されているか、別アプリがHIDデバイスを掴んでいないか確認してください。
- **アイコンが小さい**: 最新版では最大サイズで描画されるよう改善されました。Windowsのタスクバー設定で「すべてのアイコンを表示する」か、本アプリを常に表示するようにドラッグして配置することをお勧めします。
- **設定のリセット**: `.\scripts\reset_config.ps1` を実行すると、設定ファイルが初期化されます。

## 技術スタック
- **GUI**: CustomTkinter, Pystray, Pillow (Icon Rendering)
- **HID**: hidapi (Real device communication)
- **Font**: Arial Bold (Max visibility)

## ライセンス

このリポジトリのコードは [MIT License](LICENSE) で公開しています。
