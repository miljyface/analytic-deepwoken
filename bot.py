import discord
import os
import json
import numpy as np
from dotenv import load_dotenv

import methods.initmethods as init
import methods.dwbapi as dwb
import methods.embeds as emb
from methods.lookup import find
from methods.lookup import fetch_mantra, fetch_outfit, fetch_equipment, fetch_talent
from methods.shrineoforder import order

with open('data/talents.json') as f:
    talentBase = json.load(f)

with open('data/mantras.json') as f:
    mantraBase = json.load(f)

with open('data/equipments.json') as f:
    equipmentBase = json.load(f)

with open('data/outfits.json') as f:
    outfitBase = json.load(f)

intents = discord.Intents.default()
intents.message_content = True

#constants
PREFIX = '@'
load_dotenv()
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
client = discord.Client(intents=intents)
talent_names = [tb.get('name', '') for tb in talentBase]
mantra_names = [mb.get('name', '') for mb in mantraBase]    
equipment_names = [eb['data']['name'] for eb in equipmentBase]
outfit_names = [ob['data']['name'] for ob in outfitBase]

@client.event
async def on_ready():
    print(f'Im fucking poa at {client.user}')

#command manager
@client.event
async def on_message(message):
    if message.author == client.user:
        pass

    content_lower = message.content.lower()
    
    prefixes = {
        'talent': talent_names,
        'mantra': mantra_names,
        'outfit': outfit_names,
        'equipment': equipment_names
    }
    
    for type_name, name_list in prefixes.items():
        query_prefix = f'{PREFIX}{type_name}'
        if content_lower.startswith(query_prefix):
            item_name = message.content[len(query_prefix):].strip()
            item_substring = item_name.lower()
            
            
            match = next((name for name in name_list if item_substring in name.lower()), None)
            
            if type_name == 'talent':
                fetch_func = fetch_talent
                build_embed = emb.build_talent_embed
            elif type_name == 'mantra':
                fetch_func = fetch_mantra
                build_embed = emb.build_mantra_embed
            elif type_name == 'outfit':
                fetch_func = fetch_outfit
                build_embed = emb.build_outfit_embed
            elif type_name == 'equipment':
                fetch_func = fetch_equipment
                build_embed = emb.build_equipment_embed
            
            if match:
                embed = build_embed(fetch_func(match))
            else:
                most_similar_name = find(item_name, type_name)
                embed = build_embed(fetch_func(most_similar_name))
                await message.channel.send(f'You probably meant **{most_similar_name}**')
            
            await message.channel.send(embed=embed, reference=message)
            break

    if message.type == discord.MessageType.reply:
        referenced = message.reference
        if referenced and referenced.resolved:
            replied_msg = referenced.resolved
            if 'https://deepwoken.co/builder?id=' in replied_msg.content:
                try:
                    link = replied_msg.content.split('https://deepwoken.co/builder?id=')[1].split()[0]
                    build_id = link.split('&')[0]  # In case of extra parameters
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
                            print(embed.to_dict())  # See exactly what would be sent
                            await message.channel.send(embed=embed, reference = message)
                except Exception as e:
                    await message.channel.send(f'Error fetching build: {str(e)}')


client.run(BOT_TOKEN)
