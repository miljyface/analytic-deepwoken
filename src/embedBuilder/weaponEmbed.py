import discord
import handlers.backbone as daten


def build_weapon_embed(weapon: dict) -> discord.Embed:
    payload = weapon.get('data') if isinstance(weapon.get('data'), dict) else weapon

    name = payload.get('name', 'Unknown')
    weptype = payload.get('type', 'Unknown')

    details = payload.get('details', {})
    pen = details.get('pen', 0)
    damage = details.get('damage', 0)
    weight = details.get('weight', 0)
    speed = details.get('speed', 0)
    endlag = details.get('endlag', 0)
    scaling = details.get('scaling', {})
    reqs = details.get('reqs', {})

    embed = discord.Embed(
        title=f"{name} - {weptype}",
        color=0xffffff
    )
    def _format_reqs(reqs_dict: dict) -> str:
        """Format nested requirements dict into multiple lines.

        Expected input example:
        {
            'base': {},
            'weapon': {'Heavy Wep.': 25, 'Light Wep.': 10},
            'attunement': {'Flamecharm': 75},
            'weaponType': None
        }

        Output (multiline):
        weapon: 25 Heavy Wep. & 10 Light Wep.
        attunement: 75 Flamecharm
        weaponType: None
        """
        if not isinstance(reqs_dict, dict):
            return ""

        lines = []
        for outer_k, outer_v in reqs_dict.items():
            # skip empty dicts
            if isinstance(outer_v, dict):
                if not outer_v:
                    continue
                inner_parts = []
                for inner_k, inner_v in outer_v.items():
                    inner_parts.append(f"{inner_v} {inner_k}")
                lines.append(f"{outer_k}: {' & '.join(inner_parts)}")
            else:
                # show None or scalar values explicitly
                if outer_v is None:
                    lines.append(f"{outer_k}: None")
                elif outer_v == {} or outer_v == "":
                    # skip empty scalars/empty dicts
                    continue
                else:
                    lines.append(f"{outer_k}: {outer_v}")

        return "\n".join(lines)

    # Requirements field (hide if all empty)
    reqs_text = _format_reqs(reqs)
    if reqs_text:
        embed.add_field(name="Requirements", value=reqs_text, inline=True)

    # Base Damage (show if present/non-zero)
    if damage is not None:
        embed.add_field(name="Base Damage", value=str(damage), inline=True)

    # Penetration as percentage
    try:
        pen_val = float(pen) * 100
        # Format without decimal when integer, else one decimal
        pen_text = f"{int(pen_val)}%" if pen_val.is_integer() else f"{pen_val:.1f}%"
    except Exception:
        pen_text = str(pen)
    embed.add_field(name="Penetration", value=pen_text, inline=True)

    if weight is not None:
        embed.add_field(name="Weight", value=str(weight), inline=True)
    if speed is not None:
        embed.add_field(name="Speed", value=str(speed), inline=True)
    if endlag is not None:
        embed.add_field(name="Endlag", value=str(endlag), inline=True)

    # Scaling (hide if empty)
    if scaling:
        scaling_text = '\n'.join([f"{k}: {v}" for k, v in scaling.items()])
        embed.add_field(name="Scaling", value=scaling_text, inline=False)

    return embed