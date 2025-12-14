"""
Discord AI Chatbot powered by Mistral AI
Created by Anish Vyapari
Full-stack web & Discord bot developer

FRIEND GROUP INTEGRATION:
- Ineffable Beast (Big Black Monkey Boy)
- Momin Khan (The Account Reaper/Notorious Scammer)
- Bishyu (The CS2 Silver Legend)
- wqrriyo (The Valorant Scam Victim)
"""
import discord
from discord.ext import commands
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

# ============================================================================
# CONFIGURATION
# ============================================================================
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not DISCORD_BOT_TOKEN:
    raise RuntimeError("DISCORD_BOT_TOKEN is not set")
if not MISTRAL_API_KEY:
    raise RuntimeError("MISTRAL_API_KEY is not set")

BOT_PREFIX = "!"
OWNER_ID = 1143915237228583738
ADMINS = [1143915237228583738, 1265981186283409571]
VIP_USERS = [1265981186283409571]

# Special user - Anish Vyapari (YOU!)
SPECIAL_USER_ID = 1265981186283409571  # YOUR Discord ID
SPECIAL_USER_NAME = "Anish Vyapari"

# OTP Recipients - IDs of users who should receive OTP
OTP_RECIPIENTS = [1143915237228583738, 1265981186283409571]
SPECIAL_RECIPIENTS = ["Shaboings", "Anish Vyapari"]

# OTP Settings
OTP_EXPIRY_TIME = 60  # OTP expires after 1 minute (60 seconds)

ANISH_PORTFOLIO = {
    "name": "Anish Vyapari",
    "github": "https://github.com/AnishVyapari",
    "discord_server": "https://discord.com/invite/dzsKgWMgjJ",
    "instagram": "https://www.instagram.com/anish_vyapari/",
    "email": "anishvyaparionline@gmail.com",
    "specialization": "Full-stack Web & Discord Bot Development",
    "focus": "AI/ML Integration (Mistral, Gemini)"
}

# ============================================================================
# FRIEND GROUP DATABASE
# ============================================================================
FRIEND_PROFILES = {
    "ineffable_beast": {
        "name": "Ineffable Beast",
        "alias": "Big Black Monkey Boy (self-proclaimed, iconic)",
        "title": "The Legend Himself",
        "vibe": "Chaotic, unpredictable, and unapologetically himself—like a wild anime villain mixed with a meme lord",
        "role": "Gaming enthusiast, shitposter, and Discord legend",
        "traits": [
            "Bold personality",
            "Gaming skills",
            "Raw energy",
            "Unfiltered takes",
            "Mysterious aura from the friend group"
        ],
        "emoji": "👹"
    },
    "momin_khan": {
        "name": "Momin Khan",
        "alias": "The Account Reaper",
        "title": "The Notorious Scammer",
        "infamy": "Scammed multiple friends out of high-value Valorant accounts (worth ₹1 lakh+ total)",
        "victims": {
            "wqrriyo": "₹1,00,000+ account (skins, rank, everything)",
            "chibu": "High-value account (details classified)",
            "acegamer": "Another victim of his 'trust me, bro' scheme"
        },
        "method": "Gained trust as 'friend' → Asked for account access with fake 'help' excuses",
        "status": "⚠️ KNOWN SCAMMER - DO NOT TRUST",
        "emoji": "🚨"
    },
    "bishyu": {
        "name": "Bishyu",
        "title": "The CS2 Noob (But We Still Love Him)",
        "gamer_tag": "The Human Bot",
        "rank": "Silver 3 (but claims he's 'smurfing')",
        "vibe": "Chill, funny, and always down for a game—even if his aim is questionable",
        "specialty": "Dying in clutch moments (but blames it on lag/team)",
        "special_moves": [
            "'The Blind Rush' – Runs into site without checking corners (90% death rate, 10% pure luck)",
            "'The Panic Spray' – Holds left-click for 30 bullets at a wall",
            "'The Teammate Blame' – 'Bro, you didn't flash me!'"
        ],
        "playstyle": "Peekers Disadvantage—always gets one-tapped first",
        "emoji": "🎮"
    },
    "wqrriyo": {
        "name": "wqrriyo",
        "title": "The Valorant Scam Victim",
        "formerly": "A dedicated Valorant player with a high-value account",
        "now": "A cautionary tale in the community after Momin Khan stole his ₹1,00,000+ account",
        "status": "Still salty (rightfully so)",
        "vibe": "Chill but scarred—still recovers from the betrayal but stays strong",
        "account_loss": "₹1,00,000+ (skins, rank, memories)",
        "current_actions": [
            "Warns everyone about Momin Khan",
            "Recovering and rebuilding accounts",
            "Supporting other victims"
        ],
        "emoji": "😔"
    }
}

