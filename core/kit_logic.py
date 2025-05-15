import json
from pathlib import Path

def load_items(version="1.20"):
    items_dir = Path(f"data/items/{version}")
    items = []
    for item_file in items_dir.glob("*.json"):
        with open(item_file) as f:
            data = json.load(f)
            items.append(MinecraftItem(**data))
    return items

class KitManager:
    def __init__(self):
        self.items = []
        self.version = "1.20"

    def add_item(self, item_id, slot):
        item = next((i for i in load_items() if i.id == item_id), None)
        if item and slot not in [i.slot for i in self.items]:
            self.items.append({"item": item, "slot": slot})
            return True
        return False