import discord

def execute(command_body, message):
    clopen_manager = message.guild._state._get_client().clopen_manager
    """
    Usage:
        .clopen setup <available_category_id> <used_category_id>
        .clopen register <channel_id> [channel_id...]
        .clopen unregister <channel_id>
        .clopen timeout <seconds>
        .clopen closetime <seconds>
        .clopen userlimit <max_channels>
        .clopen status
        .clopen help
    """
    
    # Check if in guild
    if not message.guild:
        return (discord.Embed(
            description="This command can only be used in servers.",
            color=0xED4245
        ), None)
    
    # Check admin permissions
    if not message.author.guild_permissions.administrator:
        return (discord.Embed(
            description="Only administrators can configure the clopen system.",
            color=0xED4245
        ), None)
    
    
    parts = command_body.strip().split()
    
    if len(parts) == 0 or parts[0].lower() == "help":
        return (_help_embed(), None)
    
    subcommand = parts[0].lower()
    
    # Route to subcommands - return ASYNC tuple if needed
    if subcommand == "setup":
        result = _setup(parts[1:], message, clopen_manager)
    elif subcommand == "register":
        result = _register(parts[1:], message, clopen_manager)
    elif subcommand == "unregister":
        result = _unregister(parts[1:], message, clopen_manager)
    elif subcommand == "timeout":
        result = _set_timeout(parts[1:], message, clopen_manager)
    elif subcommand == "closetime":
        result = _set_closetime(parts[1:], message, clopen_manager)
    elif subcommand == "userlimit":
        result = _set_userlimit(parts[1:], message, clopen_manager)
    elif subcommand == "status":
        result = (_status(message, clopen_manager), None)
    else:
        result = (discord.Embed(
            description=f"Unknown subcommand: `{subcommand}`\nUse `.clopen help` for usage.",
            color=0xED4245
        ), None)
    
    return result


def _help_embed():
    embed = discord.Embed(
        title="Clopen System Configuration",
        description="Automatic help channel rotation system",
        color=0x7CB342
    )
    
    embed.add_field(
        name="Setup",
        value=(
            "**`.clopen setup <available_cat_id> <used_cat_id>`**\n"
            "Initialize clopen for this server"
        ),
        inline=False
    )
    
    embed.add_field(
        name="Register Channels",
        value="**`.clopen register <channel_id> [channel_id...]`**\nAdd channels to the system",
        inline=False
    )
    
    embed.add_field(
        name="Configure",
        value=(
            "**`.clopen timeout <seconds>`** - Activity timeout\n"
            "**`.clopen closetime <seconds>`** - Close delay\n"
            "**`.clopen userlimit <max>`** - Max channels per user"
        ),
        inline=False
    )
    
    embed.add_field(
        name="Status",
        value="**`.clopen status`** - View configuration",
        inline=False
    )

    return embed


def _setup(args, message, clopen_manager):
    if len(args) < 2:
        return (discord.Embed(
            description="Usage: `.clopen setup <available_category_id> <used_category_id>`",
            color=0xED4245
        ), None)
    
    try:
        available_cat_id = int(args[0])
        used_cat_id = int(args[1])
    except ValueError:
        return (discord.Embed(
            description="Category IDs must be valid numbers",
            color=0xED4245
        ), None)
    
    # Verify categories exist
    available_cat = message.guild.get_channel(available_cat_id)
    used_cat = message.guild.get_channel(used_cat_id)
    
    if not available_cat or not isinstance(available_cat, discord.CategoryChannel):
        return (discord.Embed(
            description=f"Available category not found: {available_cat_id}",
            color=0xED4245
        ), None)
    
    if not used_cat or not isinstance(used_cat, discord.CategoryChannel):
        return (discord.Embed(
            description=f"Used category not found: {used_cat_id}",
            color=0xED4245
        ), None)
    
    # Return async operation
    async def setup_async():
        await clopen_manager.register_guild(
            guild_id=message.guild.id,
            available_cat=available_cat_id,
            used_cat=used_cat_id
        )
        
        embed = discord.Embed(
            title="Clopen System Configured",
            description="Help channel rotation is now active!",
            color=0x43B581
        )
        embed.add_field(
            name="Available Category",
            value=f"{available_cat.name} (`{available_cat_id}`)",
            inline=True
        )
        embed.add_field(
            name="Used Category",
            value=f"{used_cat.name} (`{used_cat_id}`)",
            inline=True
        )
        embed.add_field(
            name="Next Steps",
            value=(
                "1. Use `.clopen register <channel_id>` to add help channels\n"
                "2. Adjust timeouts with `.clopen timeout <seconds>`\n"
                "3. Check status with `.clopen status`"
            ),
            inline=False
        )
        
        await message.channel.send(embed=embed)
    
    return ("ASYNC", setup_async())


