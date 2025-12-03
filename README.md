# 🤖 Gemini AI Discord Chatbot with Backup Token System

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.3.2-blueviolet?logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![Google Generative AI](https://img.shields.io/badge/Google-Generative%20AI-orange?logo=google&logoColor=white)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green)](#license)

**A feature-rich Discord bot powered by Google's Gemini AI with intelligent backup token management system**

[Features](#features) • [Installation](#installation) • [Configuration](#configuration) • [Usage](#usage) • [Commands](#commands)

</div>

---

## 📋 Overview

This is a sophisticated Discord chatbot that integrates Google's state-of-the-art Gemini AI model directly into Discord servers. It features an intelligent backup token management system that automatically rotates API keys, ensuring uninterrupted service even when primary tokens are exhausted.

### ✨ Key Highlights

- **Gemini 2.0 Flash Lite** integration for real-time AI responses
- **Intelligent token management** with 5 backup API key slots
- **Advanced moderation system** with admin takeover capabilities
- **Daily message limits** per user with automatic daily reset
- **VIP tier support** with unlimited access
- **Real-time streaming** for dynamic conversations

---

## 🚀 Features

### Core Functionality
- ✅ **AI-Powered Responses** - Generates intelligent, contextual responses using Gemini 2.0 Flash Lite
- ✅ **Message Management** - Works on DMs and server channels
- ✅ **Token Rotation** - Automatically rotates between 5 API keys
- ✅ **Automatic Fallover** - Seamlessly switches to backup tokens

### Moderation System
- ✅ **Basic Commands** - kick, ban, mute, warn functionality
- ✅ **Admin Takeover** - Secure system to grant highest admin permissions between users
- ✅ **HIDDEN Admin Mode** - Exclusive admin commands

### User Features
- ✅ **Daily Quota** - 20 messages per day per user
- ✅ **VIP Users** - Unlimited message access
- ✅ **Daily Reset** - Quotas reset at midnight

---

## 📦 Prerequisites

- **Python 3.11+**
- **Discord Bot Token** (from [Discord Developer Portal](https://discord.com/developers/applications))
- **Google Generative AI API Keys** (from [Google AI Studio](https://makersuite.google.com/app/apikey)) - Multiple keys for backup

---

## 🔧 Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/AnishVyapari/gemini-ai-chatbot-backup-tokens.git
cd gemini-ai-chatbot-backup-tokens
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables
Create a `.env` file in the project root:
```env
DISCORD_BOT_TOKEN=your_discord_bot_token_here
GEMINI_API_KEY_1=your_primary_api_key
GEMINI_API_KEY_2=your_backup_api_key_2
GEMINI_API_KEY_3=your_backup_api_key_3
GEMINI_API_KEY_4=your_backup_api_key_4
GEMINI_API_KEY_5=your_backup_api_key_5
```

### Step 4: Run the Bot
```bash
python main.py
```

---

## ⚙️ Configuration

### Token Management
The bot is configured with 5 API key slots. Edit `main.py` to add your keys:
```python
GEMINI_API_KEYS = [
    os.getenv("GEMINI_API_KEY_1", "your_key_1"),
    os.getenv("GEMINI_API_KEY_2", "your_key_2"),
    os.getenv("GEMINI_API_KEY_3", "your_key_3"),
    os.getenv("GEMINI_API_KEY_4", "your_key_4"),
    os.getenv("GEMINI_API_KEY_5", "your_key_5"),
]
```

### Customization
- **Daily Message Limit**: Modify the `DAILY_LIMIT` constant
- **AI Model**: Change from `gemini-2.0-flash-lite` to another Gemini model
- **Moderation**: Adjust command permissions in the moderation section

---

## 💬 Commands

### General Commands
| Command | Usage | Description |
|---------|-------|-------------|
| `@bot_name message` | `@bot hi` | Send a message to the AI |
| `/ping` | `/ping` | Check bot latency |

### Moderation Commands
| Command | Usage | Permission | Description |
|---------|-------|------------|-------------|
| `!kick` | `!kick @user reason` | Kick | Kick a user from server |
| `!ban` | `!ban @user reason` | Ban | Ban a user from server |
| `!mute` | `!mute @user` | Mute | Mute a user |
| `!warn` | `!warn @user reason` | Warn | Warn a user |
| `!takeover` | `!takeover @user_to_grant` | Hidden Admin | Grant admin to specified user |

---

## 🔐 Security Features

- **Environment Variables** - Sensitive data stored securely
- **Automatic Token Rotation** - Prevents API quota exhaustion
- **Admin Authorization** - Only admins can use moderation commands
- **VIP Verification** - Role-based access control

---

## 📊 API Support

- **Gemini 2.0 Flash Lite** - Ultra-fast inference
- **Real-time Updates** - Live streaming responses
- **Context Awareness** - Maintains conversation history

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs via Issues
- Submit PRs with improvements
- Suggest new features

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📞 Support

If you encounter issues:
1. Check the [Issues](https://github.com/AnishVyapari/gemini-ai-chatbot-backup-tokens/issues) page
2. Review the [Discussions](https://github.com/AnishVyapari/gemini-ai-chatbot-backup-tokens/discussions)
3. Ensure all environment variables are correctly set

---

## 🎯 Roadmap

- [ ] Database integration for persistent user data
- [ ] Advanced analytics dashboard
- [ ] Custom AI personality customization
- [ ] Multi-language support
- [ ] Web dashboard for bot management

---

## ⭐ Show Your Support

If this project helped you, please consider giving it a star! Your support motivates continued development.

**Made with ❤️ by [Anish Vyapari](https://github.com/AnishVyapari)**
