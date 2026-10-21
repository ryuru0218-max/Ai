# POCHI ULTIMATE — 自律Discordエージェント & AIチャットサイト

Discord Bot（**1ファイル 12,000行**）と、**友達と会話を共有できるAIチャットサイト**を一体化したものです。
外部API・Mod・自動修復・空気感オートノミーまですべてこの1ファイルにcontainedされています。

---

## 💬 AIチャットサイト（メイン）

**招待リンク**（6文字のコード）を送ると、友達と同じ部屋に入り、
**同じ会話をリアルタイム共有**できます
（SSE / タイピング表示 / 参加者一覧 / Markdown書き出し）。

| 機能 | 詳細 |
|---|---|
| 招待リンク | 6文字コード + URL。リンクを送ればそのまま参加 |
| リアルタイム | SSE 配信で友達のメッセージが即時に届く / タイピング表示 |
| AI 設定 | 会話モード26種・人格35種・応答スタイル8種を部屋ごとに切替 |
| メモリ | 会話は永続化され、POCHIの長期記憶にも連携 |
| 書き出し | 会話をMarkdownでダウンロード |

REST API：
```
POST /api/chat/rooms                     部屋作成 / 招待コードで参加
GET  /api/chat/rooms/{id}/messages       メッセージ取得
POST /api/chat/rooms/{id}/messages       メッセージ送信(AI応答は非同期生成)
GET  /api/chat/stream/{id}               SSE リアルタイム
GET  /api/chat/rooms/{id}/export         Markdown書き出し
```

### 監視ダッシュボード
`/dashboard` で内部状態（CPU/メモリ/AI/記憶/市場/ログ/コンソール）を確認できます。

### Discord から招待リンクを張る

| コマンド | 動作 |
|---|---|
| `!chat [部屋名]` | 部屋を作り、**招待リンク**とコードをDiscordに貼る |
| `!chatjoin <コード>` | コードから参加（リンクを再表示） |
| `!chatsend <コード> <本文>` | DiscordからWebチャットへ送信（AI応答はWebに届く） |
| `!chatlog <コード> [件数]` | Webチャットの会話をDiscordに貼り出す |
| `!chatlist` | 自分が作った部屋の一覧 |
| `/pochi chat` | スラッシュコマンド版（自分だけに見えるリンク） |

### 音楽を再生する

| コマンド | 動作 |
|---|---|
| `!play <曲名>` | **指定した曲を実際に再生**（iTunes検索→試聴音源をボイスで実再生。未接続なら音声ファイル添付） |
| `!radio <曲名>` | POCHIが**コード進行つきのオリジナル楽曲**を合成してWAV添付 |
| `!nowplaying` | 再生中の曲とキュー（リンク付き） |

> ボイスでの実再生には `ffmpeg` が必要です（未導入でも音声ファイルの添付はできます）。

---

## 🌐 ライブサイト

| 用途 | リンク |
|---|---|
| **チャットサイト** | **https://pochi-ai.onrender.com/** |
| ダッシュボード | https://pochi-ai.onrender.com/dashboard |
| 生存確認 | https://pochi-ai.onrender.com/healthz |
| メトリクス (Prometheus) | https://pochi-ai.onrender.com/metrics |
| 状態 JSON | https://pochi-ai.onrender.com/api/status |
| リアルタイム (SSE) | https://pochi-ai.onrender.com/api/stream |

> ⚠️ `pochi-ai` は Render 上の**サービス名が `pochi-ai` の場合**のURLです。
> まだデプロイしていない場合（`Not Found` になる場合）は
> 下の **「1クリックデプロイ」** を押してください。サービス名が固定されるため、
> デプロイ後は必ず `https://pochi-ai.onrender.com/` で開けます。
> 既に別名で作っている場合は Render ダッシュボードの「Public URL」を
> `POCHI_PUBLIC_URL` 環境変数に入れてください（ログとダッシュボードに反映されます）。

### 公式サイトを GitHub Pages で公開する（設定1クリック）

`docs/index.html` を同梱しています。リポジトリの
**Settings → Pages → Build and deployment → Source: `Deploy from a branch`**
→ Branch: `main` / Folder: `/docs` を選択して Save してください。
公開後 **https://ryuru0218-max.github.io/Ai/** で公式トップページが開きます
（ワークフローは不要で、外部依存なしの静的ページなので即公開できます）。

> トークンを設定した場合：`https://pochi-ai.onrender.com/?token=<POCHI_WEB_TOKEN>` でログインできます
> （ブラウザが localStorage に保存し、以後は Bearer ヘッダで自動認証されます）

---

## 🚀 デプロイ（1クリック）

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/ryuru0218-max/Ai)

`render.yaml` を同梱しているので、Blueprint として自動設定されます（サービス名 `pochi-ai`）。

デプロイ時に設定する環境変数：

