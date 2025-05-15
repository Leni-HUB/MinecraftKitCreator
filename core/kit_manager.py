from dataclasses import dataclass, field
from typing import List, Dict
from .models import KitSlot, MinecraftItem

class KitManager:
    def __init__(self):
        self.kits = {}          # {tab_id: List[KitSlot]}
        self.current_tab = 0    # Aktiver Tab
        self.undo_stack = []    # Für Undo/Redo
    
    def add_item(self, item: MinecraftItem, slot_id: int):
        """Fügt Item zum aktuellen Kit hinzu"""
        if slot_id in [slot.slot_id for slot in self.kits[self.current_tab]]:
            return False  # Slot belegt
        
        new_slot = KitSlot(item=item, slot_id=slot_id, enchantments=[])
        self.kits[self.current_tab].append(new_slot)
        return True
    
    def validate_enchantments(self, slot: KitSlot):
        """Prüft Verzauberungskonflikte"""
        conflicts = []
        for ench in slot.enchantments:
            for other_ench in slot.enchantments:
                if ench.id in other_ench.conflicts:
                    conflicts.append(f"{ench.name} ❌ {other_ench.name}")
        return conflicts