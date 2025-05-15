from gui.enchantment_dialog import EnchantmentDialog
from PySide6.QtWidgets import QLabel, QGridLayout, QWidget, QApplication
from PySide6.QtCore import Qt, QMimeData, QPoint
from PySide6.QtGui import QPixmap, QDrag, QPainter, QColor, QPen
import json
import logging
import os

logger = logging.getLogger(__name__)

class InventoryGrid(QWidget):
    def __init__(self, slot_restrictions=None):
        super().__init__()
        # Standardwert für slot_restrictions falls nicht angegeben
        self.slot_restrictions = slot_restrictions or {}
        self.slots = []
        self.mc_slot_map = self.create_slot_mapping()
        self.init_ui()

    def create_slot_mapping(self):
        # Dictionary für die Zuordnung von GUI-Slot-IDs zu Minecraft-Slot-IDs
        return {gui_slot: mc_slot for mc_slot, gui_slot in enumerate(range(27))}

    def init_ui(self):
        self.layout = QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.create_slots()
        self.setLayout(self.layout)

    def create_slots(self):
        for row in range(3):
            for col in range(9):
                slot = InventorySlot(row * 9 + col)
                slot.setFixedSize(36, 36)
                self.slots.append(slot)
                self.layout.addWidget(slot, row, col)

    def get_export_data(self):
        export_data = []
        for slot in self.slots:
            if not slot.item_data:
                continue
                
            if not self.is_valid_placement(slot.item_data.get("name", ""), slot.slot_id):
                continue
                
            try:
                export_data.append({
                    "slot": self.mc_slot_map[slot.slot_id],
                    "id": slot.item_data["id"],
                    "name": slot.item_data["name"],
                    "count": slot.item_data.get("count", 1)
                })
            except Exception as e:
                logger.error(f"Error exporting slot {slot.slot_id}: {e}")
                
        return export_data

    def is_valid_placement(self, item_name, slot_id):
        # Immer True zurückgeben, wenn slot_restrictions leer ist oder der Name nicht gefunden wird
        if not self.slot_restrictions or item_name not in self.slot_restrictions:
            return True
        return "inventory" in self.slot_restrictions.get(item_name, ["inventory"])

    def clear_all(self):
        for slot in self.slots:
            slot.clear_item()

    def add_item_to_first_valid_slot(self, item_data):
        if not item_data:
            return
            
        item_name = item_data.get("name", "")
        for slot in self.slots:
            if slot.is_empty() and self.is_valid_placement(item_name, slot.slot_id):
                slot.set_item(item_data)
                break

