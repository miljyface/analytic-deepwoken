import discord
import handlers.backbone as daten


def build_outfit_embed(outfit: dict) -> discord.Embed:
    payload = outfit.get('data') if isinstance(outfit.get('data'), dict) else outfit

    name = payload.get('name', 'Unknown')
    materials = payload.get('mats', 'Unknown')
    rarity = payload.get('category', 'Unknown')
    requirements = payload.get('requirements', {})

    #functional stats
    durability = payload.get('durability', 'Unknown')
    resis = payload.get('resistances', {})
    etherRegen = payload.get('ether regen', 'Unknown')
    talents = payload.get('talents', 'None')

    embed = discord.Embed(
        title=f"{name} - {rarity}",
        color=0xffffff
    )

    embed.add_field(name="Materials", value='\n'.join([f"{k}" for k in materials]) if materials else "None", inline=False)

    # Requirements: omit entries that are zero (0 or '0')
    req_lines = []
    if isinstance(requirements, dict):
        for k, v in requirements.items():
            try:
                numeric = float(v)
            except Exception:
                numeric = None
            if numeric is not None:
                if numeric == 0:
                    continue
                # format without trailing .0 when integer
                disp = int(numeric) if float(numeric).is_integer() else numeric
                req_lines.append(f"{k}: {disp}")
            else:
                # non-numeric, include if not empty/None
                if v not in (None, '', '0'):
                    req_lines.append(f"{k}: {v}")

    embed.add_field(name="Requirements", value='\n'.join(req_lines) if req_lines else "None", inline=False)

    #functional display
    # Durability: only show if meaningful and non-zero
    if isinstance(durability, (int, float)):
        if durability != 0:
            embed.add_field(name="Durability", value=str(durability), inline=True)
    else:
        # show when it's a non-numeric meaningful value
        if durability not in (None, 'Unknown'):
            embed.add_field(name="Durability", value=str(durability), inline=True)

    # Ether regen: always show if numeric (with %), otherwise show textual value
    if isinstance(etherRegen, (int, float)):
        embed.add_field(name="Ether Regen", value=f"{etherRegen}%", inline=True)
    else:
        if etherRegen not in (None,):
            embed.add_field(name="Ether Regen", value=str(etherRegen), inline=True)

    # Resistances: omit entries with 0, format included values with %
    if isinstance(resis, dict):
        # desired order (case-insensitive)
        desired_order = [
            'Physical', 'Blunt', 'Slash', 'Elemental',
            'Flamecharm', 'Frostdraw', 'Thundercall', 'Galebreathe',
            'Shadowcast', 'Ironsing', 'Bloodrend'
        ]

        # map lowercase key -> original key to support case-insensitive matching
        key_map = {k.lower(): k for k in resis.keys()}
        res_lines = []
        used = set()

        def format_entry(k, v):
            try:
                numeric = float(v)
            except Exception:
                numeric = None
            if numeric is None:
                return f"{k}: {v}" if v not in (0, '0') else None
            if numeric == 0:
                return None
            disp = int(numeric) if float(numeric).is_integer() else numeric
            return f"{k}: {disp}%"

        # add in the desired order if present
        for dk in desired_order:
            lk = dk.lower()
            if lk in key_map:
                orig = key_map[lk]
                formatted = format_entry(orig, resis[orig])
                if formatted:
                    res_lines.append(formatted)
                used.add(orig)

        # append any remaining resistances preserving original order
        for orig, v in resis.items():
            if orig in used:
                continue
            formatted = format_entry(orig, v)
            if formatted:
                res_lines.append(formatted)

        if res_lines:
            embed.add_field(name="Resistances", value='\n'.join(res_lines), inline=False)

    # Talents: resolve integer ids safely using searchTableById
    if talents:
        talent_lines = []
        for k in talents:
            if isinstance(k, int):
                try:
                    tal = daten.searchTableById('talents', k)
                    if isinstance(tal, dict):
                        tname = tal.get('data', {}).get('name') or tal.get('name') or f"talent {k}"
                    else:
                        tname = f"talent {k}"
                except Exception:
                    tname = f"talent {k}"
                talent_lines.append(str(tname))
            else:
                talent_lines.append(str(k))
        if talent_lines:
            embed.add_field(name="Talents", value='\n'.join(talent_lines), inline=False)

    return embed