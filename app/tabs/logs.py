"""Logs tab - application logging display."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QMessageBox
)
from PySide6.QtCore import Signal


class LogsTab(QWidget):
    """Tab for viewing application logs."""

    # Signals
    logs_cleared = Signal()
    logs_exported = Signal(str)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._setup_ui()
        self._register_log_callback()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("<h2>Логи работы приложения</h2>")
        layout.addWidget(title)

        # Controls
        controls_layout = self._create_controls()
        layout.addLayout(controls_layout)

        # Logs display
        self.logs_display = QTextEdit()
        self.logs_display.setReadOnly(True)
        self.logs_display.setStyleSheet(
            "background-color: #000; color: #0f0; "
            "font-family: 'Courier New'; font-size: 10pt;"
        )
        layout.addWidget(self.logs_display)

    def _create_controls(self) -> QHBoxLayout:
        """Create control buttons."""
        layout = QHBoxLayout()

        clear_btn = QPushButton("Очистить логи")
        clear_btn.clicked.connect(self._on_clear_logs)
        layout.addWidget(clear_btn)

        export_btn = QPushButton("Экспортировать логи")
        export_btn.clicked.connect(self._on_export_logs)
        layout.addWidget(export_btn)

        layout.addStretch()

        return layout

    def _register_log_callback(self):
        """Register callback to receive new log entries."""
        self.controller.logger.register_callback(self._on_new_log)

    def _on_new_log(self, log_entry: str):
        """Handle new log entry."""
        self.logs_display.append(log_entry)

    def _on_clear_logs(self):
        """Handle clearing logs."""
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите очистить все логи?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.controller.logger.clear()
            self.logs_display.clear()
            self.logs_cleared.emit()

    def _on_export_logs(self):
        """Handle exporting logs."""
        try:
            filename = self.controller.logger.export()
            QMessageBox.information(
                self,
                "Успех",
                f"Логи экспортированы в {filename}"
            )
            self.logs_exported.emit(filename)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось экспортировать логи: {str(e)}"
            )

    def load_logs(self):
        """Load existing logs into display."""
        self.logs_display.clear()
        logs = self.controller.logger.get_logs()
        for log in logs:
            self.logs_display.append(log)
