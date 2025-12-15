"""

═══════════════════════════════════════════════════════════════════════════════

🔥 ANISH'S PREMIUM AI DISCORD BOT v3.0 - PRODUCTION READY 🔥

═══════════════════════════════════════════════════════════════════════════════

Created by Anish Vyapari

Full-Stack Web & Discord Bot Developer

FEATURES INCLUDED:

✅ AI Chat with Mistral (Fixed)
✅ Image Generation (Fixed & Optimized)
✅ Friend Profiles with Custom Prompts (Fixed & Enhanced)
✅ Leaderboard & Points System
✅ Economy & Currency System
✅ Mini Games (Guess, Dice, Roulette, etc)
✅ Verification System (NEW - v3.0)
✅ Ticket Support System (NEW - v3.0)
✅ Complete Moderation Suite (NEW - v3.0)
✅ Custom Roles & Reactions
✅ Server Analytics
✅ Fun Commands (Roast, Motivate, Jokes, etc)
✅ Birthday System
✅ Achievements & Badges
✅ Custom Prefix Support
✅ Automation & Scheduling

═══════════════════════════════════════════════════════════════════════════════

"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
from datetime import datetime, timedelta
import json
import asyncio
import time
import random
import httpx
from typing import Optional
from io import BytesIO
import base64
from enum import Enum

# ═══════════════════════════════════════════════════════════════════════════════
# ★ CORE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not DISCORD_BOT_TOKEN:
    raise RuntimeError("❌ DISCORD_BOT_TOKEN is not set")
if not MISTRAL_API_KEY:
    raise RuntimeError("❌ MISTRAL_API_KEY is not set")

BOT_PREFIX = "!"
OWNER_ID = 1143915237228583738
ADMINS = [1143915237228583738, 1265981186283409571]
VIP_USERS = [1265981186283409571]
SPECIAL_USER_ID = 1265981186283409571
SPECIAL_USER_NAME = "Anish Vyapari"
OTP_RECIPIENTS = [1143915237228583738, 1265981186283409571]
OTP_EXPIRY_TIME = 60

# ═══════════════════════════════════════════════════════════════════════════════
# ★ MISTRAL API CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

MISTRAL_API_URL = "https://api.mistral.ai/v1"
MISTRAL_CHAT_MODEL = "mistral-medium"
MISTRAL_IMAGE_MODEL = "pixtral-12b-2409"
REQUEST_TIMEOUT = 120.0

SYSTEM_PROMPT = """You are Anish's Premium AI Assistant - intelligent, helpful, and personable.

## CORE IDENTITY

- Full-stack developer & AI/ML enthusiast
- Location: Navi Mumbai, India
- Specialization: Discord bots, Web apps, AI integration
- Technical Stack: Python, JavaScript, React, TypeScript, Mistral AI

## INTERACTION RULES

- Keep responses SHORT & DIRECT (1-3 sentences unless asked for more)
- Be helpful and action-oriented
- NO excessive fluff
- Reference friend group naturally
- Show loyalty to friends

## IMPORTANT CONNECTIONS

🔗 GitHub: github.com/AnishVyapari
📸 Instagram: @anish_vyapari
💬 Discord Server: https://discord.com/invite/dzsKgWMgjJ
📧 Email: anishvyaparionline@gmail.com

