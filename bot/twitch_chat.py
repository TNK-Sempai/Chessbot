import twitchio
from twitchio.ext import commands
import os
from dotenv import load_dotenv
import threading
from bot.voice import speak

load_dotenv()

class TanukiBot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=os.getenv("TWITCH_TOKEN"),
            client_id=os.getenv("TWITCH_CLIENT_ID"),
            client_secret=os.getenv("TWITCH_CLIENT_SECRET"),
            bot_id=os.getenv("TWITCH_BOT_ID"),
            prefix="!",
            initial_channels=[os.getenv("TWITCH_CHANNEL")]
        )

    async def event_ready(self):
        print(f"Twitch chat connecté ✅ | {self.bot_id}")

    async def event_message(self, message):
        if message.echo:
            return
        print(f"[Chat] {message.author.name}: {message.content}")
        await self.handle_commands(message)

    @commands.command(name="defi")
    async def defi(self, ctx):
        await ctx.send(f"@{ctx.author.name} Le Tanuki accepte ton défi ! Va sur lichess.org/@/TanukiChessBot pour me défier ♟️")
        def speak_async():
            speak(f"{ctx.author.name} has challenged the Tanuki. Come and face me on Lichess.")
        threading.Thread(target=speak_async, daemon=True).start()

    @commands.command(name="question")
    async def question(self, ctx):
        question_text = ctx.message.content.replace("!question", "").strip()
        if not question_text:
            await ctx.send("Pose une question après !question")
            return
        def answer_async():
            from ollama import Client
            client = Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
            response = client.chat(
                model="llama3.1:8b",
                messages=[{
                    "role": "user",
                    "content": f"You are TANUKI, a sarcastic chess bot. Answer in 1-2 sentences: {question_text}"
                }]
            )
            answer = response["message"]["content"]
            speak(answer)
        threading.Thread(target=answer_async, daemon=True).start()

def start_twitch_bot():
    bot = TanukiBot()
    bot.run()