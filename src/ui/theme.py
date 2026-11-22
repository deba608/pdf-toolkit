"""Design tokens and QSS stylesheet for the PDF Toolkit UI.

Evil Martians-inspired: severe, theatrical developer identity.
Black first, white second, color only where content asks for it.
Minimal, dense, bold typography — accent purple used sparingly as a signal.
"""

# ---- Design tokens (Evil Martians palette) ----
# Primary palette from opendesignmd.com evilmartians.com
BG_0 = "#0b0b0b"          # main window canvas — near-pure black
BG_1 = "#1a1a1a"          # primary surface / sidebar / tool cards
BG_2 = "#252525"          # secondary surface / inputs / toolbars / chips
BG_3 = "#3a3a3c"          # hover surface / active states
BORDER = "#4a4a4d"        # subtle container borders
BORDER_STRONG = "#8b5a6b" # emphasized / focused borders — pink accent

TEXT = "#e0e0e0"          # high-contrast primary text (off-white)
TEXT_MUTED = "#888888"    # secondary text / subtitles / metadata
TEXT_FAINT = "#555555"    # placeholders / captions / hints

# Accent palette — purple/pink used ONLY for interactive elements
ACCENT = "#550098"        # primary accent — deep purple
ACCENT_HOVER = "#6b10a6"  # vibrant purple on hover
ACCENT_PRESSED = "#7a21b5" # deep purple on click
ACCENT_SOFT = "#3d0f7e"   # subtle accent background tint
ACCENT_BORDER = "#550098" # border for accent elements

# Secondary accent — pink for high-visibility signals
ACCENT2 = "#CB009E"       # pink accent — used sparingly for warnings/actions
ACCENT2_HOVER = "#e010ae"
ACCENT2_PRESSED = "#f020bf"

DANGER = "#f85149"
DANGER_BG = "rgba(248, 81, 73, 0.12)"
SUCCESS = "#2ea043"
SUCCESS_BG = "rgba(46, 160, 67, 0.12)"
WARN = "#d29922"
WARN_BG = "rgba(210, 153, 34, 0.12)"

# Radii — smaller, tighter corners for dense layout
RADIUS = 6
RADIUS_SM = 4
RADIUS_LG = 8


