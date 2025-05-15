from dataclasses import dataclass
from typing import List, Dict

@dataclass
class MinecraftItem:
    id: str          # "minecraft:diamond_sword"
    name: str        # "Diamantschwert"
    category: str    # "Waffen"
    max_stack: int   # 1
    slots: List[str] # ["mainhand", "offhand"]
    icon: str        # "diamond_sword.png"

@dataclass
class Enchantment:
    id: str                 # "minecraft:sharpness"
    name: str               # "Schärfe"
    max_level: int          # 5
    conflicts: List[str]    # ["minecraft:smite", ...]

@dataclass
class KitSlot:
    item: MinecraftItem
    slot_id: int
    enchantments: List[Enchantment]