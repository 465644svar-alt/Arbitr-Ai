"""Client Chat tab - displays connection and processing status."""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QTextEdit,
    QGridLayout,
)
from PySide6.QtCore import Signal


class ClientChatTab(QWidget):
    """Tab for client chat management."""

    # Signals
    send_request_clicked = Signal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.connection_labels = {}
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("<h2>Клиентский чат</h2>")
        layout.addWidget(title)

        # Connection indicators
        conn_group = self._create_connection_section()
        layout.addWidget(conn_group)

        # App status
        app_group = self._create_app_status_section()
        layout.addWidget(app_group)

        # Processing status
        processing_group = self._create_processing_section()
        layout.addWidget(processing_group)

        # Send request button
        send_btn = QPushButton("Отправить запрос")
        send_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; "
            "padding: 10px; font-weight: bold;"
        )
        send_btn.clicked.connect(self._on_send_request)
        layout.addWidget(send_btn)

        layout.addStretch()

    def _create_connection_section(self) -> QGroupBox:
        """Create connection indicators section."""
        group = QGroupBox("1. Индикаторы соединения")
        layout = QGridLayout()

        models = self.controller.get_settings().get("available_models", [])
        for row, model in enumerate(models):
            name_label = QLabel(model)
            status_label = QLabel()
            status_label.setFixedWidth(120)
            self.connection_labels[model] = status_label
            layout.addWidget(name_label, row, 0)
            layout.addWidget(status_label, row, 1)

        refresh_btn = QPushButton("Обновить индикаторы")
        refresh_btn.clicked.connect(self.refresh_connection_indicators)
        layout.addWidget(refresh_btn, len(models), 0, 1, 2)

        group.setLayout(layout)
        self.refresh_connection_indicators()
        return group

    def _create_app_status_section(self) -> QGroupBox:
        """Create application status section."""
        group = QGroupBox("2. Видимость работы приложения")
        layout = QVBoxLayout()

        self.app_status_label = QLabel("Статус: Активно")
        self.app_status_label.setStyleSheet(
            "padding: 6px; background-color: #2196F3; color: white;"
        )
        layout.addWidget(self.app_status_label)

        group.setLayout(layout)
        return group

    def _create_processing_section(self) -> QGroupBox:
        """Create processing status section."""
        group = QGroupBox("3. Процесс обработки запроса")
        layout = QVBoxLayout()

        self.processing_display = QTextEdit()
        self.processing_display.setReadOnly(True)
        self.processing_display.setMinimumHeight(120)
        self.processing_display.setText(self.controller.get_processing_status())
        layout.addWidget(self.processing_display)

        status_btn = QPushButton("Показать статус обработки")
        status_btn.clicked.connect(self.refresh_processing_status)
        layout.addWidget(status_btn)

        group.setLayout(layout)
        return group

    def _on_send_request(self):
        """Emit signal to send request."""
        self.send_request_clicked.emit()

    def refresh_connection_indicators(self):
        """Refresh connection indicator labels."""
        statuses = self.controller.get_model_statuses()
        for model, label in self.connection_labels.items():
            connected = statuses.get(model, False)
            label.setText("Подключено" if connected else "Отключено")
            label.setStyleSheet(
                "padding: 4px; background-color: #4CAF50; color: white;"
                if connected
                else "padding: 4px; background-color: #f44336; color: white;"
            )

    def refresh_processing_status(self):
        """Refresh processing status display."""
        self.processing_display.setText(self.controller.get_processing_status())