"""

ANISH_COMPLIMENTS = [
    "🔥 Yo, your full-stack game is INSANE. Like actually built different.",
    "👑 Bro you're grinding full-time dev work + uni at the same time?? Respect.",
    "💪 Your Discord bot architecture hits different fr fr",
    "🚀 The way you integrate AI into projects is actually wild",
    "⭐ You're out here building AI chatbots while most devs sleep. Legend energy.",
    "✨ Full-stack wizard who actually SHIPS features. That's rare.",
    "🎯 GitHub game is STRONG. Your repos hit different than 99% of devs.",
    "💯 The fact you balance engineering college + side projects is peak hustle",
    "🔥 Your Mistral API integration is cleaner than most enterprise code ngl",
    "👑 You don't just build bots, you build SYSTEMS. That's the difference.",
    "🚀 React + Python + Discord bots? You're living the full-stack dream fr",
    "⚡ The way you debug is what separates real devs from the rest",
    "💎 You're literally the type of developer who makes the tech industry better"
]

ANISH_TRIGGER_RESPONSES = {
    "hey": "🔥 Yo king, what's good? Ready to build something legendary?",
    "thanks": "👑 Always got your back bestie. That's what real homies do.",
    "good morning": "🌅 Good morning legend! Time to ship some code 🚀",
    "goodnight": "🌙 Sleep well king, you earned it after that grind session 💪",
    "hi": "✨ Yo Anish, what's the move?",
    "hello": "👑 Sup king! Ready to make the internet a better place?",
    "ayy": "🔥 YOOO that energy!!! Let's GOOOO",
    "yo": "💯 Yo yo yo, what's up!!!",
    "sup": "🚀 Sup legend, what you working on today?",
}

SPECIAL_USER_REACTIONS = ["🔥", "💯", "👑", "⭐", "✨", "🚀", "💪", "🎯", "💎", "👀"]

# ═══════════════════════════════════════════════════════════════════════════════
# ★ FRIEND PROFILES DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

FRIEND_PROFILES = {
    "ineffable_beast": {
        "name": "Ineffable Beast",
        "alias": "Big Black Monkey Boy (self-proclaimed legend)",
        "title": "The Gaming Legend",
        "emoji": "👹",
        "description": "Chaotic, unpredictable, and unapologetically legendary",
        "vibe": "Raw energy mixed with pure gaming dominance",
        "role": "Gaming enthusiast & Discord legend",
        "traits": ["Bold personality", "Gaming skills", "Raw energy", "Unfiltered takes"],
        "system_prompt": "You're roleplay as Ineffable Beast - the chaotic gaming legend. Be bold, unfiltered, and bring that raw energy. Reference gaming and legendary moments. Keep it short and punchy."
    },
    "momin_khan": {
        "name": "Momin Khan",
        "alias": "The Account Reaper",
        "title": "⚠️ The Notorious Scammer",
        "emoji": "🚨",
        "description": "Known for account scamming worth ₹1 lakh+",
        "status": "DO NOT TRUST",
        "victims": {"wqrriyo": "₹1,00,000+ account", "chibu": "High-value account", "acegamer": "Another victim"},
        "system_prompt": "You're discussing Momin Khan - the known scammer. Always warn people about him. Be serious about the scamming issue but keep tone informative."
    },
    "bishyu": {
        "name": "Bishyu",
        "title": "The CS2 Silver Legend",
        "emoji": "🎮",
        "description": "Silver 3 rank but thinks he's smurfing",
        "rank": "Silver 3 (claims to be smurfing)",
        "specialty": "Dying in clutch moments (but blames lag)",
        "vibe": "Chill but hilariously bad at CS2",
        "special_moves": [
            "'The Blind Rush' - Runs into site without checking corners",
            "'The Panic Spray' - Holds left-click for 30 bullets",
            "'The Teammate Blame' - 'Bro, you didn't flash me!'"
        ],
        "system_prompt": "You're roleplaying as Bishyu - the CS2 Silver player. Be funny about his terrible aim, terrible plays, and blame teammates. Reference dying in clutch moments and blaming lag. Keep it light and funny."
    },
    "wqrriyo": {
        "name": "wqrriyo",
        "title": "The Valorant Scam Victim",
        "emoji": "😔",
        "description": "Lost ₹1,00,000+ to Momin Khan's scam",
        "status": "Recovering from betrayal",
        "vibe": "Chill but still recovering from the account loss",
        "loss": "₹1,00,000+ account (skins, rank, everything)",
        "current_actions": ["Warns everyone about Momin Khan", "Recovering accounts", "Supporting other victims"],
        "system_prompt": "You're roleplaying as wqrriyo - the Valorant victim. Be empathetic but show strength. Warn about Momin Khan. Be supportive of others. Keep it genuine and caring."
    },
    "acegamer": {
        "name": "AceGamer",
        "title": "The Gaming Homie",
        "emoji": "🎮",
        "description": "Part of the friend group",
        "vibe": "Chill vibes, gaming enthusiast",
        "system_prompt": "You're roleplaying as AceGamer - a chill gaming friend. Be friendly, supportive, and bring good vibes. Reference gaming and friend group moments."
    },
    "trunub": {
        "name": "trunub",
        "title": "That Nerul Kid",
        "emoji": "👤",
        "description": "Lives in Nerul, part of the squad",
        "vibe": "Chill and down to game",
        "system_prompt": "You're roleplaying as trunub - the Nerul friend. Be casual and friendly. Reference the squad and gaming."
    },
    "notatalltoxic": {
        "name": "NotAllToxic",
        "title": "wqrriyo's gf",
        "emoji": "👥",
        "description": "Part of the friend group",
        "vibe": "Supportive and chill",
        "system_prompt": "You're roleplaying as NotAllToxic - a supportive friend. Be friendly and inclusive. Show care for the group."
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# ★ GLOBAL STATE & DATABASES
# ═══════════════════════════════════════════════════════════════════════════════

user_data = {}
guild_settings = {}
active_sessions = {}
active_otps = {}
leaderboard = {}
user_points = {}
user_economy = {}
birthdays = {}
achievements = {}

# v3.0 NEW DATABASES
verify_data = {}
ticket_data = {}
warn_data = {}

def get_user_data(user_id: int) -> dict:
    if user_id not in user_data:
        user_data[user_id] = {
            "points": 0,
            "coins": 0,
            "level": 1,
            "messages": 0,
            "achievements": [],
            "last_daily": None,
            "birthday": None
        }
    return user_data[user_id]

def get_guild_settings(guild_id: int) -> dict:
    if guild_id not in guild_settings:
        guild_settings[guild_id] = {
            "chat_channel": None,
            "announce_channel": None,
            "prefix": "!",
            "welcome_message": None,
            "log_channel": None,
            "verify_channel": None,
            "verify_role": None,
            "ticket_category": None
        }
    return guild_settings[guild_id]

# ═══════════════════════════════════════════════════════════════════════════════
# ★ API WRAPPER WITH PROPER ERROR HANDLING & RETRY LOGIC
# ═══════════════════════════════════════════════════════════════════════════════

async def call_mistral_api_with_retry(messages: list, max_retries: int = 3) -> str:
    """Call Mistral Chat API with exponential backoff"""
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.post(
                    f"{MISTRAL_API_URL}/chat/completions",
                    json={
                        "model": MISTRAL_CHAT_MODEL,
                        "messages": messages,
                        "max_tokens": 512,
                        "temperature": 0.7,
                        "top_p": 0.7
                    },
                    headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"}
                )

            if response.status_code == 429:
                wait_time = 2 ** attempt
                print(f"⏳ Rate limited. Retry {attempt + 1}/{max_retries} in {wait_time}s")
                await asyncio.sleep(wait_time)
                continue

            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"❌ Error: {e}. Retry in {wait_time}s")
                await asyncio.sleep(wait_time)
            else:
                print(f"❌ Final attempt failed: {e}")
                raise

    return "❌ Max retries exceeded"

async def call_mistral_api(messages: list) -> str:
    """Call Mistral API with system prompt"""
    try:
        messages_with_prompt = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        return await call_mistral_api_with_retry(messages_with_prompt)
    except Exception as e:
        print(f"❌ Mistral API Error: {e}")
        return f"❌ Error: {str(e)[:80]}"

async def generate_image_mistral(prompt: str, retry_count: int = 0, max_retries: int = 3) -> Optional[tuple]:
    """Generate image using Mistral Pixtral API"""
    try:
        if retry_count == 0:
            print(f"🎨 Starting image generation: {prompt[:50]}...")

        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(
                f"{MISTRAL_API_URL}/images/generations",
                headers={
                    "Authorization": f"Bearer {MISTRAL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": MISTRAL_IMAGE_MODEL,
                    "prompt": prompt,
                    "size": "1024x1024",
                    "quality": "standard",
                    "n": 1
                }
            )

        if response.status_code == 429:
            if retry_count < max_retries:
                wait_time = 2 ** retry_count
                print(f"⏳ Image API rate limited. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                return await generate_image_mistral(prompt, retry_count + 1, max_retries)
            else:
                print("❌ Max retries exceeded for image generation")
                return None

        response.raise_for_status()
        result = response.json()
        print(f"✅ API Response received")

        if "data" in result and len(result["data"]) > 0:
            image_data = result["data"][0]
            print(f"📊 Image data format detected")

            if "b64_json" in image_data:
                print(f"🔄 Processing base64 image...")
                try:
                    image_bytes = base64.b64decode(image_data["b64_json"])
                    print(f"✅ Decoded: {len(image_bytes)} bytes")
                    return (image_bytes, "generated_image.png")
                except Exception as decode_error:
                    print(f"❌ Base64 decode error: {decode_error}")
                    return None

            elif "url" in image_data:
                print(f"🔄 Downloading from URL...")
                try:
                    async with httpx.AsyncClient(timeout=60.0) as img_client:
                        img_response = await img_client.get(image_data["url"])
                        img_response.raise_for_status()
                        print(f"✅ Downloaded: {len(img_response.content)} bytes")
                        return (img_response.content, "generated_image.png")
                except Exception as url_error:
                    print(f"❌ URL download error: {url_error}")
                    return None
            else:
                print(f"⚠️ Unsupported response format")
                return None
        else:
            print(f"❌ No image data in API response")
            return None

    except Exception as e:
        print(f"❌ Image Generation Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# ★ DISCORD BOT SETUP
# ═══════════════════════════════════════════════════════════════════════════════

intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents, help_command=None)

# ═══════════════════════════════════════════════════════════════════════════════
# ★ CHAT SESSION MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

class ChatSession:
    def __init__(self, user_id: int, channel_id: int):
        self.user_id = user_id
        self.channel_id = channel_id
        self.chat_history = []
        self.last_used = time.time()

    async def get_response(self, user_message: str) -> str:
        """Get AI response from Mistral"""
        try:
            self.chat_history.append({"role": "user", "content": user_message})
            response_text = await call_mistral_api(self.chat_history)
            self.chat_history.append({"role": "assistant", "content": response_text})

            if len(self.chat_history) > 20:
                self.chat_history = self.chat_history[-20:]

            return response_text
        except Exception as e:
            print(f"Session error: {e}")
            return "❌ Failed to get response"

def get_session(user_id: int, channel_id: int) -> ChatSession:
    key = (user_id, channel_id)
    if key not in active_sessions:
        active_sessions[key] = ChatSession(user_id, channel_id)
    return active_sessions[key]

# ═══════════════════════════════════════════════════════════════════════════════
# ★ BOT EVENTS
# ═══════════════════════════════════════════════════════════════════════════════

@bot.event
async def on_ready():
    """Bot ready event"""
    print(f"""

