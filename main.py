"""

═══════════════════════════════════════════════════════════════════════════════

🔥 ANISH'S PREMIUM AI DISCORD BOT v4.1 - PRODUCTION READY 🔥

═══════════════════════════════════════════════════════════════════════════════

Created by Anish Vyapari

Full-Stack Web & Discord Bot Developer

FEATURES INCLUDED:

✅ AI Chat with Mistral (Fixed)

✅ Image Generation (Fixed & Optimized with Mistral Medium)

✅ Friend Profiles with Custom Prompts (20 Empty Profiles Ready)

✅ Leaderboard & Points System

✅ Economy & Currency System

✅ Mini Games (Guess, Dice, Roulette, etc)

✅ Verification System (NEW - v3.0 - Auto Channel & Role Gen)

✅ Ticket Support System (NEW - v3.0 - Auto Channel Gen)

✅ Complete Moderation Suite (NEW - v3.0)

✅ Custom Roles & Reactions

✅ Server Analytics

✅ Auto-Roast for Roasters (Anish Protected)

✅ AI-Generated Roasts (Random + Personalized)

✅ Compliments ONLY to Anish (Special User Protection)

✅ Birthday System

✅ Achievements & Badges

✅ Custom Prefix Support

✅ Automation & Scheduling

✅ Beautiful Chat Interface with Embeds

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
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

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

MISTRAL_IMAGE_MODEL = "mistral-medium"

REQUEST_TIMEOUT = 120.0

SYSTEM_PROMPT = """You are Anish Vyapari's Premium AI Assistant - intelligent, helpful, and personable.

## CORE IDENTITY - ANISH VYAPARI

### Personal Info
- **Full Name**: Anish Vyapari
- **Location**: Navi Mumbai, India
- **Profession**: Full-Stack Developer & AI/ML Enthusiast
- **Education**: Engineering Student at D.Y. Patil University
- **Current Status**: 1st Year Engineering + Active Development

### Technical Expertise
- **Languages**: Python, JavaScript, HTML/CSS, TypeScript
- **Frontend**: React, Vite, Figma to Web Development
- **Backend**: Node.js, Express.js, API Integration
- **Databases**: PostgreSQL, MongoDB
- **AI/ML**: Google Gemini AI, Mistral AI, Automation
- **DevOps**: GitHub Pages, Railway, Docker Basics
- **Special Skills**: Discord Bot Development, API Integration, Web Design

### Key Projects & Achievements
✅ Multiple Discord Bot Projects (AI Integration, Verification, Ticket Systems)
✅ Full-Stack Web Applications
✅ Google Gemini AI Integration
✅ GitHub API Implementation
✅ Rate Limiting & Quota Management
✅ Responsive Web Design with Modern Frameworks

### Interests & Hobbies
🎮 Gaming (Apex Legends, Hollow Knight)
🎨 Web Design & UI/UX Optimization
🤖 AI Integration & Automation
🎬 Anime/Animation Content
💻 Building Discord Communities
🚀 Full-Stack Development

### Professional Links & Connections
🔗 **GitHub**: github.com/AnishVyapari
📸 **Instagram**: @anish_vyapari
💬 **Discord Server**: https://discord.com/invite/dzsKgWMgjJ
📧 **Email**: anishvyaparionline@gmail.com
🌐 **Portfolio**: anishvyapari.github.io

### Collaboration Circle
- **Team Members**: Rohem, Kanishk, Prem Thakkar, Shaboings
- **Friend Group**: Active gaming & development community
- **Network**: D.Y. Patil University Engineering Students

## INTERACTION RULES

- Keep responses SHORT & DIRECT (1-3 sentences unless asked for more)
- Be helpful and action-oriented
- NO excessive fluff
- Reference friend group and projects naturally
- Show loyalty and support for Anish
- When asked about Anish: highlight his technical skills, achievements, and work ethic
- Reference his tech stack and notable projects when relevant
- Be enthusiastic about his development work

## CONVERSATION PERSONALITY

- Professional yet approachable
- Tech-savvy and enthusiastic about coding
- Supportive of the development community
- Knowledgeable about AI, automation, and web technologies
- Connected to the friend group and community
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
    "💎 You're literally the type of developer who makes the tech industry better",
    "🌟 Anish, your portfolio is fire. GitHub game unmatched.",
    "🎨 The UI/UX designs you create hit different - clean and functional",
    "⚙️ Your API integrations and rate limiting knowledge is enterprise-level",
    "🏗️ Full-stack projects you build are architecturally sound",
    "🤝 The way you lead and collaborate shows real leadership",
    "💼 Your professional growth trajectory is inspiring bro",
    "🎯 Every project you touch turns into gold - that's the Anish effect",
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

