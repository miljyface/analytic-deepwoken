from handlers.spellCheck import find
from handlers.spellCheck import mantra_names as name_list
from handlers.backbone import searchTableByName
import embedBuilder.mantraEmbed as emb

def execute(name):
    item_substring = name.lower()
    match = next((name for name in name_list if item_substring in name.lower()), None)

    if match:
        mantra_data = searchTableByName('mantras', name)
        return emb.build_mantra_embed(mantra_data)
    else:
        most_similar_name = find(name, 'mantra')
        mantra_data = searchTableByName('mantras', most_similar_name)
        return emb.build_mantra_embed(mantra_data)