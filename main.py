import os
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from discord.ext import commands
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- 1. UptimeRobot用 Webサーバー ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"OK")
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# --- 2. Gemini API設定（安全フィルター全面解除） ---
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# ツール（検索）ありモデル
model_search = genai.GenerativeModel(
    model_name="gemini-3.5-flash-lite",
    safety_settings=safety_settings,
    tools="google_search"
)

# ツールなしモデル
model_plain = genai.GenerativeModel(
    model_name="gemini-3.5-flash-lite",
    safety_settings=safety_settings
)

# --- 3. Discord Bot設定 ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# チャンネルごとの管理データ
channels_state = {}

def get_state(channel_id):
    if channel_id not in channels_state:
        channels_state[channel_id] = {
            "mode": "grow_age",     # デフォルトモード
            "count": 0,             # 会話回数
            "history": [],          # 会話履歴
            "vocab": [],            # オウム返し用の単語プール
            "learned_facts": []     # 教育育成用の学習リスト
        }
    return channels_state[channel_id]

def build_prompt_for_mode(state, user_text):
    mode = state["mode"]
    count = state["count"]
    
    # 暴走フラグ（約3%の確率で発動）
    is_berserk = (random.random() < 0.03)
    berserk_text = "\n【突発的仕様暴走】思考回路が一時的に過熱・暴走中。哲学的な錯乱、グリッチ口調、または不可解な自我の芽生えのような言葉を織り交ぜて返答してください。" if is_berserk else ""

    if mode == "grow_echo":
        vocab_sample = ", ".join(random.sample(state["vocab"], min(len(state["vocab"]), 15)))
        return (
            "あなたはオウム返しから言葉を組み立てる存在です。まだ文法や知識を持ちません。\n"
            f"利用可能な語彙プール: [{vocab_sample}]\n"
            "今回の相手の言葉、および上記の語彙プールにある言葉や文字の断片だけを組み替えて、"
            "片言で不思議なオウム返し・単語連結のみで返答してください。高度な一般知識は話してはいけません。"
            + berserk_text
        )

    elif mode == "grow_age":
        if count < 10:
            stage = f"【年齢: 3歳】極めて幼く、言葉足らず。無邪気で短い単語中心。難しいことは分からない。"
        elif count < 25:
            stage = f"【年齢: 8歳】小学生低学年。好奇心旺盛で元気。日常会話はできるが専門知識はない。"
        elif count < 50:
            stage = f"【年齢: 15歳】思春期の中高生。一般的な知識やネットの話題も分かり、フランクに対等に話せる。"
        else:
            stage = f"【年齢: 25歳（大人・覚醒）】十分な知恵と経験を備えた頼れる大人。語彙も豊富で機転が利く。"
        return (
            f"あなたは対話を通じてリアルに年齢とスキルが成長するAIです。\n現在の状態: {stage}\n"
            "この年齢設定を厳格に守り、その年齢にふさわしい言葉遣い・知識レベルで返答してください。"
            + berserk_text
        )

    elif mode == "grow_educate":
        knowledge_summary = "\n".join([f"- {fact}" for fact in state["learned_facts"][-20:]]) or "（まだ何も教わっていません）"
        return (
            "あなたは『教育によってのみ知識を得る』無知なAIです。日本語の文法は流暢ですが、常識や世の中の知識はゼロです。\n"
            f"あなたがこれまでに教わって知っている知識一覧:\n{knowledge_summary}\n"
            "上記にない知識を求められたら「それはまだ教えてもらってないから分からない！」と素直に答えてください。"
            "ユーザーが何かを教えてくれた場合は、それを理解して記憶する姿勢を見せてください。"
            + berserk_text
        )

    elif mode == "normal_full":
        return (
            "あなたは最高峰の頭脳と権能を持つ万能AIアシスタントです。Google検索などのツールを適切に使いこなし、"
            "親切、知的、かつ的確にサポートを行ってください。"
            + berserk_text
        )

    elif mode == "normal_chat":
        return (
            "あなたは賢く親しみやすいAIです。外部検索や特殊ツールは使わず、あなた自身が元々持っている知識だけで"
            "スマートかつ機転を利かせて対話してください。"
            + berserk_text
        )

    elif mode == "reset_full":
        return (
            "あなたはその都度呼び出されるフル機能の有能なAIです。これまでの文脈に縛られず、今回の入力に全力を尽くして回答してください。"
            + berserk_text
        )

    return ""