STYLESHEET = f"""
/* ---------- Base ---------- */
* {{
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Inter", "Helvetica Neue", sans-serif;
    font-size: 13px;
    color: {TEXT};
}}

QMainWindow, QWidget {{
    background: {BG_0};
}}

QToolTip {{
    background: {BG_2};
    color: {TEXT};
    border: 1px solid {BORDER_STRONG};
    padding: 6px 10px;
    border-radius: {RADIUS_SM}px;
    font-size: 12px;
}}

QListWidget#Sidebar {{
    background: {BG_1};
    border: none;
    border-right: 1px solid {BORDER};
    padding: 10px 8px;
    outline: 0;
}}
QListWidget#Sidebar::item {{
    padding: 8px 12px;
    margin: 2px 2px;
    border-radius: {RADIUS_SM}px;
    color: {TEXT_MUTED};
    font-size: 13px;
    font-weight: 500;
    border: 1px solid transparent;
}}
QListWidget#Sidebar::item:hover {{
    background: {BG_2};
    color: {TEXT};
}}
QListWidget#Sidebar::item:selected {{
    background: {ACCENT_SOFT};
    color: #ffffff;
    font-weight: 600;
    border: 1px solid rgba(85, 0, 154, 0.4);
}}

QLabel#SidebarTitle {{
    color: {TEXT};
    font-size: 16px;
    font-weight: 700;
    letter-spacing: -0.3px;
}}
QLabel#SidebarSubtitle {{
    color: {TEXT_FAINT};
    font-size: 11px;
}}
QLabel#SidebarSection {{
    color: {TEXT_FAINT};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    padding: 14px 12px 4px 12px;
}}

QFrame#Header {{
    background: {BG_1};
    border-bottom: 1px solid {BORDER};
    min-height: 56px;
    max-height: 56px;
}}
QLabel#HeaderTitle {{
    color: {TEXT};
    font-size: 16px;
    font-weight: 600;
    letter-spacing: -0.2px;
}}
QLabel#HeaderSubtitle {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}

QFrame.Card {{
    background: {BG_1};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_LG}px;
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
    color: {TEXT};
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 2px;
}}
QLabel.Hint {{
    color: {TEXT_MUTED};
    font-size: 12px;
    line-height: 16px;
}}
QLabel.SectionHeading {{
    color: {TEXT};
    font-size: 13px;
    font-weight: 600;
    letter-spacing: -0.1px;
    padding-top: 6px;
}}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {{
    background: {BG_2};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    padding: 7px 11px;
    color: {TEXT};
    min-height: 20px;
    selection-background-color: {ACCENT};
    selection-color: #ffffff;
}}
QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover,
QTextEdit:hover, QPlainTextEdit:hover {{
    border: 1px solid {BORDER_STRONG};
    background: {BG_2};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {ACCENT};
    background: {BG_1};
}}
QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {{
    color: {TEXT_FAINT};
    background: {BG_1};
    border: 1px solid {BORDER};
}}

QComboBox {{
    padding-right: 26px;
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: none;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {TEXT_MUTED};
    margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background: {BG_1};
    border: 1px solid {BORDER_STRONG};
    border-radius: {RADIUS_SM}px;
    selection-background-color: {ACCENT_SOFT};
    selection-color: #ffffff;
    color: {TEXT};
    padding: 4px;
    outline: 0;
}}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background: transparent;
    border: none;
    width: 18px;
    margin: 1px;
    border-radius: 3px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
    background: {BG_3};
}}

QCheckBox {{
    color: {TEXT};
    spacing: 8px;
    font-size: 13px;
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

QPushButton {{
    background: {BG_2};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    padding: 7px 14px;
    font-weight: 500;
    min-height: 20px;
}}
QPushButton:hover {{
    background: {BG_3};
    border: 1px solid {BORDER_STRONG};
    color: #ffffff;
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
    color: #ffffff;
    border: 1px solid {ACCENT};
    padding: 9px 20px;
    font-weight: 600;
    font-size: 13px;
}}
QPushButton#Primary:hover {{
    background: {ACCENT_HOVER};
    border: 1px solid {ACCENT_HOVER};
}}
QPushButton#Primary:pressed {{
    background: {ACCENT_PRESSED};
    border: 1px solid {ACCENT_PRESSED};
}}
QPushButton#Primary:disabled {{
    background: {BG_2};
    color: {TEXT_FAINT};
    border: 1px solid {BORDER};
}}

QPushButton#Ghost {{
    background: transparent;
    border: 1px solid transparent;
    color: {TEXT_MUTED};
}}
QPushButton#Ghost:hover {{
    background: {BG_2};
    border: 1px solid {BORDER};
    color: {TEXT};
}}
QPushButton#Ghost:pressed {{
    background: {BG_1};
}}

QPushButton#Danger {{
    background: transparent;
    color: {DANGER};
    border: 1px solid rgba(248, 81, 73, 0.4);
}}
QPushButton#Danger:hover {{
    background: {DANGER_BG};
    border: 1px solid {DANGER};
    color: #ffffff;
}}

QPushButton#PresetBtn {{
    background: {BG_2};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 500;
    color: {TEXT_MUTED};
}}
QPushButton#PresetBtn:hover {{
    background: {BG_3};
    border: 1px solid {BORDER_STRONG};
    color: {TEXT};
}}
QPushButton#PresetBtn:checked, QPushButton#PresetBtn:pressed {{
    background: {ACCENT_SOFT};
    border: 1px solid {ACCENT};
    color: #ffffff;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: {BG_3};
    border-radius: 4px;
    min-height: 28px;
}}
QScrollBar::handle:vertical:hover {{
    background: {BORDER_STRONG};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
    margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background: {BG_3};
    border-radius: 4px;
    min-width: 28px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {BORDER_STRONG};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

QMenuBar {{
    background: {BG_1};
    color: {TEXT};
    border-bottom: 1px solid {BORDER};
    padding: 2px 4px;
}}
QMenuBar::item {{
    background: transparent;
    padding: 6px 12px;
    border-radius: {RADIUS_SM}px;
}}
QMenuBar::item:selected {{
    background: {BG_2};
    color: #ffffff;
}}
QMenu {{
    background: {BG_1};
    border: 1px solid {BORDER_STRONG};
    border-radius: {RADIUS_SM}px;
    padding: 4px;
}}
QMenu::item {{
    padding: 7px 22px 7px 14px;
    border-radius: 4px;
    color: {TEXT};
}}
QMenu::item:selected {{
    background: {ACCENT_SOFT};
    color: #ffffff;
}}
QMenu::item:disabled {{
    color: {TEXT_FAINT};
}}
QMenu::separator {{
    height: 1px;
    background: {BORDER};
    margin: 4px 6px;
}}

QSplitter::handle {{
    background: {BORDER};
}}
QSplitter::handle:horizontal {{
    width: 1px;
}}
QSplitter::handle:vertical {{
    height: 1px;
}}

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