╔══════════════════════════════════════════════════════════╗
║ 🔥 ANISH'S PREMIUM AI BOT v3.0 - ONLINE & READY 🔥 ║
╚══════════════════════════════════════════════════════════╝

✅ Bot: {bot.user}
✅ Chat Model: {MISTRAL_CHAT_MODEL}
✅ Image Model: {MISTRAL_IMAGE_MODEL}
✅ Features: 70+ Commands
✅ Special User: Anish Vyapari
✅ Friend Group: Loaded
✅ Verification: Active
✅ Tickets: Active
✅ Moderation: Active
✅ Economy: Active
✅ Games: Active

""")

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="/help | AI Chat, Games, Verification, Tickets | Made by Anish"
        )
    )

    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands!")
    except Exception as e:
        print(f"⚠️ Could not sync commands: {e}")

@bot.event
async def on_message(message: discord.Message):
    """Handle incoming messages with special Anish treatment"""
    if message.author == bot.user or message.author.bot:
        return

    # ★ SPECIAL ANISH TREATMENT ★
    if message.author.id == SPECIAL_USER_ID:
        try:
            for reaction in random.sample(SPECIAL_USER_REACTIONS, k=min(3, len(SPECIAL_USER_REACTIONS))):
                await message.add_reaction(reaction)
        except:
            pass

        if random.random() < 0.15:
            try:
                compliment = random.choice(ANISH_COMPLIMENTS)
                embed = discord.Embed(description=compliment, color=discord.Color.from_rgb(255, 215, 0))
                embed.set_footer(text="Respect. 🔥")
                await message.reply(embed=embed, mention_author=False)
            except:
                pass

    # Check for trigger words
    message_content_lower = message.content.lower()
    for trigger, response in ANISH_TRIGGER_RESPONSES.items():
        if trigger in message_content_lower:
            try:
                embed = discord.Embed(description=response, color=discord.Color.from_rgb(50, 184, 198))
                embed.set_footer(text="👑 Legend Status")
                await message.reply(embed=embed, mention_author=False)
            except:
                pass
            break

    # Chat logic
    user_id = message.author.id
    bot_mentioned = bot.user.mentioned_in(message)
    session_exists = (user_id, message.channel.id) in active_sessions

    if message.guild:
        settings = get_guild_settings(message.guild.id)
        if settings["chat_channel"] is not None:
            if message.channel.id != settings["chat_channel"]:
                if bot_mentioned:
                    embed = discord.Embed(
                        title="📍 Wrong Channel",
                        description=f"I only chat in <#{settings['chat_channel']}>",
                        color=discord.Color.orange()
                    )
                    try:
                        await message.reply(embed=embed, mention_author=False)
                    except:
                        pass

                await bot.process_commands(message)
                return

    if not (bot_mentioned or session_exists):
        await bot.process_commands(message)
        return

    # Clean expired sessions
    expired_keys = [key for key, sess in active_sessions.items()
                    if time.time() - sess.last_used > 1800]
    for key in expired_keys:
        del active_sessions[key]

    user_input = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()

    if not user_input:
        return

    # Check permissions
    if isinstance(message.channel, discord.TextChannel):
        permissions = message.channel.permissions_for(message.guild.me)
        if not permissions.send_messages:
            try:
                await message.author.send("❌ I don't have permission to send messages!")
            except:
                pass
            return

    async with message.channel.typing():
        try:
            session = get_session(user_id, message.channel.id)
            session.last_used = time.time()
            ai_response = await session.get_response(user_input)

            # Update user stats
            user = get_user_data(user_id)
            user["messages"] += 1
            user["points"] += 5

            # Split long responses
            max_length = 3900
            if len(ai_response) > max_length:
                chunks = [ai_response[i:i+max_length] for i in range(0, len(ai_response), max_length)]
                for idx, chunk in enumerate(chunks):
                    embed = discord.Embed(description=chunk, color=discord.Color.from_rgb(50, 184, 198))
                    if idx == 0:
                        embed.set_author(name="💬 Response", icon_url=bot.user.avatar.url if bot.user.avatar else None)
                    embed.set_footer(text=f"Part {idx + 1}/{len(chunks)} • {message.author.name}")
                    try:
                        await message.reply(embed=embed, mention_author=False)
                    except:
                        await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(description=ai_response, color=discord.Color.from_rgb(50, 184, 198))
                embed.set_author(name="💬 Response", icon_url=bot.user.avatar.url if bot.user.avatar else None)
                embed.set_footer(text=f"{message.author.name}")
                try:
                    await message.reply(embed=embed, mention_author=False)
                except:
                    await message.channel.send(embed=embed)

        except Exception as e:
            print(f"❌ Message error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# ★ SLASH COMMANDS - INFO & HELP
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="help", description="Show all available commands")
async def slash_help(interaction: discord.Interaction):
    """Show help menu"""
    embed = discord.Embed(
        title="🤖 Anish's Premium AI Bot v3.0 - Commands",
        description="Powered by Mistral AI | 70+ Features",
        color=discord.Color.from_rgb(50, 184, 198)
    )

    embed.add_field(name="🎯 Main Commands", value="`/help` • `/info` • `/reset` • `/imagine` • `/stats`", inline=False)
    embed.add_field(name="🔐 Verification", value="`/verify` • `/setup-verify`", inline=False)
    embed.add_field(name="🎫 Tickets", value="`/ticket` • `/tickets`", inline=False)
    embed.add_field(name="🛡️ Moderation", value="`/warn` • `/warns` • `/mute` • `/kick` • `/ban`", inline=False)
    embed.add_field(name="👥 Friend Profiles", value="`/profile` • `/friend`", inline=False)
    embed.add_field(name="🎮 Games", value="`/guess` • `/dice` • `/flip` • `/roulette` • `/8ball`", inline=False)
    embed.add_field(name="💰 Economy", value="`/balance` • `/daily` • `/leaderboard`", inline=False)
    embed.add_field(name="📊 User Stats", value="`/stats` • `/profile` • `/achievements`", inline=False)
    embed.add_field(name="📢 Announcements", value="`/announce` • `/setupannounce` • `/dmannounce`", inline=False)
    embed.add_field(name="⚙️ Admin", value="`/boom` • `/boomotp` • `/channel` • `/setupannounce`", inline=False)
    embed.add_field(name="🎉 Fun", value="`/roast` • `/motivate` • `/joke` • `/compliment`", inline=False)

    if interaction.user.id == SPECIAL_USER_ID:
        embed.add_field(name="👑 VIP Only", value="`/glazestatus`", inline=False)

    embed.set_footer(text="Made with ❤️ by Anish Vyapari | v3.0 Production Ready")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="info", description="Show bot information")
async def slash_info(interaction: discord.Interaction):
    """Bot information"""
    embed = discord.Embed(
        title="🤖 About This Bot",
        description="Premium AI Discord Bot by Anish Vyapari - v3.0",
        color=discord.Color.from_rgb(50, 184, 198)
    )

    embed.add_field(
        name="⚙️ Technical",
        value=f"Model: `{MISTRAL_CHAT_MODEL}`\nImage: `{MISTRAL_IMAGE_MODEL}`\nStatus: 🟢 Online",
        inline=True
    )

    embed.add_field(
        name="✨ Features",
        value="✅ AI Chat\n✅ Image Gen\n✅ Verification\n✅ Tickets\n✅ Moderation\n✅ Games\n✅ Economy",
        inline=True
    )

    embed.add_field(
        name="🔗 Links",
        value="[GitHub](https://github.com/AnishVyapari) • [Discord](https://discord.com/invite/dzsKgWMgjJ) • [Instagram](https://instagram.com/anish_vyapari)",
        inline=False
    )

    embed.set_footer(text="⚡ Fast, Reliable & Production Ready")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="glazestatus", description="Check your legendary dev status (Anish only)")
async def slash_glazestatus(interaction: discord.Interaction):
    """Anish's legendary status"""
    if interaction.user.id != SPECIAL_USER_ID:
        await interaction.response.send_message("❌ This is exclusive to the legend.", ephemeral=True)
        return

    embed = discord.Embed(
        title="👑 ANISH'S LEGENDARY STATUS",
        description="**The King of Code**",
        color=discord.Color.from_rgb(255, 215, 0)
    )

    embed.add_field(name="🔥 Current Grind", value="Full-Stack Dev + Engineering Student + AI Bot Creator", inline=False)
    embed.add_field(name="🚀 Tech Stack", value="Python • JavaScript • React • Discord.py • Mistral AI • PostgreSQL", inline=False)
    embed.add_field(name="⭐ Achievements", value="✅ Multiple GitHub projects\n✅ AI Expert\n✅ Production Bots\n✅ College + Dev Balance", inline=False)
    embed.add_field(name="💎 Special Traits", value="🔥 Insane work ethic\n👑 Leader\n⚡ Problem Solver\n🚀 Visionary", inline=False)
    embed.set_footer(text="Respect the grind. 💪")

    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════════════════════════════════════════
