import json
import torch
import numpy as np
from methods.shrineoforder import order
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("google/embeddinggemma-300m")
talent_embeddings = np.load('data/weights/talent_embeddings.npy')
mantra_embeddings = np.load('data/weights/mantra_embeddings.npy')
outfit_embeddings = np.load('data/weights/outfit_embeddings.npy')
equipment_embeddings = np.load('data/weights/equipment_embeddings.npy')

embeddings_dict = {
        "talent": talent_embeddings,
        "mantra": mantra_embeddings,
        "outfit": outfit_embeddings,
        "equipment": equipment_embeddings
    }

with open('data/talents.json') as f:
    talentBase = json.load(f)

with open('data/mantras.json') as f:
    mantraBase = json.load(f)

with open('data/equipments.json') as f:
    equipmentBase = json.load(f)

with open('data/outfits.json') as f:
    outfitBase = json.load(f)

talent_names = [tb.get('name', '') for tb in talentBase]
mantra_names = [mb.get('name', '') for mb in mantraBase]    
equipment_names = [eb['data']['name'] for eb in equipmentBase]
outfit_names = [ob['data']['name'] for ob in outfitBase]

names_dict = {
    "talent": talent_names,
    "mantra": mantra_names,
    "outfit": outfit_names,
    "equipment": equipment_names
}
def find(argument, type):
    query_embedding = model.encode_query(argument)
    similarities = model.similarity(query_embedding, embeddings_dict[type])
    most_similar_index = torch.argmax(similarities).item()
    most_similar_name = names_dict[type][most_similar_index]
    return most_similar_name

#fetching functions
def fetch_mantra(mantra_name):
    for mb in mantraBase:
        if mb.get('name', '').lower() == mantra_name.lower():
            return mb
    return None

def fetch_outfit(outfit_name):  
    for ob in outfitBase:
        if ob.get('data', {}).get('name', '').lower() == outfit_name.lower():
            return ob
    return None

def fetch_equipment(equipment_name):
    for eb in equipmentBase:
        if eb.get('data', {}).get('name', '').lower() == equipment_name.lower():
            return eb
    return None

def fetch_talent(talent_name):
    for tb in talentBase:
        if tb.get('name', '').lower() == talent_name.lower():
            return tb
    return None