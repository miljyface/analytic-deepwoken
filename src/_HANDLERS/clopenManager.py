import discord
import asyncio
import json
import os
from enum import Enum
from datetime import datetime
from typing import Optional, Dict
from dataclasses import dataclass, asdict
from collections import defaultdict


class ChannelState(Enum):
    AVAILABLE = "available"
    USED = "used"
    CLOSED = "closed"


@dataclass
class ChannelData:
    channel_id: int
    state: str  # ChannelState value
    owner_id: Optional[int] = None
    claimed_at: Optional[str] = None  # ISO timestamp
    last_activity: Optional[str] = None
    prompt_message_id: Optional[int] = None
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass  
class GuildConfig:
    guild_id: int
    available_category_id: int
    used_category_id: int
    
    # Timeouts in seconds
    activity_timeout: int = 1800  # 30 minutes
    close_timeout: int = 15      # 15 seconds after close
    
    # Channel management
    min_available: int = 2
    max_available: int = 5
    
    # User limits
    max_per_user: int = 2
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class ClopenManager:
    
    def __init__(self, client: discord.Client, config_path: str = "data/clopen_config.json"):
        self.client = client
        self.config_path = config_path
        
        # In-memory state
        self.guild_configs: Dict[int, GuildConfig] = {}
        self.channels: Dict[int, ChannelData] = {}  # channel_id -> ChannelData
        self.locks: Dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)
        
        # Background task
        self.scheduler_task: Optional[asyncio.Task] = None
        
    async def load_config(self):
        if not os.path.exists(self.config_path):
            # Create directory if needed
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Create default config
            default = {
                "guilds": {},
                "channels": {}
            }
            with open(self.config_path, 'w') as f:
                json.dump(default, f, indent=2)
            return
        
        with open(self.config_path, 'r') as f:
            data = json.load(f)
        
        # Load guild configs
        for guild_id_str, config_data in data.get("guilds", {}).items():
            guild_id = int(guild_id_str)
            self.guild_configs[guild_id] = GuildConfig.from_dict(config_data)
        
        # Load channel states
        for channel_id_str, channel_data in data.get("channels", {}).items():
            channel_id = int(channel_id_str)
            self.channels[channel_id] = ChannelData.from_dict(channel_data)
    
    async def save_config(self):
        data = {
            "guilds": {
                str(guild_id): config.to_dict() 
                for guild_id, config in self.guild_configs.items()
            },
            "channels": {
                str(channel_id): channel.to_dict()
                for channel_id, channel in self.channels.items()
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_config(self, guild_id: int) -> Optional[GuildConfig]:
        return self.guild_configs.get(guild_id)
    
    async def register_guild(self, guild_id: int, available_cat: int, used_cat: int, **kwargs):

        config = GuildConfig(
            guild_id=guild_id,
            available_category_id=available_cat,
            used_category_id=used_cat,
            **kwargs
        )
        self.guild_configs[guild_id] = config
        await self.save_config()
    
    async def register_channel(self, channel_id: int, guild_id: int):
        if channel_id not in self.channels:
            self.channels[channel_id] = ChannelData(
                channel_id=channel_id,
                state=ChannelState.AVAILABLE.value
            )
            await self.save_config()
    
    # ===== STATE TRANSITIONS =====
    
    async def claim_channel(self, channel: discord.TextChannel, user: discord.User, message_id: int):
        async with self.locks[channel.id]:
            if channel.id not in self.channels:
                return False
            
            chan_data = self.channels[channel.id]
            if chan_data.state != ChannelState.AVAILABLE.value:
                return False
            
            config = self.get_config(channel.guild.id)
            if not config:
                return False
            
            # Check user limit
            user_channels = sum(
                1 for c in self.channels.values()
                if c.owner_id == user.id and c.state == ChannelState.USED.value
            )
            if user_channels >= config.max_per_user:
                await channel.send(
                    embed=discord.Embed(
                        description=f"You already have {config.max_per_user} active help channels. Please close one first.",
                        color=0xED4245
                    )
                )
                return False
            
            # Update state
            now = datetime.utcnow().isoformat()
            chan_data.state = ChannelState.USED.value
            chan_data.owner_id = user.id
            chan_data.claimed_at = now
            chan_data.last_activity = now
            
            await self.save_config()
            
            # Move to used category and rename
            try:
                used_cat = self.client.get_channel(config.used_category_id)
                await channel.edit(
                    category=used_cat,
                    name=f"{channel.name.split('-')[0]}-{user.display_name[:20]}"
                )
                
                # Pin the original message
                try:
                    msg = await channel.fetch_message(message_id)
                    await msg.pin()
                except:
                    pass
                
            except discord.Forbidden:
                print(f"Missing permissions to move channel {channel.id}")
            except Exception as e:
                print(f"Error moving channel {channel.id}: {e}")
            
            return True
    
    async def update_activity(self, channel_id: int, user_id: int):
        if channel_id not in self.channels:
            return
        
        chan_data = self.channels[channel_id]
        if chan_data.state == ChannelState.USED.value:
            chan_data.last_activity = datetime.utcnow().isoformat()
            await self.save_config()
    
    async def close_channel(self, channel: discord.TextChannel, reason: str):
        async with self.locks[channel.id]:
            if channel.id not in self.channels:
                return False
            
            chan_data = self.channels[channel.id]
            if chan_data.state != ChannelState.USED.value:
                return False
            
            config = self.get_config(channel.guild.id)
            if not config:
                return False
            
            chan_data.state = ChannelState.CLOSED.value
            chan_data.owner_id = None
            chan_data.claimed_at = None
            chan_data.last_activity = None
            
            await self.save_config()
        
        # Send close message (outside lock)
        try:
            await channel.send(
                embed=discord.Embed(
                    title="Channel Closed",
                    description=f"{reason}\nThis channel will be available for others soon.",
                    color=0x000000
                )
            )
        except:
            pass
        
        # Unpin all messages (outside lock)
        try:
            pins = await channel.pins()
            for msg in pins:
                try:
                    await msg.unpin()
                except:
                    pass
        except:
            pass
        
        asyncio.create_task(self._delayed_make_available(channel.id, config.close_timeout))
        
        return True
    
    async def _delayed_make_available(self, channel_id: int, delay: int):
        """Helper to delay making channel available"""
        await asyncio.sleep(delay)
        
        channel = self.client.get_channel(channel_id)
        if isinstance(channel, discord.TextChannel):
            await self.make_available(channel)
    
    async def make_available(self, channel: discord.TextChannel):
        """Make a closed channel available again"""
        async with self.locks[channel.id]:
            if channel.id not in self.channels:
                return
            
            chan_data = self.channels[channel.id]
            config = self.get_config(channel.guild.id)
            if not config:
                return
            
            # Update state
            chan_data.state = ChannelState.AVAILABLE.value
            chan_data.owner_id = None
            chan_data.prompt_message_id = None
            
            await self.save_config()
        
        # Move to available category (outside lock to prevent deadlock)
        try:
            avail_cat = self.client.get_channel(config.available_category_id)
            base_name = channel.name.split('-')[0]
            await channel.edit(
                category=avail_cat,
                name=base_name
            )
            
            # Send available message
            embed = discord.Embed(
                title="Available Help Channel!",
                description=(
                    "Send your question here to claim this channel.\n"
                    "**Remember:**\n"
                    "• Ask your question clearly and concisely\n"
                    "• Use `.close` when you're done\n"
                ),
                color=0x7CB342
            )
            msg = await channel.send(embed=embed)
            
            # Update prompt message ID
            async with self.locks[channel.id]:
                if channel.id in self.channels:
                    self.channels[channel.id].prompt_message_id = msg.id
                    await self.save_config()
                
        except discord.Forbidden:
            print(f"Missing permissions to move channel {channel.id} to available")
        except Exception as e:
            print(f"Error making channel {channel.id} available: {e}")
    
    # ===== BACKGROUND TASKS =====
    
    async def check_timeouts(self):
        """Check for channels that need timeout actions"""
        now = datetime.utcnow()
        
        for channel_id, chan_data in list(self.channels.items()):
            if chan_data.state != ChannelState.USED.value:
                continue
            
            if not chan_data.last_activity:
                continue
            
            channel = self.client.get_channel(channel_id)
            if not channel or not isinstance(channel, discord.TextChannel):
                continue
                
            config = self.get_config(channel.guild.id)
            if not config:
                continue
            
            last_activity = datetime.fromisoformat(chan_data.last_activity)
            elapsed = (now - last_activity).total_seconds()
            
            if elapsed > config.activity_timeout:
                await self.prompt_close(channel)
    
    async def prompt_close(self, channel: discord.TextChannel):
        chan_data = self.channels.get(channel.id)
        if not chan_data or not chan_data.owner_id:
            return
        
        embed = discord.Embed(
            description=f"<@{chan_data.owner_id}> Is your question resolved?\nReact with ✅ to close or ❌ to keep open.",
            color=0xFFCC00
        )
        msg = await channel.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        
        chan_data.prompt_message_id = msg.id
        await self.save_config()
    
    async def start_scheduler(self):
        await self.client.wait_until_ready()
        
        while not self.client.is_closed():
            try:
                await self.check_timeouts()
            except Exception as e:
                print(f"Error in clopen scheduler: {e}")
            
            await asyncio.sleep(60)  # Check every minute
    
    # ===== EVENT HANDLERS =====
    
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        if not message.guild:
            return
        
        channel_id = message.channel.id
        if channel_id not in self.channels:
            return
        
        chan_data = self.channels[channel_id]
        
        # Claim available channel
        if chan_data.state == ChannelState.AVAILABLE.value:
            # Don't claim if it's a command
            if message.content.startswith('.'):
                return
            
            await self.claim_channel(message.channel, message.author, message.id)
        
        # Update activity for used channel
        elif chan_data.state == ChannelState.USED.value:
            await self.update_activity(channel_id, message.author.id)
    
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if user.bot:
            return
        
        channel_id = reaction.message.channel.id
        if channel_id not in self.channels:
            return
        
        chan_data = self.channels[channel_id]
        if chan_data.prompt_message_id != reaction.message.id:
            return
        
        if user.id != chan_data.owner_id:
            return
        
        # Close on ✅
        if str(reaction.emoji) == "✅":
            await self.close_channel(reaction.message.channel, f"Closed by <@{user.id}>")
        
        # Keep open on ❌
        elif str(reaction.emoji) == "❌":
            chan_data.last_activity = datetime.utcnow().isoformat()
            await self.save_config()
            try:
                await reaction.message.delete()
            except:
                pass