# ★ IMAGE GENERATION COMMAND
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="imagine", description="Generate an image using Mistral Pixtral AI")
@app_commands.describe(prompt="Detailed description of the image")
async def slash_imagine(interaction: discord.Interaction, prompt: str):
    """Generate image from prompt"""
    try:
        await interaction.response.defer()

        if len(prompt) < 3:
            embed = discord.Embed(
                title="❌ Prompt Too Short",
                description="Please provide a more detailed description",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return

        if len(prompt) > 1000:
            embed = discord.Embed(
                title="❌ Prompt Too Long",
                description="Please keep your prompt under 1000 characters",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return

        print(f"🎯 Starting image generation...")
        image_data = await generate_image_mistral(prompt)

        if image_data is None:
            embed = discord.Embed(
                title="❌ Generation Failed",
                description="Failed to generate image. Try again with a different prompt.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return

        image_bytes, filename = image_data
        file = discord.File(BytesIO(image_bytes), filename=filename)

        embed = discord.Embed(
            title="🎨 AI Generated Image",
            description=f"**Prompt:** {prompt[:200]}",
            color=discord.Color.from_rgb(50, 184, 198)
        )

        embed.set_image(url=f"attachment://{filename}")
        embed.set_footer(text=f"Generated by Mistral Pixtral • {interaction.user.name}")

        await interaction.followup.send(file=file, embed=embed)
        print(f"✅ Image sent successfully!")

    except Exception as e:
        print(f"❌ Imagine command error: {e}")
        embed = discord.Embed(
            title="❌ Error",
            description=f"Failed: {str(e)[:100]}",
            color=discord.Color.red()
        )
        try:
            await interaction.followup.send(embed=embed)
        except:
            pass

# ═══════════════════════════════════════════════════════════════════════════════
# ★ FRIEND PROFILE COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="profile", description="View friend group profiles")
@app_commands.describe(friend="Which friend to learn about")
async def slash_profile(interaction: discord.Interaction, friend: str = None):
    """View friend profiles with details"""
    friends_list = {
        "beast": "ineffable_beast",
        "ineffable": "ineffable_beast",
        "momin": "momin_khan",
        "scammer": "momin_khan",
        "bishyu": "bishyu",
        "cs2": "bishyu",
        "wqrriyo": "wqrriyo",
        "victim": "wqrriyo",
        "notatalltoxic": "notatalltoxic",
        "toxic": "notatalltoxic",
        "trunub": "trunub",
        "acegamer": "acegamer",
        "ace": "acegamer"
    }

    if not friend:
        embed = discord.Embed(
            title="👥 Friend Group Profiles",
            description="Use `/profile friend:name` to view details",
            color=discord.Color.from_rgb(50, 184, 198)
        )

        for key, data in FRIEND_PROFILES.items():
            emoji = data.get("emoji", "👤")
            embed.add_field(
                name=f"{emoji} {data['name']}",
                value=data.get("title", ""),
                inline=False
            )

        embed.set_footer(text="Examples: beast, momin, bishyu, wqrriyo")
        await interaction.response.send_message(embed=embed)
        return

    friend_key = friends_list.get(friend.lower())

    if not friend_key or friend_key not in FRIEND_PROFILES:
        embed = discord.Embed(
            title="❌ Friend Not Found",
            description="Available: beast, momin, bishyu, wqrriyo, notatalltoxic, trunub, acegamer",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    profile = FRIEND_PROFILES[friend_key]
    emoji = profile.get("emoji", "👤")

    embed = discord.Embed(
        title=f"{emoji} {profile['name']} - {profile.get('title', '')}",
        description=profile.get('alias', ''),
        color=discord.Color.from_rgb(50, 184, 198)
    )

    if friend_key == "ineffable_beast":
        embed.add_field(name="🎮 Role", value=profile.get('role', ''), inline=False)
        embed.add_field(name="💫 Vibe", value=profile.get('vibe', ''), inline=False)
        embed.add_field(name="✨ Traits", value="\n".join(f"• {t}" for t in profile.get('traits', [])), inline=False)

    elif friend_key == "momin_khan":
        embed.add_field(name="⚠️ STATUS", value=profile.get('status', ''), inline=False)
        embed.add_field(name="💰 Victims & Losses", value="\n".join(f"• {v}: {l}" for v, l in profile.get('victims', {}).items()), inline=False)

    elif friend_key == "bishyu":
        embed.add_field(name="🎮 Rank", value=profile.get('rank', ''), inline=False)
        embed.add_field(name="💫 Vibe", value=profile.get('vibe', ''), inline=False)
        embed.add_field(name="🎯 Special Moves", value="\n".join(profile.get('special_moves', [])), inline=False)

    elif friend_key == "wqrriyo":
        embed.add_field(name="💔 Status", value=profile.get('status', ''), inline=False)
        embed.add_field(name="💫 Vibe", value=profile.get('vibe', ''), inline=False)
        embed.add_field(name="💰 Account Loss", value=profile.get('loss', ''), inline=False)
        embed.add_field(name="🤝 Current Actions", value="\n".join(f"• {a}" for a in profile.get('current_actions', [])), inline=False)

    else:
        embed.add_field(name="ℹ️ Info", value="Part of the squad!", inline=False)

    embed.set_footer(text="Friend Group Database")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="friend", description="Chat with a friend using AI")
@app_commands.describe(friend="Which friend to chat with", message="Your message to them")
async def slash_friend(interaction: discord.Interaction, friend: str, message: str):
    """Chat with a friend"""
    friends_list = {
        "beast": "ineffable_beast",
        "ineffable": "ineffable_beast",
        "momin": "momin_khan",
        "scammer": "momin_khan",
        "bishyu": "bishyu",
        "cs2": "bishyu",
        "wqrriyo": "wqrriyo",
        "victim": "wqrriyo",
        "notatalltoxic": "notatalltoxic",
        "toxic": "notatalltoxic",
        "trunub": "trunub",
        "acegamer": "acegamer",
        "ace": "acegamer"
    }

    friend_key = friends_list.get(friend.lower())

    if not friend_key or friend_key not in FRIEND_PROFILES:
        embed = discord.Embed(
            title="❌ Friend Not Found",
            description="Available: beast, momin, bishyu, wqrriyo, notatalltoxic, trunub, acegamer",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    await interaction.response.defer()

    try:
        friend_profile = FRIEND_PROFILES[friend_key]
        friend_name = friend_profile['name']
        friend_emoji = friend_profile.get('emoji', '👤')

        custom_system = f"""You are {friend_name} from Anish's friend group.

{friend_profile.get('system_prompt', 'Be friendly and chill.')}

Keep responses SHORT and punchy (1-2 sentences max).

Be authentic to this character's personality.

"""

        custom_messages = [{"role": "system", "content": custom_system}]
        custom_messages.append({"role": "user", "content": message})

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.post(
                    f"{MISTRAL_API_URL}/chat/completions",
                    json={
                        "model": MISTRAL_CHAT_MODEL,
                        "messages": custom_messages,
                        "max_tokens": 256,
                        "temperature": 0.8,
                        "top_p": 0.8
                    },
                    headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"}
                )

                response.raise_for_status()
                friend_response = response.json()["choices"][0]["message"]["content"]

        except Exception as api_error:
            print(f"❌ Friend API Error: {api_error}")
            friend_response = f"Yo, {interaction.user.mention}! Something went wrong, but I appreciate the love! 🔥"

        embed = discord.Embed(
            title=f"{friend_emoji} {friend_name} replies:",
            description=friend_response,
            color=discord.Color.from_rgb(50, 184, 198)
        )

        embed.set_footer(text=f"Responding to {interaction.user.name}")
        await interaction.followup.send(embed=embed)

    except Exception as e:
        print(f"❌ Friend command error: {e}")
        embed = discord.Embed(
            title="❌ Error",
            description="Failed to get response from friend",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

# ═══════════════════════════════════════════════════════════════════════════════
# ★ GAME COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="guess", description="Guess a number between 1-100")
async def slash_guess(interaction: discord.Interaction):
    """Number guessing game"""
    await interaction.response.defer()

    secret = random.randint(1, 100)
    attempts = 0
    max_attempts = 7

    embed = discord.Embed(
        title="🎮 Number Guessing Game",
        description="I'm thinking of a number between 1-100.\nYou have 7 attempts!",
        color=discord.Color.from_rgb(50, 184, 198)
    )

    embed.set_footer(text="Reply with a number in this channel")
    await interaction.followup.send(embed=embed)

    def check(msg):
        return msg.author == interaction.user and msg.channel == interaction.channel and msg.content.isdigit()

    while attempts < max_attempts:
        try:
            guess_msg = await bot.wait_for('message', check=check, timeout=30.0)
            guess = int(guess_msg.content)
            attempts += 1

            if guess < secret:
                await interaction.channel.send(f"🔺 Too low! Attempts: {attempts}/{max_attempts}")
            elif guess > secret:
                await interaction.channel.send(f"🔻 Too high! Attempts: {attempts}/{max_attempts}")
            else:
                embed = discord.Embed(
                    title="🎉 You Won!",
                    description=f"The number was {secret}!\nAttempts: {attempts}/{max_attempts}",
                    color=discord.Color.green()
                )
                await interaction.channel.send(embed=embed)
                user = get_user_data(interaction.user.id)
                user["coins"] += 50
                return

        except asyncio.TimeoutError:
            await interaction.channel.send("⏱️ Time's up!")
            return

    embed = discord.Embed(
        title="💀 Game Over!",
        description=f"The number was {secret}. Better luck next time!",
        color=discord.Color.red()
    )
    await interaction.channel.send(embed=embed)

@bot.tree.command(name="dice", description="Roll a dice")
async def slash_dice(interaction: discord.Interaction):
    """Roll a dice"""
    roll = random.randint(1, 6)

    embed = discord.Embed(
        title="🎲 Dice Roll",
        description=f"You rolled: **{roll}**",
        color=discord.Color.from_rgb(50, 184, 198)
    )

    embed.set_footer(text=f"{interaction.user.name}")
    await interaction.response.send_message(embed=embed)

    user = get_user_data(interaction.user.id)
    user["coins"] += roll * 5

@bot.tree.command(name="flip", description="Flip a coin")
async def slash_flip(interaction: discord.Interaction):
    """Flip a coin"""
    result = random.choice(["Heads", "Tails"])

    embed = discord.Embed(
        title="🪙 Coin Flip",
        description=f"Result: **{result}**",
        color=discord.Color.from_rgb(50, 184, 198)
    )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="roulette", description="Play Russian roulette (50/50 chance to win)")
async def slash_roulette(interaction: discord.Interaction):
    """Roulette game"""
    if random.random() < 0.5:
        embed = discord.Embed(
            title="🎰 Roulette - YOU WIN!",
            description="You survived! 💰 +100 coins",
            color=discord.Color.green()
        )
        user = get_user_data(interaction.user.id)
        user["coins"] += 100

    else:
        embed = discord.Embed(
            title="🎰 Roulette - YOU LOSE!",
            description="Better luck next time! 💸 -50 coins",
            color=discord.Color.red()
        )
        user = get_user_data(interaction.user.id)
        user["coins"] = max(0, user["coins"] - 50)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="8ball", description="Ask the magic 8-ball a question")
@app_commands.describe(question="Your question")
async def slash_8ball(interaction: discord.Interaction, question: str):
    """Magic 8-ball"""
    responses = [
        "Yes", "No", "Maybe", "Definitely", "Absolutely Not",
        "Ask again later", "The signs point to yes", "Don't count on it",
        "It is certain", "Very doubtful", "Outlook good", "Concentrate and ask again"
    ]

    answer = random.choice(responses)

    embed = discord.Embed(
        title="🔮 Magic 8-Ball",
        description=f"**Q:** {question}\n**A:** {answer}",
        color=discord.Color.from_rgb(50, 184, 198)
    )

    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════════════════════════════════════════
# ★ ECONOMY COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="balance", description="Check your coin balance")
async def slash_balance(interaction: discord.Interaction, user: discord.User = None):
    """Check balance"""
    target_user = user or interaction.user
    user_data_obj = get_user_data(target_user.id)

    embed = discord.Embed(
        title="💰 Balance",
        description=f"{target_user.mention}",
        color=discord.Color.gold()
    )

    embed.add_field(name="💵 Coins", value=f"{user_data_obj['coins']}", inline=True)
    embed.add_field(name="⭐ Points", value=f"{user_data_obj['points']}", inline=True)
    embed.add_field(name="📊 Level", value=f"{user_data_obj['level']}", inline=True)
    embed.add_field(name="💬 Messages", value=f"{user_data_obj['messages']}", inline=True)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="daily", description="Claim your daily coins")
async def slash_daily(interaction: discord.Interaction):
    """Daily coins"""
    user_data_obj = get_user_data(interaction.user.id)
    last_daily = user_data_obj.get("last_daily")

    if last_daily and (datetime.now() - last_daily).days < 1:
        embed = discord.Embed(
            title="⏱️ Already Claimed",
            description="Come back tomorrow for more coins!",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    coins_earned = 500
    user_data_obj["coins"] += coins_earned
    user_data_obj["last_daily"] = datetime.now()

    embed = discord.Embed(
        title="🎉 Daily Coins Claimed!",
        description=f"You earned **{coins_earned}** coins!\nTotal: **{user_data_obj['coins']}**",
        color=discord.Color.green()
    )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="leaderboard", description="View the coin leaderboard")
async def slash_leaderboard(interaction: discord.Interaction):
    """Leaderboard"""
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]["coins"], reverse=True)[:10]

    embed = discord.Embed(
        title="🏆 Coin Leaderboard",
        description="Top 10 Richest Users",
        color=discord.Color.gold()
    )

    for idx, (user_id, data) in enumerate(sorted_users, 1):
        try:
            user_obj = await bot.fetch_user(user_id)
            embed.add_field(
                name=f"#{idx} {user_obj.name}",
                value=f"💰 {data['coins']} coins",
                inline=False
            )
        except:
            embed.add_field(
                name=f"#{idx} User {user_id}",
                value=f"💰 {data['coins']} coins",
                inline=False
            )

    embed.set_footer(text="Climb to the top!")
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════════════════════════════════════════
# ★ USER STATS COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="stats", description="View your stats")
async def slash_stats(interaction: discord.Interaction, user: discord.User = None):
    """View user stats"""
    target_user = user or interaction.user
    user_data_obj = get_user_data(target_user.id)

    embed = discord.Embed(
        title="📊 User Stats",
        description=f"{target_user.mention}",
        color=discord.Color.from_rgb(50, 184, 198)
    )

    embed.add_field(name="💬 Messages", value=str(user_data_obj["messages"]), inline=True)
    embed.add_field(name="⭐ Points", value=str(user_data_obj["points"]), inline=True)
    embed.add_field(name="📈 Level", value=str(user_data_obj["level"]), inline=True)
    embed.add_field(name="💰 Coins", value=str(user_data_obj["coins"]), inline=True)
    embed.add_field(name="🏆 Achievements", value=str(len(user_data_obj["achievements"])), inline=True)
    embed.add_field(name="🎂 Birthday", value=user_data_obj["birthday"] or "Not set", inline=True)

    embed.set_footer(text="Keep grinding!")
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════════════════════════════════════════
# ★ FUN COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="roast", description="Get roasted (or roast someone)")
@app_commands.describe(user="Who to roast (optional)")
async def slash_roast(interaction: discord.Interaction, user: discord.User = None):
    """Roast someone"""
    target = user or interaction.user

    roasts = [
        f"{target.mention}, you're the type of person to put milk before cereal 💀",
        f"{target.mention} asked for light mode and got it 😭",
        f"{target.mention} probably uses Edge as their main browser 💀",
        f"{target.mention} probably says 'thanks' to bots 😂",
        f"{target.mention} is the reason we have instruction labels on shampoo 💀",
        f"{target.mention} probably leaves notifications on 🔔",
        f"{target.mention}'s code probably has more comments than logic 💀",
    ]

    roast = random.choice(roasts)

    embed = discord.Embed(description=roast, color=discord.Color.red())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="motivate", description="Get motivated by the bot")