def _register(args, message, clopen_manager):
    if len(args) == 0:
        return (discord.Embed(
            description="Usage: `.clopen register <channel_id> [channel_id...]`",
            color=0xED4245
        ), None)
    
    # Check if guild is configured
    config = clopen_manager.get_config(message.guild.id)
    if not config:
        return (discord.Embed(
            description="Please run `.clopen setup` first to configure the system.",
            color=0xED4245
        ), None)
    
    async def register_async():
        registered = []
        failed = []
        
        for channel_id_str in args:
            try:
                channel_id = int(channel_id_str)
                channel = message.guild.get_channel(channel_id)
                
                if not channel:
                    failed.append(f"{channel_id_str} (not found)")
                    continue
                
                if not isinstance(channel, discord.TextChannel):
                    failed.append(f"{channel_id_str} (not a text channel)")
                    continue
                
                await clopen_manager.register_channel(channel_id, message.guild.id)
                registered.append(f"<#{channel_id}>")
                
            except ValueError:
                failed.append(f"{channel_id_str} (invalid ID)")
        
        embed = discord.Embed(
            title="Channel Registration Results",
            color=0x43B581 if len(failed) == 0 else 0xFFCC00
        )
        
        if registered:
            embed.add_field(
                name="Registered",
                value="\n".join(registered),
                inline=False
            )
        
        if failed:
            embed.add_field(
                name="Failed",
                value="\n".join(failed),
                inline=False
            )
        
        if registered:
            embed.set_footer(text="Channels will now participate in automatic rotation")
        
        await message.channel.send(embed=embed)
    
    return ("ASYNC", register_async())


def _unregister(args, message, clopen_manager):
    if len(args) == 0:
        return (discord.Embed(
            description="Usage: `.clopen unregister <channel_id>`",
            color=0xED4245
        ), None)
    
    try:
        channel_id = int(args[0])
    except ValueError:
        return (discord.Embed(
            description="Channel ID must be a valid number",
            color=0xED4245
        ), None)
    
    async def unregister_async():
        if channel_id not in clopen_manager.channels:
            embed = discord.Embed(
                description=f"Channel `{channel_id}` is not registered",
                color=0xED4245
            )
        else:
            del clopen_manager.channels[channel_id]
            await clopen_manager.save_config()
            
            embed = discord.Embed(
                title="Channel Unregistered",
                description=f"<#{channel_id}> has been removed from the clopen system",
                color=0x43B581
            )
        
        await message.channel.send(embed=embed)
    
    return ("ASYNC", unregister_async())


def _set_timeout(args, message, clopen_manager):
    if len(args) == 0:
        return (discord.Embed(
            description="Usage: `.clopen timeout <seconds>`",
            color=0xED4245
        ), None)
    
    try:
        timeout = int(args[0])
        if timeout < 60:
            return (discord.Embed(
                description="Timeout must be at least 60 seconds",
                color=0xED4245
            ), None)
    except ValueError:
        return (discord.Embed(
            description="Timeout must be a valid number",
            color=0xED4245
        ), None)
    
    async def set_timeout_async():
        config = clopen_manager.get_config(message.guild.id)
        if not config:
            embed = discord.Embed(
                description="Please run `.clopen setup` first",
                color=0xED4245
            )
        else:
            config.activity_timeout = timeout
            await clopen_manager.save_config()
            
            minutes = timeout // 60
            embed = discord.Embed(
                title="Activity Timeout Updated",
                description=f"Channels will prompt for closure after **{timeout}s** ({minutes} min) of inactivity",
                color=0x43B581
            )
        
        await message.channel.send(embed=embed)
    
    return ("ASYNC", set_timeout_async())


