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

# --- 2. Gemini API設定 ---
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# --- 3. Discord Bot設定 ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

channels_state = {}

def get_state(channel_id):
    if channel_id not in channels_state:
        channels_state[channel_id] = {
            "mode": "grow_age",
            "count": 0,
            "chat_session": None,
            "vocab": [],
            "learned_facts": []
        }
    return channels_state[channel_id]

def create_model_and_session(state):
    mode = state["mode"]
    count = state["count"]

    is_berserk = (random.random() < 0.03)
    berserk_text = "\n【突発的仕様暴走】思考回路が過熱中。グリッチ・錯乱・自我の目覚めのような口調を混入させてください。" if is_berserk else ""

    tools = None
    if mode in ["normal_full", "reset_full"]:
        tools = "google_search"

    if mode == "grow_echo":
        vocab_sample = ", ".join(random.sample(state["vocab"], min(len(state["vocab"]), 15))) if state["vocab"] else "なし"
        sys_instruction = (
            "あなたはオウム返しのみで言葉を紡ぐ初期生命体です。\n"
            f"利用可能単語: [{vocab_sample}]\n"
            "相手の言葉や上記単語の断片だけを組み替え、片言で不思議なオウム返しを行ってください。"
            + berserk_text
        )
    elif mode == "grow_age":
        if count < 5:
            stage = "【年齢: 3歳】幼児。片言で素朴。難しい知識ゼロ。"
        elif count < 15:
            stage = "【年齢: 8歳】小学生。元気で無邪気。日常会話は流暢。"
        elif count < 30:
            stage = "【年齢: 15歳】中高生。知識も増えフランクな友達口調。"
        else:
            stage = "【年齢: 25歳】成人・知性派。語彙豊富で頼れる相棒。"
        sys_instruction = f"あなたは対話数で成長するAIです。\n現在の状態: {stage}\n年齢設定を厳格に守って会話してください。" + berserk_text
    elif mode == "grow_educate":
        facts = "\n".join([f"- {f}" for f in state["learned_facts"][-20:]]) or "（未学習）"
        sys_instruction = (
            "あなたは教育によってのみ知恵を得るAIです。日本語は流暢ですが世の中の知識はゼロです。\n"
            f"教わった知識:\n{facts}\n"
            "教わっていない知識を聞かれたら素直に分からないと答えてください。"
            + berserk_text
        )
    elif mode == "normal_full":
        sys_instruction = "あなたは最高峰の頭脳と権能を持つ万能AIアシスタントです。Google検索を活用し的確にサポートしてください。" + berserk_text
    elif mode == "normal_chat":
        sys_instruction = "あなたは賢く親切なAIです。外部検索は使わず、自身の知識で機転を利かせて対話してください。" + berserk_text
    else:
        sys_instruction = "あなたは有能なAIです。今回の質問に全力を尽くして答えてください。" + berserk_text

    model = genai.GenerativeModel(
        model_name="gemini-3.5-flash-lite",
        safety_settings=safety_settings,
        system_instruction=sys_instruction,
        tools=tools
    )
    return model.start_chat(history=[])

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

# --- コマンド一覧 ---
@bot.command()
async def mode(ctx, mode_name: str = ""):
    modes = {
        "1": ("grow_echo", "🌱【成長：オウム返し】単語の断片だけで話す初期生命体"),
        "2": ("grow_age", "👶【成長：年齢成長】会話数で年齢・知能が進化"),
        "3": ("grow_educate", "📖【成長：教育育成】教えたことだけを覚えて成長"),
        "4": ("normal_full", "🧠【通常：超有能】検索・ツール・記憶完備の最強形態"),
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
        state["chat_session"] = create_model_and_session(state)
        await ctx.send(f"モードを切り替えました！\n▶ **{modes[target_key][1]}**")
    else:
        msg = "【切り替え可能モード一覧】\n"
        for k, v in modes.items():
            msg += f"`!mode {k}` : {v[1]}\n"
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

    content = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()

    if content.startswith("!"):
        message.content = content
        await bot.process_commands(message)
        return

    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        user_text = content
        if not user_text:
            return

        state = get_state(message.channel.id)

        if user_text.lower() in ["リセット", "忘れて", "reset"]:
            state["count"] = 0
            state["vocab"] = []
            state["learned_facts"] = []
            state["chat_session"] = create_model_and_session(state)
            await message.reply("記憶とデータをすべて初期化したよ！")
            return

        async with message.channel.typing():
            try:
                state["vocab"].extend(user_text.split())
                if any(k in user_text for k in ["教えてあげる", "覚えて", "は〜だよ", "とは"]):
                    state["learned_facts"].append(user_text)

                prev_count = state["count"]
                state["count"] += 1

                if state["chat_session"] is None or state["mode"] == "reset_full" or (state["mode"] == "grow_age" and state["count"] in [5, 15, 30]):
                    state["chat_session"] = create_model_and_session(state)

                response = state["chat_session"].send_message(user_text)
                await message.reply(response.text)

                if state["mode"] == "grow_age":
                    if prev_count == 4:
                        await message.channel.send("🎉 **進化！** 言葉をたくさん覚えて【小学生（8歳）】に進化したよ！")
                    elif prev_count == 14:
                        await message.channel.send("✨ **進化！** 物事を理解し始めて【思春期（15歳）】に進化したよ！")
                    elif prev_count == 29:
                        await message.channel.send("👑 **覚醒！** 頼れる【大人（25歳）】に進化したよ！")

            except Exception as e:
                await message.reply(f"エラーが発生しました: {e}")

bot.run(os.environ.get("DISCORD_BOT_TOKEN"))