class InventorySlot(QLabel):
    def __init__(self, slot_id):
        super().__init__()
        self.slot_id = slot_id
        self.item_data = None
        self.highlight_color = QColor(255, 255, 255, 30)
        self.invalid_color = QColor(255, 0, 0, 30)
        self.highlight = False
        self.init_ui()

    def init_ui(self):
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.update_style()

    def update_style(self, valid=True):
        color = "#8B8B8B" if valid else "#6B3A3A"
        self.setStyleSheet(f"""
            background: {color};
            border: 1px solid #5A5A5A;
            margin: 0px;
            padding: 0px;
        """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/item-data"):
            try:
                item_data = json.loads(event.mimeData().data("application/item-data").data().decode())
                # Überprüfen, ob parent() den slot_restrictions hat und ob valid ist
                valid = True
                parent_widget = self.parent()
                
                if parent_widget and hasattr(parent_widget, "slot_restrictions"):
                    item_name = item_data.get("name", "")
                    if item_name in parent_widget.slot_restrictions:
                        valid = "inventory" in parent_widget.slot_restrictions.get(item_name, ["inventory"])
                
                self.set_highlight(valid)
                if valid:
                    event.accept()
                else:
                    event.ignore()
            except Exception as e:
                logger.error(f"Drag error: {str(e)}")
                event.ignore()
        else:
            # Akzeptiere auch Text-Format (für einfache Kompatibilität)
            if event.mimeData().hasText():
                self.set_highlight(True)
                event.accept()
            else:
                event.ignore()

    def dragLeaveEvent(self, event):
        self.set_highlight(False)

    def dropEvent(self, event):
        self.set_highlight(False)
        try:
            # Versuche zuerst das spezifische Format
            if event.mimeData().hasFormat("application/item-data"):
                item_data = json.loads(event.mimeData().data("application/item-data").data().decode())
                
                # Prüfe Platzierungsregeln
                valid = True
                parent_widget = self.parent()
                
                if parent_widget and hasattr(parent_widget, "slot_restrictions") and parent_widget.slot_restrictions:
                    item_name = item_data.get("name", "")
                    if item_name in parent_widget.slot_restrictions:
                        valid = "inventory" in parent_widget.slot_restrictions.get(item_name, [])
                
                if valid:
                    self.set_item(item_data)
                    event.accept()
                else:
                    event.ignore()
                    self.show_error_indicator()
            # Fallback für Text-Format
            elif event.mimeData().hasText():
                item_name = event.mimeData().text()
                main_window = None
                
                # Versuche, zum MainWindow zu navigieren
                current = self
                while current:
                    if hasattr(current, "items_db"):
                        main_window = current
                        break
                    current = current.parent()
                
                # Versuche, Item aus der items_db zu bekommen
                if main_window and hasattr(main_window, "items_db") and item_name in main_window.items_db:
                    self.set_item(main_window.items_db[item_name])
                    event.accept()
                else:
                    # Minimales Item-Objekt erstellen
                    self.set_item({
                        "name": item_name,
                        "id": f"minecraft:{item_name.lower().replace(' ', '_')}",
                        "icon": f"{item_name.lower().replace(' ', '_')}.png",
                        "count": 1
                    })
                    event.accept()
            else:
                event.ignore()
        except Exception as e:
            logger.error(f"Drop failed: {str(e)}")
            event.ignore()

    def set_item(self, item_data):
        self.item_data = item_data
        try:
            self.setPixmap(self.load_icon())
            self.update_style()
        except Exception as e:
            logger.error(f"Set item error: {str(e)}")

    def load_icon(self):
        try:
            if not self.item_data:
                return QPixmap()
                
            icon_path = os.path.join("icons", self.item_data.get("icon", ""))
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
            else:
                # Fallback-Icon verwenden oder ein leeres Pixmap erstellen
                pixmap = QPixmap(32, 32)
                pixmap.fill(Qt.transparent)
            return pixmap.scaled(34, 34, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        except Exception as e:
            logger.error(f"Icon error: {str(e)}")
            return QPixmap()

    def clear_item(self):
        self.item_data = None
        self.clear()
        self.update_style()

    def set_highlight(self, state):
        self.highlight = state
        self.update()

    def show_error_indicator(self):
        self.update_style(False)
        self.repaint()

    def paintEvent(self, event):
        super().paintEvent(event)
        
        try:
            painter = QPainter(self)
            
            if self.highlight:
                painter.fillRect(self.rect(), self.highlight_color)
            
            if self.item_data:
                self.draw_stack_size(painter)
        except Exception as e:
            logger.error(f"Paint error: {str(e)}")

    def draw_stack_size(self, painter):
        if not self.item_data:
            return
            
        try:
            count = str(self.item_data.get("count", 1))
            painter.setPen(QPen(Qt.white))
            painter.drawText(
                self.rect().adjusted(2, 2, -2, -2),
                Qt.AlignBottom | Qt.AlignRight,
                count
            )
        except Exception as e:
            logger.error(f"Draw stack size error: {str(e)}")

    def mousePressEvent(self, event):
        if self.item_data and event.button() == Qt.LeftButton:
            self.start_drag(event)
        else:
            super().mousePressEvent(event)

    def start_drag(self, widget, point):
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

def edit_item_enchantments(self, item_data):
    """Edit enchantments for a selected item."""
    dialog = EnchantmentDialog(self, item_data)
    if dialog.exec_():
        return dialog.item_data
    return item_data