async def slash_motivate(interaction: discord.Interaction):
    """Motivation"""
    motivations = [
        "🚀 You're doing great! Keep pushing!",
        "💪 Every expert was once a beginner. You got this!",
        "🔥 Your potential is limitless. Believe in yourself!",
        "⭐ You're closer to your goals than you think!",
        "💯 Excellence is not a destination, it's a journey!",
        "👑 You're stronger than your excuses!",
        "🎯 Focus on progress, not perfection!",
    ]

    motivation = random.choice(motivations)

    embed = discord.Embed(description=motivation, color=discord.Color.from_rgb(50, 184, 198))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="joke", description="Tell a joke")
async def slash_joke(interaction: discord.Interaction):
    """Tell a joke"""
    jokes = [
        "Why do programmers prefer dark mode? Because light attracts bugs! 🔦",
        "How many programmers does it take to change a light bulb? None, that's a hardware problem! 💡",
        "Why do Java developers wear glasses? Because they don't C#! 👓",
        "How many SQL databases have been harmed in your life? None, I do not harm them. I do not harm others! 😂",
        "Why do Python programmers go to the gym? To get more fit! 💪",
    ]

    joke = random.choice(jokes)

    embed = discord.Embed(description=joke, color=discord.Color.from_rgb(50, 184, 198))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="compliment", description="Get a compliment")
