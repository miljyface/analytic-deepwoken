import discord
import methods.dwbapi as dwb
from methods.shrineoforder import order
import methods.lookup as lookup
import json

with open('data/categories.json') as f:
    categories = json.load(f)
category_map = {entry["id"]: entry["name"] for entry in categories}


def build_talent_embed(talent: dict) -> discord.Embed:
    data = talent.get("data", {})
    stats = data.get('base', {})
    weapons = data.get("weapons", {})
    attunements = data.get("attunements", {})
    exclusive_with = data.get("exclusive with", [])
    category_name = category_map.get(data.get("category", 1), "Unknown")
    embed = discord.Embed(
        title=f'{talent.get("name", "Unknown Talent")} - {category_name}',
        description=data.get("desc", "No description available."),
        color=0xffffff
    )
    embed.add_field(name="ID", value=str(talent.get("id", "N/A")), inline=True)
    embed.add_field(name="Rarity", value=data.get("rarity", "Unknown"), inline=True)
    embed.add_field(name="Power", value=str(data.get("power", 0)), inline=True)
    if attunements:
        attune_text = "\n".join(f"{k.capitalize()}: {v}" for k, v in attunements.items())
        embed.add_field(name="Attunement Requirements", value=attune_text, inline=False)
    if stats:
        stats_text = "\n".join(f"{k.capitalize()}: {v}" for k, v in stats.items())
        embed.add_field(name="Base Requirements", value=stats_text, inline=False)
    if weapons:
        wep_text = "\n".join(f"{k.capitalize()}: {v}" for k, v in weapons.items())
        embed.add_field(name="Weapon Requirements", value=wep_text, inline=False)

    embed.add_field(name="Exclusive With", value="\n".join(exclusive_with), inline=False) if exclusive_with else None
    embed.add_field(name="Vaulted", value=str(data.get("vaulted", False)), inline=True)

    embed.set_footer(
        text=f"Does not count toward total: {data.get('dontcounttowardstotal', False)}"
    )
    return embed

def build_mantra_embed(mantra: dict) -> discord.Embed:
    name = mantra.get('name', 'Unknown')
    description = mantra.get('description', 'No description available.')
    stars = mantra.get('stars', 'N/A')
    category = mantra.get('category', 'N/A')
    mantra_type = mantra.get('mantra_type', 'N/A')
    attributes = ', '.join(mantra.get('attribute', [])) if mantra.get('attribute') else 'None'
    gif_url = mantra.get('gif', '')

    reqs = mantra.get('reqs', {})
    attunement_reqs = ', '.join(f"{k}: {v}" for k, v in reqs.get('attunement', {}).items()) if reqs.get('attunement') else 'None'
    base_reqs = ', '.join(f"{k}: {v}" for k, v in reqs.get('base', {}).items()) if reqs.get('base') else 'None'
    weapon_reqs = ', '.join(f"{k}: {v}" for k, v in reqs.get('weapon', {}).items()) if reqs.get('weapon') else 'None'

    embed = discord.Embed(
        title=f"{name} {'★' * int(stars) if str(stars).isdigit() else ''}",
        description=description,
        color=0xffffff
    )
    embed.add_field(name="Category", value=category, inline=True)
    embed.add_field(name="Type", value=mantra_type, inline=True)
    embed.add_field(name="Attribute", value=attributes, inline=True)
    embed.add_field(name="Attunement Requirement", value=attunement_reqs, inline=False) if attunement_reqs != 'None' else None
    embed.add_field(name="Base Requirement", value=base_reqs, inline=False) if base_reqs != 'None' else None
    embed.add_field(name="Weapon Requirement", value=weapon_reqs, inline=False) if weapon_reqs != 'None' else None

    if gif_url:
        embed.set_image(url=gif_url)
    return embed


def build_equipment_embed(equipment: dict) -> discord.Embed:
    name = equipment.get('data', {}).get('name', 'Unknown')
    equipmenttype = equipment.get('data', {}).get('type', 'Unknown')
    equipmentstats = equipment.get('data', {}).get('stats', {})
    equipmenttalents = equipment.get('data', {}).get('talents', [])
    pips = equipment.get('data', {}).get('rarities', {})

    embed = discord.Embed(
        title = f"{name} ({equipmenttype})",
        color = 0xffffff
    )

    embed.add_field(name="Stats", value='\n'.join([f"{k}: {v}" for k, v in equipmentstats.items()]) if equipmentstats else "None", inline=False)
    embed.add_field(name="Talents", value='\n'.join([f"{k}" if type(k) != int else f"f{lookup.fetch_talent_by_id(k)}" for k in equipmenttalents]), inline = False) if equipmenttalents else None
    embed.add_field(name="Pips", value=', '.join([f"{k}: {v} pips" for k, v in pips.items()]) if pips else "None", inline=False)

    return embed

