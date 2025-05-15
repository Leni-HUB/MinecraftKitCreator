def generate_give_command(kit_slots) -> str:
    """Erzeugt /give-Befehl aus Kit-Daten"""
    command = "/give @p minecraft:player_head{display:{Name:'[Kit]'},"

    items = []
    for slot in kit_slots:
        item = slot.item.id
        enchants = ",".join([f"{{id:{e.id},lvl:{e.level}}}" for e in slot.enchantments])
        items.append(f"{{Slot:{slot.slot_id},id:{item},Enchantments:[{enchants}]}}")
    
    return command + "Items:[" + ",".join(items) + "]}"