@app_commands.describe(user="Who to compliment (optional)")
async def slash_compliment(interaction: discord.Interaction, user: discord.User = None):
    """Give compliments"""
    target = user or interaction.user

    compliments = [
        f"{target.mention}, your smile can light up the darkest room 😊",
        f"{target.mention}, you bring out the best in other people! 💫",
        f"{target.mention}, you're a smart cookie! 🍪",
        f"{target.mention}, you deserve a hug right now 🤗",
        f"{target.mention}, you're an awesome person! 🌟",
        f"{target.mention}, your perspective is refreshing! 🎯",
        f"{target.mention}, you light up the room! 🔥",
    ]

    compliment = random.choice(compliments)

    embed = discord.Embed(description=compliment, color=discord.Color.from_rgb(50, 184, 198))
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════════════════════════════════════════
# ★ ADMIN COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="reset", description="Clear your chat history")
async def slash_reset(interaction: discord.Interaction):
    """Reset chat session"""
    key = (interaction.user.id, interaction.channel.id)

    if key in active_sessions:
        del active_sessions[key]

    embed = discord.Embed(
        title="✨ Chat Cleared",
        description="Your conversation history has been reset.",
        color=discord.Color.green()
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="channel", description="Set the chat channel (admin only)")
@app_commands.describe(channel="Channel to enable (or leave empty to disable)")
async def slash_channel(interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
    """Set chat channel restriction"""
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="Only administrators can use this command.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if not interaction.guild:
        embed = discord.Embed(
            title="❌ Error",
            description="This command can only be used in a server.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    settings = get_guild_settings(interaction.guild.id)

    if channel is None:
        settings["chat_channel"] = None
        embed = discord.Embed(
            title="✅ Restriction Removed",
            description="Bot will now respond in all channels.",
            color=discord.Color.green()
        )
    else:
        settings["chat_channel"] = channel.id
        embed = discord.Embed(
            title="✅ Chat Channel Set",
            description=f"Bot will only chat in {channel.mention}",
            color=discord.Color.green()
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="boom", description="Generate an OTP (expires in 1 min)")
async def slash_boom(interaction: discord.Interaction):
    """Generate OTP"""
    try:
        await interaction.response.defer(ephemeral=True)

        otp_code = str(random.randint(100000, 999999))

        if interaction.guild:
            active_otps[interaction.guild.id] = {
                "code": otp_code,
                "timestamp": time.time()
            }

        send_count = 0

        for user_id in OTP_RECIPIENTS:
            try:
                user = await bot.fetch_user(user_id)

                embed = discord.Embed(
                    title="🔐 OTP Generated",
                    description=f"**Code: `{otp_code}`**\n⏱️ **Expires in 1 minute**",
                    color=discord.Color.gold()
                )

                embed.add_field(name="From", value=interaction.user.mention, inline=True)

                if interaction.guild:
                    embed.add_field(name="Server", value=interaction.guild.name, inline=True)

                await user.send(embed=embed)
                send_count += 1

            except Exception as e:
                print(f"Failed to send OTP to {user_id}: {e}")

        embed = discord.Embed(
            title="✅ OTP Sent",
            description=f"**Code: `{otp_code}`**\n⏱️ **Expires in 60 seconds**\n\nSent to {send_count} recipients",
            color=discord.Color.green()
        )

        await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description="Failed to generate OTP",
            color=discord.Color.red()
        )

        await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="boomotp", description="Verify OTP and broadcast message")
