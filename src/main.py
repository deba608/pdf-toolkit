import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src.__version__ import __version__
from src.paths import resource_path
from src.ui.main_window import MainWindow
from src.ui.theme import apply_theme


def main():
    # Must be set before the QApplication exists, otherwise Qt ignores it.
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("PDF Toolkit")
    app.setApplicationDisplayName("PDF Toolkit")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("deba608")
    # Fusion renders the stylesheet consistently on every platform.
    app.setStyle("Fusion")

    icon_path = resource_path("icon.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    apply_theme(app)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
