""" Minecraft Kit Creator - Anleitung zur Projektstruktur

Damit das Programm richtig funktioniert, sollte die folgende Verzeichnisstruktur eingehalten werden:

MinecraftKitCreator/ │ ├── main.py # Hauptskript zum Starten der Anwendung │ ├── gui/ # GUI-Module │ ├── init.py # Leere Datei, um das Verzeichnis als Paket zu markieren │ ├── main_window.py # Hauptfenster-Klasse │ └── inventory_grid.py # Inventar-Grid-Klasse │ ├── data/ # Spieldaten │ └── 1.20/ # Version-spezifische Daten │ └── items.json # Item-Definitionen für Minecraft 1.20 │ ├── icons/ # Item-Icons (müssen mit item["icon"] übereinstimmen) │ ├── diamond_sword.png │ ├── iron_pickaxe.png │ └── ... weitere Icons │ └── assets/ # UI-Assets ├── export_icon.png # Icon für Export-Button └── clear_icon.png # Icon für Clear-Button """

