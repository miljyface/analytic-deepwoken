import discord
import os
from dotenv import load_dotenv

import plugins.dwbapi as dwb
from embedBuilder import statevoEmbed as emb
from handlers.commandManager import commandManager
from plugins.ehpbreakdown import plot_breakdown

intents = discord.Intents.default()
intents.message_content = True

#constants
load_dotenv()
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
client = discord.Client(intents=intents)
commands = commandManager(client)
commands.loadCommands()

@client.event
async def on_ready():
    print(f'Im fucking poa at {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith(commands.PREFIX):
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
                        buf = emb.statevograph(build)
                        file = discord.File(buf, filename="evo_plot.png")
                        embed = discord.Embed(
                            title = "Stat Evolution",
                            color=0xffffff
                        )
                        embed.set_image(url="attachment://evo_plot.png")
                        await message.channel.send(embed=embed, file=file, reference = message)

                        buf = plot_breakdown(build, talentBase=dwb.talentBase, params = {'dps':100, 'pen':50, 'kithp':112, 'kitresis':33})
                        file = discord.File(buf, filename="ehp_plot.png")
                        embed = discord.Embed(
                            title = "Phys Kit",
                            color=0xffffff
                        )
                        embed.set_image(url="attachment://ehp_plot.png")
                        await message.channel.send(embed=embed, file=file, reference = message)

                        buf = plot_breakdown(build, talentBase=dwb.talentBase, params = {'dps':100, 'pen':50, 'kithp':149, 'kitresis':7})
                        file = discord.File(buf, filename="ehp_plot.png")
                        embed = discord.Embed(
                            title = "HP Kit",
                            color=0xffffff
                        )
                        embed.set_image(url="attachment://ehp_plot.png")
                        await message.channel.send(embed=embed, file=file, reference = message)                   
                except Exception as e:
                    await message.channel.send(f'Error fetching build: {str(e)}')


client.run(BOT_TOKEN)
