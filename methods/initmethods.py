from supabase import create_client, Client
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
import json
import dotenv
import os

dotenv.load_dotenv()
DATABASE_KEY = str(os.getenv("DATABASE_KEY"))

# Supabase configuration
SUPABASE_URL = "https://idyjvmmldtdvpklkzrgr.supabase.co"
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
talent_names = [tb.get('name', '') for tb in talentBase]
model = SentenceTransformer("google/embeddinggemma-300m")
doc_embeddings = model.encode_document(talent_names)
np.save('data/talent_embeddings.npy', doc_embeddings)
