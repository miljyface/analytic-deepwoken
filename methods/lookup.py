import json
import torch
import numpy as np
from methods.shrineoforder import order
from sentence_transformers import SentenceTransformer
from methods.initmethods import talentBase, mantraBase, equipmentBase, outfitBase, weaponBase
from methods.initmethods import talent_names, mantra_names, equipment_names, outfit_names, weapon_names

model = SentenceTransformer("google/embeddinggemma-300m")
talent_embeddings = np.load('data/weights/talent_embeddings.npy')
mantra_embeddings = np.load('data/weights/mantra_embeddings.npy')
outfit_embeddings = np.load('data/weights/outfit_embeddings.npy')
equipment_embeddings = np.load('data/weights/equipment_embeddings.npy')
weapon_embeddings = np.load('data/weights/weapon_embeddings.npy')

embeddings_dict = {
        "talent": talent_embeddings,
        "mantra": mantra_embeddings,
        "outfit": outfit_embeddings,
        "equipment": equipment_embeddings,
        "weapon": weapon_embeddings
    }

names_dict = {
    "talent": talent_names,
    "mantra": mantra_names,
    "outfit": outfit_names,
    "equipment": equipment_names,
    "weapon": weapon_names
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

def fetch_weapon(weapon_name):
    for wb in weaponBase:
        if wb.get('name', '').lower() == weapon_name.lower():
            return wb
    return None

def fetch_talent_by_id(talent_id):
    for tb in talentBase:
        if str(tb.get('id', '')) == str(talent_id):
            return tb
    return None