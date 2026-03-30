import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import yt_dlp
import asyncio
import re

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

YOUTUBE_URL_REGEX = r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)"

# Improved FFmpeg options
ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -fflags +genpts",
    "options": "-vn -b:a 128k"
}

ytdl_options = {
    'format': 'bestaudio/best',
    'noplaylist': False,
    'quiet': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
    'extractor_args': {
        'youtube': {
            'player_client': ['web', 'ios', 'android'],  # web first to avoid many PO Token issues
        }
    }
}

ytdl = yt_dlp.YoutubeDL(ytdl_options)

class MusicQueue:
    def __init__(self):
        self.queue = []

    def add(self, item):
        self.queue.append(item)

    def pop(self):
        return self.queue.pop(0) if self.queue else None

    def is_empty(self):
        return len(self.queue) == 0

    def clear(self):
        self.queue.clear()


music_queues = {}

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")


@bot.event
async def on_voice_state_update(member, before, after):
    if member.guild.voice_client is None or member.guild.voice_client.channel is None:
        return

    humans = [m for m in member.guild.voice_client.channel.members if not m.bot]
    if len(humans) == 0:
        await member.guild.voice_client.disconnect()
        print("🔌 Auto-disconnected: no humans left.")


@bot.command()
async def commands(ctx):
    embed = discord.Embed(title="🎧 Music Bot Help", description="Available commands:", color=0x3498db)
    embed.add_field(
        name="🎵 Music Commands",
        value=(
            "**$play <song or url>** - Play or add to queue\n"
            "**$skip** - Skip current song\n"
            "**$show_queue** - Show queue\n"
            "**$stop** - Stop and clear queue\n"
            "**$pause** - Pause\n"
            "**$resume** - Resume\n"
            "**$join** - Join your voice channel\n"
            "**$leave** - Leave voice"
        ),
        inline=False
    )
    embed.set_footer(text="Music Bot | Powered by DiapazonRecords")
    await ctx.send(embed=embed)


@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        return await ctx.send("❌ You must be in a voice channel first!")

    channel = ctx.author.voice.channel
    if ctx.voice_client:
        if ctx.voice_client.channel == channel:
            return await ctx.send("✅ Already in your channel.")
        await ctx.voice_client.move_to(channel)
        return await ctx.send(f"✅ Moved to **{channel.name}**")

    try:
        await channel.connect(timeout=15.0)   # Increased timeout
        await ctx.send(f"✅ Joined **{channel.name}**")
    except asyncio.TimeoutError:
        await ctx.send("❌ Timed out while trying to join voice channel.")
    except Exception as e:
        await ctx.send(f"❌ Failed to join: {str(e)}")


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send(f"👋 НА МАЙКА ТИ В ПУТКАТА {ctx.author.name}")
    else:
        await ctx.send("I'm not in a voice channel.")


@bot.command(name="show_queue")
async def show_queue(ctx):
    if ctx.guild.id not in music_queues or music_queues[ctx.guild.id].is_empty():
        return await ctx.send("📭 The queue is empty.")

    queue = music_queues[ctx.guild.id].queue
    msg = "**🎶 Upcoming songs:**\n"
    for i, item in enumerate(queue[:12], 1):
        msg += f"**{i}.** {item['title']}\n"
    if len(queue) > 12:
        msg += f"\n... and {len(queue)-12} more."
    await ctx.send(msg)


async def play_next_song(ctx):
    queue = music_queues.get(ctx.guild.id)
    if not queue or queue.is_empty():
        return

    song = queue.pop()
    url = song["url"]
    title = song["title"]

    source = discord.FFmpegOpusAudio(
        url,
        before_options=ffmpeg_options["before_options"],
        options=ffmpeg_options["options"]
    )

    def after_play(err):
        if err:
            print(f"Playback error: {err}")
        asyncio.run_coroutine_threadsafe(play_next_song(ctx), bot.loop)

    ctx.voice_client.play(source, after=after_play)
    await ctx.send(f"🎶 Now playing: **{title}**")


@bot.command()
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("❌ Join a voice channel first!")

    # Join if not connected
    if not ctx.voice_client:
        try:
            await ctx.author.voice.channel.connect(timeout=15.0)
        except asyncio.TimeoutError:
            return await ctx.send("❌ Timed out joining voice channel.")
        except Exception as e:
            return await ctx.send(f"❌ Could not join voice: {str(e)}")

    if ctx.guild.id not in music_queues:
        music_queues[ctx.guild.id] = MusicQueue()

    queue = music_queues[ctx.guild.id]

    try:
        if re.match(YOUTUBE_URL_REGEX, search):
            info = ytdl.extract_info(search, download=False)
        else:
            search_result = ytdl.extract_info(f"ytsearch:{search}", download=False)
            if not search_result or not search_result.get("entries"):
                return await ctx.send("❌ No results found for that song.")
            info = search_result["entries"][0]

        url = info.get("url") or info.get("webpage_url")
        title = info.get("title", search)

        queue.add({"url": url, "title": title})

        if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            await play_next_song(ctx)
        else:
            await ctx.send(f"➕ Added to queue: **{title}**")

    except Exception as e:
        await ctx.send(f"❌ Error while searching/playing **{search}**: {str(e)}")


@bot.command()
async def skip(ctx):
    if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
        ctx.voice_client.stop()
        await ctx.send("⏭ Skipped.")
    else:
        await ctx.send("❌ Nothing is playing.")


@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        if ctx.guild.id in music_queues:
            music_queues[ctx.guild.id].clear()
        await ctx.send("⏹ Stopped and cleared queue.")
    else:
        await ctx.send("❌ Not playing anything.")


@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸ Paused.")
    else:
        await ctx.send("❌ Nothing to pause.")


@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Resumed.")
    else:
        await ctx.send("❌ Nothing is paused.")


bot.run(os.getenv("DISCORD_TOKEN"))
