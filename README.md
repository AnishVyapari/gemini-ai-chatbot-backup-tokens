# 🤖 Mistral AI Discord Chatbot with Image Generation

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.3+-blueviolet?logo=discord)](https://discordpy.readthedocs.io/)
[![Mistral AI](https://img.shields.io/badge/Mistral%20AI-Powered-orange)](https://mistral.ai)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**A feature-rich Discord bot powered by Mistral AI with advanced conversational capabilities, image generation, and intelligent moderation systems.**

## Features • [Installation](#installation) • [Configuration](#configuration) • [Usage](#usage) • [Commands](#commands)

---

## ✨ Overview

This is a sophisticated Discord chatbot that integrates Mistral AI's powerful language models directly into Discord. It features:

- **Real-time AI conversations** with context awareness
- **Image generation** using Mistral's Pixtral model
- **Smart confession system** with IP-based rate limiting
- **Advanced moderation tools** with admin capabilities
- **Fast, optimized responses** with configurable models

## 🎯 Key Features

- **Mistral AI Integration** - mistral-small-2506 model for conversational AI
- **Image Generation** - `/generateimage` command powered by Pixtral-12b-2409
- **System Prompts** - Customizable AI personality and behavior
- **IP-based Confession System** - 2 confessions/day, 4 with passkey
- **Advanced Moderation** - Warn, kick, ban, unban with admin takeover
- **Message Rate Limiting** - Configurable per-user limits with daily reset
- **VIP Tier Support** - Premium features for selected users
- **Real-time Streaming** - Dynamic conversations with typing indicators
- **Auto-retry System** - Graceful error handling and API fallbacks

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/AnishVyapari/gemini-ai-chatbot-backup-tokens.git
cd gemini-ai-chatbot-backup-tokens

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file with your credentials:

```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
MISTRAL_API_KEY=your_mistral_api_key_here
```

### Running the Bot

```bash
python main.py
```

Deployment on Railway:
```bash
git push  # Automatically triggers Railway deployment
```

## 📝 Commands

### Chat Commands
- `@Bot <message>` - Have a conversation with the AI
- `/confess <message> [crime: yes/no] [passkey]` - Submit a confession (2/day)
- `/generateimage <prompt>` - Generate an image (5-500 characters)
- `/reset` - Clear your chat history

### Moderation Commands (Admin Only)
- `/warn @user [reason]` - Warn a user (3 warnings = auto-kick)
- `/kick @user [reason]` - Kick a user from the server
- `/ban @user [reason]` - Ban a user from the server
- `/unban <user_id> [reason]` - Unban a user

### Server Commands (Admin Only)
- `/setupannounce #channel` - Set announcement channel
- `/announce <message>` - Post an announcement

### Info Commands
- `/help` - Show all available commands
- `/info` - Display bot information

## 🛠️ Configuration Options

### System Prompt
Edit the `SYSTEM_PROMPT` in `main.py` to customize the AI's behavior:

```python
SYSTEM_PROMPT = "You are a helpful Discord AI assistant. Be friendly, concise, and helpful..."
```

### Moderation Settings
- `BOT_PREFIX` - Command prefix (default: `!`)
- `ADMINS` - List of admin user IDs
- `VIP_USERS` - List of VIP user IDs
- `CONFESSION_PASSKEY` - Passkey to unlock extra confessions

## 📊 Project Structure

```
.
├── main.py                 # Main bot file with all commands
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── Procfile               # Heroku/Railway deployment config
└── .env                   # Environment variables (create this)
```

## 🔑 Environment Variables

- `DISCORD_BOT_TOKEN` - Your Discord bot token
- `MISTRAL_API_KEY` - Your Mistral AI API key

## 📦 Dependencies

- `discord.py` (2.3.2) - Discord bot framework
- `mistral-ai` (1.9.11+) - Mistral AI API client
- `httpx` (0.28.1+) - Async HTTP client
- `python-dotenv` (1.0.0) - Environment variable management

## 🌐 Deployment

### Railway.app (Recommended)

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Automatic deployment on push to main branch

### Heroku

```bash
heroku create your-app-name
heroku config:set DISCORD_BOT_TOKEN=xxx MISTRAL_API_KEY=xxx
git push heroku main
```

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 👨‍💻 Author

**Anish Vyapari**
- Portfolio: https://anishvyapari.github.io
- GitHub: https://github.com/anishvyapari
- Discord: @shaboings

## 🙏 Acknowledgments

- Mistral AI for powerful language models
- Discord.py for the excellent bot framework
- The open-source community

---

**Built with ❤️ by Anish Vyapari**
