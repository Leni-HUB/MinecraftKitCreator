Step-by-Step Guide for Fixing Your Minecraft Kit Creator
Based on your project structure, here's exactly what you need to do to implement the fixes:
Step 1: Set up the enchantments.json file

Open your project folder
Navigate to data/1.20/ directory
If enchantments.json doesn't exist, create it
Copy the complete JSON content from my "Minecraft Kit Creator Enchantment Data" artifact into this file
Save the file

Step 2: Download missing icons

Navigate to your project's icons folder (create it if it doesn't exist)
Add the following code to your main.py file (right after your imports):

pythondef download_minecraft_icons(icon_dir="icons"):
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

Call this function in your main.py file's main section:

pythonif __name__ == "__main__":
    download_minecraft_icons()
    # Your existing code...
Step 3: Fix the inventory_grid.py file

Open the gui/inventory_grid.py file
Look for the start_drag method
Replace it with this fixed version:

pythondef start_drag(self, widget, point):
    """Start drag operation with proper rendering."""
    try:
        # Create mime data with item information
        mime_data = QMimeData()
        item_data_str = json.dumps(widget.item_data)
        mime_data.setData("application/minecraft-item", QByteArray(item_data_str.encode()))
        
        # Create drag object
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        
        # Create pixmap for drag icon
        pixmap = QPixmap(widget.size())
        pixmap.fill(Qt.transparent)
        
        # Use a temporary device to render
        painter = QPainter(pixmap)
        widget.render(painter, QPoint(0, 0))
        painter.end()  # Must end the painter before setting the pixmap
        
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))
        
        # Execute drag
        result = drag.exec_(Qt.CopyAction | Qt.MoveAction)
        
        if result == Qt.MoveAction:
            # Clear the source if it was a move operation
            self.clear_slot(widget)
            
    except Exception as e:
        logging.error(f"Drag start error: {str(e)}")
Step 4: Create the EnchantmentDialog

Create a new file in the gui folder called enchantment_dialog.py
Copy the following code into it:

pythonimport json
import logging
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QComboBox, QSpinBox, QPushButton,
                              QScrollArea, QWidget)
from PySide6.QtCore import Qt

