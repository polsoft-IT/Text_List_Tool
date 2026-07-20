"""
Text List Tool / Lista tekstów - polsoft.ITS
PyQt6 rewrite: paste text, 15 editable list items, per-item copy button.
EN/PL language switcher, light/dark (Catppuccin Mocha) theme switcher.

Author: Sebastian Januchowski / polsoft.ITS Group
"""

import json
import os
import re
import sys

from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF, QMimeData
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QPen, QColor, QPolygonF, QCursor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QWidget, QDialog, QLabel, QPushButton, QLineEdit, QTextEdit,
    QFrame, QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox,
    QListWidget, QListWidgetItem, QAbstractItemView, QComboBox, QCheckBox, QMenu,
)

DEFAULT_ITEM_COUNT = 15
MIN_ITEM_COUNT = 1

# --- Language Plugin System ---------------------------------------------
def load_language_plugin():
    """Load language plugin from the same directory if it exists."""
    plugin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lang_plugin.json")
    if os.path.exists(plugin_path):
        try:
            with open(plugin_path, "r", encoding="utf-8") as f:
                plugin_data = json.load(f)
            if "languages" in plugin_data:
                return plugin_data["languages"]
        except (json.JSONDecodeError, OSError):
            pass
    return {}

# Load plugin languages
PLUGIN_LANGUAGES = load_language_plugin()

# --- Base Translations (fallback if plugin not loaded) -----------------
BASE_STRINGS = {
    "en": {
        "window_title": "Text List Tool - polsoft.ITS",
        "title": "Text List ({count} items)",
        "split_btn": "Split into list ⬇",
        "add_item_btn": "Add another position",
        "remove_item_btn": "Remove last position",
        "auto_expand_btn": "Auto-expand",
        "auto_expand_on": "Auto-expand: ON",
        "auto_expand_off": "Auto-expand: OFF",
        "clear_btn": "Clear all",
        "copy_all_btn": "Copy all",
        "copied_all_btn": "Copied all!",
        "copy_btn": "Copy",
        "copied_btn": "Copied!",
        "lang_btn": "PL",
        "lang_tip_en": "Switch to English",
        "lang_tip_pl": "Switch to Polish",
        "theme_tip_dark": "Switch to light theme",
        "theme_tip_light": "Switch to dark theme",
        "ontop_on": "📌 On top",
        "ontop_off": "📌 Normal",
        "compact_btn": "🗕 Compact",
        "compact_hint": "Double-click icon to restore",
        "about_btn": "ℹ About",
        "about_title": "About",
        "status_filled": "{n}/{total} filled",
        "status_saved": "Saved ✓",
        "export_btn": "⬇ Export .txt",
        "import_btn": "⬆ Import .txt",
        "export_dialog_title": "Export list to text file",
        "import_dialog_title": "Import list from text file",
        "file_filter_txt": "Text files (*.txt);;All files (*)",
        "status_exported": "Exported ✓",
        "status_imported": "Imported ✓",
        "export_error_title": "Export error",
        "export_error_msg": "Could not save the file:\n{err}",
        "import_error_title": "Import error",
        "import_error_msg": "Could not read the file:\n{err}",
        "split_mode_newline": "Split by newline",
        "split_mode_comma": "Split by comma",
        "split_mode_semicolon": "Split by semicolon",
        "split_mode_dot": "Split by dot",
        "split_mode_bullet": "Split by bullet (•/-)",
        "split_mode_double_space": "Split by double space",
        "split_mode_regex": "Split by regex",
        "split_mode_label": "Split mode:",
        "split_regex_placeholder": "Regex pattern...",
        "auto_normalize_btn": "Auto-normalize",
        "auto_normalize_on": "Auto-normalize: ON",
        "auto_normalize_off": "Auto-normalize: OFF",
        "auto_normalize_tip": "Auto-trim and normalize text",
        "checklist_btn": "Checklist",
        "checklist_on": "Checklist: ON",
        "checklist_off": "Checklist: OFF",
        "checklist_tip": "Enable checklist mode with checkboxes",
        "context_copy": "Copy",
        "context_delete": "Delete",
        "context_move_up": "Move Up",
        "context_move_down": "Move Down",
        "auto_save_btn": "Auto-save",
        "auto_save_on": "Auto-save: ON",
        "auto_save_off": "Auto-save: OFF",
        "auto_save_tip": "Auto-save every 30 seconds",
        "select_all_btn": "Select All",
        "deselect_all_btn": "Deselect All",
    },
}

# Merge plugin languages with base strings (plugin can add new languages or override existing ones)
STRINGS = {**BASE_STRINGS, **PLUGIN_LANGUAGES}

# --- Themes -------------------------------------------------------------
# "dark" = Catppuccin Mocha (default), "light" = Visual Studio style
THEMES = {
    "dark": {
        "bg": "#1e1e2e",             # base
        "fg": "#cdd6f4",             # text
        "entry_bg": "#181825",       # mantle
        "entry_border": "#45475a",   # surface1
        "accent": "#89b4fa",         # blue
        "accent_fg": "#1e1e2e",
        "accent_dark": "#74a8f5",
        "success": "#a6e3a1",        # green
        "muted": "#a6adc8",          # subtext0
        "btn_neutral": "#313244",    # surface0
        "btn_neutral_hover": "#45475a",
        "danger": "#f38ba8",         # red
    },
    "light": {
        "bg": "#f3f3f3",
        "fg": "#1e1e1e",
        "entry_bg": "#ffffff",
        "entry_border": "#c8c8c8",
        "accent": "#0078d4",
        "accent_fg": "#ffffff",
        "accent_dark": "#005a9e",
        "success": "#107c10",
        "muted": "#6e6e6e",
        "btn_neutral": "#e1e1e1",
        "btn_neutral_hover": "#cfcfcf",
        "danger": "#c42b1c",
    },
}


def get_app_dir():
    """Return the folder next to the script, or next to the .exe when frozen (PyInstaller)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(relative_path):
    """Return path to a bundled resource (icon, etc.), working both in dev
    and inside a PyInstaller onefile .exe (where files are unpacked to _MEIPASS)."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


DATA_PATH = os.path.join(get_app_dir(), "text_list_data.json")
ICON_ICO_PATH = resource_path("icon.ico")

ABOUT_INFO = {
    "author": "Sebastian Januchowski",
    "group": "polsoft.ITS\u2122 Group",
    "github": "https://github.com/polsoft-seb07uk",
    "email": "polsoft.its@mail.com",
    "license": "Freeware",
}


