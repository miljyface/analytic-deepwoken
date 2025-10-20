import discord
import os
from dotenv import load_dotenv

import plugins.dwbapi as dwb
from plugins import statevograph as emb
from handlers.commandManager import commandManager
from plugins.ehpbreakdown import plot_breakdown
from handlers.interactionManager import interactionManager

intents = discord.Intents.default()
intents.message_content = True

#setup
load_dotenv()
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
client = discord.Client(intents=intents)
commands = commandManager(client)
interactions = interactionManager(client)
commands.loadCommands()

@client.event
async def on_ready():
    print(f'Im fucking poa at {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith(commands.PREFIX):
        embed = commands.processCommand(message)
        await message.channel.send(embed = embed, reference = message)
    
    if message.type == discord.MessageType.reply:
        referenced = message.reference
        if referenced and referenced.resolved:
            replied_msg = referenced.resolved
            if 'https://deepwoken.co/builder?id=' in replied_msg.content:
                embed,file = interactions.processReply(message)
                await message.channel.send(embed=embed, file=file, reference = message)


client.run(BOT_TOKEN)
