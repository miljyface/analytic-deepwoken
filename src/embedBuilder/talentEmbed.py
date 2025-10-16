import discord
import handlers.backbone as daten


def build_talent_embed(talent: dict) -> discord.Embed:
    payload = talent.get('data') if isinstance(talent.get('data'), dict) else talent
    data = payload or {}
    stats = data.get('base', {})
    weapons = data.get('weapons', {})
    attunements = data.get('attunements', {})
    exclusive_with = data.get('exclusive with', [])

    cat = daten.searchTableById("categories", data.get("category", "Unknown Category"))
    category_name = cat.get("name", "Unknown Category") if isinstance(cat, dict) else str(cat)

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

    if exclusive_with:
        embed.add_field(name="Exclusive With", value="\n".join(exclusive_with), inline=False)
    embed.add_field(name="Vaulted", value=str(data.get("vaulted", False)), inline=True)

    # Invert the 'dontcounttowardstotal' value and present it as 'Count toward total'
    raw_flag = data.get('dontcounttowardstotal', False)
    # Interpret non-bool values as truthy/falsey
    try:
        flag_bool = bool(raw_flag)
    except Exception:
        flag_bool = False
    inverted = not flag_bool
    embed.set_footer(
        text=f"Count toward total: {inverted}"
    )
    return embed