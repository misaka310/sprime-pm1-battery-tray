# UI仕様: SPRIME PM1 Battery Tray

## 目的

Windows 11のタスクトレイ周辺に、SPRIME PM1系マウスのバッテリー残量を常時確認できる表示を追加する。

## 参照画像

- `assets/original-task-tray-screenshot.png`
- `assets/reference-ui-mockup.png`

## 表示方針

Windowsの標準通知領域は、通常のアプリが任意の長い文字列を常時タスクバー上に直接表示する用途には向かない。
そのため、実装では次の2系統を用意する。

1. **トレイアイコン表示**
   - 電池残量を数字入りアイコンとして描画する。
   - 例: `78`、低残量なら警告風アイコン。
   - ホバー時のツールチップに正確な表示を出す。
   - 例: `SPRIME PM1 Battery: 78% / Connected`

2. **任意のフローティングバッジ表示**
   - 常に数字を読みたい場合のため、右下付近に小さい常時表示バッジを出せるようにする。
   - 表示例: `🖱 78%`
   - ドラッグ移動可能。
   - 常に手前表示のON/OFFを設定できる。

## 設定UI

参照モックの雰囲気に寄せる。
Windows 11風の軽量ユーティリティとして、少なくとも以下を持つ。

- 現在の状態
  - デバイス名
  - 接続状態
  - バッテリー残量
  - 最終更新時刻
- Start on boot
  - Windows起動時に自動起動
- Refresh interval
  - 1分 / 5分 / 10分 / 30分
- Low battery notification
  - ON/OFF
- Notify at
  - 10% / 15% / 20% / 25%
- Display style
  - Tray icon only
  - Tray icon with number
  - Floating badge
  - Tray icon + floating badge
- Device selection
  - 自動検出
  - 検出されたSPRIMEらしきHIDデバイスから選択
- Manual refresh
- Open logs
- About

## トレイメニュー

右クリックメニューを用意する。

- Refresh now
- Show settings
- Toggle floating badge
- Start on boot
- Open logs
- Quit

## 表示ステータス

- Connected
- Disconnected
- Unknown protocol
- Battery read failed
- Low battery

## 完了条件

UIだけでなく、実際のSPRIME PM1系マウスまたはレシーバーから読み取ったバッテリー値を表示できていること。
`sprime.pro` の表示値とおおむね一致すること。