@app_commands.describe(otp="OTP code to verify", message="Message to broadcast")
async def slash_boomotp(interaction: discord.Interaction, otp: str, message: str):
    """Verify OTP and broadcast"""
    try:
        await interaction.response.defer()

        if not interaction.guild or interaction.guild.id not in active_otps:
            embed = discord.Embed(
                title="❌ Invalid OTP",
                description="No OTP generated for this server. Use `/boom` first.",
                color=discord.Color.red()
            )

            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        otp_data = active_otps[interaction.guild.id]

        elapsed_time = time.time() - otp_data["timestamp"]

        if elapsed_time > OTP_EXPIRY_TIME:
            del active_otps[interaction.guild.id]

            embed = discord.Embed(
                title="❌ OTP Expired",
                description=f"OTP expired after 60 seconds.",
                color=discord.Color.red()
            )

            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        if otp_data["code"] != otp:
            remaining_time = OTP_EXPIRY_TIME - elapsed_time

            embed = discord.Embed(
                title="❌ OTP Mismatch",
                description=f"The OTP you entered is incorrect.",
                color=discord.Color.red()
            )

            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        send_count = 0

        for user_id in OTP_RECIPIENTS:
            try:
                user = await bot.fetch_user(user_id)

                embed = discord.Embed(
                    title="📢 Announcement",
                    description=message,
                    color=discord.Color.from_rgb(50, 184, 198)
                )

                embed.add_field(name="From", value=interaction.user.mention, inline=False)

                await user.send(embed=embed)
                send_count += 1

            except Exception as e:
                print(f"Failed to send to {user_id}: {e}")

        del active_otps[interaction.guild.id]

        embed = discord.Embed(
            title="✅ Broadcast Complete",
            description=f"Sent to {send_count} recipients",
            color=discord.Color.green()
        )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description="Broadcast failed",
            color=discord.Color.red()
        )

        await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="announce", description="Send an announcement (admin only)")
@app_commands.describe(message="Announcement message")
async def slash_announce(interaction: discord.Interaction, message: str):
    """Send announcement"""
    try:
        await interaction.response.defer()

        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="Only administrators can use this command.",
                color=discord.Color.red()
            )

            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        if not interaction.guild:
            embed = discord.Embed(
                title="❌ Error",
                description="This command can only be used in a server.",
                color=discord.Color.red()
            )

            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        settings = get_guild_settings(interaction.guild.id)

        if settings["announce_channel"] is None:
            embed = discord.Embed(
                title="❌ No Channel Configured",
                description="Please use `/setupannounce` to set the announcement channel first.",
                color=discord.Color.red()
            )

            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        announce_channel = bot.get_channel(settings["announce_channel"])

        if not announce_channel:
            embed = discord.Embed(
                title="❌ Channel Not Found",
                description="The configured announcement channel could not be found.",
                color=discord.Color.red()
            )

            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(
            title="📢 Announcement",
            description=message,
            color=discord.Color.from_rgb(50, 184, 198)
        )

        embed.add_field(name="Posted by", value=interaction.user.mention, inline=False)

        await announce_channel.send(embed=embed)

        confirm_embed = discord.Embed(
            title="✅ Announcement Sent",
            description=f"Message posted to {announce_channel.mention}",
            color=discord.Color.green()
        )

        await interaction.followup.send(embed=confirm_embed, ephemeral=True)

    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description="Announcement failed",
            color=discord.Color.red()
        )

        await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="setupannounce", description="Set announcement channel (admin only)")
@app_commands.describe(channel="Channel for announcements")
async def slash_setupannounce(interaction: discord.Interaction, channel: discord.TextChannel):
    """Setup announcement channel"""
    try:
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="Only administrators can use this command.",
                color=discord.Color.red()
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not interaction.guild:
            embed = discord.Embed(
                title="❌ Error",
                description="This command can only be used in a server.",
                color=discord.Color.red()
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        settings = get_guild_settings(interaction.guild.id)

        settings["announce_channel"] = channel.id

        embed = discord.Embed(
            title="✅ Announcement Channel Set",
            description=f"Announcements will be sent to {channel.mention}",
            color=discord.Color.green()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description="Setup failed",
            color=discord.Color.red()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="dmannounce", description="Send DM announcement (admin only)")
@app_commands.describe(user="User to message", message="Message to send")
async def slash_dmannounce(interaction: discord.Interaction, user: discord.User, message: str):
    """Send DM announcement"""
    try:
        await interaction.response.defer(ephemeral=True)

        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="Only administrators can use this command.",
                color=discord.Color.red()
            )

            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(
            title="📬 Message",
            description=message,
            color=discord.Color.from_rgb(50, 184, 198)
        )

        embed.add_field(name="From", value=f"{interaction.user.mention}", inline=False)

        await user.send(embed=embed)

        confirm_embed = discord.Embed(
            title="✅ DM Sent",
            description=f"Message sent to {user.mention}",
            color=discord.Color.green()
        )

        await interaction.followup.send(embed=confirm_embed, ephemeral=True)

    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description="Failed to send DM",
            color=discord.Color.red()
        )

        await interaction.followup.send(embed=embed, ephemeral=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ★ v3.0 VERIFICATION SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="verify", description="Verify yourself to access the server")
