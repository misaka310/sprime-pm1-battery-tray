# Public Release Checklist

このリポジトリを公開する前に確認する項目です。

## 1. 実機動作

SPRIME PM1を接続した状態で確認します。

```powershell
.\scripts\e2e.ps1
```

確認すること:

- `pytest tests/` が通る
- HID読み取り結果が `connected` または `disconnected` になる
- EXEが生成される
- 生成されたEXEの `--smoke-test` が通る

## 2. 手動UX確認

```powershell
.\scripts\run.ps1
```

確認すること:

- タスクトレイに残量数字が出る
- マウスがスリープまたは切断状態のとき `--` になる
- HID読み取りエラー時に `!` になる
- 右クリックメニューから `Refresh now` が使える
- `Refresh now` を連打してもアプリが固まらない
- `Show settings` が開く
- `Start on boot` のオン/オフがHKCU Runに反映される
- `Quit` で常駐プロセスが終了する

## 3. 互換性表記

READMEに次を明記します。

- 確認済みOS
- 確認済みデバイス
- 接続方式
- VID / PID
- PM1以外のSPRIME製品は未確認であること
- 実機がない環境ではE2Eが失敗すること

## 4. Gitに含めないもの

公開前に以下が含まれていないことを確認します。

- `.venv/`
- `dist/`
- `build/`
- `*.spec`
- `*.log`
- ローカル設定ファイル
- HID調査時の個人環境ログ

確認例:

```powershell
git status --short
git ls-files | Select-String -Pattern "dist/|.venv/|.log|.spec"
```

## 5. 最小リリース条件

公開してよい最低ライン:

- READMEだけで用途と制約が分かる
- 実機E2Eが通る
- 手動更新連打でHID多重アクセスしない
- EXE生成手順がREADME通りに動く
- 確認済みデバイス範囲を誇張していない

## 6. 公開後に受ける想定問い合わせ

想定される問い合わせ:

- PM1以外のSPRIMEマウスでも使えるか
- USB有線接続でも読めるか
- バッテリーが `--` のままになる
- `!` 表示になる
- Windows起動時に自動起動しない

回答方針:

- PM1以外は未確認と明示する
- VID/PIDが一致してもHID report仕様が違えば読めない可能性があると説明する
- `scripts\probe.ps1` と `scripts\e2e.ps1` の結果を確認してもらう
