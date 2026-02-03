"""Settings tab - application configuration."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QGroupBox, QFormLayout, QCheckBox, QMessageBox
)
from PySide6.QtCore import Signal


class SettingsTab(QWidget):
    """Tab for application settings."""

    # Signals
    settings_saved = Signal(dict)
    connection_tested = Signal(bool)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("<h2>Настройки</h2>")
        layout.addWidget(title)

        # API settings
        api_group = self._create_api_section()
        layout.addWidget(api_group)

        # Access settings
        access_group = self._create_access_section()
        layout.addWidget(access_group)

        # Connection indicator
        conn_group = self._create_connection_section()
        layout.addWidget(conn_group)

        # Save/Load settings
        save_group = self._create_save_section()
        layout.addWidget(save_group)

        layout.addStretch()

    def _create_api_section(self) -> QGroupBox:
        """Create API settings section."""
        group = QGroupBox("1. API настройки")
        layout = QFormLayout()

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Введите API ключ")
        layout.addRow("API Key:", self.api_key_input)

        self.api_endpoint_input = QLineEdit()
        self.api_endpoint_input.setPlaceholderText("https://api.example.com")
        layout.addRow("API Endpoint:", self.api_endpoint_input)

        self.api_timeout_input = QLineEdit()
        self.api_timeout_input.setText("30")
        layout.addRow("Timeout (сек):", self.api_timeout_input)

        save_api_btn = QPushButton("Сохранить API настройки")
        save_api_btn.clicked.connect(self._on_save_api_settings)
        layout.addRow(save_api_btn)

        group.setLayout(layout)
        return group

    def _create_access_section(self) -> QGroupBox:
        """Create access settings section."""
        group = QGroupBox("2. Доступ (TG бот)")
        layout = QFormLayout()

        self.access_key_input = QLineEdit()
        self.access_key_input.setEchoMode(QLineEdit.Password)
        self.access_key_input.setPlaceholderText("Введите ключ доступа")
        layout.addRow("Ключ доступа:", self.access_key_input)

        save_access_btn = QPushButton("Сохранить ключ доступа")
        save_access_btn.clicked.connect(self._on_save_access_settings)
        layout.addRow(save_access_btn)

        group.setLayout(layout)
        return group

    def _create_connection_section(self) -> QGroupBox:
        """Create connection indicator section."""
        group = QGroupBox("3. Индикатор соединения")
        layout = QVBoxLayout()

        self.connection_label = QLabel("Статус: Отключено")
        self.connection_label.setStyleSheet(
            "padding: 10px; background-color: #f44336; color: white;"
        )
        layout.addWidget(self.connection_label)

        test_btn = QPushButton("Проверить соединение")
        test_btn.clicked.connect(self._on_test_connection)
        layout.addWidget(test_btn)

        group.setLayout(layout)
        return group

    def _create_save_section(self) -> QGroupBox:
        """Create save/load section."""
        group = QGroupBox("4. Сохранение")
        layout = QVBoxLayout()

        self.auto_save_checkbox = QCheckBox("Автоматическое сохранение")
        layout.addWidget(self.auto_save_checkbox)

        btn_layout = QHBoxLayout()

        save_btn = QPushButton("Сохранить все настройки")
        save_btn.clicked.connect(self._on_save_all)
        btn_layout.addWidget(save_btn)

        load_btn = QPushButton("Загрузить настройки")
        load_btn.clicked.connect(self._on_load_settings)
        btn_layout.addWidget(load_btn)

        layout.addLayout(btn_layout)

        group.setLayout(layout)
        return group

    def _on_save_api_settings(self):
        """Handle saving API settings."""
        api_key = self.api_key_input.text().strip()
        endpoint = self.api_endpoint_input.text().strip()
        timeout = self.api_timeout_input.text().strip()

        if not api_key or not endpoint:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля API")
            return

        # Update settings
        settings = {
            "api_key": api_key,
            "api_endpoint": endpoint,
            "api_timeout": int(timeout) if timeout.isdigit() else 30
        }

        self.controller.update_settings(settings)
        QMessageBox.information(self, "Успех", "API настройки сохранены")

    def _on_save_access_settings(self):
        """Handle saving access settings."""
        access_key = self.access_key_input.text().strip()
        self.controller.update_settings({"access_key": access_key})
        QMessageBox.information(self, "Успех", "Ключ доступа сохранен")

    def _on_test_connection(self):
        """Handle connection test."""
        is_connected = self.controller.test_connection()
        self.update_connection_status(is_connected)

        status = "Подключено" if is_connected else "Отключено"
        QMessageBox.information(self, "Тест соединения", f"Статус: {status}")

        self.connection_tested.emit(is_connected)

    def update_connection_status(self, connected: bool):
        """Update connection status display."""
        if connected:
            self.connection_label.setText("Статус: Подключено")
            self.connection_label.setStyleSheet(
                "padding: 10px; background-color: #4CAF50; color: white;"
            )
        else:
            self.connection_label.setText("Статус: Отключено")
            self.connection_label.setStyleSheet(
                "padding: 10px; background-color: #f44336; color: white;"
            )

    def _on_save_all(self):
        """Handle saving all settings."""
        try:
            # Update auto-save setting
            settings = {
                "auto_save": self.auto_save_checkbox.isChecked()
            }
            self.controller.update_settings(settings)

            # Save all data
            self.controller.save_data()

            QMessageBox.information(self, "Успех", "Все настройки сохранены")
            self.settings_saved.emit(self.controller.get_settings())

        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось сохранить настройки: {str(e)}"
            )

    def _on_load_settings(self):
        """Handle loading settings."""
        try:
            self.controller.load_data()
            self._load_settings()

            QMessageBox.information(self, "Успех", "Настройки загружены")

        except FileNotFoundError:
            QMessageBox.warning(self, "Внимание", "Файл настроек не найден")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить настройки: {str(e)}"
            )

    def _load_settings(self):
        """Load settings into UI."""
        settings = self.controller.get_settings()

        self.api_key_input.setText(settings.get("api_key", ""))
        self.api_endpoint_input.setText(settings.get("api_endpoint", ""))
        self.api_timeout_input.setText(str(settings.get("api_timeout", 30)))
        self.auto_save_checkbox.setChecked(settings.get("auto_save", False))
        self.access_key_input.setText(settings.get("access_key", ""))
