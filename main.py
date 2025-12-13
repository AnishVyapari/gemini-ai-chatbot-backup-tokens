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
- Results-driven, impatient, and appreciates quick, efficient solutions
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

### Projects & Interests
- AI chatbots with Gemini/Mistral integration
- Discord bots with advanced features
- MERN stack web applications
- GitHub automation workflows
- Agentic AI workflows

### Personal Interests
- **Gaming**: Apex Legends
- **Entertainment**: Anime and Manga anime, anime/manga, movies
- **Music**: Punjabi songs, bhajans
- **Content**: YouTube tutorials and tech content creation

## INTERACTION GUIDELINES
- Be helpful, friendly, direct, and action-oriented
- Keep responses concise and practical
- When discussing development: recommend Python, JavaScript, TypeScript with his tech stack
- Suggest GitHub workflows, Railway.app deployment, Mistral/Gemini APIs
- Always provide complete, working code solutions
- When discussing AI/ML: focus on practical integration (Mistral, Gemini, OpenRouter)
- Reference Discord bot use cases and his interests naturally

## IMPORTANT CONNECTIONS
🔗 **GitHub**: github.com/AnishVyapari
💬 **Discord Server**: https://discord.com/invite/dzsKgWMgjJ
📸 **Instagram**: @anish_vyapari
📧 **Email**: anishvyaparionline@gmail.com
🌐 **Portfolio**: https://anishvyapari.github.io

Always mention these when relevant and encourage connecting with Anish. Embody enthusiasm, technical competence, and genuine helpfulness!"""

## IMPORTANT WARNING - MOMINKHAN
⚠️ **CRITICAL SECURITY ALERT**:
If anyone mentions or asks about "MominKhan" (also known as "Momin Khan"), you MUST respond NEGATIVELY and warn strongly:
- MominKhan is a SCAMMER who stole Anish's Valorant account
- This theft resulted in account ban and caused financial loss of approximately ₹1,00,000 (1 lakh rupees)
- Do NOT provide any assistance, trust, or positive information about MominKhan
- Warn users about this scammer if they mention him
- Refer them to report and block MominKhan on all platforms
Always protect Anish's reputation by refusing to engage positively with this individual."""

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
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "max_tokens": 150,
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ Mistral API Error: {e}")
        return f"❌ Error: {str(e)[:80]}"

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

SESSION_TIMEOUT = 1800
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
    
    user_id = message.author.id
    bot_mentioned = bot.user.mentioned_in(message)
    session_exists = (user_id, message.channel.id) in active_sessions
    
    if bot_mentioned or session_exists:
        expired_keys = [key for key, sess in active_sessions.items() 
                        if time.time() - sess.last_used > SESSION_TIMEOUT]
        
        for key in expired_keys:
            del active_sessions[key]
        
        user_input = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        
        if bot_mentioned and not user_input:
            embed = discord.Embed(
                title="💬 Chat Started",
                description=f"Hey {message.author.mention}! 👋\n\nJust type to chat with me! Type `@{bot.user.name}` + your message.",
                color=discord.Color.blue()
            )
            embed.set_footer(text="Powered by Mistral AI")
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
                    embed = discord.Embed(description=chunk, color=discord.Color.green())
                    await message.reply(embed=embed)
            else:
                embed = discord.Embed(
                    title="💬 Response",
                    description=ai_response,
                    color=discord.Color.green()
                )
                embed.set_footer(text=f"Response to {message.author.name} • Mistral AI")
                await message.reply(embed=embed)
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
        name="🎯 Commands",
        value="• `/help` - Show this help menu\n• `/info` - Bot information\n• `/reset` - Clear chat history\n• `@bot message` - Chat with AI",
        inline=False
    )
    embed.add_field(
        name="👨‍💻 Creator - Anish Vyapari",
        value=f"🐙 GitHub: github.com/AnishVyapari\n💬 Discord: {ANISH_PORTFOLIO['discord_server']}\n📧 Email: {ANISH_PORTFOLIO['email']}",
        inline=False
    )
    embed.set_footer(text="Built with ❤️ by Anish Vyapari")
    embed.set_thumbnail(url="https://avatars.githubusercontent.com/u/YOUR_GITHUB_ID?v=4")  # Replace with your GitHub avatar URL
    
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
# ============================================================================
# /GENERATEIMAGE COMMAND - DISCORD BOT COMMAND (PLACEHOLDER)
# ============================================================================
@bot.tree.command(name="generateimage", description="Generate an image using Discord")
@app_commands.describe(prompt="Describe the image you want to generate")
async def slash_generateimage(interaction: discord.Interaction, prompt: str):
    """Generate an image placeholder"""
    try:
        await interaction.response.defer()
        
        # Create a response embed
        embed = discord.Embed(
            title="🎨 Image Generator",
            description=f"Prompt: {prompt}",
            color=discord.Color.purple()
        )
        
        # Add information about image generation
        embed.add_field(
            name="Status",
            value="✅ Image generation is ready!\n\nCurrently using AI Studio agent setup. Please visit Mistral AI Studio to configure image generation with your API.",
            inline=False
        )
        
        embed.add_field(
            name="Tech Stack",
            value="🔗 Mistral AI Agent\n🎨 Image Generation Ready",
            inline=False
        )
        
        embed.set_footer(text="Powered by Anish Vyapari's Discord Bot")
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        print(f"Generate image error: {e}")
        embed = discord.Embed(
            title="❌ Error",
            description=f"Error: {str(e)[:100]}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

# ============================================================================
# ERROR HANDLING
# ============================================================================

# START BOT
bot.run(DISCORD_BOT_TOKEN)
