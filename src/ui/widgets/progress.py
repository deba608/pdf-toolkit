from PySide6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor


class ProgressWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.jobs_list = QListWidget()
        layout.addWidget(self.jobs_list)

    def add_job(self, job_id: str, operation: str):
        item = QListWidgetItem(f"{operation} — Starting...")
        item.setData(Qt.UserRole, job_id)
        self.jobs_list.addItem(item)
        self.jobs_list.setCurrentItem(item)

    def update_job(self, job_id: str, progress: int, status: str):
        for i in range(self.jobs_list.count()):
            item = self.jobs_list.item(i)
            if item.data(Qt.UserRole) == job_id:
                item.setText(f"{item.text().split(' — ')[0]} — {progress}% {status}")
                break