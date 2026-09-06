# UI仕様: SPRIME PM1 Battery Tray

## 目的

Windows 11のタスクトレイ周辺に、SPRIME PM1系マウスのバッテリー残量を常時確認できる表示を追加する。

## 参照画像

- `assets/original-task-tray-screenshot.png`
- `assets/reference-ui-mockup.png`

## 表示方針

Windowsの標準通知領域は、通常のアプリが任意の長い文字列を常時タスクバー上に直接表示する用途には向かない。
そのため、トレイアイコンへ電池残量を数字入りアイコンとして描画する。

- 例: `78`、低残量なら警告風アイコン。
- ホバー時のツールチップに正確な表示を出す。
- 例: `SPRIME PM1 Battery: 78% / Connected`

## 設定画面

`Show settings`から開く設定画面は、少なくとも以下を持つ。

- 現在の状態
  - デバイス名
  - 接続状態
  - バッテリー残量
  - 最終更新時刻
- Refresh interval（秒単位の自由入力、既定300秒、最小5秒）
- Low battery threshold（％単位の自由入力、既定20%）
- Manual refresh
- Open logs

## トレイメニュー

右クリックメニューを用意する。

- Refresh now
- Show settings
- Start on boot（トグル、Windowsログイン時の自動起動）
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
