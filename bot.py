import discord
import methods.dwbapi as dwb
from methods.shrineoforder import order
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import torch
import os
import json
import data.extraction as ext
print('All libraries loaded!')

with open('data/talents.json') as f:
    talentBase = json.load(f)
talent_names = [tb.get('name', '') for tb in talentBase]

model = SentenceTransformer("google/embeddinggemma-300m")
doc_embeddings = model.encode_document(talent_names)
print(talent_names)

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

def build_talent_embed(talent: dict) -> discord.Embed:
    data = talent.get("data", {})
    attunements = data.get("attunements", {})
    exclusive_with = data.get("exclusive with", [])
    embed = discord.Embed(
        title=talent.get("name", "Unknown Talent"),
        description=data.get("desc", "No description available."),
        color=0x1A1A1A
    )
    embed.add_field(name="ID", value=str(talent.get("id", "N/A")), inline=True)
    embed.add_field(name="Rarity", value=data.get("rarity", "Unknown"), inline=True)
    embed.add_field(name="Power", value=str(data.get("power", 0)), inline=True)
    # Attunements
    if attunements:
        attune_text = "\n".join(f"{k.capitalize()}: {v}" for k, v in attunements.items())
        embed.add_field(name="Attunement Requirements", value=attune_text, inline=False)
    # Exclusivity
    if exclusive_with:
        embed.add_field(name="Exclusive With", value="\n".join(exclusive_with), inline=False)
    # Category and Vaulted
    embed.add_field(name="Category", value=str(data.get("category", "N/A")), inline=True)
    embed.add_field(name="Vaulted", value=str(data.get("vaulted", False)), inline=True)
    # Footer
    embed.set_footer(
        text=f"Auto Talent: {data.get('autotalent', False)} • "
             f"Does not count toward total: {data.get('dontcounttowardstotal', False)}"
    )
    return embed

def add_split_field(embed, name, items):
    current = ""
    for item in items:
        line = item + ", "
        if len(current) + len(line) > 1024:
            embed.add_field(name=name, value=current.rstrip(", "), inline=False)
            name += " (cont.)"
            current = line
        else:
            current += line
    if current:
        embed.add_field(name=name, value=current.rstrip(", "), inline=False)

def get_deepwoken_build_embed(build_id):
    build1 = dwb.dwbBuild(build_id).rawdata  # expects a dict matching your sample

    stats = build1['stats']
    meta = stats['meta']
    pre_shrine = build1.get('preShrine', {})
    post_shrine = build1.get('postShrine', {})
    talents = build1.get('talents', [])
    mantras = build1.get('mantras', [])
    trait_dict = stats.get('traits', {})

    # Format trait dictionary
    traits_str = ', '.join([f"{k}: {v}" for k, v in trait_dict.items()]) if trait_dict else "None"

    # Helper for stat blocks
    def stats_section(d):
        result = []
        for sub, subdict in d.items():
            result.append(f"{sub.capitalize()}:")
            for stat, value in subdict.items():
                result.append(f"  {stat}: {value}")
        return '\n'.join(result)

    embed = discord.Embed(
        title=stats.get('buildName', 'Deepwoken Build'),
        description=stats.get('buildDescription', 'No description.'),
        color=discord.Color.teal()
    )

    # Meta
    embed.add_field(name="Race", value=meta.get('Race', 'Unknown'), inline=True)
    embed.add_field(name="Outfit", value=meta.get('Outfit', 'Unknown'), inline=True)
    embed.add_field(name="Origin", value=meta.get('Origin', 'Unknown'), inline=True)
    embed.add_field(name="Oath", value=meta.get('Oath', 'Unknown'), inline=True)
    embed.add_field(name="Murmur", value=meta.get('Murmur', 'None'), inline=True)
    embed.add_field(name="Bell", value=meta.get('Bell', 'None'), inline=True)
    embed.add_field(name="Traits", value=traits_str, inline=False)

    # Talents & Mantras
    add_split_field(embed, "Talents", talents)
    add_split_field(embed, "Mantras", mantras)
    
    # Stat blocks
    if post_shrine:
        embed.add_field(name="Post Shrine Attributes", value=stats_section(post_shrine), inline=False)
    if pre_shrine:
        embed.add_field(name="Pre Shrine Attributes", value=stats_section(pre_shrine), inline=False)

    # Tags
    tags = ', '.join(build1.get('meta', {}).get('tags', []))
    if tags:
        embed.add_field(name="Tags", value=tags, inline=False)

    # Author
    author_name = build1['author']['name'] if build1.get('author') else ""
    if author_name:
        embed.set_author(name=f"by {author_name}")

    return embed

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
            embed = build_talent_embed(fetch_talent(match))
            print(embed.to_dict())  # See exactly what would be sent            
        else:
            query_embedding = model.encode_query(talent_name)
            similarities = model.similarity(query_embedding, doc_embeddings)
            most_similar_index = torch.argmax(similarities).item()
            most_similar_talent_name = talent_names[most_similar_index]
            print(most_similar_talent_name)
            embed = build_talent_embed(fetch_talent(most_similar_talent_name))
            await message.channel.send(f'You probably meant **{most_similar_talent_name}**')
        await message.channel.send(embed=embed)

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
                        embed = get_deepwoken_build_embed(build_id)
                        await message.channel.send(embed=embed)
                except Exception as e:
                    await message.channel.send(f'Error fetching build: {str(e)}')


client.run(BOT_TOKEN)
