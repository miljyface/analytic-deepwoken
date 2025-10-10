from supabase import create_client, Client
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
import json
import dotenv
import os

dotenv.load_dotenv()
DATABASE_KEY = str(os.getenv("DATABASE_KEY"))
DATABASE_URL = str(os.getenv("DATABASE_URL"))

# Supabase configuration
SUPABASE_URL = DATABASE_URL
SUPABASE_KEY = DATABASE_KEY

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_table(table_name):
    response = supabase.table(table_name).select("*").execute()
    return response.data

def update_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data)} rows to {file_path}")

with open('data/talents.json') as f:
        talentBase = json.load(f)

with open('data/mantras.json') as f:
    mantraBase = json.load(f)

with open('data/equipments.json') as f:
    equipmentBase = json.load(f)

with open('data/outfits.json') as f:
    outfitBase = json.load(f)

with open('data/weapons.json') as f:
    weaponBase = json.load(f)

def update_weights():
    weapon_names = [wb['name'] for wb in weaponBase]
    mantra_names = [mb.get('name', '') for mb in mantraBase]
    equipment_names = [eb['data']['name'] for eb in equipmentBase]
    outfit_names = [ob['data']['name'] for ob in outfitBase]
    talent_names = [tb.get('name', '') for tb in talentBase]

    model = SentenceTransformer("google/embeddinggemma-300m")

    np.save('data/weights/mantra_embeddings.npy', model.encode_document(mantra_names))
    np.save('data/weights/equipment_embeddings.npy', model.encode_document(equipment_names))
    np.save('data/weights/outfit_embeddings.npy', model.encode_document(outfit_names))
    np.save('data/weights/talent_embeddings.npy', model.encode_document(talent_names))
    np.save('data/weights/weapon_embeddings.npy', model.encode_document(weapon_names))

    return weapon_names, mantra_names, equipment_names, outfit_names, talent_names

weapon_names, mantra_names, equipment_names, outfit_names, talent_names = update_weights()