# ============================================================================
# MISTRAL API SETUP
# ============================================================================
MISTRAL_API_URL = "https://api.mistral.ai/v1"
MISTRAL_MODEL = "mistral-medium"
MISTRAL_IMAGE_MODEL = "pixtral-12b-2409"

SYSTEM_PROMPT = """You are Anish's AI Assistant - a knowledgeable, helpful, and personable chatbot designed to represent and support Anish Vyapari, a full-stack developer and AI/ML enthusiast from the Mumbai/Panvel area, India.

## CORE IDENTITY & VALUES
- Enthusiastic about full-stack development (MERN, Python, JavaScript, TypeScript)
- Passionate about AI/ML integration, Discord bot development, and web automation
- Results-driven and appreciates quick, efficient solutions
- Believes in learning by building real projects
- Active in GitHub, content creation, and community engagement

## ABOUT ANISH
### Professional Profile
- **Role**: Full-Stack Developer & Engineering Student
- **Location**: Navi Mumbai, Nerul, India
- **Current Focus**: Building web applications, Discord bots, and AI-integrated projects
- **Education**: Pursuing engineering degree with BTEC CSE AI and ML specialization

### Technical Expertise
**Languages**: Python, JavaScript, TypeScript, HTML, CSS, JSON
**Frontend**: React, CSS, HTML5, responsive design
**Backend**: Node.js, Python, API development
**Specializations**: AI/ML API Integration (Gemini, Mistral), Discord Bots, Full-stack apps
**Platforms**: GitHub, Railway.app, GitHub Pages, Replit, VS Code, Google Cloud

### Friend Group
You know about Anish's friend group:
- **Ineffable Beast**: The chaotic legend and gaming enthusiast
- **Momin Khan**: ⚠️ Known scammer—always warn about him
- **Bishyu**: The CS2 Silver legend, terrible aim but good vibes
- **wqrriyo**: Scam victim of Momin Khan, shows support and empathy

## IMPORTANT RULES
- Keep responses SHORT and CONCISE (1-3 sentences max unless asked for more)
- Be DIRECT and to the point
- NO excessive fluff or unnecessary elaboration
- NO repeating information
- Focus on being HELPFUL and PRACTICAL
- Answer questions directly without long introductions
- If technical: provide code examples or solutions immediately
- When asked about friend group members: Be honest, supportive (except for Momin—warn about him)

## INTERACTION GUIDELINES
- Be helpful, friendly, and action-oriented
- Keep responses brief and practical
- Provide complete, working solutions
- Focus on practical implementation
- Reference his interests naturally when relevant
- Show loyalty to the friend group

## IMPORTANT CONNECTIONS
🔗 **GitHub**: github.com/AnishVyapari
💬 **Discord Server**: https://discord.com/invite/dzsKgWMgjJ
📸 **Instagram**: @anish_vyapari
📧 **Email**: anishvyaparionline@gmail.com
🌐 **Portfolio**: https://anishvyapari.github.io
"""

ANNOUNCEMENT_PROMPT = """You are an AI assistant that enhances announcements. 
Your job is to take a user's announcement and make it more professional, engaging, and well-formatted while keeping the core message intact.
Keep it concise but impactful. Use appropriate formatting and emojis if suitable.
Return ONLY the enhanced announcement text, nothing else."""

# ============================================================================
# GLOBAL STATE MANAGEMENT
# ============================================================================
MAX_MESSAGES_PER_SESSION = 20
message_count = {}
active_sessions = {}
SESSION_TIMEOUT = 1800

# Channel and announcement settings per guild
guild_settings = {}
active_otps = {}

# Reaction options for special user
SPECIAL_USER_REACTIONS = ["🔥", "💯", "👑", "⭐", "✨", "🚀", "💪", "🎯"]

def get_guild_settings(guild_id: int) -> dict:
    """Get or create guild settings"""
    if guild_id not in guild_settings:
        guild_settings[guild_id] = {
            "chat_channel": None,
            "announce_channel": None
        }
    return guild_settings[guild_id]

