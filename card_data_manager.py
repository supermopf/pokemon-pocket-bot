# src/card_data_manager.py
import requests
import json
import os


class CardDataManager:
    API_URL = "https://api.dotgg.gg/cgfw/getcards?game=pokepocket&mode=indexed"
    CACHE_FILE = "card_data_cache.json"

    def __init__(self):
        self.card_data = {}
        self.load_card_data()

    def load_card_data(self):
        if os.path.exists(self.CACHE_FILE):
            with open(self.CACHE_FILE, "r") as f:
                self.card_data = json.load(f)
        else:
            self.fetch_and_cache_card_data()

    def fetch_and_cache_card_data(self):
        response = requests.get(self.API_URL)
        if response.status_code == 200:
            data = response.json()
            self.process_card_data(data)
            with open(self.CACHE_FILE, "w") as f:
                json.dump(self.card_data, f)
        else:
            print(f"Failed to fetch card data. Status code: {response.status_code}")

    def process_card_data(self, data):
        names = data["names"]
        for card_info in data["data"]:
            card_dict = dict(zip(names, card_info))
            card_id = card_dict["name"]
            self.card_data[card_id] = card_dict

    def get_card_by_name(self, name):
        if name is None:
            return []
        name = name.lower()
        matches = []
        for card in self.card_data.values():
            if name in card["name"].lower():
                matches.append(card)
        return matches

    def get_card_by_id(self, _id):
        return self.card_data.get(_id, None)

    def get_card_image_url(self, card_id):
        return f"https://static.dotgg.gg/pokepocket/card/{card_id}.webp"
