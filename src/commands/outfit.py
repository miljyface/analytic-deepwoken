from handlers.spellCheck import find
from handlers.spellCheck import outfit_names as name_list
from handlers.backbone import searchTableByName
import embedBuilder.outfitEmbed as emb

def execute(name):
    item_substring = name.lower()
    match = next((name for name in name_list if item_substring in name.lower()), None)

    if match:
        outfit_data = searchTableByName('outfits', name)
        return emb.build_outfit_embed(outfit_data)
    else:
        most_similar_name = find(name, 'outfit')
        outfit_data = searchTableByName('outfits', most_similar_name)
        return emb.build_outfit_embed(outfit_data)