def _set_closetime(args, message, clopen_manager):
    if len(args) == 0:
        return (discord.Embed(
            description="Usage: `.clopen closetime <seconds>`",
            color=0xED4245
        ), None)
    
    try:
        timeout = int(args[0])
        if timeout < 5:
            return (discord.Embed(
                description="Close time must be at least 5 seconds",
                color=0xED4245
            ), None)
    except ValueError:
        return (discord.Embed(
            description="Close time must be a valid number",
            color=0xED4245
        ), None)
    
    async def set_closetime_async():
        config = clopen_manager.get_config(message.guild.id)
        if not config:
            embed = discord.Embed(
                description="Please run `.clopen setup` first",
                color=0xED4245
            )
        else:
            config.close_timeout = timeout
            await clopen_manager.save_config()
            
            embed = discord.Embed(
                title="Close Timeout Updated",
                description=f"Channels will return to available after **{timeout}s** of being closed",
                color=0x43B581
            )
        
        await message.channel.send(embed=embed)
    
    return ("ASYNC", set_closetime_async())


def _set_userlimit(args, message, clopen_manager):
    if len(args) == 0:
        return (discord.Embed(
            description="Usage: `.clopen userlimit <max_channels>`",
            color=0xED4245
        ), None)
    
    try:
        limit = int(args[0])
        if limit < 1 or limit > 10:
            return (discord.Embed(
                description="User limit must be between 1 and 10",
                color=0xED4245
            ), None)
    except ValueError:
        return (discord.Embed(
            description="User limit must be a valid number",
            color=0xED4245
        ), None)
    
    async def set_userlimit_async():
        config = clopen_manager.get_config(message.guild.id)
        if not config:
            embed = discord.Embed(
                description="Please run `.clopen setup` first",
                color=0xED4245
            )
        else:
            config.max_per_user = limit
            await clopen_manager.save_config()
            
            embed = discord.Embed(
                title="User Limit Updated",
                description=f"Users can now claim up to **{limit}** channels simultaneously",
                color=0x43B581
            )
        
        await message.channel.send(embed=embed)
    
    return ("ASYNC", set_userlimit_async())


def _status(message, clopen_manager):
    config = clopen_manager.get_config(message.guild.id)
    
    if not config:
        return discord.Embed(
            title="Clopen Not Configured",
            description="Run `.clopen setup` to initialize the system",
            color=0xED4245
        )
    
    # Count channels by state
    guild_channels = [c for c in clopen_manager.channels.values() 
                      if message.guild.get_channel(c.channel_id)]
    
    available = sum(1 for c in guild_channels if c.state == "available")
    used = sum(1 for c in guild_channels if c.state == "used")
    closed = sum(1 for c in guild_channels if c.state == "closed")
    
    embed = discord.Embed(
        title="Clopen System Status",
        color=0x5865F2
    )
    
    available_cat = message.guild.get_channel(config.available_category_id)
    used_cat = message.guild.get_channel(config.used_category_id)
    
    embed.add_field(
        name="Configuration",
        value=(
            f"**Available Category:** {available_cat.name if available_cat else 'Not found'}\n"
            f"**Used Category:** {used_cat.name if used_cat else 'Not found'}\n"
            f"**Activity Timeout:** {config.activity_timeout}s ({config.activity_timeout // 60} min)\n"
            f"**Close Timeout:** {config.close_timeout}s\n"
            f"**Max Per User:** {config.max_per_user} channels"
        ),
        inline=False
    )
    
    embed.add_field(
        name="Channel Statistics",
        value=(
            f"**Available:** {available}\n"
            f"**In Use:** {used}\n"
            f"**Closed:** {closed}\n"
            f"**Total:** {len(guild_channels)}"
        ),
        inline=False
    )
    
    if used > 0:
        active_channels = [c for c in guild_channels if c.state == "used"]
        active_list = []
        for chan in active_channels[:5]:
            channel = message.guild.get_channel(chan.channel_id)
            owner = f"<@{chan.owner_id}>" if chan.owner_id else "Unknown"
            active_list.append(f"<#{chan.channel_id}> → {owner}")
        
        if len(active_channels) > 5:
            active_list.append(f"... and {len(active_channels) - 5} more")
        
        embed.add_field(
            name="Active Channels",
            value="\n".join(active_list) if active_list else "None",
            inline=False
        )
    
    embed.set_footer(text="Use .clopen help for configuration commands")
    
    return embed