| 変数 | 必須 | 説明 |
|---|---|---|
| `DISCORD_TOKEN` | ✅ | Discord Bot トークン |
| `GEMINI_API_KEY` | | 複数可（`,` 区切り）。未設定でもローカル推論エンジンで動作 |
| `POCHI_WEB_TOKEN` | 推奨 | ダッシュボードの認証パスワード。**未設定だと誰でも閲覧可能** |
| `POCHI_PUBLIC_CHANNEL` | | 自動ダイジェスト/通知の投稿先チャンネルID |
| `PORT` | 自動 | Render が設定 |

---

## 🤖 主な機能

### 会話・認知
- 多重思考エンジン：6系統council合議（論理 / 感情 / 毒性 / 裏意図 / 安全 / 文体）
- 会話モード 26種 / 人格RP 35種 / 思考エンジン 6種（Gemini 3.8 Flash ほか）
- 話者プロファイリング + 深層記憶（ベクター近傍 + 木構造 + 自動統合）
- 感情トレンド分析と能動的な提案

### 機能面（UIアクション 248種 / コマンド 71個）
- **音楽**：`!play <曲名>` で**指定した曲を実際に再生**（iTunes検索→試聴音源をボイス実再生 / ファイル添付）、
  `!radio <曲名>` でコード進行つきオリジナル楽曲を合成、プレイリスト、歌詞・曲検索
- **経済**：POCHIcoin台帳、市場シミュレーション（ランダムウォーク）、株取引emias&nbsp;・ショップ・ギャンブル
- **ゲーム**：ダンジョン / ブラックジャック / マルバツ / 2048 / マインスイーパー / ポーカー
- **モデレーション**：AutoMod（キーワード・スパム・リンク）、BAN・TO・掃除、監査ログ
- **サーバー**：レベルXP / ノートWiki / 習慣トラッカー / ポモドーロ / 発言検索 / マクロ / リアクショRole
- **UI**：Rich Embed + View + Modal の Eisenhower UI（11タブ）

### 内部・OS層
- asyncio + ThreadPool + ProcessPool ハイブリッド並列
- CPU/メモリ/スレッド監視 → 動的スロットリング
- サンドボックス実行（AST検証 + プロセス隔離 + rlimit）
- **自己修復ループ**：例外を構造解析 → ASTで関数書き換え → ホットバインド再投入
- タスク監督（失敗 → 診断 → 自動再投入）
- 機能フラグ / 監査ログ / ローカルバックアップ / **自己更新**（GitHubから構文検証付きで）

### 外部・Mod
- キー不要の公開API **57種**（天気・為替・暗号資産・ニュース・論文・Steam・RSS・翻訳…）
- **四次元ポケット**：仕様から実動くプラグイン生成 → 安全検証 → 即時メモリ展開 → 動的コマンド登録
- **実PyPI Modインストーラ**：取得 → 安全展開 → 静的検査 → 隔離プロセスで実行
- DuckDuckGo実検索 / スクレイピング / 画像生成 / TTS

### 裏（自律性）
- 空気感検知（HEATED / NOISY / SILENT / レイド）→ 先回りアクション
- 隠しコマンド（所有者限定）/ 監査付き深層シェルブリッジ
- 1時間ごとの自動ダイジェスト / 自動バックアップ

---

## 🧪 動作確認

```bash
pip install -r requirements.txt
python main.py --selfcheck    # 内部52項目の自己診断(Discord接続不要)
python main.py --preflight    # 起動前チェック(サイトの公開可否を含む)
```

`main.py` は Discord ライブラリが無い環境でも**スタブで完全動作**するため、
オフラインでも全機能・全コマンドをテストできます。

---

## 構成

| ファイル | 説明 |
|---|---|
| `main.py` | 実装本体（単一ファイル / 11,900行） |
| `requirements.txt` | 依存パッケージ |
| `render.yaml` | Render Blueprint（デプロイ設定） |
| `README.md` | このファイル（機能一覧・リンク） |
| `docs/index.html` | 公式トップページ（GitHub Pages で公開） |
| `web/chat.html` | AIチャットサイトの本体（`/` で配信） |

---

## ❓ 自分のURLがわからないとき

Render 側のサービス名は**私有**なので、外部からは自動特定できません。次の方法で確認できます。

1. **Bot の起動ログ**に自分のURLが出力されます：
   ```
   🌐 Webダッシュボード: https://<サービス名>.onrender.com/
      ├ 監視: https://.../healthz  / メトリクス: https://.../metrics
      └ 認証トークン: 設定済み
   ```
2. **ダッシュボード右上**の「🌐 URL」ピルにも同じリンクが出ます。
3. **Render ダッシュボード** → 該当サービス → 画面上部の「Public URL」

`render.yaml` 経由でデプロイした場合、サービス名は `pochi-ai` に固定されるため
URLは **https://pochi-ai.onrender.com/** になります。
既に別の名前で作成済みの場合は、`POCHI_PUBLIC_URL` 環境変数に自分のURLを設定すれば
ログとダッシュボードに反映されます。

