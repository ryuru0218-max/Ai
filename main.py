import discord
from google import genai
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Renderのポート検出用（無料枠で落とされないための設定）
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_web():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_web, daemon=True).start()

# --- Discord Bot & Gemini の設定 ---
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

ai_client = genai.Client(api_key=GEMINI_KEY)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"ログイン成功: {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Bot宛てのメンションに反応
    if client.user in message.mentions:
        prompt = message.content.replace(f"<@{client.user.id}>", "").strip()
        if not prompt:
            await message.reply("何か質問ある？")
            return

        async with message.channel.typing():
            try:
                response = ai_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                await message.reply(response.text[:1900])
            except Exception as e:
                await message.reply(f"エラーが発生しました: {e}")

client.run(DISCORD_TOKEN)
