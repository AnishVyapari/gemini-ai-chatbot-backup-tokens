# 🔥 COMPLETE FIXES - RUN LOCALLY IN VS CODE

## STEP 1: Clone and Setup
```bash
git clone https://github.com/AnishVyapari/gemini-ai-chatbot-backup-tokens.git
cd gemini-ai-chatbot-backup-tokens
git pull origin main  # Get latest with HuggingFace API key config
```

## STEP 2: Open main.py in VS Code and make these 4 changes:

### CHANGE #1: Replace generate_image_mistral function (Lines 607-668)

**FIND:** Line 607 starts with `async def generate_image_mistral`
**DELETE:** Everything from line 607 to the closing `except` block before the next function
**REPLACE WITH:**

```python
async def generate_image_mistral(prompt: str, retry_count: int = 0, max_retries: int = 3) -> Optional[tuple]:
    """Generate image using HuggingFace Runwayml Stable Diffusion v1.5 (30+ gens/day)"""
    try:
        if retry_count == 0:
            print(f"🎨 Starting image generation: {prompt[:50]}...")
        
        HF_API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        
        if not HUGGINGFACE_API_KEY:
            print("⚠️ HUGGINGFACE_API_KEY not set in environment")
            return None
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                HF_API_URL,
                headers={"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"},
                json={"inputs": prompt}
            )
            
            if response.status_code == 429:
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    print(f"⏳ Rate limited. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    return await generate_image_mistral(prompt, retry_count + 1, max_retries)
                else:
                    print("❌ Max retries exceeded")
                    return None
            
            if response.status_code == 200:
                image_bytes = response.content
                print(f"✅ Generated image: {len(image_bytes)} bytes")
                return (image_bytes, "generated_image.png")
            else:
                print(f"❌ API error: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"❌ Image Generation Error: {e}")
        return None
```

### CHANGE #2: Add /setup command (Before /setup-verify, around line 1460)

**INSERT THIS NEW COMMAND:**

```python
@bot.tree.command(name="setup", description="⚡ AUTO SETUP - Creates all channels, roles, and permissions")
async def slash_setup(interaction: discord.Interaction):
    """Automatic complete server setup"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return
    
    if not interaction.guild:
        await interaction.response.send_message("❌ Server only", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        guild_id = interaction.guild.id
        settings = get_guild_settings(guild_id)
        
        # 1. Create Verified Role
        verified_role = await interaction.guild.create_role(
            name="Verified",
            color=discord.Color.from_rgb(50, 184, 198),
            reason="Bot auto-generated"
        )
        if guild_id not in bot_created_roles:
            bot_created_roles[guild_id] = []
        bot_created_roles[guild_id].append(verified_role.id)
        
        # 2. Create Verify Channel
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        verify_channel = await interaction.guild.create_text_channel(
            "verify",
            overwrites=overwrites,
            reason="Bot auto-generated"
        )
        if guild_id not in bot_created_channels:
            bot_created_channels[guild_id] = []
        bot_created_channels[guild_id].append(verify_channel.id)
        
        # 3. Create Announcements Channel
        announce_channel = await interaction.guild.create_text_channel(
            "announcements",
            reason="Bot auto-generated"
        )
        bot_created_channels[guild_id].append(announce_channel.id)
        
        # 4. Create Tickets Category
        tickets_category = await interaction.guild.create_category(
            "tickets",
            reason="Bot auto-generated"
        )
        
        # 5. Save settings
        settings["verify_channel"] = verify_channel.id
        settings["verify_role"] = verified_role.id
        settings["announce_channel"] = announce_channel.id
        settings["ticket_category"] = tickets_category.id
        
        # 6. Send verification embed
        embed = discord.Embed(
            title="🔐 Server Verification",
            description="Run `/verify` to gain access",
            color=discord.Color.from_rgb(50, 184, 198)
        )
        embed.add_field(name="Role You'll Get", value=verified_role.mention)
        await verify_channel.send(embed=embed)
        
        # 7. Confirm to admin
        confirm = discord.Embed(
            title="✅ Server Setup Complete!",
            color=discord.Color.green()
        )
        confirm.add_field(name="✅ Verified Role", value=verified_role.mention, inline=False)
        confirm.add_field(name="✅ Verify Channel", value=verify_channel.mention, inline=False)
        confirm.add_field(name="✅ Announcements", value=announce_channel.mention, inline=False)
        confirm.add_field(name="✅ Tickets Category", value=tickets_category.mention, inline=False)
        
        await interaction.followup.send(embed=confirm, ephemeral=True)
        
    except Exception as e:
        print(f"Setup error: {e}")
        await interaction.followup.send(f"❌ Error: {str(e)[:100]}", ephemeral=True)
```

### CHANGE #3: Add /setup-tickets command (After tickets section, around line 1950)

