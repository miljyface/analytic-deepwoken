import discord
import os
import json
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

import methods.initmethods as init
import methods.dwbapi as dwb
import methods.embeds as emb
from methods.shrineoforder import order

model = SentenceTransformer("google/embeddinggemma-300m")
doc_embeddings = np.load('data/talent_embeddings.npy')

with open('data/talents.json') as f:
    talentBase = json.load(f)
talent_names = [tb.get('name', '') for tb in talentBase]

try:
    print('All deps loaded !')
except Exception as e:
    if e == "/Users/guanrong/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020warnings.warn(\"NotOpenSSLWarning\")":
        pass
    else:
        print(f'Error loading deps: {str(e)}')

load_dotenv()
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def fetch_talent(talent_name):
    for tb in talentBase:
        if tb.get('name', '').lower() == talent_name.lower():
            return tb
    return None

@client.event
async def on_ready():
    print(f'Im fucking poa at {client.user}')

#command manager
@client.event
async def on_message(message):
    if message.author == client.user:
        pass

    if message.content.startswith('@talent'):
        # Get the talent name from command and lowercase it
        talent_name = message.content[len('@talent'):].strip()
        talent_substring = message.content[len('@talent'):].strip().lower()
        # Find the first entry in talent_names that contains the substring, case-insensitive
        match = next((name for name in talent_names if talent_substring in name.lower()),None)  
        if match:
            embed = emb.build_talent_embed(fetch_talent(match))
            print(embed.to_dict())  # See exactly what would be sent            
        else:
            query_embedding = model.encode_query(talent_name)
            similarities = model.similarity(query_embedding, doc_embeddings)
            most_similar_index = torch.argmax(similarities).item()
            most_similar_talent_name = talent_names[most_similar_index]
            print(most_similar_talent_name)
            embed = emb.build_talent_embed(fetch_talent(most_similar_talent_name))
            await message.channel.send(f'You probably meant **{most_similar_talent_name}**')
        await message.channel.send(embed=embed, reference=message)

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
