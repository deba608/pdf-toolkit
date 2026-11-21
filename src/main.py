import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.ui.main_window import MainWindow
from src import __version__


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PDF Toolkit")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("deba608")

    # High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()