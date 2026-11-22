"""Design tokens and QSS stylesheet for the PDF Toolkit UI.

Vite Design Language (vite.dev):
- Deep dark charcoal & obsidian surfaces: #1b1b1f (canvas), #161618 (alt), #202127 (elv), #252529 (soft).
- Electric indigo brand CTA: #646cff, hover #747bff, active #535bf2.
- Vibrant purple-to-cyan gradient accents: #bd34fe (purple) to #41d1ff (cyan).
- Translucent hairlines: rgba(82, 82, 89, 0.48) and #2e2e32.
- High-contrast crisp typography: rgba(255, 255, 245, 0.88) on Inter font stack.
- Tight 8px / 12px radii with clean developer-focused minimalism.
"""

# ==============================================================================
# Vite Design Tokens (vite.dev)
# ==============================================================================

# Brand & Accent
PRIMARY = "#646cff"             # Electric Indigo (Vite brand CTA)
PRIMARY_HOVER = "#747bff"       # Hover state
PRIMARY_ACTIVE = "#535bf2"      # Pressed / active state
PRIMARY_SOFT = "rgba(100, 108, 255, 0.16)" # Active nav items, chips, focus rings

ACCENT_PURPLE = "#bd34fe"       # Vite lightning electric purple
ACCENT_CYAN = "#41d1ff"         # Vite lightning electric cyan

# Surfaces (VitePress Dark Palette)
CANVAS = "#1b1b1f"              # Main window surface (charcoal)
CANVAS_ALT = "#161618"          # Deeper surface (sidebar, toolbars, view canvas)
CANVAS_ELV = "#202127"          # Elevated container cards, dialogs
CANVAS_SOFT = "#252529"         # Secondary inputs, controls, chips
CANVAS_MUTE = "#2e2e32"         # Hover surface

# Borders & Hairlines
BORDER = "rgba(82, 82, 89, 0.48)"     # Standard element borders
BORDER_SUBTLE = "rgba(82, 82, 89, 0.28)" # Hairline dividers, subtle frames
BORDER_SOFT = "#2e2e32"               # Container border
BORDER_FOCUS = "#646cff"              # Focus ring

# Typography & Text Colors
TEXT_1 = "rgba(255, 255, 245, 0.88)" # Primary text (headings, high-emphasis)
TEXT_2 = "rgba(235, 235, 245, 0.60)" # Secondary text, subtitles, helper copy
TEXT_3 = "rgba(235, 235, 245, 0.38)" # Tertiary text, placeholders, disabled

# Semantic Accents
DANGER = "#f43f5e"              # Rose / destructive
DANGER_BG = "rgba(244, 63, 94, 0.12)"
SUCCESS = "#10b981"             # Emerald green status
SUCCESS_BG = "rgba(16, 185, 129, 0.12)"
WARN = "#f59e0b"                # Amber warning
WARN_BG = "rgba(245, 158, 11, 0.12)"

# Corner Radii
RADIUS_XS = 4
RADIUS_SM = 6
RADIUS_MD = 8                   # Buttons, form controls, chips
RADIUS_LG = 12                  # Cards, containers, modals
RADIUS_FULL = 9999              # Badges, pills

# Backward-compatibility aliases
BG_0 = CANVAS                   # #1b1b1f
BG_1 = CANVAS_ELV               # #202127
BG_2 = CANVAS_SOFT              # #252529
BG_3 = CANVAS_MUTE              # #2e2e32
BORDER_STRONG = BORDER
TEXT = TEXT_1                   # rgba(255, 255, 245, 0.88)
TEXT_MUTED = TEXT_2             # rgba(235, 235, 245, 0.60)
TEXT_FAINT = TEXT_3             # rgba(235, 235, 245, 0.38)
ACCENT = PRIMARY                # #646cff
ACCENT_HOVER = PRIMARY_HOVER    # #747bff
ACCENT_PRESSED = PRIMARY_ACTIVE # #535bf2
ACCENT_SOFT = PRIMARY_SOFT
ACCENT_BORDER = PRIMARY
ACCENT2 = ACCENT_PURPLE
ON_PRIMARY = "#ffffff"
ON_DARK = "#ffffff"
HAIRLINE = BORDER_SUBTLE
HAIRLINE_STRONG = BORDER
HAIRLINE_COOL = BORDER_SUBTLE
INK = TEXT_1
INK_MUTE = TEXT_2
INK_MUTE_2 = TEXT_3
INK_FAINT = TEXT_3
RADIUS = RADIUS_MD