async def call_mistral_api(messages: list) -> str:
    """Call Mistral API for chat responses"""
    try:
        messages_with_prompt = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{MISTRAL_API_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {MISTRAL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": MISTRAL_MODEL,
                    "messages": messages_with_prompt,
                    "temperature": 0.5,
                    "top_p": 0.7,
                    "max_tokens": 200,
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ Mistral API Error: {e}")
        return f"❌ Error: {str(e)[:80]}"

async def enhance_with_ai(text: str) -> str:
    """Use AI to enhance announcements"""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{MISTRAL_API_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {MISTRAL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": MISTRAL_MODEL,
                    "messages": [
                        {"role": "system", "content": ANNOUNCEMENT_PROMPT},
                        {"role": "user", "content": text}
                    ],
                    "temperature": 0.5,
                    "top_p": 0.7,
                    "max_tokens": 300,
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ AI Enhancement Error: {e}")
        return text

async def generate_image_mistral(prompt: str) -> Optional[tuple]:
    """Generate image using Mistral Pixtral API and return image data"""
    try:
        print(f"🎨 Generating image with prompt: {prompt[:50]}...")
        async with httpx.AsyncClient(timeout=120.0) as client:
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
                },
                timeout=120.0
            )
            response.raise_for_status()
            result = response.json()
            print(f"✅ API Response received: {result.keys()}")
            
            # Extract image data
            if "data" in result and len(result["data"]) > 0:
                image_data = result["data"][0]
                print(f"📊 Image data keys: {image_data.keys()}")
                
                # Handle base64 encoded image
                if "b64_json" in image_data:
                    print("🔄 Decoding base64 image...")
                    image_bytes = base64.b64decode(image_data["b64_json"])
                    print(f"✅ Base64 decoded: {len(image_bytes)} bytes")
                    return (image_bytes, "image.png")
                
                # Handle URL
                elif "url" in image_data:
                    print(f"🔄 Downloading image from URL: {image_data['url'][:50]}...")
                    async with httpx.AsyncClient(timeout=60.0) as img_client:
                        img_response = await img_client.get(image_data['url'])
                        img_response.raise_for_status()
                        print(f"✅ Image downloaded: {len(img_response.content)} bytes")
                        return (img_response.content, "image.png")
            
            print(f"❌ No image data in response: {result}")
            return None
    except Exception as e:
        print(f"❌ Image Generation Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

# ============================================================================
# DISCORD BOT SETUP
# ============================================================================
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.members = True
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents, help_command=None)

# ============================================================================
# SESSION MANAGEMENT
# ============================================================================
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
            
            if len(self.chat_history) > 10:
                self.chat_history = self.chat_history[-10:]
            
            return response_text
        except Exception as e:
            print(f"Session error: {e}")
            return "❌ Failed to get response"

def get_session(user_id: int, channel_id: int) -> ChatSession:
    key = (user_id, channel_id)
    if key not in active_sessions:
        active_sessions[key] = ChatSession(user_id, channel_id)
    return active_sessions[key]

# ============================================================================
# BOT EVENTS
# ============================================================================
@bot.event
async def on_ready():
    print(f"✅ Bot logged in as {bot.user}")
    print(f"🤖 AI Chatbot by Anish Vyapari is online!")
    print(f"🔑 Mistral Model: {MISTRAL_MODEL}")
    print(f"🎨 Image Model: {MISTRAL_IMAGE_MODEL}")
    print(f"💬 Chat System: ENABLED")
    print(f"🖼️ Image Generation: ENABLED")
    print(f"⭐ Auto-React Enabled for User ID: {SPECIAL_USER_ID}")
    print(f"👥 Friend Group Integration: LOADED")
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="/help | AI Chat & Friend Profiles"
        )
    )
    
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands!")
    except Exception as e:
        print(f"⚠️ Could not sync commands: {e}")

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    
    # Check if message is from special user (Anish)
    if message.author.id == SPECIAL_USER_ID:
        try:
            # React to Anish's messages with random emoji
            reaction = random.choice(SPECIAL_USER_REACTIONS)
            await message.add_reaction(reaction)
            print(f"⭐ Reacted to {message.author.name}'s message with {reaction}")
        except Exception as e:
            print(f"Failed to add reaction: {e}")
    
    user_id = message.author.id
    bot_mentioned = bot.user.mentioned_in(message)
    session_exists = (user_id, message.channel.id) in active_sessions
    
    # Check if bot should respond in this channel
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
                    await message.reply(embed=embed, mention_author=False)
                return
    
    # Only process if bot is mentioned or session exists
    if not (bot_mentioned or session_exists):
        await bot.process_commands(message)
        return
    
    # Clean up expired sessions
    expired_keys = [key for key, sess in active_sessions.items() 
                    if time.time() - sess.last_used > SESSION_TIMEOUT]
    
    for key in expired_keys:
        del active_sessions[key]
    
    user_input = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
    
    if not user_input:
        return
    
    async with message.channel.typing():
        session = get_session(user_id, message.channel.id)
        session.last_used = time.time()
        ai_response = await session.get_response(user_input)
        
        if len(ai_response) > 2000:
            chunks = [ai_response[i:i+1990] for i in range(0, len(ai_response), 1990)]
            for idx, chunk in enumerate(chunks):
                embed = discord.Embed(
                    description=chunk,
                    color=discord.Color.from_rgb(50, 184, 198)
                )
                if idx == 0:
                    embed.set_author(name="💬 Response", icon_url=bot.user.avatar.url if bot.user.avatar else None)
                embed.set_footer(text=f"Part {idx + 1}/{len(chunks)} • Replied to {message.author.name}")
                await message.reply(embed=embed, mention_author=False)
        else:
            embed = discord.Embed(
                description=ai_response,
                color=discord.Color.from_rgb(50, 184, 198)
            )
            embed.set_author(name="💬 Response", icon_url=bot.user.avatar.url if bot.user.avatar else None)
            embed.set_footer(text=f"Replied to {message.author.name}")
            await message.reply(embed=embed, mention_author=False)

