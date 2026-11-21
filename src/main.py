import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.ui.main_window import MainWindow
from src.ui.theme import apply_theme


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PDF Toolkit")
    # Version: update src/__version__.py and change this string
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("deba608")

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