def build_outfit_embed(outfit: dict) -> discord.Embed:
    name = outfit.get('data', {}).get('name', 'Unknown')
    materials = outfit.get('data', {}).get('mats', 'Unknown')
    rarity = outfit.get('data', {}).get('category', 'Unknown')
    requirements = outfit.get('data', {}).get('requirements', {})

    #functional stats
    durability = outfit.get('data', {}).get('durability', 'Unknown')
    resis = outfit.get('data', {}).get('resistances', {})
    etherRegen = outfit.get('data', {}).get('ether regen', 'Unknown')
    talents = outfit.get('data', {}).get('talents', 'None')

    embed = discord.Embed(
        title = f"{name} - {rarity}",
        color = 0xffffff
    )

    embed.add_field(name="Materials", value='\n'.join([f"{k}" for k in materials]) if materials else "None", inline=False)
    embed.add_field(name="Requirements", value='\n'.join([f"{k}: {v}" for k, v in requirements.items()]) if requirements else "None", inline=False)

    #functional display
    embed.add_field(name="Durability", value=str(durability), inline=True)
    embed.add_field(name="Ether Regen", value=str(etherRegen), inline=True)
    embed.add_field(name="Resistances", value='\n'.join(f"{k}: {v}" for k, v in resis.items()) if resis else "None", inline=False)
    embed.add_field(name="Talents", value='\n'.join([f"{k}" if type(k) != int else f"f{lookup.fetch_talent_by_id(k)}" for k in talents]), inline = False) if talents else None

    return embed

def build_weapon_embed(weapon: dict) -> discord.Embed:
    name = weapon.get('name', 'Unknown')
    weptype = weapon.get('type', 'Unknown')

    pen = weapon.get('details', {}).get('pen', 0)
    damage = weapon.get('details', {}).get('damage', 0)
    weight = weapon.get('details', {}).get('weight', 0)
    speed = weapon.get('details', {}).get('speed', 0)
    endlag = weapon.get('details', {}).get('endlag', 0)
    scaling = weapon.get('details', {}).get('scaling', {})
    reqs = weapon.get('details', {}).get('reqs', {})

    embed = discord.Embed(
        title = f"{name} - {weptype}",
        color = 0xffffff
    )

    embed.add_field(name="Requirements", value='\n'.join([f"{k}: {v}" for k, v in reqs.items()]) if reqs else "None", inline=True)
    embed.add_field(name="Base Damage", value=str(damage), inline=True)
    embed.add_field(name="Penetration", value=str(pen), inline=True)
    embed.add_field(name="Weight", value=str(weight), inline=True)
    embed.add_field(name="Speed", value=str(speed), inline=True)
    embed.add_field(name="Endlag", value=str(endlag), inline=True)
    embed.add_field(
        name="Scaling",
        value='\n'.join([f"{k}: {v}" for k, v in scaling.items()]) if scaling else "None",
        inline=False
    )

    return embed


def get_deepwoken_build_embed(build_id: str):
    build = dwb.dwbBuild(build_id)
    stats = build.rawdata
    meta = stats['stats']['meta']
    pre_shrine = stats.get('preShrine', {})
    
    embed_meta = discord.Embed(
        title=f"**{getattr(build, 'name', '')}**\n{getattr(build, 'desc', '')}",
        color=0xffffff,
        url = f"https://deepwoken.co/builder?id={build_id}",
    )
    embed_meta.add_field(name="Race", value=meta.get('Race', 'Unknown'), inline=True)
    embed_meta.add_field(name="Outfit", value=meta.get('Outfit', 'Unknown'), inline=True)
    embed_meta.add_field(name="Origin", value=meta.get('Origin', 'Unknown'), inline=True)
    embed_meta.add_field(name="Oath", value=meta.get('Oath', 'None'), inline=True)
    embed_meta.add_field(name="Murmur", value=meta.get('Murmur', 'None'), inline=True)
    embed_meta.add_field(name="Bell", value=meta.get('Bell', 'None'), inline=True)
    traits = stats.get('traits', {})
    traits_str = '\n'.join([f"{v} {k}" for k, v in traits.items() if v > 0]) or "None"
    embed_meta.add_field(name="Traits", value=traits_str, inline=False)

    weapon_names = ['Heavy Wep.', 'Medium Wep.', 'Light Wep.']
    base_names = ['Strength', 'Fortitude', 'Agility', 'Intelligence', 'Willpower', 'Charisma']
    attunement_names = ['Flamecharm', 'Frostdraw', 'Thundercall', 'Galebreathe', 'Shadowcast', 'Ironsing', 'Bloodrend']

    display_wep = ['HVY', 'MED', 'LHT']
    display_base = ['STR', 'FOR', 'AGI', 'INT', 'WIL', 'CHA']
    display_att = ['FLM', 'ICE', 'LTN', 'WND', 'SDW', 'MTL', 'BLD']

    def stat_blockline(names, curr, pre):
        if names == weapon_names:
            dispnames = display_wep
        elif names == base_names:
            dispnames = display_base
        elif names == attunement_names:
            dispnames = display_att
        else:
            dispnames = names  # fallback if names doesn't match any predefined group

        lines = [
            f"{disp:<5}({pre.get(name, 0):>1}){curr.get(name, 0)}"
            for disp, name in zip(dispnames, names)
        ]
        return '```' + '\n'.join(lines) + '```'


    embed_stats = discord.Embed(
        title="Stats",
        color=0xffffff
    )
    # Correct field construction
    embed_stats.add_field(
        name="Weapon",
        value=stat_blockline(
            weapon_names,
            stats.get('attributes', {}).get('weapon', {}),
            pre_shrine.get('weapon', {})
        ),
        inline=True
    )
    embed_stats.add_field(
        name="Base",
        value=stat_blockline(
            base_names,
            stats.get('attributes', {}).get('base', {}),
            pre_shrine.get('base', {})
        ),
        inline=True
    )
    embed_stats.add_field(
        name="Attunements",
        value=stat_blockline(
            attunement_names,
            stats.get('attributes', {}).get('attunement', {}),
            pre_shrine.get('attunement', {})
        ),
        inline=True
    )

    embeds = [embed_meta, embed_stats]

    return embeds