**INSERT THIS NEW COMMAND:**

```python
@bot.tree.command(name="setup-tickets", description="⚡ AUTO SETUP TICKETS - Auto creates ticket category and channels")
async def slash_setup_tickets(interaction: discord.Interaction):
    """Auto setup tickets system"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return
    
    if not interaction.guild:
        await interaction.response.send_message("❌ Server only", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        guild_id = interaction.guild.id
        settings = get_guild_settings(guild_id)
        
        # Create Tickets Category if doesn't exist
        tickets_category = None
        for cat in interaction.guild.categories:
            if cat.name.lower() == "tickets":
                tickets_category = cat
                break
        
        if not tickets_category:
            tickets_category = await interaction.guild.create_category(
                "tickets",
                reason="Bot auto-generated"
            )
        
        # Create initial ticket info channel
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(send_messages=False),
            interaction.guild.me: discord.PermissionOverwrite(send_messages=True)
        }
        
        info_channel = await interaction.guild.create_text_channel(
            "ticket-info",
            category=tickets_category,
            overwrites=overwrites,
            reason="Bot auto-generated"
        )
        
        # Save settings
        settings["ticket_category"] = tickets_category.id
        
        # Send info message
        embed = discord.Embed(
            title="🎫 Ticket Support System",
            description="Use `/ticket` to create a support ticket\n\nChoose a topic: support, report, suggestion, or appeal",
            color=discord.Color.from_rgb(50, 184, 198)
        )
        await info_channel.send(embed=embed)
        
        # Confirm
        confirm = discord.Embed(
            title="✅ Tickets Setup Complete!",
            color=discord.Color.green()
        )
        confirm.add_field(name="📁 Category", value=tickets_category.mention, inline=False)
        confirm.add_field(name="📌 Info Channel", value=info_channel.mention, inline=False)
        
        await interaction.followup.send(embed=confirm, ephemeral=True)
        
    except Exception as e:
        print(f"Tickets setup error: {e}")
        await interaction.followup.send(f"❌ Error: {str(e)[:100]}", ephemeral=True)
```

### CHANGE #4: Update /setup-verify to auto-create everything

**FIND:** Existing `/setup-verify` command around line 1460
**REPLACE THE ENTIRE FUNCTION with:**

```python
@bot.tree.command(name="setup-verify", description="🔐 AUTO SETUP VERIFICATION - Auto creates verify channel and role")
async def slash_setup_verify(interaction: discord.Interaction):
    """Auto setup verification system"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return
    
    if not interaction.guild:
        await interaction.response.send_message("❌ Server only", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        guild_id = interaction.guild.id
        settings = get_guild_settings(guild_id)
        
        # Create Verified Role
        verified_role = await interaction.guild.create_role(
            name="Verified",
            color=discord.Color.from_rgb(50, 184, 198),
            reason="Bot auto-generated"
        )
        if guild_id not in bot_created_roles:
            bot_created_roles[guild_id] = []
        bot_created_roles[guild_id].append(verified_role.id)
        
        # Create Verify Channel
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        verify_channel = await interaction.guild.create_text_channel(
            "verify",
            overwrites=overwrites,
            reason="Bot auto-generated"
        )
        if guild_id not in bot_created_channels:
            bot_created_channels[guild_id] = []
        bot_created_channels[guild_id].append(verify_channel.id)
        
        # Save settings
        settings["verify_channel"] = verify_channel.id
        settings["verify_role"] = verified_role.id
        
        # Send verification embed
        embed = discord.Embed(
            title="🔐 Welcome!",
            description="Run `/verify` to access the server",
            color=discord.Color.from_rgb(50, 184, 198)
        )
        embed.add_field(name="Role", value=verified_role.mention)
        await verify_channel.send(embed=embed)
        
        # Confirm
        confirm = discord.Embed(
            title="✅ Verification Setup Complete!",
            color=discord.Color.green()
        )
        confirm.add_field(name="✅ Role", value=verified_role.mention, inline=False)
        confirm.add_field(name="✅ Channel", value=verify_channel.mention, inline=False)
        
        await interaction.followup.send(embed=confirm, ephemeral=True)
        
    except Exception as e:
        print(f"Verify setup error: {e}")
        await interaction.followup.send(f"❌ Error: {str(e)[:100]}", ephemeral=True)
```

## STEP 3: Save, Commit & Push

```bash
git add main.py
git commit -m "✨ Complete fixes: HuggingFace image gen + auto-setup commands"
git push origin main
```

## STEP 4: Wait for Railway Deploy
- Railway will auto-deploy in 2-3 minutes
- Watch the deployment logs

## STEP 5: TEST IN DISCORD

```
/setup              # Creates everything at once
/setup-verify       # Just verification  
/setup-tickets      # Just tickets
/imagine sunset     # Test image generation
```

✅ ALL DONE!
