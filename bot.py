import discord
import methods.dwbapi as dwb
from methods.shrineoforder import order
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import torch
import os
import pandas as pd
print('All libraries loaded!')

model = SentenceTransformer("google/embeddinggemma-300m")
df = pd.read_json('data/talentlist.json')
talent_names = df['talent_names'].tolist()
doc_embeddings = model.encode_document(talent_names)
print(talent_names)

load_dotenv()
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        pass

    if message.content.startswith('+talent'):
        # Get the talent name from command
        talent_name = message.content[len('+talent'):].strip()
        if talent_name in talent_names:
            talent = dwb.talent(talent_name)
        else:
            query_embedding = model.encode_query(talent_name)
            similarities = model.similarity(query_embedding, doc_embeddings)
            most_similar_index = torch.argmax(similarities).item()
            most_similar_talent_name = talent_names[most_similar_index]
            print(most_similar_talent_name)
            await message.channel.send(f'You probably meant: **{most_similar_talent_name}**')
        
        if not talent:
            await message.channel.send(
                f"Talent '{talent_name}' not found or API returned no data."
            )
            return

        embed = discord.Embed(
            title=f"Talent: {talent['name']}",
            description=talent.get('desc', ''),
            color=discord.Color.purple()
        )

        embed.add_field(name="Rarity", value=talent.get('rarity', 'Unknown'), inline=True)
        embed.add_field(name="Category", value=talent.get('category', 'Unknown'), inline=True)
        embed.add_field(name="Stat Bonus", value=talent.get('stats', 'None'), inline=True)
        embed.add_field(name="Vaulted", value="Yes" if talent.get('vaulted') else "No", inline=True)
        embed.add_field(name="Counts Toward Total", value="No" if talent.get('dontCountTowardsTotal') else "Yes", inline=True)

        # Requirements
        reqs = talent.get('reqs', {})
        base_stats = reqs.get('base', {})
        weapon = reqs.get('weapon', {})
        attunement = reqs.get('attunement', {})

        requirements = (
            f"Power: {reqs.get('power', 0)}\n"
            f"Weapon Type: {reqs.get('weaponType', 'None')}\n"
            f"Strength: {base_stats.get('Strength', 0)} | "
            f"Fortitude: {base_stats.get('Fortitude', 0)} | "
            f"Agility: {base_stats.get('Agility', 0)} | "
            f"Body: {base_stats.get('Body', 0)}\n"
            f"Intelligence: {base_stats.get('Intelligence', 0)} | "
            f"Willpower: {base_stats.get('Willpower', 0)} | "
            f"Charisma: {base_stats.get('Charisma', 0)} | "
            f"Mind: {base_stats.get('Mind', 0)}"
        )
        embed.add_field(name="Base Requirements", value=requirements, inline=False)

        weapon_req = (
            f"Heavy Weapon: {weapon.get('Heavy Wep.', 0)}\n"
            f"Medium Weapon: {weapon.get('Medium Wep.', 0)}\n"
            f"Light Weapon: {weapon.get('Light Wep.', 0)}"
        )
        embed.add_field(name="Weapon Requirements", value=weapon_req, inline=True)

        attunement_req = (
            f"Flamecharm: {attunement.get('Flamecharm', 0)} | "
            f"Frostdraw: {attunement.get('Frostdraw', 0)} | "
            f"Thundercall: {attunement.get('Thundercall', 0)} | "
            f"Galebreathe: {attunement.get('Galebreathe', 0)} | "
            f"Shadowcast: {attunement.get('Shadowcast', 0)} | "
            f"Ironsing: {attunement.get('Ironsing', 0)} | "
            f"Bloodrend: {attunement.get('Bloodrend', 0)}"
        )
        embed.add_field(name="Attunement Requirements", value=attunement_req, inline=False)

        # Exclusive talents
        excl = ', '.join([ex for ex in talent.get('exclusiveWith', []) if ex])
        embed.add_field(name="Exclusive With", value=excl if excl else "None", inline=False)

        await message.channel.send(embed=embed)
    
    if message.content.startswith(''):
        pass

client.run(BOT_TOKEN)
