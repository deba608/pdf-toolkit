import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from src.ui.main_window import MainWindow
from src.ui.theme import apply_theme


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PDF Toolkit")
    # Version: update src/__version__.py and change this string
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("deba608")

    # Set application icon (for taskbar, window, alt-tab, etc.)
    icon_path = Path(__file__).parent / "resources" / "icon.ico"
    if icon_path.exists():
        app_icon = QIcon(str(icon_path))
        app.setWindowIcon(app_icon)

    # High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    apply_theme(app)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()