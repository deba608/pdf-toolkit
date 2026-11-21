"""Check UI state and identify enhancement areas."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QListWidget, QProgressBar, QTabWidget, QStatusBar, QMenuBar
from PySide6.QtCore import Qt, QObject

app = QApplication.instance() or QApplication(sys.argv)

from src.ui.main_window import MainWindow
from src.ui.widgets.tool_panels import ToolPanelsStack

w = MainWindow()
w.show()

results = {}

# 1. Tool panels state
tp = w.tool_panels
results['tool_panels_count'] = tp.stack.count()
results['tool_panels_current'] = tp.stack.currentWidget().objectName() if tp.stack.currentWidget() else None

# 2. File list
fl = w.file_list
results['file_list_count'] = fl.count() if hasattr(fl, 'count') else 0
results['file_list_selected'] = fl.selectedItems().count() if hasattr(fl, 'selectedItems') else 0

# 3. Progress bar
pb = w.progress_bar
results['progress_visible'] = pb.isVisible()
results['progress_min'] = pb.minimum()
results['progress_max'] = pb.maximum()

# 4. Tabs
tabs = w.centralWidget()
if tabs and hasattr(tabs, 'count'):
    results['tab_count'] = tabs.count()
    tab_names = []
    for i in range(tabs.count()):
        tw = tabs.widget(i)
        if tw:
            tab_names.append(tw.objectName() if tw.objectName() else type(tw).__name__)
    results['tab_names'] = tab_names

# 5. Menu bar
results['menubar'] = w.menuBar() is not None

# 6. Status bar
results['statusbar'] = w.statusBar() is not None

# 7. Check all QPushButton texts for tool operations
buttons = w.findChildren(QPushButton)
button_texts = [b.text() for b in buttons if b.text() and len(b.text()) > 1]
results['button_count'] = len(buttons)
results['button_texts'] = button_texts

# 8. Check QLineEdit fields
line_edits = w.findChildren(QLineEdit)
results['lineedit_count'] = len(line_edits)
results['lineedit_placeholder'] = []
for le in line_edits:
    try:
        ph = le.placeholderText()
        if ph:
            results['lineedit_placeholder'].append(f"{type(le).__name__}: {ph}")
    except:
        pass

# 9. Check QSpinBox ranges
spin_info = []
for wdg in w.findChildren(QWidget):
    try:
        if hasattr(wdg, 'minimum') and hasattr(wdg, 'maximum'):
            mins = wdg.minimum()
            maxs = wdg.maximum()
            if mins != 0 or maxs != 100:
                spin_info.append(f"{type(wdg).__name__}({mins}-{maxs})")
    except:
        pass
results['spin_info'] = spin_info[:10]

print("=== UI CHECK RESULTS ===")
for k, v in sorted(results.items()):
    print(f"  {k}: {v}")

print("\n=== ENHANCEMENT SUMMARY ===")
print(f"1. Tool panels: {results['tool_panels_count']} panels, current: {results['tool_panels_current']}")
print(f"2. File list: {results['file_list_count']} files, selected: {results['file_list_selected']}")
print(f"3. Progress bar: visible={results['progress_visible']}, range {results['progress_min']}-{results['progress_max']}")
print(f"4. Tabs: {results.get('tab_count', 'N/A')} - {results.get('tab_names', [])}")
print(f"5. Menu bar: {results['menubar']}, Status bar: {results['statusbar']}")
print(f"6. Line edits: {results['lineedit_count']} - placeholders: {results['lineedit_placeholder'][:5]}")
print(f"7. Spin boxes: {results['spin_info']}")

print("\n=== RECOMMENDED ENHANCEMENTS ===")
print("1. Add drag-drop visual feedback (highlight on drop)")
print("2. Add keyboard shortcuts help dialog (F1 or Ctrl+/)")
print("3. Add progress percentage text to progress bar")
print("4. Add status bar messages with operation details")
print("5. Add tool panel enable/disable based on file state")
print("6. Add preview zoom controls")
print("7. Add file type validation on drop")
print("8. Add recent files menu")