# ---------------------------------------------------------------------
# Vector logo (mirrors icon.ico artwork) - painted with QPainter so it
# stays crisp at any size and can be re-themed instantly.
# ---------------------------------------------------------------------
def make_logo_pixmap(colors, size):
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    s = size / 64.0

    painter = QPainter(pm)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Body (clipboard)
    body_path = QPainterPath()
    body_path.addRoundedRect(QRectF(10 * s, 6 * s, 44 * s, 52 * s), 6 * s, 6 * s)
    painter.fillPath(body_path, QColor(colors["entry_bg"]))
    border_pen = QPen(QColor(colors["entry_border"]))
    border_pen.setWidthF(max(1.0, 2 * s))
    painter.setPen(border_pen)
    painter.drawPath(body_path)

    # Clip
    clip_path = QPainterPath()
    clip_path.addRoundedRect(QRectF(24 * s, 2 * s, 16 * s, 8 * s), 2 * s, 2 * s)
    painter.fillPath(clip_path, QColor(colors["danger"]))

    # Text lines
    line_w = max(2.0, 3 * s)
    pen_fg = QPen(QColor(colors["fg"]))
    pen_fg.setWidthF(line_w)
    pen_fg.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_fg)
    painter.drawLine(QPointF(20 * s, 24 * s), QPointF(44 * s, 24 * s))
    painter.drawLine(QPointF(20 * s, 34 * s), QPointF(44 * s, 34 * s))

    pen_muted = QPen(QColor(colors["muted"]))
    pen_muted.setWidthF(line_w)
    pen_muted.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_muted)
    painter.drawLine(QPointF(20 * s, 44 * s), QPointF(34 * s, 44 * s))

    # Paste-arrow accent
    ax = 46 * s
    arrow = QPolygonF([
        QPointF(ax, 38 * s), QPointF(ax, 46 * s), QPointF(ax - 4 * s, 46 * s),
        QPointF(ax + 2 * s, 54 * s), QPointF(ax + 8 * s, 46 * s),
        QPointF(ax + 4 * s, 46 * s), QPointF(ax + 4 * s, 38 * s),
    ])
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(colors["success"]))
    painter.drawPolygon(arrow)

    painter.end()
    return pm


def build_stylesheet(c):
    """Build the app-wide QSS from the current theme's color dict."""
    return f"""
        QWidget#root {{ background-color: {c['bg']}; }}
        QLabel {{ color: {c['fg']}; background: transparent; }}
        QLabel#titleLabel {{ color: {c['accent']}; font-size: 15px; font-weight: bold; }}
        QLabel#statusLabel {{ color: {c['muted']}; font-size: 11px; }}
        QLabel#statusLabel[state="saved"] {{ color: {c['success']}; }}
        QLabel#numLabel {{ color: {c['muted']}; font-size: 11px; }}

        QFrame#divider1 {{ background-color: {c['accent']}; max-height: 2px; min-height: 2px; border: none; }}
        QFrame#divider2 {{ background-color: {c['entry_border']}; max-height: 1px; min-height: 1px; border: none; }}

        QLineEdit, QTextEdit {{
            background-color: {c['entry_bg']};
            color: {c['fg']};
            border: 1px solid {c['entry_border']};
            border-radius: 4px;
            padding: 4px 6px;
            selection-background-color: {c['accent']};
            selection-color: {c['accent_fg']};
        }}
        QLineEdit:focus, QTextEdit:focus {{
            border: 1px solid {c['accent']};
        }}

        QPushButton {{
            border: none;
            border-radius: 4px;
            padding: 6px 10px;
            font-weight: bold;
        }}
        QPushButton#neutralBtn {{
            background-color: {c['btn_neutral']};
            color: {c['fg']};
        }}
        QPushButton#neutralBtn:hover {{ background-color: {c['btn_neutral_hover']}; }}

        QPushButton#accentBtn, QPushButton#copyBtn {{
            background-color: {c['accent']};
            color: {c['accent_fg']};
        }}
        QPushButton#accentBtn:hover, QPushButton#copyBtn:hover {{ background-color: {c['accent_dark']}; }}
        QPushButton#copyBtn[state="success"] {{ background-color: {c['success']}; }}

        QPushButton#copyAllBtn {{
            background-color: {c['btn_neutral']};
            color: {c['fg']};
        }}
        QPushButton#copyAllBtn:hover {{ background-color: {c['btn_neutral_hover']}; }}
        QPushButton#copyAllBtn[state="success"] {{ background-color: {c['success']}; color: {c['accent_fg']}; }}

        QPushButton#rowClearBtn {{
            background: transparent;
            color: {c['danger']};
            font-weight: bold;
        }}
        QPushButton#rowClearBtn:hover {{ background-color: {c['danger']}; color: {c['bg']}; }}

        QPushButton#ontopBtn {{
            background-color: {c['btn_neutral']};
            color: {c['fg']};
        }}
        QPushButton#ontopBtn:hover {{ background-color: {c['btn_neutral_hover']}; }}
        QPushButton#ontopBtn[active="true"] {{ background-color: {c['accent']}; color: {c['accent_fg']}; }}
        QPushButton#ontopBtn[active="true"]:hover {{ background-color: {c['accent_dark']}; }}

        QPushButton[icon="true"] {{
            font-size: 15px;
            font-weight: normal;
            padding: 4px;
        }}

        QDialog {{ background-color: {c['bg']}; }}
        QLabel#aboutLink {{ color: {c['accent']}; text-decoration: underline; }}
        QLabel#aboutGroup {{ color: {c['muted']}; }}
        QLabel#aboutLicense {{ color: {c['success']}; font-weight: bold; }}
    """


class ClickableLabel(QLabel):
    """A QLabel that copies its assigned text to the clipboard when clicked
    (used for the GitHub/email 'links' in the About dialog)."""

    def __init__(self, text, copy_value, parent=None):
        super().__init__(text, parent)
        self._copy_value = copy_value
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    def mousePressEvent(self, event):
        QApplication.clipboard().setText(self._copy_value)
        super().mousePressEvent(event)


