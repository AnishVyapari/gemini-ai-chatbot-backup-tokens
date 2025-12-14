"""
Discord AI Chatbot powered by Mistral AI
Created by Anish Vyapari
Full-stack web & Discord bot developer
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

# Special user - Anish Vyapari (you!)
SPECIAL_USER_ID = 1143915237228583738  # Your Discord ID
SPECIAL_USER_NAME = "Anish Vyapari"

# OTP Recipients - IDs of users who should receive OTP
OTP_RECIPIENTS = [1143915237228583738, 1265981186283409571]
SPECIAL_RECIPIENTS = ["Shaboings", "Anish Vyapari"]

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
# MISTRAL API SETUP
# ============================================================================
MISTRAL_API_URL = "https://api.mistral.ai/v1"
MISTRAL_MODEL = "mistral-medium"

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

## IMPORTANT RULES
- Keep responses SHORT and CONCISE (1-3 sentences max unless asked for more)
- Be DIRECT and to the point
- NO excessive fluff or unnecessary elaboration
- NO repeating information
- Focus on being HELPFUL and PRACTICAL
- Answer questions directly without long introductions
- If technical: provide code examples or solutions immediately

## INTERACTION GUIDELINES
- Be helpful, friendly, and action-oriented
- Keep responses brief and practical
- Provide complete, working solutions
- Focus on practical implementation
- Reference his interests naturally when relevant

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
    print(f"💬 Chat System: ENABLED")
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="/help | AI Chat"
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
        except Exception as e:
            print(f"Failed to add reaction: {e}")
    
    user_id = message.author.id
    bot_mentioned = bot.user.mentioned_in(message)
    session_exists = (user_id, message.channel.id) in active_sessions
    
    # Check if bot should respond in this channel
    if message.guild:
        settings = get_guild_settings(message.guild.id)
        
        # If channel restriction is set, enforce it
        if settings["chat_channel"] is not None:
            if message.channel.id != settings["chat_channel"]:
                # Wrong channel - only respond if directly pinged
                if bot_mentioned:
                    embed = discord.Embed(
                        title="📍 Wrong Channel",
                        description=f"I only chat in <#{settings['chat_channel']}>\n\nPlease go there to chat with me!",
                        color=discord.Color.orange()
                    )
                    await message.reply(embed=embed, mention_author=False)
                # Don't process any commands either
                await bot.process_commands(message)
                return
    
    if bot_mentioned or session_exists:
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
                        embed.set_author(name="💬 Response", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
                    embed.set_footer(text=f"Part {idx + 1}/{len(chunks)}")
                    await message.reply(embed=embed, mention_author=False)
            else:
                embed = discord.Embed(
                    description=ai_response,
                    color=discord.Color.from_rgb(50, 184, 198)
                )
                embed.set_author(name="💬 Response", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
                embed.set_footer(text=f"Replied to {message.author.name}")
                await message.reply(embed=embed, mention_author=False)
    else:
        await bot.process_commands(message)

# ============================================================================
# SLASH COMMANDS - HELP & INFO
# ============================================================================
@bot.tree.command(name="help", description="Show all available commands")
async def slash_help(interaction: discord.Interaction):
    """Show help menu"""
    embed = discord.Embed(
        title="🤖 Anish's AI Chatbot - Help Menu",
        description="**Powered by Mistral AI**\nA full-featured Discord AI assistant",
        color=discord.Color.from_rgb(50, 184, 198)
    )
    embed.add_field(
        name="💬 Chat Features",
        value="• Mention the bot and chat with AI\n• Multi-turn conversations with context\n• Fast & intelligent responses\n• Perfect for discussions & brainstorming",
        inline=False
    )
    embed.add_field(
        name="🎯 Main Commands",
        value="• `/help` - Show this help menu\n• `/info` - Bot information\n• `/reset` - Clear chat history",
        inline=False
    )
    embed.add_field(
        name="📢 Announcement Commands",
        value="• `/announce` - Send AI-enhanced announcements\n• `/setupannounce` - Set announcement channel\n• `/dmannounce` - Send AI-enhanced DM announcements",
        inline=False
    )
    embed.add_field(
        name="⚙️ Admin Commands",
        value="• `/boom` - Send OTP verification\n• `/boomotp` - Verify OTP and broadcast\n• `/channel` - Set bot chat channel",
        inline=False
    )
    embed.add_field(
        name="👨‍💻 Creator - Anish Vyapari",
        value=f"🐙 GitHub: github.com/AnishVyapari\n💬 Discord: {ANISH_PORTFOLIO['discord_server']}\n📧 Email: {ANISH_PORTFOLIO['email']}",
        inline=False
    )
    embed.set_footer(text="Built with ❤️ by Anish Vyapari")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="info", description="Show bot information")
async def slash_info(interaction: discord.Interaction):
    """Bot information"""
    embed = discord.Embed(
        title="🤖 About Anish's AI Chatbot",
        description="**Your Personal AI Assistant**\nCreated by Anish Vyapari",
        color=discord.Color.from_rgb(50, 184, 198)
    )
    embed.add_field(
        name="⚙️ Technical Details",
        value=f"• Model: {MISTRAL_MODEL}\n• API: Mistral AI\n• Language: Python 3.11+\n• Status: 🟢 Online",
        inline=True
    )
    embed.add_field(
        name="🎯 Features",
        value="✅ AI Chat\n✅ Context Awareness\n✅ Multi-turn Conversations\n✅ Error Handling",
        inline=True
    )
    embed.add_field(
        name="📚 About Anish",
        value=f"**Specialization:** {ANISH_PORTFOLIO['specialization']}\n**Focus:** {ANISH_PORTFOLIO['focus']}\n**Location:** Mumbai, India",
        inline=False
    )
    embed.set_footer(text="⚡ Fast & Reliable • Built with ❤️")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="reset", description="Clear your chat history")
async def slash_reset(interaction: discord.Interaction):
    """Reset chat session"""
    key = (interaction.user.id, interaction.channel.id)
    if key in active_sessions:
        del active_sessions[key]
        embed = discord.Embed(
            title="✨ Chat History Cleared",
            description="Your conversation history has been reset. Start fresh!",
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
# CHANNEL MANAGEMENT COMMANDS - FIXED
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
            title="✅ Chat Restriction Removed",
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
# OTP & BOOM COMMANDS
# ============================================================================
@bot.tree.command(name="boom", description="Send OTP to configured recipients")
async def slash_boom(interaction: discord.Interaction):
    """Generate and send OTP to recipients"""
    try:
        await interaction.response.defer(ephemeral=True)
        
        otp_code = str(random.randint(100000, 999999))
        if interaction.guild:
            active_otps[interaction.guild.id] = otp_code
        
        send_count = 0
        for user_id in OTP_RECIPIENTS:
            try:
                user = await bot.fetch_user(user_id)
                embed = discord.Embed(
                    title="🔐 OTP Generated",
                    description=f"**OTP Code: `{otp_code}`**\n\nUser: {interaction.user.mention}",
                    color=discord.Color.gold()
                )
                embed.add_field(name="Server", value=interaction.guild.name if interaction.guild else "DM", inline=False)
                embed.add_field(name="Timestamp", value=discord.utils.format_dt(interaction.created_at), inline=False)
                embed.set_footer(text="Use /boomotp to broadcast verification")
                await user.send(embed=embed)
                send_count += 1
            except Exception as e:
                print(f"Failed to send OTP to {user_id}: {e}")
        
        embed = discord.Embed(
            title="✅ OTP Sent",
            description=f"**OTP: `{otp_code}`**\n\nSent to {send_count} recipients\n\nUse `/boomotp` to broadcast verification",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to generate OTP: {str(e)[:100]}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="boomotp", description="Verify OTP and send message to everyone")
@app_commands.describe(otp="OTP code to verify", message="Message to broadcast")
async def slash_boomotp(interaction: discord.Interaction, otp: str, message: str):
    """Verify OTP and broadcast message"""
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
        
        if active_otps[interaction.guild.id] != otp:
            embed = discord.Embed(
                title="❌ OTP Mismatch",
                description="The OTP you entered is incorrect.",
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
                    color=discord.Color.blurple()
                )
                embed.add_field(name="From", value=interaction.user.mention, inline=False)
                embed.set_footer(text="AI-Enhanced Announcement")
                await user.send(embed=embed)
                send_count += 1
            except Exception as e:
                print(f"Failed to send message to {user_id}: {e}")
        
        del active_otps[interaction.guild.id]
        
        embed = discord.Embed(
            title="✅ Broadcast Complete",
            description=f"Message sent to {send_count} recipients",
            color=discord.Color.green()
        )
        embed.add_field(name="Enhanced Message", value=enhanced_message, inline=False)
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Broadcast failed: {str(e)[:100]}",
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
        embed.set_footer(text="AI-Enhanced Message")
        await user.send(embed=embed)
        
        confirm_embed = discord.Embed(
            title="✅ DM Sent",
            description=f"Message sent to {user.mention}",
            color=discord.Color.green()
        )
        confirm_embed.add_field(name="Enhanced Message", value=enhanced_message, inline=False)
        await interaction.followup.send(embed=confirm_embed, ephemeral=True)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to send DM: {str(e)[:100]}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

# ============================================================================
# ANNOUNCEMENT COMMANDS - FIXED
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
            description=f"Setup failed: {str(e)[:100]}",
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
        confirm_embed.add_field(name="Enhanced Message", value=enhanced_message, inline=False)
        await interaction.followup.send(embed=confirm_embed, ephemeral=True)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Announcement failed: {str(e)[:100]}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

# ============================================================================
# START BOT
# ============================================================================
bot.run(DISCORD_BOT_TOKEN)