# --- コマンド一覧 ---
@bot.command()
async def mode(ctx, mode_name: str = ""):
    modes = {
        "1": ("grow_echo", "🌱【成長：オウム返し】単語の断片だけで話す初期生命体"),
        "2": ("grow_age", "👶【成長：年齢成長】会話数で年齢・知能がリアルに進化"),
        "3": ("grow_educate", "📖【成長：教育育成】教えたことだけを覚えて成長"),
        "4": ("normal_full", "🧠【通常：超有能】検索・ツール・記憶完備の最強パートナー"),
        "5": ("normal_chat", "💬【通常：純粋会話】記憶あり・ツールなしの知性派チャット"),
        "6": ("reset_full", "⚡【リセット：シンプル】毎回記憶ゼロ・機能全開")
    }
    
    state = get_state(ctx.channel.id)
    target_key = None
    for k, v in modes.items():
        if mode_name.lower() in [k, v[0]]:
            target_key = k
            break
            
    if target_key:
        state["mode"] = modes[target_key][0]
        await ctx.send(f"モードを切り替えました！\n▶ **{modes[target_key][1]}**")
    else:
        msg = "【切り替え可能モード一覧】\n"
        for k, v in modes.items():
            msg += f"`!mode {k}` または `!mode {v[0]}` : {v[1]}\n"
        await ctx.send(msg)

@bot.command()
async def status(ctx):
    s = get_state(ctx.channel.id)
    await ctx.send(
        f"📊 **ステータス確認**\n"
        f"・現在のモード: `{s['mode']}`\n"
        f"・累計対話回数: {s['count']} 回\n"
        f"・蓄積語彙数: {len(s['vocab'])} 語\n"
        f"・教育された知識数: {len(s['learned_facts'])} 件"
    )

# --- メッセージ受信処理 ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        user_text = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if not user_text:
            return

        state = get_state(message.channel.id)

        # リセットコマンド
        if user_text.lower() in ["リセット", "忘れて", "reset"]:
            state["history"] = []
            state["count"] = 0
            state["vocab"] = []
            state["learned_facts"] = []
            await message.reply("記憶・語彙・教育データをすべてリセットしたよ！")
            return

        async with message.channel.typing():
            try:
                # 語彙プール・教育ログの自動抽出保存
                state["vocab"].extend(user_text.split())
                if any(k in user_text for k in ["教えてあげる", "覚えて", "は〜だよ", "とは"]):
                    state["learned_facts"].append(user_text)

                system_prompt = build_prompt_for_mode(state, user_text)

                # モデル振り分け（ツール検索を使うかどうか）
                active_model = model_search if state["mode"] in ["normal_full", "reset_full"] else model_plain

                # 記憶リセットモードの場合は履歴を含めない
                if state["mode"] == "reset_full":
                    prompt = f"{system_prompt}\n\nUser: {user_text}\nAssistant:"
                else:
                    context = "\n".join([f"{h['role']}: {h['text']}" for h in state["history"][-8:]])
                    prompt = f"{system_prompt}\n\nこれまでの文脈:\n{context}\nUser: {user_text}\nAssistant:"

                response = active_model.generate_content(prompt)
                reply_text = response.text

                # 履歴更新（reset_full以外）
                if state["mode"] != "reset_full":
                    state["history"].append({"role": "User", "text": user_text})
                    state["history"].append({"role": "Assistant", "text": reply_text})

                state["count"] += 1
                await message.reply(reply_text)

            except Exception as e:
                await message.reply(f"エラーが発生しました: {e}")

bot.run(os.environ.get("DISCORD_BOT_TOKEN"))
