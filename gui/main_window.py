from PySide6.QtWidgets import (QMainWindow, QListWidget, QWidget, 
                              QHBoxLayout, QVBoxLayout, QToolBar, 
                              QFileDialog, QListWidgetItem, QMessageBox,
                              QApplication)
from PySide6.QtCore import Qt, QSize, QMimeData, QPoint
from PySide6.QtGui import QIcon, QDrag, QAction, QPixmap

# Relativen Import durch absoluten Import ersetzen
import sys
import os
# Füge den übergeordneten Ordner zum Suchpfad hinzu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gui.inventory_grid import InventoryGrid

import json
import logging
import nbtlib
from nbtlib.tag import Compound, List, Int, String

# Konfiguriere Logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.items_db = {}
        self.slot_restrictions = {}
        self.init_ui()
        self.load_items()

    def init_ui(self):
        self.setWindowTitle("Minecraft Kit Creator")
        self.setGeometry(100, 100, 1000, 450)
        self.setup_toolbar()
        self.setup_main_layout()
        self.setup_styles()

    def setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        
        # Export Action
        export_action = QAction("Export Shulker Box", self)
        if os.path.exists("assets/export_icon.png"):
            export_action.setIcon(QIcon("assets/export_icon.png"))
        export_action.triggered.connect(self.export_shulker)
        toolbar.addAction(export_action)
        
        # Clear Action
        clear_action = QAction("Clear Inventory", self)
        if os.path.exists("assets/clear_icon.png"):
            clear_action.setIcon(QIcon("assets/clear_icon.png"))
        clear_action.triggered.connect(self.clear_inventory)
        toolbar.addAction(clear_action)
        
        self.addToolBar(toolbar)

    def setup_main_layout(self):
        main_widget = QWidget()
        layout = QHBoxLayout()
        
        # Item List
        self.item_list = DraggableListWidget(self)
        self.item_list.setDragEnabled(True)
        self.item_list.setDragDropMode(QListWidget.DragOnly)
        self.item_list.setFixedWidth(250)
        self.item_list.setIconSize(QSize(32, 32))
        self.item_list.doubleClicked.connect(self.on_item_double_click)
        
        # Inventory Grid
        self.inventory = InventoryGrid(self.slot_restrictions)
        
        layout.addWidget(self.item_list)
        layout.addWidget(self.inventory)
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def load_items(self):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_dir, "data", "1.20", "items.json")
            
            logger.debug(f"Loading items from: {data_path}")
            
            if os.path.exists(data_path):
                with open(data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    items = data.get("items", [])
                    
                    for item in items:
                        self.add_item_to_list(item)
                        self.slot_restrictions[item["name"]] = item.get("slots", ["inventory"])
                        
                logger.debug(f"Loaded {len(items)} items")
            else:
                logger.error(f"Items file not found: {data_path}")
                QMessageBox.warning(self, "File not found", f"Could not find items.json at {data_path}")

        except Exception as e:
            logger.error(f"Loading error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load items.json: {str(e)}")

    def add_item_to_list(self, item):
        list_item = QListWidgetItem(item.get("name", "Unknown Item"))
        icon_path = os.path.join("icons", item.get("icon", ""))
        
        if os.path.exists(icon_path):
            list_item.setIcon(QIcon(icon_path))
        else:
            logger.warning(f"Icon not found: {icon_path}")
        
        list_item.setData(Qt.UserRole, item)
        self.item_list.addItem(list_item)
        self.items_db[item["name"]] = item

    def export_shulker(self):
        try:
            items = self.inventory.get_export_data()
            
            if not items:
                QMessageBox.warning(self, "Empty", "Inventory is empty!")
                return

            nbt_data = self.create_nbt_structure(items)
            self.save_nbt_file(nbt_data)
            
        except Exception as e:
            logger.error(f"Export error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to export shulker box: {str(e)}")

    def create_nbt_structure(self, items):
        nbt_items = []
        for item in items:
            try:
                item_compound = Compound({
                    'Slot': Int(item['slot']),
                    'id': String(item['id']),
                    'Count': Int(item.get('count', 1))
                })
                
                # Nur hinzufügen, wenn name vorhanden
                if 'name' in item:
                    item_compound['tag'] = Compound({
                        'display': Compound({
                            'Name': String(item['name'])
                        })
                    })
                
                nbt_items.append(item_compound)
            except Exception as e:
                logger.error(f"Error creating NBT for item {item}: {e}")
        
        return List(nbt_items)

    def save_nbt_file(self, nbt_data):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Shulker Box", 
            os.path.expanduser("~/Desktop"), 
            "NBT Files (*.nbt)"
        )
        
        if path:
            try:
                nbtlib.File({'Items': nbt_data}).save(path)
                QMessageBox.information(self, "Success", f"Shulker box saved to:\n{path}")
            except Exception as e:
                logger.error(f"Error saving NBT file: {e}")
                QMessageBox.critical(self, "Error", f"Failed to save NBT file: {str(e)}")

    def clear_inventory(self):
        self.inventory.clear_all()

    def on_item_double_click(self):
        current_item = self.item_list.currentItem()
        if current_item:
            item_data = current_item.data(Qt.UserRole)
            self.inventory.add_item_to_first_valid_slot(item_data)

    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow { background: #333; }
            QListWidget {
                background: #404040;
                color: white;
                border: 2px solid #505050;
                border-radius: 4px;
                font-family: Arial;
            }
            QToolBar { 
                background: #2A2A2A; 
                border-bottom: 1px solid #404040;
                spacing: 5px;
                padding: 2px;
            }
            QToolButton { 
                padding: 3px; 
                margin: 1px;
            }
        """)


class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_start_position = None
        
    def mouseMoveEvent(self, event):
        if not event.buttons() & Qt.LeftButton:
            return super().mouseMoveEvent(event)
            
        if not self.drag_start_position:
            return super().mouseMoveEvent(event)
            
        # Starte nur Drag, wenn Button gedrückt ist und etwas Bewegung stattgefunden hat
        app = QApplication.instance()
        if app:
            drag_distance = (event.position() - self.drag_start_position).manhattanLength()
            if drag_distance > app.startDragDistance():
                self.startDrag(event)
                
        return super().mouseMoveEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.position()
        super().mousePressEvent(event) 

    def startDrag(self, event):
        current_item = self.currentItem()
        if not current_item:
            return
            
        item_data = current_item.data(Qt.UserRole)
        if not item_data:
            return
            
        # Erstelle Drag-Objekt
        drag = QDrag(self)
        mime_data = QMimeData()
        
        # Setze Text (einfacher Fallback)
        mime_data.setText(item_data["name"])
        
        # Setze das spezialisierte Format mit allen Item-Daten
        try:
            json_data = json.dumps(item_data)
            if json_data:
                mime_data.setData(
                    "application/item-data", 
                    json_data.encode("utf-8")
                )
        except Exception as e:
            logger.error(f"JSON serialization error: {e}")
        
        # Icon für Drag-Anzeige
        icon_path = os.path.join("icons", item_data.get("icon", ""))
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            drag.setPixmap(pixmap)
            # Hot spot in der Mitte des Icons
            drag.setHotSpot(QPoint(16, 16))
        
        # Setze MIME-Daten und führe Drag-Operation aus
        drag.setMimeData(mime_data)
        result = drag.exec()  # In PySide6 kann exec oder exec_ verwendet werden


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())