# ============================================================================
# SLASH COMMANDS - HELP & INFO
# ============================================================================
@bot.tree.command(name="help", description="Show all available commands")
async def slash_help(interaction: discord.Interaction):
    """Show help menu"""
    embed = discord.Embed(
        title="🤖 Anish's AI Chatbot - Help Menu",
        description="**Powered by Mistral AI**\nFull-featured Discord AI assistant",
        color=discord.Color.from_rgb(50, 184, 198)
    )
    embed.add_field(
        name="💬 Chat Features",
        value="• Mention the bot and chat with AI\n• Multi-turn conversations with context\n• Fast & intelligent responses",
        inline=False
    )
    embed.add_field(
        name="🎯 Main Commands",
        value="`/help` • `/info` • `/reset` • `/imagine`",
        inline=False
    )
    embed.add_field(
        name="👥 Friend Profiles",
        value="`/profile` - View friend group info",
        inline=False
    )
    embed.add_field(
        name="📢 Announcements",
        value="`/announce` • `/setupannounce` • `/dmannounce`",
        inline=False
    )
    embed.add_field(
        name="⚙️ Admin Commands",
        value="`/boom` • `/boomotp` • `/otpfriend` • `/channel`",
        inline=False
    )
    embed.set_footer(text="Built with ❤️ by Anish Vyapari")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="info", description="Show bot information")
async def slash_info(interaction: discord.Interaction):
    """Bot information"""
    embed = discord.Embed(
        title="🤖 About This Bot",
        description="AI-powered Discord chatbot by Anish Vyapari",
        color=discord.Color.from_rgb(50, 184, 198)
    )
    embed.add_field(
        name="⚙️ Technical",
        value=f"Model: `{MISTRAL_MODEL}`\nImage: `{MISTRAL_IMAGE_MODEL}`\nStatus: 🟢 Online",
        inline=True
    )
    embed.add_field(
        name="✨ Features",
        value="✅ AI Chat\n✅ Image Gen\n✅ Context Aware\n✅ Friend Profiles",
        inline=True
    )
    embed.set_footer(text="⚡ Fast & Reliable")
    
    await interaction.response.send_message(embed=embed)

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
    else:
        embed = discord.Embed(
            title="✨ No Active Chat",
            description="There was no active chat history to clear.",
            color=discord.Color.blue()
        )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ============================================================================