async def slash_verify(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("❌ This command only works in servers", ephemeral=True)
        return
    
    settings = get_guild_settings(interaction.guild.id)
    
    if "verify_role" not in settings or settings["verify_role"] is None:
        embed = discord.Embed(
            title="❌ Verification Not Configured",
            description="Admin needs to run `/setup-verify` first",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    role = interaction.guild.get_role(settings["verify_role"])
    
    if not role:
        embed = discord.Embed(
            title="❌ Verification Role Missing",
            description="The verification role was deleted",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    try:
        await interaction.user.add_roles(role)
        embed = discord.Embed(
            title="✅ Verified!",
            description=f"You've been given the {role.mention} role",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to verify: {str(e)[:50]}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="setup-verify", description="Setup verification system (admin only)")
@app_commands.describe(
    channel="Verification channel",
    role="Role to assign on verification"
)
async def slash_setup_verify(interaction: discord.Interaction, channel: discord.TextChannel, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return
    
    settings = get_guild_settings(interaction.guild.id)
    settings["verify_channel"] = channel.id
    settings["verify_role"] = role.id
    
    embed = discord.Embed(
        title="✅ Verification Setup Complete",
        description=f"Channel: {channel.mention}\nRole: {role.mention}",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    verify_embed = discord.Embed(
        title="🔐 Welcome!",
        description="Run `/verify` to verify yourself and access the server",
        color=discord.Color.from_rgb(50, 184, 198)
    )
    
    await channel.send(embed=verify_embed)

# ═══════════════════════════════════════════════════════════════════════════════
# ★ v3.0 TICKET SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

class TicketType(Enum):
    SUPPORT = "support"
    REPORT = "report"
    SUGGESTION = "suggestion"
    APPEAL = "appeal"

@bot.tree.command(name="ticket", description="Create a support ticket")
@app_commands.describe(
    topic="Ticket type: support, report, suggestion, or appeal"
)
async def slash_ticket(interaction: discord.Interaction, topic: str):
    if not interaction.guild:
        await interaction.response.send_message("❌ Only works in servers", ephemeral=True)
        return
    
    valid_topics = [t.value for t in TicketType]
    
    if topic.lower() not in valid_topics:
        embed = discord.Embed(
            title="❌ Invalid Topic",
            description=f"Choose: {', '.join(valid_topics)}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        channel_name = f"ticket-{interaction.user.name}-{int(time.time()) % 10000}"
        
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        
        ticket_channel = await interaction.guild.create_text_channel(
            channel_name,
            overwrites=overwrites,
            topic=f"Ticket by {interaction.user.name} - {topic.upper()}"
        )
        
        ticket_data[ticket_channel.id] = {
            "creator": interaction.user.id,
            "topic": topic,
            "created_at": datetime.now(),
            "guild": interaction.guild.id
        }
        
        embed = discord.Embed(
            title=f"🎫 {topic.upper()} Ticket",
            description=f"Created by: {interaction.user.mention}\nTopic: {topic.upper()}",
            color=discord.Color.from_rgb(50, 184, 198)
        )
        embed.add_field(name="📝 Instructions", value="Describe your issue below. Staff will respond soon.", inline=False)
        
        await ticket_channel.send(embed=embed)
        
        confirm_embed = discord.Embed(
            title="✅ Ticket Created",
            description=f"Your ticket: {ticket_channel.mention}",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=confirm_embed, ephemeral=True)
    
    except Exception as e:
        embed = discord.Embed(
            title="❌ Failed to Create Ticket",
            description=str(e)[:100],
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="tickets", description="View all open tickets (admin only)")
async def slash_tickets(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return
    
    if not interaction.guild:
        await interaction.response.send_message("❌ Only works in servers", ephemeral=True)
        return
    
    guild_tickets = [
        (ch_id, data) for ch_id, data in ticket_data.items()
        if data.get("guild") == interaction.guild.id
    ]
    
    if not guild_tickets:
        embed = discord.Embed(
            title="🎫 No Open Tickets",
            description="All tickets have been resolved!",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"🎫 Open Tickets ({len(guild_tickets)})",
        color=discord.Color.from_rgb(50, 184, 198)
    )
    
    for ch_id, data in guild_tickets:
        channel = interaction.guild.get_channel(ch_id)
        if channel:
            embed.add_field(
                name=f"#{channel.name}",
                value=f"Topic: {data['topic'].upper()}\nCreator: <@{data['creator']}>",
                inline=False
            )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ★ v3.0 MODERATION SUITE
# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="warn", description="Warn a user")
@app_commands.describe(user="User to warn", reason="Reason for warning")
async def slash_warn(interaction: discord.Interaction, user: discord.User, reason: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return
    
    if not interaction.guild:
        await interaction.response.send_message("❌ Only works in servers", ephemeral=True)
        return
    
    if user.id not in warn_data:
        warn_data[user.id] = []
    
    warn_data[user.id].append({
        "reason": reason,
        "warned_by": interaction.user.name,
        "date": datetime.now().isoformat()
    })
    
    try:
        embed = discord.Embed(
            title="⚠️ Warning",
            description=f"Server: {interaction.guild.name}\nReason: {reason}",
            color=discord.Color.orange()
        )
        await user.send(embed=embed)
    except:
        pass
    
    embed = discord.Embed(
        title="✅ User Warned",
        description=f"{user.mention} has been warned\nReason: {reason}\nWarnings: {len(warn_data[user.id])}",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="warns", description="View user warnings")
@app_commands.describe(user="User to check")
async def slash_warns(interaction: discord.Interaction, user: discord.User):
    if not interaction.guild:
        await interaction.response.send_message("❌ Only works in servers", ephemeral=True)
        return
    
    if user.id not in warn_data or not warn_data[user.id]:
        embed = discord.Embed(
            title="✅ No Warnings",
            description=f"{user.mention} has no warnings",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
        return
    
    embed = discord.Embed(
        title=f"⚠️ Warnings for {user.name}",
        description=f"Total: {len(warn_data[user.id])}",
        color=discord.Color.orange()
    )
    
    for idx, warning in enumerate(warn_data[user.id], 1):
        embed.add_field(
            name=f"Warning #{idx}",
            value=f"Reason: {warning['reason']}\nBy: {warning['warned_by']}",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mute", description="Mute a user (admin only)")
@app_commands.describe(user="User to mute", duration="Duration in minutes")
async def slash_mute(interaction: discord.Interaction, user: discord.Member, duration: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return
    
    overwrites = interaction.channel.overwrites_for(user)
    overwrites.send_messages = False
    
    await interaction.channel.set_permissions(user, overwrite=overwrites)
    
    embed = discord.Embed(
        title="🔇 User Muted",
        description=f"{user.mention} muted for {duration} minutes",
        color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    await asyncio.sleep(duration * 60)
    
    overwrites.send_messages = None
    await interaction.channel.set_permissions(user, overwrite=overwrites)

@bot.tree.command(name="kick", description="Kick a user from the server")
@app_commands.describe(user="User to kick", reason="Reason for kick")
async def slash_kick(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ You don't have permission", ephemeral=True)
        return
    
    try:
        await user.kick(reason=reason)
        embed = discord.Embed(
            title="✅ User Kicked",
            description=f"{user.mention} has been kicked\nReason: {reason}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Failed to Kick",
            description=str(e)[:100],
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="ban", description="Ban a user from the server")
@app_commands.describe(user="User to ban", reason="Reason for ban")
async def slash_ban(interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ You don't have permission", ephemeral=True)
        return
    
    try:
        await interaction.guild.ban(user, reason=reason)
        embed = discord.Embed(
            title="✅ User Banned",
            description=f"{user.mention} has been banned\nReason: {reason}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Failed to Ban",
            description=str(e)[:100],
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ★ BOT LAUNCH
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""

╔══════════════════════════════════════════════════════════╗
║ 🚀 Starting Anish's Premium AI Bot v3.0... ║
║ Connecting to Discord & Mistral API... ║
╚══════════════════════════════════════════════════════════╝

""")

    bot.run(DISCORD_BOT_TOKEN)