class EnchantmentDialog(QDialog):
    """
    Dialog for efficiently setting enchantments on items.
    Allows quick selection and configuration.
    """
    def __init__(self, parent=None, item_data=None):
        super().__init__(parent)
        self.setWindowTitle("Enchantment Editor")
        self.setMinimumWidth(400)
        self.item_data = item_data if item_data else {}
        
        # Load enchantment data
        self.enchantments = self.load_enchantments()
        
        # Create UI
        self.init_ui()
        
        # Load current enchantments
        self.load_current_enchantments()
    
    def load_enchantments(self):
        """Load enchantment data from JSON file."""
        try:
            with open("data/1.20/enchantments.json", "r") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading enchantments: {str(e)}")
            return {}
    
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Create scroll area for enchantments
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.enchantment_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # Create preset buttons
        preset_layout = QHBoxLayout()
        presets = {
            "PvP": self.apply_pvp_preset,
            "PvE": self.apply_pve_preset,
            "Max All": self.apply_max_all
        }
        
        for name, func in presets.items():
            btn = QPushButton(name)
            btn.clicked.connect(func)
            preset_layout.addWidget(btn)
        
        main_layout.addLayout(preset_layout)
        
        # Sort enchantments by category for better organization
        categorized = self.categorize_enchantments()
        
        # Add enchantment controls by category
        for category, enchants in categorized.items():
            # Add category header
            category_label = QLabel(f"--- {category} ---")
            category_label.setStyleSheet("font-weight: bold; color: #5555FF;")
            self.enchantment_layout.addWidget(category_label)
            
            for enchant_id, enchant_data in enchants.items():
                self.add_enchantment_control(enchant_id, enchant_data)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_enchantments)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(cancel_btn)
        main_layout.addLayout(button_layout)
    
    def categorize_enchantments(self):
        """Categorize enchantments for better organization."""
        categories = {
            "Weapon": {},
            "Armor": {},
            "Tool": {},
            "Special": {}
        }
        
        for enchant_id, enchant_data in self.enchantments.items():
            # Determine category based on applicable items
            target = enchant_data.get("target", "").lower()
            
            if any(x in target for x in ["sword", "axe", "bow", "crossbow", "trident"]):
                categories["Weapon"][enchant_id] = enchant_data
            elif any(x in target for x in ["helmet", "chestplate", "leggings", "boots", "armor"]):
                categories["Armor"][enchant_id] = enchant_data
            elif any(x in target for x in ["pickaxe", "shovel", "hoe", "fishing"]):
                categories["Tool"][enchant_id] = enchant_data
            else:
                categories["Special"][enchant_id] = enchant_data
        
        return categories
    
    def add_enchantment_control(self, enchant_id, enchant_data):
        """Add control for a single enchantment."""
        row = QHBoxLayout()
        
        # Checkbox for enabling/disabling
        enable_check = QComboBox()
        enable_check.addItem("Off", False)
        enable_check.addItem("On", True)
        enable_check.setObjectName(f"enable_{enchant_id}")
        
        # Level selector
        level_spin = QSpinBox()
        level_spin.setMinimum(1)
        level_spin.setMaximum(enchant_data.get("max_level", 5))
        level_spin.setObjectName(f"level_{enchant_id}")
        level_spin.setEnabled(False)  # Disabled by default
        
        # Connect checkbox to enable/disable level spinner
        enable_check.currentIndexChanged.connect(
            lambda idx: level_spin.setEnabled(idx == 1)
        )
        
        # Label with enchantment name
        name_label = QLabel(enchant_data.get("name", enchant_id))
        tooltip = f"{enchant_data.get('description', '')}\nMax Level: {enchant_data.get('max_level', 1)}"
        name_label.setToolTip(tooltip)
        
        # Add widgets to row
        row.addWidget(name_label, 3)
        row.addWidget(enable_check, 1)
        row.addWidget(level_spin, 1)
        
        # Add row to layout
        self.enchantment_layout.addLayout(row)
    
    def load_current_enchantments(self):
        """Load current enchantments from item data."""
        current_enchants = self.item_data.get("enchantments", [])
        
        for enchant in current_enchants:
            enchant_id = enchant.get("id", "").split(":")[-1]
            level = enchant.get("level", 1)
            
            # Set UI elements
            enable_widget = self.findChild(QComboBox, f"enable_{enchant_id}")
            level_widget = self.findChild(QSpinBox, f"level_{enchant_id}")
            
            if enable_widget and level_widget:
                enable_widget.setCurrentIndex(1)  # Enable
                level_widget.setValue(level)
                level_widget.setEnabled(True)
    
    def apply_enchantments(self):
        """Apply selected enchantments to the item."""
        enchantments = []
        
        for enchant_id in self.enchantments:
            enable_widget = self.findChild(QComboBox, f"enable_{enchant_id}")
            level_widget = self.findChild(QSpinBox, f"level_{enchant_id}")
            
            if enable_widget and level_widget and enable_widget.currentData():
                enchantments.append({
                    "id": f"minecraft:{enchant_id}",
                    "level": level_widget.value()
                })
        
        self.item_data["enchantments"] = enchantments
        self.accept()
    
    def apply_pvp_preset(self):
        """Apply PvP-focused enchantment preset."""
        preset = {
            "sharpness": 5,
            "fire_aspect": 2,
            "protection": 4,
            "feather_falling": 4,
            "unbreaking": 3,
            "mending": 1,
            "sweeping": 3,
            "knockback": 2
        }
        self.apply_preset(preset)
    
    def apply_pve_preset(self):
        """Apply PvE-focused enchantment preset."""
        preset = {
            "efficiency": 5,
            "fortune": 3,
            "unbreaking": 3,
            "mending": 1,
            "silk_touch": 1,
            "looting": 3
        }
        self.apply_preset(preset)
    
    def apply_max_all(self):
        """Apply maximum level for all applicable enchantments."""
        for enchant_id, enchant_data in self.enchantments.items():
            enable_widget = self.findChild(QComboBox, f"enable_{enchant_id}")
            level_widget = self.findChild(QSpinBox, f"level_{enchant_id}")
            
            if enable_widget and level_widget:
                # Check if enchantment is applicable for the item
                if self.is_enchantment_applicable(enchant_id, enchant_data):
                    enable_widget.setCurrentIndex(1)  # Enable
                    level_widget.setValue(enchant_data.get("max_level", 1))
                    level_widget.setEnabled(True)
    
    def apply_preset(self, preset):
        """Apply a preset configuration of enchantments."""
        # First reset all
        for enchant_id in self.enchantments:
            enable_widget = self.findChild(QComboBox, f"enable_{enchant_id}")
            level_widget = self.findChild(QSpinBox, f"level_{enchant_id}")
            
            if enable_widget and level_widget:
                enable_widget.setCurrentIndex(0)  # Disable
                level_widget.setEnabled(False)
        
        # Apply preset values
        for enchant_id, level in preset.items():
            enable_widget = self.findChild(QComboBox, f"enable_{enchant_id}")
            level_widget = self.findChild(QSpinBox, f"level_{enchant_id}")
            
            if enable_widget and level_widget and self.is_enchantment_applicable(enchant_id, self.enchantments.get(enchant_id, {})):
                enable_widget.setCurrentIndex(1)  # Enable
                level_widget.setValue(min(level, level_widget.maximum()))
                level_widget.setEnabled(True)
    
    def is_enchantment_applicable(self, enchant_id, enchant_data):
        """Check if an enchantment is applicable for the current item."""
        if not self.item_data:
            return True
        
        item_id = self.item_data.get("id", "").split(":")[-1]
        target = enchant_data.get("target", "").lower()
        
        # Simple logic to determine if enchantment is applicable
        if "all" in target:
            return True
        elif "weapon" in target and any(x in item_id for x in ["sword", "axe", "bow", "crossbow", "trident"]):
            return True
        elif "armor" in target and any(x in item_id for x in ["helmet", "chestplate", "leggings", "boots"]):
            return True
        elif "tool" in target and any(x in item_id for x in ["pickaxe", "shovel", "hoe"]):
            return True
        
        # Check for specific item matches
        for item_type in target.split(","):
            if item_type.strip() in item_id:
                return True
        
        return False