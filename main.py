"""
MinecraftKitCreator
Dieses Programm ermöglicht die Erstellung von Minecraft-Kits in Shulkerboxen.

Verwendung:
    python main.py

Autor: Leni
"""

import sys
import os
from PySide6.QtWidgets import QApplication

def download_minecraft_icons(icon_dir="icons"):
    """Download missing Minecraft icons from a reliable source."""
    import os
    import requests
    from pathlib import Path
    from io import BytesIO
    from PIL import Image
    import logging
    
    # Create icons directory if it doesn't exist
    if not os.path.exists(icon_dir):
        os.makedirs(icon_dir)
        
    # List of items that need icons
    items = [
        "crossbow", "shield", "stone", "oak_log", "oak_planks", "cobblestone",
        "dirt", "grass_block", "obsidian", "diamond_block", "gold_block", 
        "iron_block", "netherite_block", "enchanted_golden_apple", "compass", 
        "clock", "beacon", "conduit"
    ]
    
    # Base URL for Minecraft Wiki icons
    base_url = "https://minecraft.fandom.com/wiki/Special:FilePath/"
    
    for item in items:
        icon_path = os.path.join(icon_dir, f"{item}.png")
        if not os.path.exists(icon_path):
            try:
                # Format item name for URL
                formatted_item = item.replace("_", " ").title()
                url = f"{base_url}{formatted_item}.png"
                
                response = requests.get(url)
                if response.status_code == 200:
                    # Save the image
                    img = Image.open(BytesIO(response.content))
                    # Resize to standard size if needed (e.g. 32x32)
                    img = img.resize((32, 32))
                    img.save(icon_path)
                    logging.info(f"Downloaded icon for {item}")
                else:
                    logging.warning(f"Failed to download icon for {item}: HTTP {response.status_code}")
            except Exception as e:
                logging.error(f"Error downloading icon for {item}: {str(e)}")
    
    logging.info(f"Icon download process completed. Check the {icon_dir} folder.")

# Füge den aktuellen Pfad zum Python-Suchpfad hinzu
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# GUI importieren
try:
    # Erst den GUI-Ordner zum Suchpfad hinzufügen
    gui_dir = os.path.join(current_dir, "gui")
    sys.path.append(gui_dir)
    
    # Dann die MainWindow importieren
    from gui.main_window import MainWindow
except ImportError as e:
    print(f"Fehler beim Importieren der GUI-Module: {e}")
    print("Stellen Sie sicher, dass die Dateien korrekt installiert sind.")
    sys.exit(1)

def main():
    """Hauptfunktion zum Starten der Anwendung"""
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Fehler beim Starten der Anwendung: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    download_minecraft_icons()
    main()
