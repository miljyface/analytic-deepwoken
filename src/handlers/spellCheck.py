"""
Fuzzy string matching for spell-checking using RapidFuzz.
Replaces the previous PyTorch/sentence-transformers implementation.
"""
from rapidfuzz import process, fuzz
from handlers.backbone import fetch_table


# Load name lists from the backend on module import (lightweight operation)
def _load_names():
    """Load all item names from the database."""
    weapon_names = [wb['name'] for wb in fetch_table('weapons')]
    mantra_names = [mb.get('name', '') for mb in fetch_table('mantras')]
    equipment_names = [eb.get('data', {}).get('name') or eb.get('name', '') for eb in fetch_table('equipment')]
    outfit_names = [ob.get('data', {}).get('name') or ob.get('name', '') for ob in fetch_table('outfits')]
    talent_names = [tb.get('name', '') for tb in fetch_table('talents')]
    return weapon_names, mantra_names, equipment_names, outfit_names, talent_names


weapon_names, mantra_names, equipment_names, outfit_names, talent_names = _load_names()

names_dict = {
    "talent": talent_names,
    "mantra": mantra_names,
    "outfit": outfit_names,
    "equipment": equipment_names,
    "weapon": weapon_names
}



# Example: if a user types "flame hb" for the weapon, map it to the exact
# database name "Hero's Blade Of Flame" so the fuzzy lookup returns that.
ALIASES = {
    "weapon": {
        # user input -> canonical DB name
        "flame hb": "Hero's Blade Of Flame",
        "frost hb": "Hero's Blade Of Frost",
        "lightning hb": "Hero's Blade Of Lightning",
        "wind hb": "Hero's Blade Of Wind",
        "shadow hb": "Hero's Blade Of Shadow",
        
        
    },
    "mantra": {
        # "short": "Full Mantra Name",
    },
    "equipment": {
    },
    "outfit": {
        "negro diver": "Black diver", 
    },
    "talent": {
    }
}


# Small synonyms map to handle common word variants
SYNONYMS = {
    "fire": "flame",
    "flmae": "flame",
    "gale": "wind",
    "thunder": "lightning",
    "sdw": "shadow",
    
}


def _normalize(s: str) -> str:
    """Lowercase, remove punctuation (keep spaces), and collapse whitespace."""
    import re
    if not s:
        return ""
    s = s.lower()
    # replace non-alphanumeric characters with space
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    # collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s


# Build normalized alias index for faster/robust matching
ALIASES_INDEX = {}
for t, amap in ALIASES.items():
    ai = {}
    for k, v in amap.items():
        nk = _normalize(k)
        ai[nk] = v
    ALIASES_INDEX[t] = ai


def find(argument, type):
    """
    Find the most similar name for `argument` among the given `type` using fuzzy matching.
    
    Args:
        argument (str): The query string to match.
        type (str): The type of item ('talent', 'mantra', 'outfit', 'equipment', 'weapon').
    
    Returns:
        str: The best matching name from the database.
    """
    argument = (argument or "").strip()
    names = names_dict.get(type, [])
    if not names:
        return ""

    # Normalize input for alias lookup
    arg_key = _normalize(argument)

    # Apply simple token-level synonyms (e.g., 'fire' -> 'flame')
    tokens = arg_key.split()
    tokens = [SYNONYMS.get(t, t) for t in tokens]
    arg_key = " ".join(tokens)

    # 1) Exact normalized alias match
    type_aliases = ALIASES_INDEX.get(type, {}) or {}
    if arg_key in type_aliases:
        argument = type_aliases[arg_key]

    else:
        # 2) Fuzzy alias match against normalized alias keys with lower threshold
        if type_aliases:
            alias_keys = list(type_aliases.keys())
            alias_match = process.extractOne(arg_key, alias_keys, scorer=fuzz.WRatio)
            # lower threshold to catch variants like 'fire hb' -> 'flame hb'
            if alias_match and alias_match[1] >= 70:
                mapped = type_aliases.get(alias_match[0])
                if mapped:
                    argument = mapped
    
    # Use RapidFuzz extractOne to get the best match
    # scorer=fuzz.WRatio gives good results for partial/typo matching
    result = process.extractOne(argument, names, scorer=fuzz.WRatio)
    
    if result:
        # result is a tuple: (matched_string, score, index)
        return result[0]
    
    # Fallback: return first name if no match (shouldn't happen with WRatio)
    return names[0] if names else ""