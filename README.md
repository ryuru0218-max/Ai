# POCHI ULTIMATE — 自律Discordエージェント & 公式ダッシュボード

Discord Bot（**1ファイル / 11,900行**）と、実装済みの公式Webダッシュボードを一体化したものです。
外部API・Mod・自動修復・空気感オートノミーまで-containedで動作します。

---

## 🌐 ライブサイト

| 用途 | リンク |
|---|---|
| **ダッシュボード** | **https://pochi-ai.onrender.com/** |
| 生存確認 | https://pochi-ai.onrender.com/healthz |
| メトリクス (Prometheus) | https://pochi-ai.onrender.com/metrics |
| 状態 JSON | https://pochi-ai.onrender.com/api/status |
| リアルタイム (SSE) | https://pochi-ai.onrender.com/api/stream |

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

### 機能面（UIアクション 248種 / コマンド 65個）
- **音楽**：手続き生成WAVの合成・再生、プレイリスト、歌詞・曲検索
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

