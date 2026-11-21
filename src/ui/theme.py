"""Design tokens and QSS stylesheet for the PDF Toolkit UI.

Single dark theme tuned for a professional desktop look. Keep tokens in sync
with the stylesheet below when changing any color.
"""

# ---- Design tokens ----
BG_0 = "#0f1115"        # window background
BG_1 = "#161922"        # elevated surfaces / cards
BG_2 = "#1d2130"        # inputs / list rows
BG_3 = "#262b3c"        # hovered rows
BORDER = "#2a2f42"
BORDER_STRONG = "#363c52"

TEXT = "#e7eaf3"
TEXT_MUTED = "#9aa1b2"
TEXT_FAINT = "#6b7284"

ACCENT = "#5b8cff"       # primary brand
ACCENT_HOVER = "#7aa0ff"
ACCENT_PRESSED = "#4877e6"
ACCENT_SOFT = "#223055"  # low-emphasis accent background

DANGER = "#e5484d"
SUCCESS = "#30a46c"
WARN = "#e5a23d"

RADIUS = 8
RADIUS_SM = 6


STYLESHEET = f"""
/* ---------- Base ---------- */
* {{
    font-family: "Segoe UI", "Inter", "SF Pro Text", sans-serif;
    font-size: 13px;
    color: {TEXT};
}}
QMainWindow, QWidget {{
    background: {BG_0};
}}
QToolTip {{
    background: {BG_2};
    color: {TEXT};
    border: 1px solid {BORDER};
    padding: 6px 8px;
    border-radius: {RADIUS_SM}px;
}}

/* ---------- Sidebar ---------- */
QListWidget#Sidebar {{
    background: {BG_1};
    border: none;
    border-right: 1px solid {BORDER};
    padding: 8px 6px;
    outline: 0;
}}
QListWidget#Sidebar::item {{
    padding: 10px 12px;
    margin: 2px 4px;
    border-radius: {RADIUS}px;
    color: {TEXT_MUTED};
}}
QListWidget#Sidebar::item:hover {{
    background: {BG_2};
    color: {TEXT};
}}
QListWidget#Sidebar::item:selected {{
    background: {ACCENT_SOFT};
    color: {TEXT};
    border-left: 3px solid {ACCENT};
    padding-left: 9px;
}}

QLabel#SidebarTitle {{
    color: {TEXT};
    font-size: 16px;
    font-weight: 600;
    padding: 14px 14px 4px 14px;
}}
QLabel#SidebarSubtitle {{
    color: {TEXT_FAINT};
    font-size: 11px;
    padding: 0 14px 10px 14px;
}}
QLabel#SidebarSection {{
    color: {TEXT_FAINT};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 12px 14px 4px 14px;
}}

/* ---------- Header bar ---------- */
QFrame#Header {{
    background: {BG_1};
    border-bottom: 1px solid {BORDER};
    min-height: 56px;
    max-height: 56px;
}}
QLabel#HeaderTitle {{
    color: {TEXT};
    font-size: 15px;
    font-weight: 600;
}}
QLabel#HeaderSubtitle {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}

/* ---------- Cards ---------- */
QFrame.Card {{
    background: {BG_1};
    border: 1px solid {BORDER};
    border-radius: {RADIUS}px;
}}
QLabel.CardTitle {{
    color: {TEXT};
    font-size: 15px;
    font-weight: 600;
}}
QLabel.CardDescription {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}
QLabel.FieldLabel {{
    color: {TEXT_MUTED};
    font-size: 12px;
    font-weight: 500;
}}
QLabel.Hint {{
    color: {TEXT_FAINT};
    font-size: 11px;
}}

/* ---------- Inputs ---------- */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {{
    background: {BG_2};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    padding: 7px 10px;
    color: {TEXT};
    selection-background-color: {ACCENT};
    selection-color: white;
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {ACCENT};
}}
QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {{
    color: {TEXT_FAINT};
    background: {BG_1};
}}

QComboBox::drop-down {{
    width: 20px;
    border: none;
}}
QComboBox QAbstractItemView {{
    background: {BG_2};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    selection-background-color: {ACCENT_SOFT};
    color: {TEXT};
    padding: 4px;
}}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background: {BG_2};
    border: none;
    width: 16px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
    background: {BG_3};
}}

QCheckBox {{
    color: {TEXT};
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {BORDER_STRONG};
    border-radius: 4px;
    background: {BG_2};
}}
QCheckBox::indicator:hover {{
    border: 1px solid {ACCENT};
}}
QCheckBox::indicator:checked {{
    background: {ACCENT};
    border: 1px solid {ACCENT};
    image: none;
}}

/* ---------- Buttons ---------- */
QPushButton {{
    background: {BG_2};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    padding: 7px 14px;
    font-weight: 500;
}}
QPushButton:hover {{
    background: {BG_3};
    border: 1px solid {BORDER_STRONG};
}}
QPushButton:pressed {{
    background: {BG_1};
}}
QPushButton:disabled {{
    color: {TEXT_FAINT};
    background: {BG_1};
    border: 1px solid {BORDER};
}}

QPushButton#Primary {{
    background: {ACCENT};
    color: white;
    border: 1px solid {ACCENT};
    padding: 9px 18px;
    font-weight: 600;
}}
QPushButton#Primary:hover {{
    background: {ACCENT_HOVER};
    border: 1px solid {ACCENT_HOVER};
}}
QPushButton#Primary:pressed {{
    background: {ACCENT_PRESSED};
}}
QPushButton#Primary:disabled {{
    background: {ACCENT_SOFT};
    color: {TEXT_FAINT};
    border: 1px solid {ACCENT_SOFT};
}}

QPushButton#Ghost {{
    background: transparent;
    border: 1px solid transparent;
    color: {TEXT_MUTED};
}}
QPushButton#Ghost:hover {{
    background: {BG_2};
    color: {TEXT};
}}

QPushButton#Danger {{
    background: transparent;
    color: {DANGER};
    border: 1px solid {BORDER};
}}
QPushButton#Danger:hover {{
    background: rgba(229, 72, 77, 0.12);
    border: 1px solid {DANGER};
}}

/* ---------- File list ---------- */
QListWidget#FileList {{
    background: {BG_1};
    border: 1px solid {BORDER};
    border-radius: {RADIUS}px;
    padding: 4px;
    outline: 0;
}}
QListWidget#FileList::item {{
    background: transparent;
    border-radius: {RADIUS_SM}px;
    padding: 10px 12px;
    margin: 2px 0;
    color: {TEXT};
}}
QListWidget#FileList::item:hover {{
    background: {BG_2};
}}
QListWidget#FileList::item:selected {{
    background: {ACCENT_SOFT};
    color: {TEXT};
}}

/* ---------- Status bar ---------- */
QStatusBar {{
    background: {BG_1};
    border-top: 1px solid {BORDER};
    color: {TEXT_MUTED};
    padding: 2px 10px;
}}
QStatusBar::item {{ border: none; }}

/* ---------- Progress bar ---------- */
QProgressBar {{
    background: {BG_2};
    border: 1px solid {BORDER};
    border-radius: 4px;
    min-height: 6px;
    max-height: 6px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background: {ACCENT};
    border-radius: 3px;
}}

/* ---------- Menu & menubar ---------- */
QMenuBar {{
    background: {BG_1};
    color: {TEXT};
    border-bottom: 1px solid {BORDER};
    padding: 2px;
}}
QMenuBar::item {{
    background: transparent;
    padding: 6px 10px;
    border-radius: {RADIUS_SM}px;
}}
QMenuBar::item:selected {{
    background: {BG_2};
}}
QMenu {{
    background: {BG_1};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    padding: 4px;
}}
QMenu::item {{
    padding: 7px 18px;
    border-radius: 4px;
}}
QMenu::item:selected {{
    background: {ACCENT_SOFT};
    color: {TEXT};
}}
QMenu::separator {{
    height: 1px;
    background: {BORDER};
    margin: 4px 6px;
}}

/* ---------- Splitter ---------- */
QSplitter::handle {{
    background: {BG_0};
}}
QSplitter::handle:horizontal {{ width: 6px; }}
QSplitter::handle:vertical {{ height: 6px; }}

/* ---------- Scrollbars ---------- */
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: {BG_3};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{ background: {BORDER_STRONG}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}

QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background: {BG_3};
    border-radius: 4px;
    min-width: 24px;
}}
QScrollBar::handle:horizontal:hover {{ background: {BORDER_STRONG}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ---------- Tabs (kept for stray usage) ---------- */
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: {RADIUS}px;
    background: {BG_1};
    top: -1px;
}}
QTabBar::tab {{
    background: transparent;
    color: {TEXT_MUTED};
    padding: 8px 14px;
    border: none;
    border-bottom: 2px solid transparent;
}}
QTabBar::tab:selected {{
    color: {TEXT};
    border-bottom: 2px solid {ACCENT};
}}
QTabBar::tab:hover {{
    color: {TEXT};
}}

/* ---------- Toolbar (hidden by default via code; style kept for safety) ---------- */
QToolBar {{
    background: {BG_1};
    border: none;
    padding: 4px;
    spacing: 4px;
}}

/* ---------- Dialogs / message boxes ---------- */
QDialog, QMessageBox, QInputDialog {{
    background: {BG_1};
}}
QMessageBox QLabel, QInputDialog QLabel {{
    color: {TEXT};
}}
"""


def apply_theme(app):
    """Apply the stylesheet to the whole QApplication."""
    app.setStyleSheet(STYLESHEET)