STYLESHEET = f"""
/* ---------- Base & Typography ---------- */
* {{
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    color: {TEXT_1};
}}

QMainWindow, QWidget {{
    background: {CANVAS};
}}

QToolTip {{
    background: {CANVAS_ALT};
    color: {TEXT_1};
    border: 1px solid {BORDER};
    padding: 6px 10px;
    border-radius: {RADIUS_SM}px;
    font-size: 12px;
}}

/* ---------- Sidebar (Vite Dark Obsidian #161618) ---------- */
QListWidget#Sidebar {{
    background: {CANVAS_ALT};
    border: none;
    border-right: 1px solid {BORDER_SUBTLE};
    padding: 10px 8px;
    outline: 0;
}}
QListWidget#Sidebar::item {{
    padding: 8px 12px;
    margin: 2px 2px;
    border-radius: {RADIUS_MD}px;
    color: {TEXT_2};
    font-size: 13px;
    font-weight: 500;
    border: 1px solid transparent;
}}
QListWidget#Sidebar::item:hover {{
    background: {CANVAS_ELV};
    color: {TEXT_1};
}}
QListWidget#Sidebar::item:selected {{
    background: {PRIMARY_SOFT};
    color: {PRIMARY_HOVER};
    font-weight: 600;
    border: 1px solid rgba(100, 108, 255, 0.36);
}}

QLabel#SidebarTitle {{
    color: {TEXT_1};
    font-size: 16px;
    font-weight: 600;
    letter-spacing: -0.3px;
}}
QLabel#SidebarSubtitle {{
    color: {TEXT_3};
    font-size: 11px;
}}
QLabel#SidebarSection {{
    color: {TEXT_3};
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.0px;
    text-transform: uppercase;
    padding: 12px 12px 4px 12px;
}}

/* ---------- Header (Vite Workspace Canvas) ---------- */
QFrame#Header {{
    background: {CANVAS};
    border-bottom: 1px solid {BORDER_SUBTLE};
    min-height: 54px;
    max-height: 54px;
}}
QLabel#HeaderTitle {{
    color: {TEXT_1};
    font-size: 18px;
    font-weight: 600;
    letter-spacing: -0.2px;
}}
QLabel#HeaderSubtitle {{
    color: {TEXT_2};
    font-size: 12px;
}}

/* ---------- Containers & Feature Cards (Elevated #202127) ---------- */
QFrame.Card {{
    background: {CANVAS_ELV};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: {RADIUS_LG}px;
}}
QLabel.CardTitle {{
    color: {TEXT_1};
    font-size: 15px;
    font-weight: 600;
    letter-spacing: -0.1px;
}}
QLabel.CardDescription {{
    color: {TEXT_2};
    font-size: 12px;
}}
QLabel.FieldLabel {{
    color: {TEXT_1};
    font-size: 12px;
    font-weight: 500;
    margin-bottom: 2px;
}}
QLabel.Hint {{
    color: {TEXT_2};
    font-size: 12px;
    line-height: 16px;
}}
QLabel.SectionHeading {{
    color: {TEXT_1};
    font-size: 13px;
    font-weight: 600;
    letter-spacing: -0.1px;
    padding-top: 4px;
}}

/* ---------- Form Controls & Inputs (Deep #161618 / #252529) ---------- */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {{
    background: {CANVAS_ALT};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: {RADIUS_MD}px;
    padding: 7px 11px;
    color: {TEXT_1};
    min-height: 20px;
    selection-background-color: {PRIMARY};
    selection-color: #ffffff;
}}
QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover,
QTextEdit:hover, QPlainTextEdit:hover {{
    border: 1px solid {BORDER};
    background: {CANVAS_ALT};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {PRIMARY};
    background: {CANVAS_ALT};
}}
QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {{
    color: {TEXT_3};
    background: {CANVAS_SOFT};
    border: 1px solid {BORDER_SUBTLE};
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
    border-top: 5px solid {TEXT_2};
    margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background: {CANVAS_ELV};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_MD}px;
    selection-background-color: {PRIMARY_SOFT};
    selection-color: {PRIMARY_HOVER};
    color: {TEXT_1};
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
    background: {CANVAS_MUTE};
}}

QCheckBox {{
    color: {TEXT_1};
    spacing: 8px;
    font-size: 13px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {BORDER};
    border-radius: 4px;
    background: {CANVAS_ALT};
}}
QCheckBox::indicator:hover {{
    border: 1px solid {PRIMARY};
}}
QCheckBox::indicator:checked {{
    background: {PRIMARY};
    border: 1px solid {PRIMARY};
    image: none;
}}

/* ---------- Buttons (Vite Style) ---------- */
/* Secondary / default button */
QPushButton {{
    background: {CANVAS_SOFT};
    color: {TEXT_1};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_MD}px;
    padding: 7px 14px;
    font-weight: 500;
    font-size: 13px;
    min-height: 20px;
}}
QPushButton:hover {{
    background: {CANVAS_MUTE};
    border: 1px solid rgba(100, 108, 255, 0.48);
    color: #ffffff;
}}
QPushButton:pressed {{
    background: {CANVAS_ALT};
    border: 1px solid {PRIMARY};
}}
QPushButton:disabled {{
    color: {TEXT_3};
    background: {CANVAS_ELV};
    border: 1px solid {BORDER_SUBTLE};
}}

/* Primary Electric Indigo CTA (#646cff) */
QPushButton#Primary {{
    background: {PRIMARY};
    color: #ffffff;
    border: 1px solid {PRIMARY};
    border-radius: {RADIUS_MD}px;
    padding: 8px 18px;
    font-weight: 500;
    font-size: 13px;
}}
QPushButton#Primary:hover {{
    background: {PRIMARY_HOVER};
    border: 1px solid {PRIMARY_HOVER};
    color: #ffffff;
}}
QPushButton#Primary:pressed {{
    background: {PRIMARY_ACTIVE};
    border: 1px solid {PRIMARY_ACTIVE};
    color: #ffffff;
}}
QPushButton#Primary:disabled {{
    background: {CANVAS_SOFT};
    color: {TEXT_3};
    border: 1px solid {BORDER_SUBTLE};
}}

/* Ghost / text button */
QPushButton#Ghost {{
    background: transparent;
    border: 1px solid transparent;
    color: {TEXT_2};
    border-radius: {RADIUS_MD}px;
}}
QPushButton#Ghost:hover {{
    background: {PRIMARY_SOFT};
    border: 1px solid rgba(100, 108, 255, 0.24);
    color: {TEXT_1};
}}
QPushButton#Ghost:pressed {{
    background: {CANVAS_MUTE};
}}

/* Destructive / Danger button */
QPushButton#Danger {{
    background: transparent;
    color: {DANGER};
    border: 1px solid rgba(244, 63, 94, 0.32);
    border-radius: {RADIUS_MD}px;
}}
QPushButton#Danger:hover {{
    background: {DANGER_BG};
    border: 1px solid {DANGER};
    color: #ffffff;
}}

/* Quick filter / preset chip button */
QPushButton#PresetBtn {{
    background: {CANVAS_SOFT};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: {RADIUS_MD}px;
    padding: 5px 11px;
    font-size: 12px;
    font-weight: 500;
    color: {TEXT_2};
}}
QPushButton#PresetBtn:hover {{
    background: {CANVAS_MUTE};
    border: 1px solid {BORDER};
    color: {TEXT_1};
}}
QPushButton#PresetBtn:checked, QPushButton#PresetBtn:pressed {{
    background: {PRIMARY_SOFT};
    border: 1px solid {PRIMARY};
    color: {PRIMARY_HOVER};
    font-weight: 600;
}}

/* ---------- Scrollbars (Clean & Translucent) ---------- */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: {CANVAS_MUTE};
    border-radius: 4px;
    min-height: 28px;
}}
QScrollBar::handle:vertical:hover {{
    background: rgba(100, 108, 255, 0.40);
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
    background: {CANVAS_MUTE};
    border-radius: 4px;
    min-width: 28px;
}}
QScrollBar::handle:horizontal:hover {{
    background: rgba(100, 108, 255, 0.40);
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ---------- Progress Bar ---------- */
QProgressBar {{
    background: {CANVAS_ALT};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 4px;
    height: 6px;
    text-align: center;
}}
QProgressBar::chunk {{
    background: {PRIMARY};
    border-radius: 3px;
}}

/* ---------- Tables & Tree Views (Batch queue / Library) ---------- */
QTreeWidget, QTableWidget {{
    background: {CANVAS_ELV};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: {RADIUS_MD}px;
    gridline-color: {BORDER_SUBTLE};
    color: {TEXT_1};
    selection-background-color: {PRIMARY_SOFT};
    selection-color: {TEXT_1};
    outline: 0;
}}
QTreeWidget::item, QTableWidget::item {{
    padding: 6px 10px;
    border-bottom: 1px solid {BORDER_SUBTLE};
}}
QTreeWidget::item:selected, QTableWidget::item:selected {{
    background: {PRIMARY_SOFT};
    color: #ffffff;
}}
QHeaderView::section {{
    background: {CANVAS_ALT};
    color: {TEXT_2};
    border: none;
    border-bottom: 1px solid {BORDER_SUBTLE};
    padding: 7px 10px;
    font-weight: 600;
    font-size: 12px;
}}

/* ---------- Popup Menus & Dialogs ---------- */
QMenu {{
    background: {CANVAS_ELV};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_MD}px;
    padding: 4px;
}}
QMenu::item {{
    padding: 7px 22px 7px 14px;
    border-radius: 4px;
    color: {TEXT_1};
}}
QMenu::item:selected {{
    background: {PRIMARY_SOFT};
    color: {PRIMARY_HOVER};
}}
QMenu::item:disabled {{
    color: {TEXT_3};
}}
QMenu::separator {{
    height: 1px;
    background: {BORDER_SUBTLE};
    margin: 4px 6px;
}}

QSplitter::handle {{
    background: {BORDER_SUBTLE};
}}
QSplitter::handle:horizontal {{
    width: 1px;
}}
QSplitter::handle:vertical {{
    height: 1px;
}}

QDialog, QMessageBox, QInputDialog {{
    background: {CANVAS_ELV};
}}
QMessageBox QLabel, QInputDialog QLabel {{
    color: {TEXT_1};
}}
"""

def apply_theme(app):
    """Apply the Vite stylesheet to the whole QApplication."""
    app.setStyleSheet(STYLESHEET)
