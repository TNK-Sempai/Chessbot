import twitchio
from twitchio.ext import commands
import os
from dotenv import load_dotenv
import threading
from bot.voice import speak
from bot.stats import get_score_text

load_dotenv()

# File d'attente globale
_queue = []
_queue_lock = threading.Lock()

def get_queue():
    with _queue_lock:
        return list(_queue)

def pop_queue():
    with _queue_lock:
        if _queue:
            return _queue.pop(0)
        return None

def add_to_queue(username):
    with _queue_lock:
        if username not in _queue:
            _queue.append(username)
            return len(_queue)
        return None

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
        position = add_to_queue(ctx.author.name)
        if position:
            if position == 1:
                await ctx.send(f"@{ctx.author.name} Tu es le prochain à affronter le Tanuki ! ♟️")
                speak(f"{ctx.author.name} is next to challenge the Tanuki.")
            else:
                await ctx.send(f"@{ctx.author.name} Tu es #{position} dans la file d'attente. ♟️")
                speak(f"{ctx.author.name} joins the queue at position {position}.")
        else:
            await ctx.send(f"@{ctx.author.name} Tu es déjà dans la file d'attente !")

    @commands.command(name="file")
    async def file(self, ctx):
        queue = get_queue()
        if not queue:
            await ctx.send("La file d'attente est vide — défie le Tanuki avec !defi ♟️")
        else:
            queue_text = " → ".join([f"#{i+1} {name}" for i, name in enumerate(queue)])
            await ctx.send(f"File d'attente : {queue_text}")

    @commands.command(name="score")
    async def score(self, ctx):
        score_text = get_score_text()
        await ctx.send(score_text)
        def speak_async():
            speak(score_text)
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