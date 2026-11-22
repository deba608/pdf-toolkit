"""Design tokens and QSS stylesheet for the PDF Toolkit UI.

Supabase Design Language (supabase.com):
- Clean white-and-near-black system with minimal chrome.
- Single signature emerald-green CTA (#3ecf8e) with near-black text (#171717).
- Humanist sans display tier (Inter / Segoe UI / Circular fallback) at weight 500.
- Calibrated grey ladder from #ededed (hairline-cool) to #171717 (ink).
- Tight 6px / 8px radii (square-ish, technical, never pill-shaped).
- Code & preview workbench rendered in deep canvas-night (#1c1c1c).
"""

# ==============================================================================
# Supabase Design Tokens
# ==============================================================================

# Brand & Accent
PRIMARY = "#3ecf8e"             # Signature CTA emerald green
PRIMARY_DEEP = "#24b47e"        # Pressed state
PRIMARY_SOFT = "#4ade80"        # Hover / accent highlight
ON_PRIMARY = "#171717"          # Near-black on green (the button reads as "lit" with dark type)
ON_DARK = "#ffffff"             # Text on canvas-night surfaces

# Text
INK = "#171717"                 # Default body / heading text (near-black, never pure black)
INK_SECONDARY = "#212121"       # Body emphasis
INK_MUTE = "#707070"            # Secondary text and helper copy
INK_MUTE_2 = "#9a9a9a"          # Tertiary text / placeholders
INK_FAINT = "#b2b2b2"           # Disabled text / subtle hints

# Surface
CANVAS = "#ffffff"              # Default page background (pure white)
CANVAS_SOFT = "#fafafa"         # Alternating section bands / secondary surface
CANVAS_NIGHT = "#1c1c1c"        # Deep near-black used in code blocks / preview backdrop
CANVAS_NIGHT_SOFT = "#202020"   # Nested night chrome

# Hairlines & Borders
HAIRLINE = "#dfdfdf"            # 1px borders on cards and tables
HAIRLINE_STRONG = "#c7c7c7"     # Slightly darker border for form inputs & buttons
HAIRLINE_COOL = "#ededed"       # Grey ladder fine chrome / subtle dividers
HAIRLINE_COOL_2 = "#efefef"
HAIRLINE_COOL_3 = "#d4d4d4"

# Semantic Accents (reserved for status indicators / badges)
DANGER = "#ff2201"              # Accent Tomato
DANGER_BG = "rgba(255, 34, 1, 0.08)"
SUCCESS = "#3ecf8e"             # Primary Emerald
SUCCESS_BG = "rgba(62, 207, 142, 0.12)"
WARN = "#ffdb13"                # Accent Yellow
WARN_BG = "rgba(255, 219, 19, 0.12)"
ACCENT_PURPLE = "#6b01c2"
ACCENT_VIOLET = "#644fc1"

# Radii (tight 6px / 8px button radii - square-ish, technical)
RADIUS_XS = 4
RADIUS_SM = 6                   # Signature button and input radius
RADIUS_MD = 8                   # Compact cards, alerts
RADIUS_LG = 12                  # Feature cards, containers, dialogs
RADIUS_XL = 16
RADIUS_FULL = 9999              # Pill tags, badges

# Backward-compatibility token aliases so existing imports work seamlessly
BG_0 = CANVAS                   # #ffffff
BG_1 = CANVAS_SOFT              # #fafafa
BG_2 = CANVAS                   # #ffffff
BG_3 = "#f2f2f2"                # hover surface
BORDER = HAIRLINE               # #dfdfdf
BORDER_STRONG = HAIRLINE_STRONG # #c7c7c7
TEXT = INK                     # #171717
TEXT_MUTED = INK_MUTE           # #707070
TEXT_FAINT = INK_FAINT          # #b2b2b2
ACCENT = PRIMARY                # #3ecf8e
ACCENT_HOVER = PRIMARY_SOFT     # #4ade80
ACCENT_PRESSED = PRIMARY_DEEP   # #24b47e
ACCENT_SOFT = "rgba(62, 207, 142, 0.12)"
ACCENT_BORDER = PRIMARY
ACCENT2 = PRIMARY
RADIUS = RADIUS_SM