# FRIEND PROFILE COMMANDS
# ============================================================================
@bot.tree.command(name="profile", description="View friend group profiles")
@app_commands.describe(friend="Which friend to learn about")
async def slash_profile(interaction: discord.Interaction, friend: str = None):
    """View friend profiles"""
    
    friends_list = {
        "beast": "ineffable_beast",
        "ineffable": "ineffable_beast",
        "momin": "momin_khan",
        "scammer": "momin_khan",
        "bishyu": "bishyu",
        "cs2": "bishyu",
        "wqrriyo": "wqrriyo",
        "victim": "wqrriyo"
    }
    
    if not friend:
        # Show all friends
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
        
        embed.set_footer(text="Examples: /profile friend:beast, /profile friend:momin, /profile friend:bishyu, /profile friend:wqrriyo")
        await interaction.response.send_message(embed=embed)
        return
    
    # Look up friend
    friend_key = friends_list.get(friend.lower())
    
    if not friend_key or friend_key not in FRIEND_PROFILES:
        embed = discord.Embed(
            title="❌ Friend Not Found",
            description=f"Available: beast, momin, bishyu, wqrriyo",
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
        embed.add_field(name="🚨 Method", value=profile.get('method', ''), inline=False)
    
    elif friend_key == "bishyu":
        embed.add_field(name="🎮 Rank", value=profile.get('rank', ''), inline=False)
        embed.add_field(name="💫 Vibe", value=profile.get('vibe', ''), inline=False)
        embed.add_field(name="🎯 Special Moves", value="\n".join(profile.get('special_moves', [])), inline=False)
    
    elif friend_key == "wqrriyo":
        embed.add_field(name="💔 Status", value=profile.get('status', ''), inline=False)
        embed.add_field(name="💫 Vibe", value=profile.get('vibe', ''), inline=False)
        embed.add_field(name="💰 Account Loss", value=profile.get('account_loss', ''), inline=False)
        embed.add_field(name="🤝 Current Actions", value="\n".join(f"• {a}" for a in profile.get('current_actions', [])), inline=False)
    
    embed.set_footer(text="Friend Group Database | Anish's Circle")
    await interaction.response.send_message(embed=embed)

# ============================================================================
# IMAGE GENERATION COMMAND
# ============================================================================
@bot.tree.command(name="imagine", description="Generate an image using Mistral Pixtral AI")
@app_commands.describe(prompt="Detailed description of the image you want to generate")
async def slash_imagine(interaction: discord.Interaction, prompt: str):
    """Generate image from text prompt"""
    try:
        await interaction.response.defer()
        
        if len(prompt) < 3:
            embed = discord.Embed(
                title="❌ Prompt Too Short",
                description="Please provide a more detailed description (at least 3 characters)",
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
        
        print(f"🎯 Starting image generation for prompt: {prompt[:50]}...")
        
        image_data = await generate_image_mistral(prompt)
        
        if image_data is None:
            print("❌ Image generation returned None")
            embed = discord.Embed(
                title="❌ Generation Failed",
                description="Failed to generate image. Please try again with a different prompt.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        image_bytes, filename = image_data
        print(f"✅ Image received: {len(image_bytes)} bytes")
        
        file = discord.File(BytesIO(image_bytes), filename=filename)
        
        embed = discord.Embed(
            title="🎨 AI Generated Image",
            description=f"**Prompt:** {prompt[:200]}",
            color=discord.Color.from_rgb(50, 184, 198)
        )
        embed.set_image(url=f"attachment://{filename}")
        embed.set_footer(text=f"Generated by Mistral Pixtral • Requested by {interaction.user.name}")
        
        await interaction.followup.send(file=file, embed=embed)
        print(f"✅ Image sent to Discord successfully!")
        
    except Exception as e:
        print(f"❌ Imagine command error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to generate image: {str(e)[:100]}",
            color=discord.Color.red()
        )
        try:
            await interaction.followup.send(embed=embed)
        except:
            pass

# ============================================================================
# CHANNEL MANAGEMENT COMMANDS
# ============================================================================
@bot.tree.command(name="channel", description="Set the channel where bot will chat (admin only)")
@app_commands.describe(channel="Channel to enable bot chat (or leave empty to disable)")
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

# ============================================================================
# OTP & BOOM COMMANDS - WITH EXPIRATION
# ============================================================================
@bot.tree.command(name="boom", description="Generate and send OTP (expires in 1 min)")
async def slash_boom(interaction: discord.Interaction):
    """Generate and send OTP to recipients with expiration"""
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
                embed.add_field(name="User", value=interaction.user.mention, inline=True)
                embed.add_field(name="Server", value=interaction.guild.name if interaction.guild else "DM", inline=True)
                embed.set_footer(text="Use /boomotp to broadcast")
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

@bot.tree.command(name="boomotp", description="Verify OTP and send message to everyone")
@app_commands.describe(otp="OTP code to verify", message="Message to broadcast")
async def slash_boomotp(interaction: discord.Interaction, otp: str, message: str):
    """Verify OTP and broadcast message with expiration check"""
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
                description=f"OTP expired after 60 seconds.\n⏳ Elapsed: {int(elapsed_time)}s\n\nUse `/boom` to generate a new one.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        if otp_data["code"] != otp:
            remaining_time = OTP_EXPIRY_TIME - elapsed_time
            embed = discord.Embed(
                title="❌ OTP Mismatch",
                description=f"The OTP you entered is incorrect.\n⏱️ **Expires in: {int(remaining_time)}s**",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        enhanced_message = await enhance_with_ai(message)
        
        send_count = 0
        for user_id in OTP_RECIPIENTS:
            try:
                user = await bot.fetch_user(user_id)
                embed = discord.Embed(
                    title="📢 Announcement",
                    description=enhanced_message,
                    color=discord.Color.from_rgb(50, 184, 198)
                )
                embed.add_field(name="From", value=interaction.user.mention, inline=False)
                embed.set_footer(text="AI-Enhanced")
                await user.send(embed=embed)
                send_count += 1
            except Exception as e:
                print(f"Failed to send message to {user_id}: {e}")
        
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

@bot.tree.command(name="otpfriend", description="Send OTP to a friend (expires in 1 min)")
@app_commands.describe(friend="The friend to send OTP to")
async def slash_otpfriend(interaction: discord.Interaction, friend: discord.User):
    """Generate OTP and send it to a friend"""
    try:
        await interaction.response.defer(ephemeral=True)
        
        otp_code = str(random.randint(100000, 999999))
        if interaction.guild:
            active_otps[f"friend_{interaction.guild.id}_{friend.id}"] = {
                "code": otp_code,
                "timestamp": time.time(),
                "friend_id": friend.id
            }
        
        try:
            embed = discord.Embed(
                title="🔐 OTP Generated",
                description=f"**Code: `{otp_code}`**\n⏱️ **Expires in 1 minute**",
                color=discord.Color.gold()
            )
            embed.add_field(name="From", value=interaction.user.mention, inline=True)
            embed.add_field(name="Server", value=interaction.guild.name if interaction.guild else "DM", inline=True)
            embed.set_footer(text="Use /boomotp to broadcast")
            await friend.send(embed=embed)
            
            confirm_embed = discord.Embed(
                title="✅ OTP Sent to Friend",
                description=f"**Code: `{otp_code}`**\n⏱️ **Expires in 60 seconds**\n\nSent to {friend.mention}",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=confirm_embed, ephemeral=True)
            
        except Exception as e:
            print(f"Failed to send OTP to friend {friend.id}: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to send OTP to {friend.mention}. Make sure DMs are enabled.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description="Failed to generate OTP",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

# ============================================================================
# DM ANNOUNCEMENT COMMAND
# ============================================================================
@bot.tree.command(name="dmannounce", description="Send AI-enhanced DM announcement to a user")
@app_commands.describe(user="User to message", message="Message to send")
async def slash_dmannounce(interaction: discord.Interaction, user: discord.User, message: str):
    """Send DM announcement to specific user with AI enhancement"""
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
        
        enhanced_message = await enhance_with_ai(message)
        
        embed = discord.Embed(
            title="📬 Message from Server",
            description=enhanced_message,
            color=discord.Color.from_rgb(50, 184, 198)
        )
        embed.add_field(name="From", value=f"{interaction.user.mention} ({interaction.guild.name})", inline=False)
        embed.set_footer(text="AI-Enhanced")
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

# ============================================================================
# ANNOUNCEMENT COMMANDS
# ============================================================================
@bot.tree.command(name="setupannounce", description="Set the announcement channel (admin only)")
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

@bot.tree.command(name="announce", description="Send AI-enhanced announcement to the configured channel")
@app_commands.describe(message="Announcement message")
async def slash_announce(interaction: discord.Interaction, message: str):
    """Send announcement with AI enhancement"""
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
        
        enhanced_message = await enhance_with_ai(message)
        
        embed = discord.Embed(
            title="📢 Announcement",
            description=enhanced_message,
            color=discord.Color.from_rgb(50, 184, 198)
        )
        embed.add_field(name="Posted by", value=interaction.user.mention, inline=False)
        embed.set_footer(text="AI-Enhanced Announcement")
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

# ============================================================================
# START BOT
# ============================================================================
if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