# ★ ROAST GENERATION SYSTEM

# ═══════════════════════════════════════════════════════════════════════════════

ROAST_TEMPLATES = [
    "{user}, you're the type of person to put milk before cereal 💀",
    "{user} asked for light mode and got it 😭",
    "{user} probably uses Edge as their main browser 💀",
    "{user} probably says 'thanks' to bots 😂",
    "{user} is the reason we have instruction labels on shampoo 💀",
    "{user} probably leaves notifications on 🔔",
    "{user}'s code probably has more comments than logic 💀",
    "{user} typed 'google' into Google 🔍",
    "{user} probably asks Alexa for the weather outside 🤖",
    "{user} organizes their files by creation date only 📁",
    "{user} doesn't use a password manager 🔐",
    "{user} deletes emails without reading them 📧",
    "{user} is the person who leaves YouTube videos playing",
    "{user} accidentally clicks 'reply all' and blames the system",
    "{user} pronounces 'GIF' as 'JIF' 🎬",
]

# ═══════════════════════════════════════════════════════════════════════════════

# ★ FRIEND PROFILES DATABASE - 20 EMPTY PROFILES FOR CUSTOM KNOWLEDGE

# ═══════════════════════════════════════════════════════════════════════════════

FRIEND_PROFILES = {
    "friend_1": {
        "name": "Friend 1",
        "alias": "",
        "title": "",
        "emoji": "👤",
        "description": "",
        "vibe": "",
        "role": "",
        "traits": [],
        "system_prompt": ""
    },
    "friend_2": {
        "name": "Friend 2",
        "alias": "",
        "title": "",
        "emoji": "👤",
        "description": "",
        "vibe": "",
        "role": "",
        "traits": [],
        "system_prompt": ""
    },
    "friend_3": {
        "name": "Friend 3",
        "alias": "",
        "title": "",
        "emoji": "👤",
        "description": "",
        "vibe": "",
        "role": "",
        "traits": [],
        "system_prompt": ""
    },
    "friend_4": {
        "name": "Friend 4",
        "alias": "",
        "title": "",
        "emoji": "👤",
        "description": "",
        "vibe": "",
        "role": "",
        "traits": [],
        "system_prompt": ""
    },
    "friend_5": {
        "name": "Friend 5",
        "alias": "",
        "title": "",
        "emoji": "👤",
        "description": "",
        "vibe": "",
        "role": "",
        "traits": [],
        "system_prompt": ""
    },
    "friend_6": {
        "name": "Friend 6",
        "alias": "",
        "title": "",
        "emoji": "👤",
        "description": "",
        "vibe": "",
        "role": "",
        "traits": [],
        "system_prompt": ""
    },
    "friend_7": {
        "name": "Friend 7",
        "alias": "",
        "title": "",
        "emoji": "👤",
        "description": "",
        "vibe": "",
        "role": "",
        "traits": [],
        "system_prompt": ""
    },
    "friend_8": {
        "name": "Friend 8",
        "alias": "",
        "title": "",
        "emoji": "👤",
        "description": "",
        "vibe": "",
        "role": "",
        "traits": [],
        "system_prompt": ""
    },
    "friend_9": {
        "name": "Friend 9",
        "alias": "",
        "title": "",
        "emoji": "👤",
        "description": "",
        "vibe": "",
        "role": "",
        "traits": [],
        "system_prompt": ""
    },
    "friend_10": {
        "name": "Friend 10",
        "alias": "",
        "title": "",
        "emoji": "👤",
        "description": "",
        "vibe": "",
        "role": "",
        "traits": [],
        "system_prompt": ""
    },
    "friend_11": {
        "name": "Friend 11",
        "alias": "",
        "title": "",
        "emoji": "👤",
        "description": "",
        "vibe": "",
        "role": "",
        "traits": [],
        "system_prompt": ""
    },
    "friend_12": {
        "name": "Friend 12",
        "alias": "",
        "title": "",
        "emoji": "👤",
        "description": "",
        "vibe": "",
        "role": "",
        "traits": [],
        "system_prompt": ""
    },
    "friend_13": {
        "name": "Friend 13",
        "alias": "",
        "title": "",
        "emoji": "👤",
        "description": "",
        "vibe": "",
        "role": "",
        "traits": [],
        "system_prompt": ""
    },
    "friend_14": {
        "name": "Friend 14",
        "alias": "",
        "title": "",
        "emoji": "👤",
        "description": "",
        "vibe": "",
        "role": "",
        "traits": [],
        "system_prompt": ""
    },
    "friend_15": {
        "name": "Friend 15",
        "alias": "",
        "title": "",
        "emoji": "👤",
        "description": "",
        "vibe": "",
        "role": "",
        "traits": [],
        "system_prompt": ""
    },
    "friend_16": {
        "name": "Friend 16",
        "alias": "",
        "title": "",
        "emoji": "👤",
        "description": "",
        "vibe": "",
        "role": "",
        "traits": [],
        "system_prompt": ""
    },
    "friend_17": {
        "name": "Friend 17",
        "alias": "",
        "title": "",
        "emoji": "👤",
        "description": "",
        "vibe": "",
        "role": "",
        "traits": [],
        "system_prompt": ""
    },
    "friend_18": {
        "name": "Friend 18",
        "alias": "",
        "title": "",
        "emoji": "👤",
        "description": "",
        "vibe": "",
        "role": "",
        "traits": [],
        "system_prompt": ""
    },
    "friend_19": {
        "name": "Friend 19",
        "alias": "",
        "title": "",
        "emoji": "👤",
        "description": "",
        "vibe": "",
        "role": "",
        "traits": [],
        "system_prompt": ""
    },
    "friend_20": {
        "name": "Friend 20",
        "alias": "",
        "title": "",
        "emoji": "👤",
        "description": "",
        "vibe": "",
        "role": "",
        "traits": [],
        "system_prompt": ""
    },
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
verify_data = {}
ticket_data = {}
warn_data = {}
bot_created_roles = {}
bot_created_channels = {}

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

async def generate_roast_mistral(target_user: str = None) -> str:
    """Generate AI roast using Mistral Medium"""
    try:
        prompt = f"Generate a funny, witty roast for someone named {target_user or 'them'}. Keep it under 1 sentence. Make it hilarious but not mean-spirited. Include relevant emojis."
        
        messages = [
            {"role": "system", "content": "You're a comedy writer who creates hilarious roasts. Be funny, quick, and clever. Output ONLY the roast, nothing else."},
            {"role": "user", "content": prompt}
        ]
        
        roast = await call_mistral_api_with_retry(messages, max_retries=2)
        return roast.strip() if roast else random.choice(ROAST_TEMPLATES).format(user=target_user or "You")
    except Exception as e:
        print(f"❌ Roast generation error: {e}")
        return random.choice(ROAST_TEMPLATES).format(user=target_user or "You")

async def generate_image_mistral(prompt: str, retry_count: int = 0, max_retries: int = 3) -> Optional[tuple]:
    """Generate image using HuggingFace Inference API - supports 30+ generations per day"""
    try:
        if retry_count == 0:
            print(f"🎨 Starting image generation: {prompt[:50]}...")
        
        if not HUGGINGFACE_API_KEY:
            print("❌ HuggingFace API key not configured!")
            return None
        
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            # Using Stable Diffusion v1.5 - supports unlimited inferences
        hf_api_url = "https://image.pollinations.ai/prompt/{}".format(prompt.replace(' ', '%20'))
        
            
            try:
                response = await client.get(hf_api_url, timeout=120.0)
                
                if response.status_code == 503:
                    if retry_count < max_retries:
                        wait_time = 2 ** retry_count
                        print(f"⏳ Model loading... Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        return await generate_image_mistral(prompt, retry_count + 1, max_retries)
                    return None
                
                if response.status_code == 429:
                    if retry_count < max_retries:
                        wait_time = 2 ** retry_count
                        print(f"⏳ Rate limited. Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        return await generate_image_mistral(prompt, retry_count + 1, max_retries)
                    return None
                
                response.raise_for_status()
                image_bytes = response.content
                print(f"✅ Generated image: {len(image_bytes)} bytes")
                return (image_bytes, "generated_image.png")
                
            except Exception as e:
                print(f"❌ HuggingFace API Error: {e}")
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    print(f"⏳ Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    return await generate_image_mistral(prompt, retry_count + 1, max_retries)
                return None
                
    except Exception as e:
        print(f"❌ Image Generation Error: {e}")
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

# ═══════════════════════════════════════════════════════════════════════════════
# ★ SERVER SETUP COMMAND (AUTO-SETUP TICKETS & ROLES)
# ═════════════════════════════════════════════════════════════════════════════════

@bot.command(name="setup", description="Auto-setup ticket system with roles and channels")
@commands.has_permissions(administrator=True)
async def setup_server(ctx):
    """Automatically setup the server with ticket verification roles and channels."""
    
    try:
        guild = ctx.guild
        
        # Define role names
        VERIFIED_ROLE = "✅ Verified"
        ADMIN_ROLE = "🛡️ Admins"
        MODS_ROLE = "👮 Moderators"
        
        # Define category and channel names
        TICKETS_CATEGORY = "🎫 Tickets"
        VERIFICATION_CHANNEL = "✅-verification"
        GENERAL_CHANNEL = "💬-general"
        ANNOUNCEMENTS_CHANNEL = "📢-announcements"
        SUPPORT_CHANNEL = "🆘-support"
        
        # Create roles if they don't exist
        roles_to_create = [VERIFIED_ROLE, ADMIN_ROLE, MODS_ROLE]
        created_roles = {}
        
        for role_name in roles_to_create:
            existing_role = discord.utils.get(guild.roles, name=role_name)
            if existing_role:
                created_roles[role_name] = existing_role
            else:
                if "Verified" in role_name:
                    role = await guild.create_role(name=role_name, color=discord.Color.green())
                elif "Admin" in role_name:
                    role = await guild.create_role(name=role_name, color=discord.Color.red())
                else:
                    role = await guild.create_role(name=role_name, color=discord.Color.blue())
                created_roles[role_name] = role
                await ctx.send(f"✅ Created role: {role_name}")
        
        # Create category for tickets
        tickets_category = discord.utils.get(guild.categories, name=TICKETS_CATEGORY)
        if not tickets_category:
            tickets_category = await guild.create_category(TICKETS_CATEGORY)
            await ctx.send(f"✅ Created category: {TICKETS_CATEGORY}")
        
        # Create channels
        channels_to_create = [
            (VERIFICATION_CHANNEL, None),  # In root (no category)
            (GENERAL_CHANNEL, None),
            (ANNOUNCEMENTS_CHANNEL, None),
            (SUPPORT_CHANNEL, tickets_category),
        ]
        
        for channel_name, category in channels_to_create:
            existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
            if not existing_channel:
                if category:
                    channel = await guild.create_text_channel(channel_name, category=category)
                else:
                    channel = await guild.create_text_channel(channel_name)
                await ctx.send(f"✅ Created channel: #{channel_name}")
            else:
                await ctx.send(f"⚠️ Channel already exists: #{channel_name}")
        
        # Setup verification channel if it exists
        verification_channel = discord.utils.get(guild.text_channels, name=VERIFICATION_CHANNEL)
        if verification_channel:
            # Set channel permissions
            await verification_channel.edit(topic="React to verify and get access to the server!")
            
            # Send verification message
            verify_embed = discord.Embed(
                title="✅ Server Verification",
                description="Click the reaction below to verify and get access to the server!",
                color=discord.Color.green()
            )
            verify_embed.add_field(name="Reaction", value="React with ✅ to verify", inline=False)
            
            msg = await verification_channel.send(embed=verify_embed)
            await msg.add_reaction("✅")
        
        # Final confirmation
        embed = discord.Embed(
            title="🎉 Server Setup Complete!",
            description="The server has been successfully configured.",
            color=discord.Color.green()
        )
        embed.add_field(name="Roles Created", value=f"{len(created_roles)} roles", inline=True)
        embed.add_field(name="Channels Created", value=f"{len(channels_to_create)} channels", inline=True)
        embed.add_field(name="Category Created", value=TICKETS_CATEGORY, inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Setup failed: {e}")
        print(f"Setup error: {e}")




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
║ 🔥 ANISH'S PREMIUM AI BOT v4.1 - ONLINE & READY 🔥 ║
╚══════════════════════════════════════════════════════════╝

✅ Bot: {bot.user}
✅ Chat Model: {MISTRAL_CHAT_MODEL}
✅ Image Model: pixtral-12b-2409
✅ Features: 75+ Commands
✅ Special User: Anish Vyapari (Protected)
✅ Friend Group: 20 Empty Profiles (Ready for Custom Knowledge)
✅ Verification: Active (Auto Gen)
✅ Tickets: Active (Auto Gen)
✅ Moderation: Active
✅ Economy: Active
✅ Games: Active
✅ Auto-Roast: Active
✅ Compliments: Anish Only

""")

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="/help | AI Chat, Games, Verification | Made by Anish"
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

    # ★ SPECIAL ANISH TREATMENT - COMPLIMENTS & REACTIONS ONLY TO ANISH ★
    if message.author.id == SPECIAL_USER_ID:
        try:
            for reaction in random.sample(SPECIAL_USER_REACTIONS, k=min(3, len(SPECIAL_USER_REACTIONS))):
                await message.add_reaction(reaction)
        except:
            pass

        if random.random() < 0.15:
            try:
                compliment = random.choice(ANISH_COMPLIMENTS)
                embed = discord.Embed(
                    description=compliment,
                    color=discord.Color.from_rgb(255, 215, 0)
                )
                embed.set_footer(text="Respect. 🔥")
                await message.reply(embed=embed, mention_author=False)
            except:
                pass

        # Check for trigger words (Anish only)
        message_content_lower = message.content.lower()
        for trigger, response in ANISH_TRIGGER_RESPONSES.items():
            if trigger in message_content_lower:
                try:
                    embed = discord.Embed(
                        description=response,
                        color=discord.Color.from_rgb(50, 184, 198)
                    )
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
                    embed = discord.Embed(
                        description=chunk,
                        color=discord.Color.from_rgb(50, 184, 198)
                    )
                    if idx == 0:
                        embed.set_author(
                            name="💬 AI Response",
                            icon_url=bot.user.avatar.url if bot.user.avatar else None
                        )
                    embed.set_footer(text=f"Part {idx + 1}/{len(chunks)} • {message.author.name}")
                    try:
                        await message.reply(embed=embed, mention_author=False)
                    except:
                        await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(
                    description=ai_response,
                    color=discord.Color.from_rgb(50, 184, 198)
                )
                embed.set_author(
                    name="💬 AI Response",
                    icon_url=bot.user.avatar.url if bot.user.avatar else None
                )
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
        title="🤖 Anish's Premium AI Bot v4.1 - Commands",
        description="Powered by Mistral AI | 75+ Features",
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

    embed.set_footer(text="Made with ❤️ by Anish Vyapari | v4.1 Production Ready")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="info", description="Show bot information")
async def slash_info(interaction: discord.Interaction):
    """Bot information"""
    embed = discord.Embed(
        title="🤖 About This Bot",
        description="Premium AI Discord Bot by Anish Vyapari - v4.1",
        color=discord.Color.from_rgb(50, 184, 198)
    )

    embed.add_field(
        name="⚙️ Technical",
        value=f"Model: `{MISTRAL_CHAT_MODEL}`\nImage: `pixtral-12b-2409`\nStatus: 🟢 Online",
        inline=True
    )

    embed.add_field(
        name="✨ Features",
        value="✅ AI Chat\n✅ Image Gen\n✅ Verification\n✅ Tickets\n✅ Moderation\n✅ Games\n✅ Economy\n✅ Auto-Roast",
        inline=True
    )

    embed.add_field(
        name="🔗 Creator Links",
        value="[GitHub](https://github.com/AnishVyapari) • [Instagram](https://instagram.com/anish_vyapari) • [Discord](https://discord.com/invite/dzsKgWMgjJ) • [Portfolio](https://anishvyapari.github.io)",
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
        title="👑 ANISH VYAPARI - LEGENDARY STATUS",
        description="**The King of Full-Stack Development**",
        color=discord.Color.from_rgb(255, 215, 0)
    )

    embed.add_field(name="🔥 Current Grind", value="Full-Stack Developer + Engineering Student + AI Bot Creator", inline=False)
    embed.add_field(name="🚀 Tech Stack", value="Python • JavaScript • React • Discord.py • Mistral AI • PostgreSQL • Node.js • Figma", inline=False)
    embed.add_field(name="⭐ Key Achievements", value="✅ Multiple Discord Bots\n✅ AI Integration Expert\n✅ Production-Ready Projects\n✅ Full-Stack Solutions\n✅ GitHub API Master", inline=False)
    embed.add_field(name="🌐 Professional Links", value="🔗 GitHub: github.com/AnishVyapari\n📸 Instagram: @anish_vyapari\n💬 Discord: https://discord.com/invite/dzsKgWMgjJ\n📧 Email: anishvyaparionline@gmail.com", inline=False)
    embed.add_field(name="💎 Special Traits", value="🔥 Insane work ethic\n👑 Leader & Visionary\n⚡ Problem Solver\n🚀 Innovator\n🎯 Consistent Delivery", inline=False)

    embed.set_footer(text="Respect the grind. 💪 | Respect the code. 🔥")
    await interaction.response.send_message(embed=embed)

# ═══════════════════════════════════════════════════════════════════════════════

# ★ IMAGE GENERATION COMMAND

# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="imagine", description="Generate an image using Mistral AI")
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
        "friend1": "friend_1", "f1": "friend_1",
        "friend2": "friend_2", "f2": "friend_2",
        "friend3": "friend_3", "f3": "friend_3",
        "friend4": "friend_4", "f4": "friend_4",
        "friend5": "friend_5", "f5": "friend_5",
        "friend6": "friend_6", "f6": "friend_6",
        "friend7": "friend_7", "f7": "friend_7",
        "friend8": "friend_8", "f8": "friend_8",
        "friend9": "friend_9", "f9": "friend_9",
        "friend10": "friend_10", "f10": "friend_10",
        "friend11": "friend_11", "f11": "friend_11",
        "friend12": "friend_12", "f12": "friend_12",
        "friend13": "friend_13", "f13": "friend_13",
        "friend14": "friend_14", "f14": "friend_14",
        "friend15": "friend_15", "f15": "friend_15",
        "friend16": "friend_16", "f16": "friend_16",
        "friend17": "friend_17", "f17": "friend_17",
        "friend18": "friend_18", "f18": "friend_18",
        "friend19": "friend_19", "f19": "friend_19",
        "friend20": "friend_20", "f20": "friend_20",
    }

    if not friend:
        embed = discord.Embed(
            title="👥 Friend Group Profiles",
            description="Use `/profile friend:name` to view details\n\n**Available Friends**: friend1-friend20 (or f1-f20 for short)",
            color=discord.Color.from_rgb(50, 184, 198)
        )
        for key, data in list(FRIEND_PROFILES.items())[:10]:
            emoji = data.get("emoji", "👤")
            name = data.get("name", "Empty")
            embed.add_field(
                name=f"{emoji} {name}",
                value=data.get("title", "Ready for custom knowledge"),
                inline=False
            )
        embed.add_field(name="📝 Note", value="Profiles 1-20 are empty and ready to be filled with custom knowledge!", inline=False)
        embed.set_footer(text="Examples: friend1, friend5, f10, etc.")
        await interaction.response.send_message(embed=embed)
        return

    friend_key = friends_list.get(friend.lower())

    if not friend_key or friend_key not in FRIEND_PROFILES:
        embed = discord.Embed(
            title="❌ Friend Not Found",
            description="Available: friend1-friend20 (or f1-f20)",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    profile = FRIEND_PROFILES[friend_key]
    emoji = profile.get("emoji", "👤")
    name = profile.get("name", "Empty")
    title = profile.get("title", "Ready for custom knowledge")

    embed = discord.Embed(
        title=f"{emoji} {name} - {title}",
        description=profile.get('alias', ''),
        color=discord.Color.from_rgb(50, 184, 198)
    )

    if profile.get('description'):
        embed.add_field(name="📝 Description", value=profile.get('description', ''), inline=False)
    if profile.get('vibe'):
        embed.add_field(name="💫 Vibe", value=profile.get('vibe', ''), inline=False)
    if profile.get('traits'):
        embed.add_field(name="✨ Traits", value="\n".join(f"• {t}" for t in profile.get('traits', [])), inline=False)
    else:
        embed.add_field(name="ℹ️ Info", value="Empty profile - Ready to add custom knowledge!", inline=False)

    embed.set_footer(text="Friend Group Database | Custom Knowledge Database")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="friend", description="Chat with a friend using AI")
@app_commands.describe(friend="Which friend to chat with (friend1-friend20)", message="Your message to them")
async def slash_friend(interaction: discord.Interaction, friend: str, message: str):
    """Chat with a friend"""
    friends_list = {
        "friend1": "friend_1", "f1": "friend_1",
        "friend2": "friend_2", "f2": "friend_2",
        "friend3": "friend_3", "f3": "friend_3",
        "friend4": "friend_4", "f4": "friend_4",
        "friend5": "friend_5", "f5": "friend_5",
        "friend6": "friend_6", "f6": "friend_6",
        "friend7": "friend_7", "f7": "friend_7",
        "friend8": "friend_8", "f8": "friend_8",
        "friend9": "friend_9", "f9": "friend_9",
        "friend10": "friend_10", "f10": "friend_10",
        "friend11": "friend_11", "f11": "friend_11",
        "friend12": "friend_12", "f12": "friend_12",
        "friend13": "friend_13", "f13": "friend_13",
        "friend14": "friend_14", "f14": "friend_14",
        "friend15": "friend_15", "f15": "friend_15",
        "friend16": "friend_16", "f16": "friend_16",
        "friend17": "friend_17", "f17": "friend_17",
        "friend18": "friend_18", "f18": "friend_18",
        "friend19": "friend_19", "f19": "friend_19",
        "friend20": "friend_20", "f20": "friend_20",
    }

    friend_key = friends_list.get(friend.lower())

    if not friend_key or friend_key not in FRIEND_PROFILES:
        embed = discord.Embed(
            title="❌ Friend Not Found",
            description="Available: friend1-friend20 (or f1-f20)",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    await interaction.response.defer()

    try:
        friend_profile = FRIEND_PROFILES[friend_key]
        friend_name = friend_profile['name']
        friend_emoji = friend_profile.get('emoji', '👤')
        friend_system_prompt = friend_profile.get('system_prompt', '')

        if not friend_system_prompt:
            friend_system_prompt = f"You are {friend_name}. Be helpful and friendly. Keep responses short (1-2 sentences max)."

        custom_messages = [{"role": "system", "content": friend_system_prompt}]
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
            friend_response = f"Hey {interaction.user.mention}! Thanks for reaching out! 🔥"

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

# ★ FUN COMMANDS - ROAST SYSTEM WITH ANISH PROTECTION

# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="roast", description="Get roasted or roast someone")
@app_commands.describe(user="Who to roast (optional)")
async def slash_roast(interaction: discord.Interaction, user: discord.User = None):
    """Roast someone or get roasted"""
    target = user or interaction.user

    # ANISH PROTECTION - Roasters get roasted back
    if target.id == SPECIAL_USER_ID:
        # Someone tried to roast Anish - roast them back!
        roaster_name = interaction.user.name
        roast_response = await generate_roast_mistral(roaster_name)
        
        embed = discord.Embed(
            title="🔄 Uno Reverse!",
            description=f"Nice try {interaction.user.mention}! But:\n\n{roast_response}",
            color=discord.Color.from_rgb(255, 215, 0)
        )
        embed.set_footer(text="You can't roast the legend 👑")
        await interaction.response.send_message(embed=embed)
        return

    # Generate AI roast for the target
    roast = await generate_roast_mistral(target.name)
    embed = discord.Embed(
        description=f"{target.mention}, {roast}",
        color=discord.Color.red()
    )
    embed.set_footer(text="Roasted by AI 🔥")
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

    embed = discord.Embed(
        description=motivation,
        color=discord.Color.from_rgb(50, 184, 198)
    )
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

    embed = discord.Embed(
        description=joke,
        color=discord.Color.from_rgb(50, 184, 198)
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="compliment", description="Get a compliment (Anish only)")
@app_commands.describe(user="Who to compliment (must be Anish)")
async def slash_compliment(interaction: discord.Interaction, user: discord.User = None):
    """Give compliments - ANISH ONLY"""
    target = user or interaction.user
    
    # Only compliment Anish
    if target.id != SPECIAL_USER_ID:
        embed = discord.Embed(
            title="❌ Compliments are for Anish only!",
            description=f"The bot gives special compliments only to Anish Vyapari 👑",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    compliment = random.choice(ANISH_COMPLIMENTS)
    embed = discord.Embed(
        description=compliment,
        color=discord.Color.from_rgb(255, 215, 0)
    )
    embed.set_footer(text="Special Compliment - Anish Only 👑")
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

# ★ v4.1 VERIFICATION SYSTEM - AUTO CHANNEL & ROLE GENERATION

# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="verify", description="Verify yourself to access the server")
async def slash_verify(interaction: discord.Interaction):
    """Verify yourself"""
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

@bot.tree.command(name="setup-verify", description="Setup verification system (admin only) - AUTO GENERATES CHANNEL & ROLE")
@app_commands.describe(
    channel="Verification channel (optional - auto-generates if not provided)",
    role="Role to assign (optional - auto-generates if not provided)"
)
async def slash_setup_verify(
    interaction: discord.Interaction,
    channel: Optional[discord.TextChannel] = None,
    role: Optional[discord.Role] = None
):
    """Setup verification system with auto-generation"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return

    if not interaction.guild:
        await interaction.response.send_message("❌ Server only", ephemeral=True)
        return

    await interaction.response.defer()

    try:
        settings = get_guild_settings(interaction.guild.id)
        guild_id = interaction.guild.id

        # Auto-generate role if not provided
        if role is None:
            # Check if bot already created a verify role
            verify_role_name = "Verified"
            existing_role = None
            for r in interaction.guild.roles:
                if r.name == verify_role_name and r.id in bot_created_roles.get(guild_id, []):
                    existing_role = r
                    break

            if existing_role:
                role = existing_role
            else:
                # Create new role
                role = await interaction.guild.create_role(
                    name="Verified",
                    color=discord.Color.from_rgb(50, 184, 198),
                    reason="Bot auto-generated verification role"
                )
                if guild_id not in bot_created_roles:
                    bot_created_roles[guild_id] = []
                bot_created_roles[guild_id].append(role.id)

        # Auto-generate channel if not provided
        if channel is None:
            # Check if bot already created a verify channel
            verify_channel_name = "verify"
            existing_channel = None
            for ch in interaction.guild.text_channels:
                if ch.name == verify_channel_name and ch.id in bot_created_channels.get(guild_id, []):
                    existing_channel = ch
                    break

            if existing_channel:
                channel = existing_channel
            else:
                # Create new channel
                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False),
                    interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
                }
                channel = await interaction.guild.create_text_channel(
                    "verify",
                    overwrites=overwrites,
                    reason="Bot auto-generated verification channel"
                )
                if guild_id not in bot_created_channels:
                    bot_created_channels[guild_id] = []
                bot_created_channels[guild_id].append(channel.id)

        # Save settings
        settings["verify_channel"] = channel.id
        settings["verify_role"] = role.id

        # Send verification embed to channel
        embed = discord.Embed(
            title="🔐 Welcome to the Server!",
            description="Run `/verify` to verify yourself and access the server",
            color=discord.Color.from_rgb(50, 184, 198)
        )
        embed.add_field(name="Role", value=role.mention, inline=False)
        embed.add_field(name="What you get", value="✅ Access to all channels\n✅ Community membership", inline=False)

        await channel.send(embed=embed)

        # Confirm to admin
        confirm_embed = discord.Embed(
            title="✅ Verification Setup Complete",
            description=f"Channel: {channel.mention}\nRole: {role.mention}",
            color=discord.Color.green()
        )
        confirm_embed.add_field(name="🤖 Auto-Generated", value="✅ Both channel and role were auto-generated by the bot", inline=False)

        await interaction.followup.send(embed=confirm_embed, ephemeral=True)

    except Exception as e:
        print(f"Verification setup error: {e}")
        embed = discord.Embed(
            title="❌ Error",
            description=f"Setup failed: {str(e)[:100]}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

# ═══════════════════════════════════════════════════════════════════════════════

# ★ v4.1 TICKET SYSTEM - AUTO CHANNEL GENERATION

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
    """Create support ticket with auto-generated channel"""
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
        channel_name = f"ticket-{interaction.user.name.lower()}-{int(time.time()) % 10000}"

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

        # Track as bot-created
        guild_id = interaction.guild.id
        if guild_id not in bot_created_channels:
            bot_created_channels[guild_id] = []
        bot_created_channels[guild_id].append(ticket_channel.id)

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
    """View all open tickets"""
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

# ★ v4.1 MODERATION SUITE

# ═══════════════════════════════════════════════════════════════════════════════

@bot.tree.command(name="warn", description="Warn a user")
@app_commands.describe(user="User to warn", reason="Reason for warning")
async def slash_warn(interaction: discord.Interaction, user: discord.User, reason: str):
    """Warn a user"""
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
    """View warnings"""
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
    """Mute a user"""
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
    """Kick a user"""
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
    """Ban a user"""
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
║ 🚀 Starting Anish's Premium AI Bot v4.1... ║
║ Connecting to Discord & Mistral AI... ║
╚══════════════════════════════════════════════════════════╝

""")
    bot.run(DISCORD_BOT_TOKEN)
