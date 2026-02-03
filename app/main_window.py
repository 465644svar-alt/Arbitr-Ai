"""Main application window."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QLabel, QStatusBar, QMessageBox, QInputDialog, QLineEdit
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

from controller import Controller
from tabs.client_chat import ClientChatTab
from tabs.main_chat import MainChatTab
from tabs.roles import RolesTab
from tabs.tasks import TasksTab
from tabs.settings import SettingsTab
from tabs.logs import LogsTab


class MainWindow(QMainWindow):
    """Main application window with tabbed interface."""

    def __init__(self):
        super().__init__()

        # Initialize controller
        self.controller = Controller()
        self._load_settings_on_startup()

        # Setup UI
        self.setWindowTitle("Арбитр - Система управления чатами")
        self.resize(1200, 800)

        self._setup_ui()
        self._setup_menubar()
        self._setup_statusbar()
        self._connect_signals()

        # Log initialization
        self.controller.logger.log("Приложение запущено")
        self.access_granted = self._require_access_key()

    def _setup_ui(self):
        """Setup the main user interface."""
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Create tab widget
        self.tabs = QTabWidget()

        # Create and add all tabs
        self.client_chat_tab = ClientChatTab(self.controller)
        self.main_chat_tab = MainChatTab(self.controller)
        self.roles_tab = RolesTab(self.controller)
        self.tasks_tab = TasksTab(self.controller)
        self.settings_tab = SettingsTab(self.controller)
        self.logs_tab = LogsTab(self.controller)

        self.tabs.addTab(self.client_chat_tab, "Клиентский чат")
        self.tabs.addTab(self.main_chat_tab, "Основной чат")
        self.tabs.addTab(self.roles_tab, "I Роль")
        self.tabs.addTab(self.tasks_tab, "II Запреты/Задачи")
        self.tabs.addTab(self.settings_tab, "Настройки")
        self.tabs.addTab(self.logs_tab, "Логи работы приложения")

        layout.addWidget(self.tabs)
        self.setCentralWidget(central_widget)

    def _setup_menubar(self):
        """Setup menu bar."""
        # File menu
        file_menu = self.menuBar().addMenu("Файл")

        save_action = QAction("Сохранить", self)
        save_action.triggered.connect(self._on_save)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)

        load_action = QAction("Загрузить", self)
        load_action.triggered.connect(self._on_load)
        load_action.setShortcut("Ctrl+L")
        file_menu.addAction(load_action)

        file_menu.addSeparator()

        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(exit_action)

        # View menu
        view_menu = self.menuBar().addMenu("Вид")

        for i, tab_name in enumerate([
            "Клиентский чат",
            "Основной чат",
            "I Роль",
            "II Запреты/Задачи",
            "Настройки",
            "Логи"
        ]):
            action = QAction(tab_name, self)
            action.triggered.connect(lambda checked, idx=i: self.tabs.setCurrentIndex(idx))
            view_menu.addAction(action)

        # Help menu
        help_menu = self.menuBar().addMenu("Помощь")

        about_action = QAction("О программе", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_statusbar(self):
        """Setup status bar."""
        self.status_label = QLabel("Готово")
        self.statusBar().addWidget(self.status_label)

        # Connection indicator
        self.connection_indicator = QLabel("● Отключено")
        self.connection_indicator.setStyleSheet("color: red; font-weight: bold;")
        self.statusBar().addPermanentWidget(self.connection_indicator)

    def _connect_signals(self):
        """Connect signals from tabs to handlers."""
        # Client Chat signals
        self.client_chat_tab.connection_added.connect(
            lambda conn: self._update_status(f"Добавлено соединение: {conn}")
        )
        self.client_chat_tab.search_requested.connect(
            lambda query: self._update_status(f"Поиск выполнен: {query}")
        )
        self.client_chat_tab.team_call_added.connect(
            lambda call: self._update_status(f"Добавлен {call}")
        )
        self.client_chat_tab.roles_started.connect(
            lambda: self._update_status("Все роли отправлены")
        )

        # Main Chat signals
        self.main_chat_tab.message_sent.connect(
            lambda msg: self._update_status(f"Сообщение отправлено: {msg[:30]}...")
        )

        # Roles signals
        self.roles_tab.role_created.connect(
            lambda name: self._update_status(f"Создана роль: {name}")
        )
        self.roles_tab.role_updated.connect(
            lambda idx: self._update_status(f"Роль обновлена")
        )
        self.roles_tab.role_deleted.connect(
            lambda idx: self._update_status(f"Роль удалена")
        )

        # Tasks signals
        self.tasks_tab.prohibition_added.connect(
            lambda: self._update_status("Запрет добавлен")
        )
        self.tasks_tab.task_added.connect(
            lambda: self._update_status("Задача добавлена")
        )
        self.tasks_tab.report_generated.connect(
            lambda: self._update_status("Отчёт сгенерирован")
        )

        # Settings signals
        self.settings_tab.settings_saved.connect(
            lambda: self._update_status("Настройки сохранены")
        )
        self.settings_tab.connection_tested.connect(
            self._update_connection_indicator
        )

        # Logs signals
        self.logs_tab.logs_cleared.connect(
            lambda: self._update_status("Логи очищены")
        )
        self.logs_tab.logs_exported.connect(
            lambda filename: self._update_status(f"Логи экспортированы: {filename}")
        )

    def _load_settings_on_startup(self):
        """Load saved settings if available."""
        try:
            self.controller.load_data()
        except FileNotFoundError:
            self.controller.logger.log("Файл настроек не найден при старте")

    def _require_access_key(self) -> bool:
        """Require access key if configured."""
        settings = self.controller.get_settings()
        access_key = settings.get("access_key", "").strip()
        if not access_key:
            return True

        entered_key, ok = QInputDialog.getText(
            self,
            "Доступ к приложению",
            "Введите ключ доступа из TG бота:",
            QLineEdit.Password
        )

        if not ok:
            QMessageBox.critical(
                self,
                "Доступ запрещен",
                "Запуск отменен без ключа доступа."
            )
            self.controller.logger.log("Доступ отменен пользователем")
            return False

        if entered_key.strip() != access_key:
            QMessageBox.critical(
                self,
                "Доступ запрещен",
                "Неверный ключ доступа."
            )
            self.controller.logger.log("Введен неверный ключ доступа")
            return False

        self.controller.logger.log("Ключ доступа подтвержден")
        return True

    def _update_status(self, message: str):
        """Update status bar message."""
        self.status_label.setText(message)

    def _update_connection_indicator(self, connected: bool):
        """Update connection indicator."""
        if connected:
            self.connection_indicator.setText("● Подключено")
            self.connection_indicator.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.connection_indicator.setText("● Отключено")
            self.connection_indicator.setStyleSheet("color: red; font-weight: bold;")

    def _on_save(self):
        """Handle save action."""
        try:
            self.controller.save_data()
            QMessageBox.information(
                self,
                "Успех",
                "Все данные сохранены в settings.json"
            )
            self._update_status("Данные сохранены")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось сохранить данные: {str(e)}"
            )

    def _on_load(self):
        """Handle load action."""
        try:
            self.controller.load_data()

            # Reload all tabs
            self.client_chat_tab.load_connections()
            self.roles_tab.load_roles()
            self.tasks_tab.load_data()
            self.settings_tab._load_settings()
            self.logs_tab.load_logs()

            QMessageBox.information(
                self,
                "Успех",
                "Данные загружены из settings.json"
            )
            self._update_status("Данные загружены")

        except FileNotFoundError:
            QMessageBox.warning(
                self,
                "Внимание",
                "Файл settings.json не найден"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить данные: {str(e)}"
            )

    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "О программе",
            "<h2>Арбитр - Система управления чатами</h2>"
            "<p><b>Версия:</b> 2.0.0</p>"
            "<p>Система для управления множественными чатами с нейросетями, "
            "включающая арбитраж ответов через GPT.</p>"
            "<p><b>Возможности:</b></p>"
            "<ul>"
            "<li>Управление клиентскими чатами</li>"
            "<li>Основной чат с мультимодельной поддержкой</li>"
            "<li>Управление ролями и промптами</li>"
            "<li>Система запретов и задач</li>"
            "<li>Арбитраж ответов через GPT</li>"
            "<li>Полное логирование</li>"
            "</ul>"
            "<p><b>Архитектура:</b> Модульная структура с MVC паттерном</p>"
        )

    def closeEvent(self, event):
        """Handle window close event."""
        settings = self.controller.get_settings()

        if settings.get("auto_save", False):
            try:
                self.controller.save_data()
                self.controller.logger.log("Автоматическое сохранение при выходе")
            except Exception as e:
                self.controller.logger.log(f"Ошибка автосохранения: {str(e)}")

        self.controller.logger.log("Приложение закрыто")
        event.accept()