class CompactIcon(QWidget):
    """Small always-on-top floating icon shown while the main window is
    collapsed into compact mode. Draggable; double-click restores the app."""

    def __init__(self, colors, on_restore, hint_text=""):
        super().__init__()
        self._on_restore = on_restore
        self._drag_pos = None
        if hint_text:
            self.setToolTip(hint_text)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        size, pad = 48, 4
        self.setFixedSize(size + pad * 2, size + pad * 2)
        self.setStyleSheet(f"background-color: {colors['accent']}; border-radius: 8px;")

        logo = QLabel(self)
        logo.setPixmap(make_logo_pixmap(colors, size))
        logo.setGeometry(pad, pad, size, size)

        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - size - pad * 2 - 40, 60)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseDoubleClickEvent(self, event):
        self._on_restore()


class TextListApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("root")

        self.lang = "en"          # English as default language
        self.theme_name = "dark"  # Catppuccin Mocha as default theme
        self.always_on_top = False
        self.auto_expand = False
        self.auto_normalize = False  # Auto-trim and normalize text
        self.checklist_mode = False  # Checklist mode with checkboxes
        self.auto_save = False  # Auto-save every 30 seconds
        self.compact_window = None
        self.split_mode = "newline"  # Default split mode
        self.split_regex = ""  # Custom regex pattern

        self.entries = []
        self.copy_buttons = []
        self.row_clear_buttons = []
        self.num_labels = []
        self.checkboxes = []
        self.row_widgets = []
        self.items_list = None

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self.save_data)

        self._status_timer = QTimer(self)
        self._status_timer.setSingleShot(True)
        self._status_timer.timeout.connect(self._revert_status)

        self._auto_save_timer = QTimer(self)
        self._auto_save_timer.setInterval(30000)  # 30 seconds
        self._auto_save_timer.timeout.connect(self.save_data)

        self._load_settings()   # restore lang/theme/always_on_top before building UI
        self._build_ui()
        self._apply_language()
        self._apply_theme()
        self._set_window_icon()
        self.load_data()
        self._update_checklist_visibility()
        self._update_status()

        # Start auto-save timer if enabled
        if self.auto_save:
            self._auto_save_timer.start()

        # Enable drag & drop for external files
        self.setAcceptDrops(True)

        # Setup keyboard shortcuts
        self._setup_shortcuts()

        self.setMinimumSize(720, 700)
        self.resize(720, 650)

    @property
    def colors(self):
        return THEMES[self.theme_name]

    def t(self, key):
        return STRINGS[self.lang][key]

    def _set_window_icon(self):
        if os.path.exists(ICON_ICO_PATH):
            self.setWindowIcon(QIcon(ICON_ICO_PATH))
        else:
            self.setWindowIcon(QIcon(make_logo_pixmap(THEMES["dark"], 64)))

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(15, 15, 15, 15)
        root.setSpacing(0)

        # --- Title row (centered, with vector logo) ---
        title_row = QHBoxLayout()
        title_row.addStretch(1)

        self.logo_label = QLabel()
        self.logo_label.setFixedSize(34, 34)
        title_row.addWidget(self.logo_label)

        self.title_label = QLabel()
        self.title_label.setObjectName("titleLabel")
        title_row.addSpacing(8)
        title_row.addWidget(self.title_label)
        title_row.addStretch(1)
        root.addLayout(title_row)
        root.addSpacing(8)

        # --- Buttons row ---
        top_bar = QHBoxLayout()
        self.about_btn = QPushButton("ℹ")
        self.about_btn.setObjectName("neutralBtn")
        self.about_btn.setProperty("icon", "true")
        self.about_btn.setFixedWidth(32)
        self.about_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.about_btn.clicked.connect(self.show_about)
        top_bar.addWidget(self.about_btn)
        top_bar.addStretch(1)

        self.ontop_btn = QPushButton("📌")
        self.ontop_btn.setObjectName("ontopBtn")
        self.ontop_btn.setProperty("icon", "true")
        self.ontop_btn.setFixedWidth(32)
        self.ontop_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.ontop_btn.clicked.connect(self.toggle_always_on_top)
        top_bar.addWidget(self.ontop_btn)

        self.compact_btn = QPushButton("🗕")
        self.compact_btn.setObjectName("neutralBtn")
        self.compact_btn.setProperty("icon", "true")
        self.compact_btn.setFixedWidth(32)
        self.compact_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.compact_btn.clicked.connect(self.enter_compact_mode)
        top_bar.addWidget(self.compact_btn)

        self.lang_btn = QPushButton("🌐")
        self.lang_btn.setObjectName("neutralBtn")
        self.lang_btn.setProperty("icon", "true")
        self.lang_btn.setFixedWidth(32)
        self.lang_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.lang_btn.clicked.connect(self.toggle_language)
        top_bar.addWidget(self.lang_btn)

        self.theme_btn = QPushButton()
        self.theme_btn.setObjectName("neutralBtn")
        self.theme_btn.setProperty("icon", "true")
        self.theme_btn.setFixedWidth(32)
        self.theme_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.theme_btn.clicked.connect(self.toggle_theme)
        top_bar.addWidget(self.theme_btn)

        root.addLayout(top_bar)
        root.addSpacing(10)

        self.divider1 = QFrame()
        self.divider1.setObjectName("divider1")
        root.addWidget(self.divider1)
        root.addSpacing(10)

        # --- Paste area ---
        paste_row = QHBoxLayout()
        self.bulk_text = QTextEdit()
        self.bulk_text.setFixedHeight(90)
        self.bulk_text.textChanged.connect(self._on_bulk_text_change)
        paste_row.addWidget(self.bulk_text, 1)

        self.split_btn = QPushButton("⬇")
        self.split_btn.setObjectName("accentBtn")
        self.split_btn.setProperty("icon", "true")
        self.split_btn.setFixedWidth(40)
        self.split_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.split_btn.clicked.connect(self.split_to_list)
        paste_row.addWidget(self.split_btn)
        root.addLayout(paste_row)
        root.addSpacing(8)

        # --- Split mode selector ---
        split_mode_row = QHBoxLayout()
        split_mode_label = QLabel()
        split_mode_label.setObjectName("splitModeLabel")
        split_mode_row.addWidget(split_mode_label)

        self.split_mode_combo = QComboBox()
        self.split_mode_combo.setFixedWidth(180)
        self.split_mode_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.split_mode_combo.currentTextChanged.connect(self.on_split_mode_changed)
        split_mode_row.addWidget(self.split_mode_combo)

        self.split_regex_input = QLineEdit()
        self.split_regex_input.setPlaceholderText(self.t("split_regex_placeholder"))
        self.split_regex_input.setFixedWidth(200)
        self.split_regex_input.setVisible(False)
        self.split_regex_input.setText(self.split_regex)
        self.split_regex_input.textChanged.connect(self.on_split_regex_changed)
        split_mode_row.addWidget(self.split_regex_input)

        split_mode_row.addStretch(1)
        root.addLayout(split_mode_row)
        root.addSpacing(10)

        # --- Toolbar ---
        toolbar = QHBoxLayout()
        self.add_item_btn = QPushButton("＋")
        self.add_item_btn.setObjectName("neutralBtn")
        self.add_item_btn.setProperty("icon", "true")
        self.add_item_btn.setFixedWidth(34)
        self.add_item_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.add_item_btn.clicked.connect(self.add_item)
        toolbar.addWidget(self.add_item_btn)

        self.remove_item_btn = QPushButton("−")
        self.remove_item_btn.setObjectName("neutralBtn")
        self.remove_item_btn.setProperty("icon", "true")
        self.remove_item_btn.setFixedWidth(34)
        self.remove_item_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.remove_item_btn.clicked.connect(self.remove_last_item)
        toolbar.addWidget(self.remove_item_btn)

        self.auto_expand_btn = QPushButton("Auto-expand")
        self.auto_expand_btn.setObjectName("neutralBtn")
        self.auto_expand_btn.setFixedWidth(110)
        self.auto_expand_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.auto_expand_btn.clicked.connect(self.toggle_auto_expand)
        toolbar.addWidget(self.auto_expand_btn)

        self.auto_normalize_btn = QPushButton("Auto-normalize")
        self.auto_normalize_btn.setObjectName("neutralBtn")
        self.auto_normalize_btn.setFixedWidth(130)
        self.auto_normalize_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.auto_normalize_btn.clicked.connect(self.toggle_auto_normalize)
        toolbar.addWidget(self.auto_normalize_btn)

        self.checklist_btn = QPushButton("Checklist")
        self.checklist_btn.setObjectName("neutralBtn")
        self.checklist_btn.setFixedWidth(100)
        self.checklist_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.checklist_btn.clicked.connect(self.toggle_checklist_mode)
        toolbar.addWidget(self.checklist_btn)

        self.auto_save_btn = QPushButton("Auto-save")
        self.auto_save_btn.setObjectName("neutralBtn")
        self.auto_save_btn.setFixedWidth(110)
        self.auto_save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.auto_save_btn.clicked.connect(self.toggle_auto_save)
        toolbar.addWidget(self.auto_save_btn)

        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.setObjectName("neutralBtn")
        self.select_all_btn.setFixedWidth(90)
        self.select_all_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.select_all_btn.clicked.connect(self.select_all_checkboxes)
        self.select_all_btn.setVisible(False)  # Only visible in checklist mode
        toolbar.addWidget(self.select_all_btn)

        self.deselect_all_btn = QPushButton("Deselect All")
        self.deselect_all_btn.setObjectName("neutralBtn")
        self.deselect_all_btn.setFixedWidth(110)
        self.deselect_all_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.deselect_all_btn.clicked.connect(self.deselect_all_checkboxes)
        self.deselect_all_btn.setVisible(False)  # Only visible in checklist mode
        toolbar.addWidget(self.deselect_all_btn)

        self.clear_btn = QPushButton("🗑")
        self.clear_btn.setObjectName("neutralBtn")
        self.clear_btn.setProperty("icon", "true")
        self.clear_btn.setFixedWidth(34)
        self.clear_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.clear_btn.clicked.connect(self.clear_all)
        toolbar.addWidget(self.clear_btn)

        self.copy_all_btn = QPushButton("📋")
        self.copy_all_btn.setObjectName("copyAllBtn")
        self.copy_all_btn.setProperty("icon", "true")
        self.copy_all_btn.setFixedWidth(34)
        self.copy_all_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.copy_all_btn.clicked.connect(self.copy_all)
        toolbar.addWidget(self.copy_all_btn)

        self.export_btn = QPushButton("💾")
        self.export_btn.setObjectName("neutralBtn")
        self.export_btn.setProperty("icon", "true")
        self.export_btn.setFixedWidth(34)
        self.export_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.export_btn.clicked.connect(self.export_to_file)
        toolbar.addWidget(self.export_btn)

        self.import_btn = QPushButton("📂")
        self.import_btn.setObjectName("neutralBtn")
        self.import_btn.setProperty("icon", "true")
        self.import_btn.setFixedWidth(34)
        self.import_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.import_btn.clicked.connect(self.import_from_file)
        toolbar.addWidget(self.import_btn)

        toolbar.addStretch(1)

        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")
        toolbar.addWidget(self.status_label)
        root.addLayout(toolbar)
        root.addSpacing(10)

        self.divider2 = QFrame()
        self.divider2.setObjectName("divider2")
        root.addWidget(self.divider2)
        root.addSpacing(12)

        # --- Item list ---
        self.items_list = QListWidget()
        self.items_list.setDragEnabled(True)
        self.items_list.setAcceptDrops(True)
        self.items_list.setDropIndicatorShown(True)
        self.items_list.setDragDropOverwriteMode(False)
        self.items_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.items_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.items_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.items_list.setFrameShape(QFrame.Shape.NoFrame)
        self.items_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.items_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.items_list.setStyleSheet("QListWidget { background: transparent; border: none; padding: 0; }")
        self.items_list.model().rowsMoved.connect(self._rebuild_row_order_from_list_widget)
        root.addWidget(self.items_list)

        for i in range(DEFAULT_ITEM_COUNT):
            self._append_item_row(i)

    def _append_item_row(self, idx):
        row_widget = QWidget()
        row_widget.setObjectName("rowWidget")
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)

        num_label = QLabel(f"{idx + 1}.")
        num_label.setObjectName("numLabel")
        num_label.setFixedWidth(22)
        num_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row_layout.addWidget(num_label)
        self.num_labels.append(num_label)

        checkbox = QCheckBox()
        checkbox.setVisible(False)  # Hidden by default, shown in checklist mode
        checkbox.setFixedWidth(24)
        row_layout.addWidget(checkbox)
        self.checkboxes.append(checkbox)

        entry = QLineEdit()
        entry.textChanged.connect(self._on_entry_change)
        entry.returnPressed.connect(lambda _, row_widget=row_widget: self._focus_next_entry_by_widget(row_widget))
        row_layout.addWidget(entry, 1)
        self.entries.append(entry)

        row_clear_btn = QPushButton("✕")
        row_clear_btn.setObjectName("rowClearBtn")
        row_clear_btn.setFixedWidth(28)
        row_clear_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        row_clear_btn.clicked.connect(lambda checked=False, row_widget=row_widget: self.clear_item_by_widget(row_widget))
        row_layout.addWidget(row_clear_btn)
        self.row_clear_buttons.append(row_clear_btn)

        copy_btn = QPushButton("📋")
        copy_btn.setObjectName("copyBtn")
        copy_btn.setProperty("icon", "true")
        copy_btn.setFixedWidth(30)
        copy_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        copy_btn.clicked.connect(lambda checked=False, row_widget=row_widget: self.copy_item_by_widget(row_widget))
        row_layout.addWidget(copy_btn)
        self.copy_buttons.append(copy_btn)

        row_widget.num_label = num_label
        row_widget.checkbox = checkbox
        row_widget.entry = entry
        row_widget.row_clear_btn = row_clear_btn
        row_widget.copy_btn = copy_btn
        
        # Enable context menu on row widget
        row_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        row_widget.customContextMenuRequested.connect(lambda pos, rw=row_widget: self._show_context_menu(pos, rw))

        item = QListWidgetItem()
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled)
        item.setSizeHint(row_widget.sizeHint())
        self.items_list.addItem(item)
        self.items_list.setItemWidget(item, row_widget)
        self.row_widgets.append(row_widget)

    def _item_count(self):
        return len(self.entries)

    def _set_item_count(self, target_count):
        target_count = max(MIN_ITEM_COUNT, target_count)
        current_count = self._item_count()

        if target_count > current_count:
            for idx in range(current_count, target_count):
                self._append_item_row(idx)
        elif target_count < current_count:
            for _ in range(current_count - target_count):
                self._remove_last_item_row()

        self._refresh_row_numbers()
        self._update_title()
        self._update_status()
        self.resize(self.sizeHint())

    def _remove_last_item_row(self):
        if self._item_count() <= MIN_ITEM_COUNT:
            return

        row_widget = self.row_widgets.pop()
        self.items_list.takeItem(self.items_list.count() - 1)
        self.num_labels.pop().deleteLater()
        self.entries.pop().deleteLater()
        self.row_clear_buttons.pop().deleteLater()
        self.copy_buttons.pop().deleteLater()
        row_widget.deleteLater()

    def _refresh_row_numbers(self):
        for idx, label in enumerate(self.num_labels):
            label.setText(f"{idx + 1}.")

    def _rebuild_row_order_from_list_widget(self):
        ordered_row_widgets = []
        for index in range(self.items_list.count()):
            item = self.items_list.item(index)
            row_widget = self.items_list.itemWidget(item)
            if row_widget is not None:
                ordered_row_widgets.append(row_widget)

        self.row_widgets = ordered_row_widgets
        self.entries = [row_widget.entry for row_widget in ordered_row_widgets]
        self.num_labels = [row_widget.num_label for row_widget in ordered_row_widgets]
        self.checkboxes = [row_widget.checkbox for row_widget in ordered_row_widgets]
        self.row_clear_buttons = [row_widget.row_clear_btn for row_widget in ordered_row_widgets]
        self.copy_buttons = [row_widget.copy_btn for row_widget in ordered_row_widgets]
        self._refresh_row_numbers()
        self._update_status()
        self.save_data()

    def add_item(self):
        self._set_item_count(self._item_count() + 1)
        self.save_data()

    def remove_last_item(self):
        self._set_item_count(self._item_count() - 1)
        self.save_data()

    def toggle_auto_expand(self):
        self.auto_expand = not self.auto_expand
        self._apply_language()
        self.save_data()

    def toggle_auto_normalize(self):
        self.auto_normalize = not self.auto_normalize
        self._apply_language()
        self.save_data()

    def toggle_checklist_mode(self):
        self.checklist_mode = not self.checklist_mode
        self._apply_language()
        self._update_checklist_visibility()
        self.save_data()

    def toggle_auto_save(self):
        self.auto_save = not self.auto_save
        if self.auto_save:
            self._auto_save_timer.start()
        else:
            self._auto_save_timer.stop()
        self._apply_language()
        self.save_data()

    def _update_checklist_visibility(self):
        """Show or hide checkboxes based on checklist_mode."""
        for checkbox in self.checkboxes:
            checkbox.setVisible(self.checklist_mode)
        # Show/hide select all/none buttons
        self.select_all_btn.setVisible(self.checklist_mode)
        self.deselect_all_btn.setVisible(self.checklist_mode)

    def select_all_checkboxes(self):
        """Select all checkboxes."""
        for checkbox in self.checkboxes:
            checkbox.setChecked(True)
        self.save_data()

    def deselect_all_checkboxes(self):
        """Deselect all checkboxes."""
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)
        self.save_data()

    def _show_context_menu(self, pos, row_widget):
        """Show context menu for a row widget."""
        idx = self._row_widget_index(row_widget)
        
        menu = QMenu(self)
        
        copy_action = menu.addAction(self.t("context_copy"))
        delete_action = menu.addAction(self.t("context_delete"))
        menu.addSeparator()
        move_up_action = menu.addAction(self.t("context_move_up"))
        move_down_action = menu.addAction(self.t("context_move_down"))
        
        # Disable move actions if at boundaries
        move_up_action.setEnabled(idx > 0)
        move_down_action.setEnabled(idx < self._item_count() - 1)
        
        action = menu.exec(row_widget.mapToGlobal(pos))
        
        if action == copy_action:
            self.copy_item_by_widget(row_widget)
        elif action == delete_action:
            self.clear_item_by_widget(row_widget)
        elif action == move_up_action:
            self._move_row_up(idx)
        elif action == move_down_action:
            self._move_row_down(idx)

    def _move_row_up(self, idx):
        """Move a row up by one position."""
        if idx <= 0:
            return
        # Swap entries
        self.entries[idx], self.entries[idx - 1] = self.entries[idx - 1], self.entries[idx]
        self.checkboxes[idx], self.checkboxes[idx - 1] = self.checkboxes[idx - 1], self.checkboxes[idx]
        self.num_labels[idx], self.num_labels[idx - 1] = self.num_labels[idx - 1], self.num_labels[idx]
        self.row_clear_buttons[idx], self.row_clear_buttons[idx - 1] = self.row_clear_buttons[idx - 1], self.row_clear_buttons[idx]
        self.copy_buttons[idx], self.copy_buttons[idx - 1] = self.copy_buttons[idx - 1], self.copy_buttons[idx]
        self.row_widgets[idx], self.row_widgets[idx - 1] = self.row_widgets[idx - 1], self.row_widgets[idx]
        self._refresh_row_numbers()
        self.save_data()

    def _move_row_down(self, idx):
        """Move a row down by one position."""
        if idx >= self._item_count() - 1:
            return
        # Swap entries
        self.entries[idx], self.entries[idx + 1] = self.entries[idx + 1], self.entries[idx]
        self.checkboxes[idx], self.checkboxes[idx + 1] = self.checkboxes[idx + 1], self.checkboxes[idx]
        self.num_labels[idx], self.num_labels[idx + 1] = self.num_labels[idx + 1], self.num_labels[idx]
        self.row_clear_buttons[idx], self.row_clear_buttons[idx + 1] = self.row_clear_buttons[idx + 1], self.row_clear_buttons[idx]
        self.copy_buttons[idx], self.copy_buttons[idx + 1] = self.copy_buttons[idx + 1], self.copy_buttons[idx]
        self.row_widgets[idx], self.row_widgets[idx + 1] = self.row_widgets[idx + 1], self.row_widgets[idx]
        self._refresh_row_numbers()
        self.save_data()

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Ctrl+S - Save
        save_shortcut = QShortcut(QKeySequence.StandardKey.Save, self)
        save_shortcut.activated.connect(self.save_data)
        
        # Ctrl+N - Add new item
        new_item_shortcut = QShortcut(QKeySequence.StandardKey.New, self)
        new_item_shortcut.activated.connect(self.add_item)
        
        # Ctrl+C - Copy all (when no entry is focused)
        copy_all_shortcut = QShortcut(QKeySequence.StandardKey.Copy, self)
        copy_all_shortcut.activated.connect(self.copy_all)
        
        # Ctrl+Delete - Clear all
        clear_shortcut = QShortcut(QKeySequence("Ctrl+Delete"), self)
        clear_shortcut.activated.connect(self.clear_all)

    def normalize_text(self, text):
        """Normalize text by removing double spaces, empty lines, tabs, and trimming whitespace."""
        # Replace tabs with spaces
        text = text.replace("\t", " ")
        # Remove double spaces
        while "  " in text:
            text = text.replace("  ", " ")
        # Split into lines, trim each, and remove empty lines
        lines = [line.strip() for line in text.split("\n") if line.strip() != ""]
        return "\n".join(lines)

    def _on_bulk_text_change(self):
        """Auto-normalize text when auto_normalize is enabled."""
        if self.auto_normalize:
            text = self.bulk_text.toPlainText()
            normalized = self.normalize_text(text)
            if normalized != text:
                # Block signals to prevent recursive calls
                self.bulk_text.blockSignals(True)
                self.bulk_text.setPlainText(normalized)
                self.bulk_text.blockSignals(False)

    def _focus_next_entry(self, idx):
        if idx + 1 < self._item_count():
            self.entries[idx + 1].setFocus()
            self.entries[idx + 1].selectAll()

    def _focus_next_entry_by_widget(self, row_widget):
        self._focus_next_entry(self._row_widget_index(row_widget))

    def _row_widget_index(self, row_widget):
        return self.row_widgets.index(row_widget)

    def on_split_mode_changed(self, text):
        self.split_mode = self.split_mode_combo.currentData()
        self.split_regex_input.setVisible(self.split_mode == "regex")
        self.save_data()

    def on_split_regex_changed(self, text):
        self.split_regex = text
        self.save_data()

    def dragEnterEvent(self, event):
        """Accept drag events if they contain file URLs."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle dropped files - read text files and populate bulk_text."""
        urls = event.mimeData().urls()
        if not urls:
            return
        
        for url in urls:
            file_path = url.toLocalFile()
            if not file_path:
                continue
            
            # Check if it's a text file
            text_extensions = ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv']
            if any(file_path.lower().endswith(ext) for ext in text_extensions):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # Block signals to prevent auto-normalization during load
                    self.bulk_text.blockSignals(True)
                    self.bulk_text.setPlainText(content)
                    self.bulk_text.blockSignals(False)
                    self.status_label.setText(self.t("status_imported"))
                    self.status_label.setProperty("state", "saved")
                    self.status_label.style().unpolish(self.status_label)
                    self.status_label.style().polish(self.status_label)
                    self._status_timer.start(1200)
                    break  # Only load first text file
                except (OSError, UnicodeDecodeError) as err:
                    QMessageBox.warning(
                        self, self.t("import_error_title"), 
                        self.t("import_error_msg").format(err=err)
                    )
        
        event.acceptProposedAction()

    # ------------------------------------------------------------------
    # Language / theme
    # ------------------------------------------------------------------
    def _apply_language(self):
        self.setWindowTitle(self.t("window_title"))
        self.title_label.setText(self.t("title"))
        self.lang_btn.setToolTip(self.t("lang_tip_pl") if self.lang == "en" else self.t("lang_tip_en"))
        self.split_btn.setToolTip(self.t("split_btn"))
        self.clear_btn.setToolTip(self.t("clear_btn"))
        self.copy_all_btn.setToolTip(self.t("copy_all_btn"))
        self.export_btn.setToolTip(self.t("export_btn"))
        self.import_btn.setToolTip(self.t("import_btn"))
        self.ontop_btn.setToolTip(self.t("ontop_on") if self.always_on_top else self.t("ontop_off"))
        self.compact_btn.setToolTip(self.t("compact_btn"))
        self.about_btn.setToolTip(self.t("about_btn"))
        self.add_item_btn.setToolTip(self.t("add_item_btn"))
        self.remove_item_btn.setToolTip(self.t("remove_item_btn"))
        self.auto_expand_btn.setText(self.t("auto_expand_on") if self.auto_expand else self.t("auto_expand_off"))
        self.auto_expand_btn.setToolTip(self.t("auto_expand_btn"))
        self.auto_normalize_btn.setText(self.t("auto_normalize_on") if self.auto_normalize else self.t("auto_normalize_off"))
        self.auto_normalize_btn.setToolTip(self.t("auto_normalize_tip"))
        self.checklist_btn.setText(self.t("checklist_on") if self.checklist_mode else self.t("checklist_off"))
        self.checklist_btn.setToolTip(self.t("checklist_tip"))
        self.auto_save_btn.setText(self.t("auto_save_on") if self.auto_save else self.t("auto_save_off"))
        self.auto_save_btn.setToolTip(self.t("auto_save_tip"))
        self.select_all_btn.setText(self.t("select_all_btn"))
        self.deselect_all_btn.setText(self.t("deselect_all_btn"))
        for btn in self.copy_buttons:
            btn.setToolTip(self.t("copy_btn"))
        
        # Update split mode UI
        split_mode_label = self.findChild(QLabel, "splitModeLabel")
        if split_mode_label:
            split_mode_label.setText(self.t("split_mode_label"))
        
        # Populate split mode combobox
        current_index = self.split_mode_combo.currentIndex()
        self.split_mode_combo.clear()
        self.split_mode_combo.addItem(self.t("split_mode_newline"), "newline")
        self.split_mode_combo.addItem(self.t("split_mode_comma"), "comma")
        self.split_mode_combo.addItem(self.t("split_mode_semicolon"), "semicolon")
        self.split_mode_combo.addItem(self.t("split_mode_dot"), "dot")
        self.split_mode_combo.addItem(self.t("split_mode_bullet"), "bullet")
        self.split_mode_combo.addItem(self.t("split_mode_double_space"), "double_space")
        self.split_mode_combo.addItem(self.t("split_mode_regex"), "regex")
        
        # Restore current selection
        for i in range(self.split_mode_combo.count()):
            if self.split_mode_combo.itemData(i) == self.split_mode:
                self.split_mode_combo.setCurrentIndex(i)
                break
        
        self.split_regex_input.setPlaceholderText(self.t("split_regex_placeholder"))
        self.split_regex_input.setVisible(self.split_mode == "regex")
        
        self._update_title()
        self._update_status()

    def toggle_language(self):
        """Cycle through available languages including plugin languages."""
        available_langs = list(STRINGS.keys())
        if not available_langs:
            return
        
        current_idx = available_langs.index(self.lang) if self.lang in available_langs else 0
        next_idx = (current_idx + 1) % len(available_langs)
        self.lang = available_langs[next_idx]
        self._apply_language()
        self.save_data()

    def _update_title(self):
        self.title_label.setText(self.t("title").format(count=self._item_count()))

    def _apply_theme(self):
        c = self.colors
        self.setStyleSheet(build_stylesheet(c))
        self.logo_label.setPixmap(make_logo_pixmap(c, 34))
        self.theme_btn.setText("☾" if self.theme_name == "dark" else "☀")
        self.theme_btn.setToolTip(self.t("theme_tip_light") if self.theme_name == "dark" else self.t("theme_tip_dark"))

    def toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self._apply_theme()
        self.save_data()

    def toggle_always_on_top(self):
        self.always_on_top = not self.always_on_top
        self.ontop_btn.setToolTip(self.t("ontop_on") if self.always_on_top else self.t("ontop_off"))
        self.ontop_btn.setProperty("active", "true" if self.always_on_top else "false")
        self.ontop_btn.style().unpolish(self.ontop_btn)
        self.ontop_btn.style().polish(self.ontop_btn)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, self.always_on_top)
        self.show()  # re-apply window flags (Qt requires re-showing the window)
        self.save_data()

    def enter_compact_mode(self):
        self.hide()

        def restore():
            self.compact_window.close()
            self.compact_window = None
            self.show()
            self.raise_()
            self.activateWindow()

        self.compact_window = CompactIcon(self.colors, restore, self.t("compact_hint"))
        self.compact_window.show()

    def show_about(self):
        c = self.colors
        dlg = QDialog(self)
        dlg.setWindowTitle(self.t("about_title"))
        dlg.setStyleSheet(build_stylesheet(c))
        dlg.setFixedSize(260, 260)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        logo = QLabel()
        logo.setPixmap(make_logo_pixmap(c, 56))
        logo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(logo)
        layout.addSpacing(8)

        author = QLabel(ABOUT_INFO["author"])
        author.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        author.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(author)

        group = QLabel(ABOUT_INFO["group"])
        group.setObjectName("aboutGroup")
        group.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(group)
        layout.addSpacing(8)

        github = ClickableLabel(ABOUT_INFO["github"], ABOUT_INFO["github"])
        github.setObjectName("aboutLink")
        github.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(github)

        email = ClickableLabel(ABOUT_INFO["email"], ABOUT_INFO["email"])
        email.setObjectName("aboutLink")
        email.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(email)
        layout.addSpacing(8)

        license_label = QLabel(ABOUT_INFO["license"])
        license_label.setObjectName("aboutLicense")
        license_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(license_label)
        layout.addSpacing(10)

        close_btn = QPushButton("OK")
        close_btn.setObjectName("accentBtn")
        close_btn.setFixedWidth(100)
        close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        dlg.exec()

    # ------------------------------------------------------------------
    # Core actions
    # ------------------------------------------------------------------
    def split_to_list(self):
        text = self.bulk_text.toPlainText()
        
        # Split based on selected mode
        if self.split_mode == "newline":
            lines = [ln.strip() for ln in text.split("\n") if ln.strip() != ""]
        elif self.split_mode == "comma":
            lines = [ln.strip() for ln in text.split(",") if ln.strip() != ""]
        elif self.split_mode == "semicolon":
            lines = [ln.strip() for ln in text.split(";") if ln.strip() != ""]
        elif self.split_mode == "dot":
            lines = [ln.strip() for ln in text.split(".") if ln.strip() != ""]
        elif self.split_mode == "bullet":
            # Split by • or - followed by space
            lines = [ln.strip() for ln in re.split(r'[•\-]\s+', text) if ln.strip() != ""]
        elif self.split_mode == "double_space":
            lines = [ln.strip() for ln in text.split("  ") if ln.strip() != ""]
        elif self.split_mode == "regex":
            if self.split_regex:
                try:
                    lines = [ln.strip() for ln in re.split(self.split_regex, text) if ln.strip() != ""]
                except re.error:
                    lines = [ln.strip() for ln in text.split("\n") if ln.strip() != ""]
            else:
                lines = [ln.strip() for ln in text.split("\n") if ln.strip() != ""]
        else:
            lines = [ln.strip() for ln in text.split("\n") if ln.strip() != ""]
        
        if self.auto_expand and len(lines) > self._item_count():
            self._set_item_count(len(lines))
        for i in range(self._item_count()):
            self.entries[i].blockSignals(True)
            self.entries[i].setText(lines[i] if i < len(lines) else "")
            self.entries[i].blockSignals(False)
        self._update_status()
        self.save_data()

    def copy_item(self, idx):
        value = self.entries[idx].text()
        if not value:
            return
        QApplication.clipboard().setText(value)

        btn = self.copy_buttons[idx]
        btn.setText("✓")
        btn.setToolTip(self.t("copied_btn"))
        btn.setProperty("state", "success")
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        QTimer.singleShot(1000, lambda: self._restore_copy_btn(idx))

    def copy_item_by_widget(self, row_widget):
        self.copy_item(self._row_widget_index(row_widget))

    def _restore_copy_btn(self, idx):
        btn = self.copy_buttons[idx]
        btn.setText("📋")
        btn.setToolTip(self.t("copy_btn"))
        btn.setProperty("state", "")
        btn.style().unpolish(btn)
        btn.style().polish(btn)

    def copy_all(self):
        values = [e.text() for e in self.entries if e.text().strip() != ""]
        if not values:
            return
        QApplication.clipboard().setText("\n".join(values))

        self.copy_all_btn.setText("✓")
        self.copy_all_btn.setToolTip(self.t("copied_all_btn"))
        self.copy_all_btn.setProperty("state", "success")
        self.copy_all_btn.style().unpolish(self.copy_all_btn)
        self.copy_all_btn.style().polish(self.copy_all_btn)
        QTimer.singleShot(1000, self._restore_copy_all_btn)

    def _restore_copy_all_btn(self):
        self.copy_all_btn.setText("📋")
        self.copy_all_btn.setToolTip(self.t("copy_all_btn"))
        self.copy_all_btn.setProperty("state", "")
        self.copy_all_btn.style().unpolish(self.copy_all_btn)
        self.copy_all_btn.style().polish(self.copy_all_btn)

    def clear_item(self, idx):
        self.entries[idx].clear()
        self._update_status()
        self.save_data()

    def clear_item_by_widget(self, row_widget):
        self.clear_item(self._row_widget_index(row_widget))

    def clear_all(self):
        self.bulk_text.clear()
        for entry in self.entries:
            entry.clear()
        self._update_status()
        self.save_data()

    def export_to_file(self):
        values = [e.text() for e in self.entries if e.text().strip() != ""]
        if not values:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, self.t("export_dialog_title"), "lista.txt", self.t("file_filter_txt")
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                if self.checklist_mode:
                    # Export with checklist format [ ] or [x]
                    for i, entry in enumerate(self.entries):
                        text = entry.text().strip()
                        if text:
                            checkbox = self.checkboxes[i] if i < len(self.checkboxes) else None
                            checked = checkbox.isChecked() if checkbox else False
                            prefix = "[x]" if checked else "[ ]"
                            f.write(f"{prefix} {text}\n")
                else:
                    # Normal export
                    f.write("\n".join(values))
            self.status_label.setText(self.t("status_exported"))
            self.status_label.setProperty("state", "saved")
            self.status_label.style().unpolish(self.status_label)
            self.status_label.style().polish(self.status_label)
            self._status_timer.start(1500)
        except OSError as err:
            QMessageBox.critical(
                self, self.t("export_error_title"), self.t("export_error_msg").format(err=err)
            )

    def import_from_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, self.t("import_dialog_title"), "", self.t("file_filter_txt")
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = [ln.strip() for ln in f.read().split("\n") if ln.strip() != ""]
        except OSError as err:
            QMessageBox.critical(
                self, self.t("import_error_title"), self.t("import_error_msg").format(err=err)
            )
            return

        if self.auto_expand and len(lines) > self._item_count():
            self._set_item_count(len(lines))
        for i in range(self._item_count()):
            self.entries[i].blockSignals(True)
            self.entries[i].setText(lines[i] if i < len(lines) else "")
            self.entries[i].blockSignals(False)
        self._update_status()
        self.save_data()
        self.status_label.setText(self.t("status_imported"))
        self.status_label.setProperty("state", "saved")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self._status_timer.start(1500)

    def _update_status(self):
        n = sum(1 for e in self.entries if e.text().strip() != "")
        self.status_label.setProperty("state", "")
        self.status_label.setText(self.t("status_filled").format(n=n, total=self._item_count()))
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def _flash_saved_status(self):
        self.status_label.setText(self.t("status_saved"))
        self.status_label.setProperty("state", "saved")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self._status_timer.start(1200)

    def _revert_status(self):
        self._update_status()

    # ------------------------------------------------------------------
    # Persistence: remember list contents + settings across restarts
    # ------------------------------------------------------------------
    def _load_settings(self):
        """Load lang/theme/always_on_top before the UI is built, so the
        window opens directly in the user's last-used language & theme."""
        if not os.path.exists(DATA_PATH):
            return
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("lang") in STRINGS:
                self.lang = data["lang"]
            if data.get("theme") in THEMES:
                self.theme_name = data["theme"]
            self.always_on_top = bool(data.get("always_on_top", False))
            self.auto_expand = bool(data.get("auto_expand", False))
            self.auto_normalize = bool(data.get("auto_normalize", False))
            self.checklist_mode = bool(data.get("checklist_mode", False))
            self.auto_save = bool(data.get("auto_save", False))
            self.split_mode = data.get("split_mode", "newline")
            self.split_regex = data.get("split_regex", "")
        except (json.JSONDecodeError, OSError, ValueError):
            pass  # corrupted or unreadable file - start fresh, don't crash

    def load_data(self):
        if self.always_on_top:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        if not os.path.exists(DATA_PATH):
            return
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data.get("items", [])
            if len(items) > self._item_count():
                self._set_item_count(len(items))
            for i in range(min(self._item_count(), len(items))):
                self.entries[i].blockSignals(True)
                self.entries[i].setText(items[i])
                self.entries[i].blockSignals(False)
        except (json.JSONDecodeError, OSError, ValueError):
            pass  # corrupted or unreadable file - start fresh, don't crash

    def save_data(self):
        items = [entry.text() for entry in self.entries]
        payload = {
            "items": items,
            "lang": self.lang,
            "theme": self.theme_name,
            "always_on_top": self.always_on_top,
            "auto_expand": self.auto_expand,
            "auto_normalize": self.auto_normalize,
            "checklist_mode": self.checklist_mode,
            "auto_save": self.auto_save,
            "split_mode": self.split_mode,
            "split_regex": self.split_regex,
        }
        try:
            with open(DATA_PATH, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            self._flash_saved_status()
        except OSError:
            pass  # if the folder isn't writable, silently skip saving

    def _on_entry_change(self, _text=None):
        self._update_status()
        self._save_timer.start(400)  # debounce: write 400ms after the last keystroke

    def closeEvent(self, event):
        self.save_data()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    window = TextListApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
