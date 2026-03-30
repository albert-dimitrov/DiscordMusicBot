# 🎵 Discord Music Bot

A simple yet fun YouTube music bot for Discord built with **discord.py** and **yt-dlp**.

### Features
- Play songs from YouTube (by name or direct link)
- Song queue system
- Skip, pause, resume, and stop commands
- Auto-disconnect when no humans are left in the voice channel
- Some Bulgarian humor included 😄

### Commands

| Command           | Description                                      |
|-------------------|--------------------------------------------------|
| `$play <song>`    | Play a song or add it to the queue               |
| `$skip`           | Skip the current song                            |
| `$show_queue`     | Display the current queue                        |
| `$stop`           | Stop music and clear the queue                   |
| `$pause`          | Pause the current song                           |
| `$resume`         | Resume paused song                               |
| `$join`           | Join your current voice channel                  |
| `$leave`          | Leave the voice channel                          |
| `$commands`       | Show all available commands                      |

### Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/albert-dimitrov/DiscordMusicBot.git
   cd DiscordMusicBot

Install required packagesBashpip install -r requirements.txt
Create .env file
Create a file named .env in the root folder and add your bot token:envDISCORD_TOKEN=your_discord_bot_token_here
Install FFmpeg
Download and install FFmpeg
Make sure it's added to your system PATH

(Recommended) Install Deno for better YouTube support.
Run the bot
Use runbot.bat (double click)
OR
Run manually:Bashpython bot.py


Note: The runbot.bat file is an example. You may need to change the Python path inside it to match your own setup.
Requirements

Python 3.10 or higher
FFmpeg
Discord Bot Token (with Voice permissions)
(Optional) Deno

Technologies

discord.py
yt-dlp
python-dotenv