STYLESHEET = f"""
/* ---------- Base & Typography ---------- */
* {{
    font-family: "Inter", "Segoe UI", -apple-system, BlinkMacSystemFont, "Circular", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    color: {INK};
}}

QMainWindow, QWidget {{
    background: {CANVAS};
}}

QToolTip {{
    background: {CANVAS_NIGHT};
    color: {ON_DARK};
    border: 1px solid {CANVAS_NIGHT_SOFT};
    padding: 6px 10px;
    border-radius: {RADIUS_SM}px;
    font-size: 12px;
}}

/* ---------- Sidebar (Canvas Soft #fafafa) ---------- */
QListWidget#Sidebar {{
    background: {CANVAS_SOFT};
    border: none;
    border-right: 1px solid {HAIRLINE};
    padding: 8px 6px;
    outline: 0;
}}
QListWidget#Sidebar::item {{
    padding: 7px 12px;
    margin: 1px 2px;
    border-radius: {RADIUS_SM}px;
    color: {INK_MUTE};
    font-size: 13px;
    font-weight: 500;
    border: 1px solid transparent;
}}
QListWidget#Sidebar::item:hover {{
    background: {HAIRLINE_COOL};
    color: {INK};
}}
QListWidget#Sidebar::item:selected {{
    background: {CANVAS};
    color: {INK};
    font-weight: 500;
    border: 1px solid {HAIRLINE};
}}

QLabel#SidebarTitle {{
    color: {INK};
    font-size: 16px;
    font-weight: 500;
    letter-spacing: -0.3px;
}}
QLabel#SidebarSubtitle {{
    color: {INK_MUTE};
    font-size: 11px;
}}
QLabel#SidebarSection {{
    color: {INK_MUTE_2};
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 1.0px;
    text-transform: uppercase;
    padding: 12px 12px 4px 12px;
}}

/* ---------- App Header (Pure White Canvas) ---------- */
QFrame#Header {{
    background: {CANVAS};
    border-bottom: 1px solid {HAIRLINE};
    min-height: 54px;
    max-height: 54px;
}}
QLabel#HeaderTitle {{
    color: {INK};
    font-size: 18px;
    font-weight: 500;
    letter-spacing: -0.2px;
}}
QLabel#HeaderSubtitle {{
    color: {INK_MUTE};
    font-size: 12px;
}}

/* ---------- Containers & Feature Cards ---------- */
QFrame.Card {{
    background: {CANVAS};
    border: 1px solid {HAIRLINE};
    border-radius: {RADIUS_LG}px;
}}
QLabel.CardTitle {{
    color: {INK};
    font-size: 15px;
    font-weight: 500;
    letter-spacing: -0.1px;
}}
QLabel.CardDescription {{
    color: {INK_MUTE};
    font-size: 12px;
}}
QLabel.FieldLabel {{
    color: {INK};
    font-size: 12px;
    font-weight: 500;
    margin-bottom: 2px;
}}
QLabel.Hint {{
    color: {INK_MUTE};
    font-size: 12px;
    line-height: 16px;
}}
QLabel.SectionHeading {{
    color: {INK};
    font-size: 13px;
    font-weight: 500;
    letter-spacing: -0.1px;
    padding-top: 4px;
}}

/* ---------- Form Controls & Inputs ---------- */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {{
    background: {CANVAS};
    border: 1px solid {HAIRLINE};
    border-radius: {RADIUS_SM}px;
    padding: 7px 11px;
    color: {INK};
    min-height: 20px;
    selection-background-color: {PRIMARY};
    selection-color: {ON_PRIMARY};
}}
QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover,
QTextEdit:hover, QPlainTextEdit:hover {{
    border: 1px solid {HAIRLINE_STRONG};
    background: {CANVAS};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {PRIMARY};
    background: {CANVAS};
}}
QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {{
    color: {INK_FAINT};
    background: {CANVAS_SOFT};
    border: 1px solid {HAIRLINE_COOL};
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
    border-top: 5px solid {INK_MUTE};
    margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background: {CANVAS};
    border: 1px solid {HAIRLINE_STRONG};
    border-radius: {RADIUS_SM}px;
    selection-background-color: {CANVAS_SOFT};
    selection-color: {INK};
    color: {INK};
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
    background: {HAIRLINE_COOL};
}}

QCheckBox {{
    color: {INK};
    spacing: 8px;
    font-size: 13px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {HAIRLINE_STRONG};
    border-radius: 4px;
    background: {CANVAS};
}}
QCheckBox::indicator:hover {{
    border: 1px solid {PRIMARY};
}}
QCheckBox::indicator:checked {{
    background: {PRIMARY};
    border: 1px solid {PRIMARY};
    image: none;
}}

/* ---------- Buttons (Supabase Style) ---------- */
/* Secondary / default outline button */
QPushButton {{
    background: {CANVAS};
    color: {INK};
    border: 1px solid {HAIRLINE_STRONG};
    border-radius: {RADIUS_SM}px;
    padding: 7px 14px;
    font-weight: 500;
    font-size: 13px;
    min-height: 20px;
}}
QPushButton:hover {{
    background: {CANVAS_SOFT};
    border: 1px solid {INK_MUTE_2};
    color: {INK};
}}
QPushButton:pressed {{
    background: {HAIRLINE_COOL};
    border: 1px solid {INK_MUTE};
}}
QPushButton:disabled {{
    color: {INK_FAINT};
    background: {CANVAS_SOFT};
    border: 1px solid {HAIRLINE};
}}

/* Signature Emerald Green Primary CTA (near-black text: "lit surface") */
QPushButton#Primary {{
    background: {PRIMARY};
    color: {ON_PRIMARY};
    border: 1px solid {PRIMARY};
    border-radius: {RADIUS_SM}px;
    padding: 8px 18px;
    font-weight: 500;
    font-size: 13px;
}}
QPushButton#Primary:hover {{
    background: {PRIMARY_SOFT};
    border: 1px solid {PRIMARY_SOFT};
    color: {ON_PRIMARY};
}}
QPushButton#Primary:pressed {{
    background: {PRIMARY_DEEP};
    border: 1px solid {PRIMARY_DEEP};
    color: {ON_PRIMARY};
}}
QPushButton#Primary:disabled {{
    background: {HAIRLINE_COOL};
    color: {INK_FAINT};
    border: 1px solid {HAIRLINE};
}}

/* Ghost / link button */
QPushButton#Ghost {{
    background: transparent;
    border: 1px solid transparent;
    color: {INK_MUTE};
    border-radius: {RADIUS_SM}px;
}}
QPushButton#Ghost:hover {{
    background: {HAIRLINE_COOL};
    border: 1px solid {HAIRLINE};
    color: {INK};
}}
QPushButton#Ghost:pressed {{
    background: {HAIRLINE};
}}

/* Destructive / Danger button */
QPushButton#Danger {{
    background: transparent;
    color: {DANGER};
    border: 1px solid rgba(255, 34, 1, 0.3);
    border-radius: {RADIUS_SM}px;
}}
QPushButton#Danger:hover {{
    background: {DANGER_BG};
    border: 1px solid {DANGER};
    color: {DANGER};
}}

/* Quick filter / preset chip button */
QPushButton#PresetBtn {{
    background: {CANVAS};
    border: 1px solid {HAIRLINE};
    border-radius: {RADIUS_SM}px;
    padding: 5px 11px;
    font-size: 12px;
    font-weight: 500;
    color: {INK_MUTE};
}}
QPushButton#PresetBtn:hover {{
    background: {CANVAS_SOFT};
    border: 1px solid {HAIRLINE_STRONG};
    color: {INK};
}}
QPushButton#PresetBtn:checked, QPushButton#PresetBtn:pressed {{
    background: rgba(62, 207, 142, 0.12);
    border: 1px solid {PRIMARY};
    color: {INK};
    font-weight: 500;
}}

/* ---------- Scrollbars (Minimal & Clean) ---------- */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: {HAIRLINE};
    border-radius: 4px;
    min-height: 28px;
}}
QScrollBar::handle:vertical:hover {{
    background: {HAIRLINE_STRONG};
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
    background: {HAIRLINE};
    border-radius: 4px;
    min-width: 28px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {HAIRLINE_STRONG};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ---------- Progress Bar ---------- */
QProgressBar {{
    background: {HAIRLINE_COOL};
    border: 1px solid {HAIRLINE};
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
    background: {CANVAS};
    border: 1px solid {HAIRLINE};
    border-radius: {RADIUS_MD}px;
    gridline-color: {HAIRLINE_COOL};
    color: {INK};
    selection-background-color: rgba(62, 207, 142, 0.12);
    selection-color: {INK};
    outline: 0;
}}
QTreeWidget::item, QTableWidget::item {{
    padding: 6px 10px;
    border-bottom: 1px solid {HAIRLINE_COOL};
}}
QTreeWidget::item:selected, QTableWidget::item:selected {{
    background: rgba(62, 207, 142, 0.12);
    color: {INK};
}}
QHeaderView::section {{
    background: {CANVAS_SOFT};
    color: {INK_MUTE};
    border: none;
    border-bottom: 1px solid {HAIRLINE};
    padding: 7px 10px;
    font-weight: 500;
    font-size: 12px;
}}

/* ---------- Popup Menus & Dialogs ---------- */
QMenu {{
    background: {CANVAS};
    border: 1px solid {HAIRLINE_STRONG};
    border-radius: {RADIUS_SM}px;
    padding: 4px;
}}
QMenu::item {{
    padding: 7px 22px 7px 14px;
    border-radius: 4px;
    color: {INK};
}}
QMenu::item:selected {{
    background: {CANVAS_SOFT};
    color: {INK};
}}
QMenu::item:disabled {{
    color: {INK_FAINT};
}}
QMenu::separator {{
    height: 1px;
    background: {HAIRLINE};
    margin: 4px 6px;
}}

QSplitter::handle {{
    background: {HAIRLINE};
}}
QSplitter::handle:horizontal {{
    width: 1px;
}}
QSplitter::handle:vertical {{
    height: 1px;
}}

QDialog, QMessageBox, QInputDialog {{
    background: {CANVAS};
}}
QMessageBox QLabel, QInputDialog QLabel {{
    color: {INK};
}}
"""

def apply_theme(app):
    """Apply the Supabase stylesheet to the whole QApplication."""
    app.setStyleSheet(STYLESHEET)
