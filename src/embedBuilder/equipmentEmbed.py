import discord
import handlers.backbone as daten


def build_equipment_embed(equipment: dict) -> discord.Embed:
    # Accept either {'data': {...}} or flat {...}
    payload = equipment.get('data') if isinstance(equipment.get('data'), dict) else equipment

    name = payload.get('name', 'Unknown')
    equipmenttype = payload.get('type', 'Unknown')
    equipmentstats = payload.get('stats', {})
    equipmenttalents = payload.get('talents', [])
    pips = payload.get('rarities', {})

    embed = discord.Embed(
        title=f"{name} ({equipmenttype})",
        color=discord.Color.blurple()
    )

    embed.add_field(name="Stats", value='\n'.join([f"{k}: {v}" for k, v in equipmentstats.items()]) if equipmentstats else "None", inline=False)
    if equipmenttalents:
        talent_lines = []
        for k in equipmenttalents:
            if isinstance(k, int):
                # try to resolve talent by id using backbone helper
                try:
                    tal = daten.searchTableById('talents', k)
                    # tal may be { 'id': ..., 'data': {...} } or flat dict
                    if isinstance(tal, dict):
                        tname = tal.get('data', {}).get('name') or tal.get('name') or f"talent {k}"
                    else:
                        tname = f"talent {k}"
                except Exception:
                    tname = f"talent {k}"
                talent_lines.append(str(tname))
            else:
                talent_lines.append(str(k))
        embed.add_field(name="Talents", value='\n'.join(talent_lines), inline=False)
    embed.add_field(name="Pips", value=', '.join([f"{k}: {v} pips" for k, v in pips.items()]) if pips else "None", inline=False)

    return embed