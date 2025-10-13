import discord
import os
from dotenv import load_dotenv

import methods.dwbapi as dwb
import embedBuilder as emb
from handlers.commandManager import commandManager
from methods.shrineoforder import order

intents = discord.Intents.default()
intents.message_content = True

#constants
load_dotenv()
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
client = discord.Client(intents=intents)
commands = commandManager(client)

@client.event
async def on_ready():
    print(f'Im fucking poa at {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    await message.channel.send(embed = commands.processCommand(message), reference = message)
    
    if message.type == discord.MessageType.reply:
        referenced = message.reference
        if referenced and referenced.resolved:
            replied_msg = referenced.resolved
            if 'https://deepwoken.co/builder?id=' in replied_msg.content:
                try:
                    link = replied_msg.content.split('https://deepwoken.co/builder?id=')[1].split()[0]
                    build_id = link.split('&')[0]
                    build = dwb.dwbBuild(build_id)
                    if message.content.strip().lower() == 'analytics':
                        summary = (
                            f"**Build Summary**: {build.summary}\n"
                            f"**EHP**: {build.ehp()}\n"
                        )
                        await message.channel.send(summary)
                    elif message.content.strip().lower() == 'display':
                        embeds = emb.get_deepwoken_build_embed(build_id)
                        for embed in embeds:
                            await message.channel.send(embed=embed, reference = message)
                except Exception as e:
                    await message.channel.send(f'Error fetching build: {str(e)}')


client.run(BOT_TOKEN)
