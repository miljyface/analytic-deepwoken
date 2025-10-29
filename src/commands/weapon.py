from handlers.spellCheck import find
from handlers import spellCheck
from handlers.backbone import searchTableByName
import embedBuilder.weaponEmbed as emb

def execute(name, guild_id=None):
    # Ensure names are loaded
    spellCheck._ensure_names_loaded()
    name_list = spellCheck.weapon_names
    
    substring = name.lower()
    match = next((wname for wname in name_list if substring.lower() in wname.lower()), None)

    if match:
        weapon_data = searchTableByName('weapons', match)
        return emb.build_weapon_embed(weapon_data, guild_id)
    else:
        most_similar_name = find(name, 'weapon')
        weapon_data = searchTableByName('weapons', most_similar_name)
        return emb.build_weapon_embed(weapon_data, guild_id)