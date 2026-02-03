from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QLineEdit, QTextEdit, QListWidget, QComboBox,
    QCheckBox, QGroupBox, QFormLayout, QTableWidget, QTableWidgetItem,
    QMessageBox, QSplitter, QStatusBar
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QColor
from datetime import datetime
import json


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Арбитр - Система управления чатами")
        self.resize(1200, 800)

        # Initialize data storage
        self.connections = []
        self.roles = []
        self.prohibitions = []
        self.tasks = []
        self.logs = []

        # Connection status
        self.is_connected = False

        self._setup_ui()
        self._setup_menubar()
        self._setup_statusbar()

    def _setup_menubar(self):
        """Setup menu bar"""
        # File menu
        file_menu = self.menuBar().addMenu("Файл")

        act_save = QAction("Сохранить", self)
        act_save.triggered.connect(self.save_data)
        file_menu.addAction(act_save)

        act_load = QAction("Загрузить", self)
        act_load.triggered.connect(self.load_data)
        file_menu.addAction(act_load)

        file_menu.addSeparator()

        act_exit = QAction("Выход", self)
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        # Help menu
        help_menu = self.menuBar().addMenu("Помощь")
        act_about = QAction("О программе", self)
        act_about.triggered.connect(self.show_about)
        help_menu.addAction(act_about)

    def _setup_statusbar(self):
        """Setup status bar with connection indicator"""
        self.status_label = QLabel("Готово")
        self.statusBar().addWidget(self.status_label)

        # Connection indicator
        self.connection_indicator = QLabel()
        self.update_connection_status(False)
        self.statusBar().addPermanentWidget(self.connection_indicator)

    def _setup_ui(self):
        """Setup the main UI with tabs"""
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Create tab widget
        self.tabs = QTabWidget()

        # Add all tabs
        self.tabs.addTab(self._create_client_chat_tab(), "Клиентский чат")
        self.tabs.addTab(self._create_main_chat_tab(), "Основной чат")
        self.tabs.addTab(self._create_role_tab(), "I Роль")
        self.tabs.addTab(self._create_prohibitions_tab(), "II Запреты/Задачи")
        self.tabs.addTab(self._create_settings_tab(), "Настройки")
        self.tabs.addTab(self._create_logs_tab(), "Логи работы приложения")

        layout.addWidget(self.tabs)
        self.setCentralWidget(central_widget)

    def _create_client_chat_tab(self):
        """Create Client Chat tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("<h2>Клиентский чат</h2>")
        layout.addWidget(title)

        # Add connection section
        conn_group = QGroupBox("1. Добавление соединения")
        conn_layout = QVBoxLayout()

        self.conn_input = QLineEdit()
        self.conn_input.setPlaceholderText("Введите URL или имя соединения")
        conn_layout.addWidget(self.conn_input)

        add_conn_btn = QPushButton("Добавить соединение")
        add_conn_btn.clicked.connect(self.add_connection)
        conn_layout.addWidget(add_conn_btn)

        self.conn_list = QListWidget()
        conn_layout.addWidget(QLabel("Активные соединения:"))
        conn_layout.addWidget(self.conn_list)

        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)

        # Search section
        search_group = QGroupBox("2. Вопрос (поиск фильтров+процедура поиска)")
        search_layout = QVBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите поисковый запрос")
        search_layout.addWidget(self.search_input)

        search_btn = QPushButton("Поиск")
        search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(search_btn)

        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # Team calls section
        calls_group = QGroupBox("3. Командный вызов (с самым строгим процессом)")
        calls_layout = QVBoxLayout()

        self.team_calls_list = QListWidget()
        calls_layout.addWidget(QLabel("Список командных вызовов:"))
        calls_layout.addWidget(self.team_calls_list)

        add_call_btn = QPushButton("Добавить командный вызов")
        add_call_btn.clicked.connect(self.add_team_call)
        calls_layout.addWidget(add_call_btn)

        calls_group.setLayout(calls_layout)
        layout.addWidget(calls_group)

        # Start button
        start_btn = QPushButton("4. /start - вся вкладка роли отправилась")
        start_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;")
        start_btn.clicked.connect(self.start_all_roles)
        layout.addWidget(start_btn)

        layout.addStretch()
        return widget

    def _create_main_chat_tab(self):
        """Create Main Chat tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("<h2>Основной чат</h2>")
        layout.addWidget(title)

        # Chat display
        chat_group = QGroupBox("Чат (роли/этапы выделяются отдельно/дата-время)")
        chat_layout = QVBoxLayout()

        self.main_chat_display = QTextEdit()
        self.main_chat_display.setReadOnly(True)
        chat_layout.addWidget(self.main_chat_display)

        chat_group.setLayout(chat_layout)
        layout.addWidget(chat_group)

        # Question answering section
        qa_group = QGroupBox("1. Ответы всех нейросетей")
        qa_layout = QVBoxLayout()

        self.qa_display = QTextEdit()
        self.qa_display.setReadOnly(True)
        self.qa_display.setPlaceholderText("Здесь будут отображаться ответы от всех нейросетей")
        qa_layout.addWidget(self.qa_display)

        qa_group.setLayout(qa_layout)
        layout.addWidget(qa_group)

        # Role tasks
        role_task_group = QGroupBox("2. Роль-задание (обратная связь от нейросети что роль задаёт)")
        role_task_layout = QVBoxLayout()

        self.role_task_display = QTextEdit()
        self.role_task_display.setReadOnly(True)
        role_task_layout.addWidget(self.role_task_display)

        role_task_group.setLayout(role_task_layout)
        layout.addWidget(role_task_group)

        # Input section
        input_layout = QHBoxLayout()
        self.main_chat_input = QLineEdit()
        self.main_chat_input.setPlaceholderText("Введите сообщение...")
        input_layout.addWidget(self.main_chat_input)

        send_btn = QPushButton("Отправить")
        send_btn.clicked.connect(self.send_main_chat_message)
        input_layout.addWidget(send_btn)

        layout.addLayout(input_layout)

        return widget

    def _create_role_tab(self):
        """Create Role (I) tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("<h2>I Роль</h2>")
        layout.addWidget(title)

        # Role necessity section
        necessity_group = QGroupBox("1. Надобности свой пройт")
        necessity_layout = QVBoxLayout()

        self.role_necessity = QTextEdit()
        self.role_necessity.setPlaceholderText("Опишите необходимость роли...")
        necessity_layout.addWidget(self.role_necessity)

        necessity_group.setLayout(necessity_layout)
        layout.addWidget(necessity_group)

        # Model selection
        model_group = QGroupBox("2. Выбор модели (заглавный/заутверждённый)")
        model_layout = QVBoxLayout()

        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "GPT-4",
            "GPT-3.5-turbo",
            "Claude-3",
            "Claude-2",
            "PaLM-2",
            "Gemini Pro"
        ])
        model_layout.addWidget(QLabel("Выберите модель:"))
        model_layout.addWidget(self.model_combo)

        model_group.setLayout(model_layout)
        layout.addWidget(model_group)

        # Creation section
        creation_group = QGroupBox("3. Промпт (каждой нейросети своё ''создание'' возможность изменить)")
        creation_layout = QVBoxLayout()

        self.creation_text = QTextEdit()
        self.creation_text.setPlaceholderText("Введите промпт для создания...")
        creation_layout.addWidget(self.creation_text)

        btn_layout = QHBoxLayout()
        save_creation_btn = QPushButton("Сохранить создание")
        save_creation_btn.clicked.connect(self.save_role_creation)
        btn_layout.addWidget(save_creation_btn)

        edit_creation_btn = QPushButton("Изменить создание")
        edit_creation_btn.clicked.connect(self.edit_role_creation)
        btn_layout.addWidget(edit_creation_btn)

        creation_layout.addLayout(btn_layout)
        creation_group.setLayout(creation_layout)
        layout.addWidget(creation_group)

        # Roles list
        roles_group = QGroupBox("Сохранённые роли")
        roles_layout = QVBoxLayout()

        self.roles_list = QListWidget()
        roles_layout.addWidget(self.roles_list)

        roles_group.setLayout(roles_layout)
        layout.addWidget(roles_group)

        layout.addStretch()
        return widget

    def _create_prohibitions_tab(self):
        """Create Prohibitions/Tasks (II) tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("<h2>II Запреты/Задачи</h2>")
        layout.addWidget(title)

        # Prohibitions section
        prohib_group = QGroupBox("1. окно со списком о запретен (промпта)")
        prohib_layout = QVBoxLayout()

        self.prohibition_input = QTextEdit()
        self.prohibition_input.setPlaceholderText("Введите запрет...")
        prohib_layout.addWidget(self.prohibition_input)

        add_prohib_btn = QPushButton("Добавить запрет")
        add_prohib_btn.clicked.connect(self.add_prohibition)
        prohib_layout.addWidget(add_prohib_btn)

        self.prohibitions_list = QListWidget()
        prohib_layout.addWidget(QLabel("Список запретов:"))
        prohib_layout.addWidget(self.prohibitions_list)

        prohib_group.setLayout(prohib_layout)
        layout.addWidget(prohib_group)

        # Tasks section
        tasks_group = QGroupBox("2. Задача запрета (алгоритма ответа нейросети)")
        tasks_layout = QVBoxLayout()

        self.task_input = QTextEdit()
        self.task_input.setPlaceholderText("Опишите задачу запрета...")
        tasks_layout.addWidget(self.task_input)

        add_task_btn = QPushButton("Добавить задачу")
        add_task_btn.clicked.connect(self.add_task)
        tasks_layout.addWidget(add_task_btn)

        self.tasks_list = QListWidget()
        tasks_layout.addWidget(QLabel("Список задач:"))
        tasks_layout.addWidget(self.tasks_list)

        tasks_group.setLayout(tasks_layout)
        layout.addWidget(tasks_group)

        # Report section
        report_group = QGroupBox("3. Создание отчёта запрета (алгоритма ответа нейросети)")
        report_layout = QVBoxLayout()

        generate_report_btn = QPushButton("Сгенерировать отчёт")
        generate_report_btn.clicked.connect(self.generate_prohibition_report)
        report_layout.addWidget(generate_report_btn)

        self.prohibition_report = QTextEdit()
        self.prohibition_report.setReadOnly(True)
        report_layout.addWidget(self.prohibition_report)

        report_group.setLayout(report_layout)
        layout.addWidget(report_group)

        return widget

    def _create_settings_tab(self):
        """Create Settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("<h2>Настройки</h2>")
        layout.addWidget(title)

        # API Settings
        api_group = QGroupBox("1. API настройки")
        api_layout = QFormLayout()

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Введите API ключ")
        api_layout.addRow("API Key:", self.api_key_input)

        self.api_endpoint_input = QLineEdit()
        self.api_endpoint_input.setPlaceholderText("https://api.example.com")
        api_layout.addRow("API Endpoint:", self.api_endpoint_input)

        self.api_timeout_input = QLineEdit()
        self.api_timeout_input.setText("30")
        api_layout.addRow("Timeout (сек):", self.api_timeout_input)

        save_api_btn = QPushButton("Сохранить API настройки")
        save_api_btn.clicked.connect(self.save_api_settings)
        api_layout.addRow(save_api_btn)

        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # Connection indicator
        conn_group = QGroupBox("2. Индикатор соединения")
        conn_layout = QVBoxLayout()

        self.connection_status_label = QLabel("Статус: Отключено")
        self.connection_status_label.setStyleSheet("padding: 10px; background-color: #f44336; color: white;")
        conn_layout.addWidget(self.connection_status_label)

        test_conn_btn = QPushButton("Проверить соединение")
        test_conn_btn.clicked.connect(self.test_connection)
        conn_layout.addWidget(test_conn_btn)

        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)

        # Save/Load settings
        save_group = QGroupBox("3. Сохранение")
        save_layout = QVBoxLayout()

        self.auto_save_checkbox = QCheckBox("Автоматическое сохранение")
        save_layout.addWidget(self.auto_save_checkbox)

        save_settings_btn = QPushButton("Сохранить все настройки")
        save_settings_btn.clicked.connect(self.save_all_settings)
        save_layout.addWidget(save_settings_btn)

        load_settings_btn = QPushButton("Загрузить настройки")
        load_settings_btn.clicked.connect(self.load_settings)
        save_layout.addWidget(load_settings_btn)

        save_group.setLayout(save_layout)
        layout.addWidget(save_group)

        layout.addStretch()
        return widget

    def _create_logs_tab(self):
        """Create Application Logs tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("<h2>Логи работы приложения</h2>")
        layout.addWidget(title)

        # Controls
        controls_layout = QHBoxLayout()

        clear_logs_btn = QPushButton("Очистить логи")
        clear_logs_btn.clicked.connect(self.clear_logs)
        controls_layout.addWidget(clear_logs_btn)

        export_logs_btn = QPushButton("Экспортировать логи")
        export_logs_btn.clicked.connect(self.export_logs)
        controls_layout.addWidget(export_logs_btn)

        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # Logs display
        self.logs_display = QTextEdit()
        self.logs_display.setReadOnly(True)
        self.logs_display.setStyleSheet("background-color: #000; color: #0f0; font-family: 'Courier New';")
        layout.addWidget(self.logs_display)

        return widget

    # Event handlers
    def add_connection(self):
        """Add a new connection"""
        conn = self.conn_input.text().strip()
        if not conn:
            QMessageBox.warning(self, "Ошибка", "Введите соединение")
            return

        self.connections.append(conn)
        self.conn_list.addItem(conn)
        self.conn_input.clear()
        self.log(f"Добавлено соединение: {conn}")
        self.status_label.setText(f"Добавлено соединение: {conn}")

    def perform_search(self):
        """Perform search"""
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Ошибка", "Введите поисковый запрос")
            return

        self.log(f"Выполнен поиск: {query}")
        QMessageBox.information(self, "Поиск", f"Поиск выполнен для: {query}\n\n(Здесь будут результаты поиска)")
        self.status_label.setText(f"Поиск выполнен: {query}")

    def add_team_call(self):
        """Add team call"""
        call_name = f"Командный вызов #{self.team_calls_list.count() + 1}"
        self.team_calls_list.addItem(call_name)
        self.log(f"Добавлен {call_name}")
        self.status_label.setText(f"Добавлен {call_name}")

    def start_all_roles(self):
        """Start all roles"""
        if len(self.roles) == 0:
            QMessageBox.warning(self, "Ошибка", "Нет доступных ролей. Создайте роли на вкладке 'I Роль'")
            return

        self.log("Запущены все роли")
        msg = f"Отправлено {len(self.roles)} ролей:\n\n"
        for role in self.roles:
            msg += f"- {role['name']}\n"

        QMessageBox.information(self, "/start", msg)
        self.status_label.setText("Все роли отправлены")

    def send_main_chat_message(self):
        """Send message in main chat"""
        msg = self.main_chat_input.text().strip()
        if not msg:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_msg = f"[{timestamp}] Пользователь: {msg}\n"
        self.main_chat_display.append(formatted_msg)
        self.main_chat_input.clear()
        self.log(f"Сообщение в основном чате: {msg}")

        # Simulate response from arbitrator
        QTimer.singleShot(1000, lambda: self.arbitrator_response(msg))

    def arbitrator_response(self, original_msg):
        """Simulate arbitrator GPT response"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response = f"[{timestamp}] Арбитр GPT: Проверка вопроса/ответов нейросетей... ✓\n"
        self.main_chat_display.append(response)

        # Show in QA display
        self.qa_display.append(f"[{timestamp}] Ответ на: {original_msg}\n")
        self.qa_display.append("GPT-4: [Симуляция ответа GPT-4]\n")
        self.qa_display.append("Claude: [Симуляция ответа Claude]\n\n")

        self.log(f"Арбитр обработал запрос: {original_msg}")

    def save_role_creation(self):
        """Save role creation"""
        necessity = self.role_necessity.toPlainText().strip()
        model = self.model_combo.currentText()
        creation = self.creation_text.toPlainText().strip()

        if not necessity or not creation:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        role = {
            "name": f"Роль #{len(self.roles) + 1}",
            "necessity": necessity,
            "model": model,
            "creation": creation,
            "timestamp": datetime.now().isoformat()
        }

        self.roles.append(role)
        self.roles_list.addItem(f"{role['name']} ({model})")
        self.log(f"Сохранена роль: {role['name']}")

        QMessageBox.information(self, "Успех", f"Роль сохранена: {role['name']}")
        self.status_label.setText(f"Сохранена роль: {role['name']}")

    def edit_role_creation(self):
        """Edit role creation"""
        if self.roles_list.currentRow() < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите роль для редактирования")
            return

        idx = self.roles_list.currentRow()
        role = self.roles[idx]

        self.role_necessity.setPlainText(role["necessity"])
        self.model_combo.setCurrentText(role["model"])
        self.creation_text.setPlainText(role["creation"])

        self.log(f"Редактирование роли: {role['name']}")
        self.status_label.setText(f"Редактирование: {role['name']}")

    def add_prohibition(self):
        """Add prohibition"""
        text = self.prohibition_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите запрет")
            return

        self.prohibitions.append(text)
        self.prohibitions_list.addItem(text[:50] + "..." if len(text) > 50 else text)
        self.prohibition_input.clear()
        self.log(f"Добавлен запрет: {text[:50]}")
        self.status_label.setText("Запрет добавлен")

    def add_task(self):
        """Add task"""
        text = self.task_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите задачу")
            return

        self.tasks.append(text)
        self.tasks_list.addItem(text[:50] + "..." if len(text) > 50 else text)
        self.task_input.clear()
        self.log(f"Добавлена задача: {text[:50]}")
        self.status_label.setText("Задача добавлена")

    def generate_prohibition_report(self):
        """Generate prohibition report"""
        if not self.prohibitions and not self.tasks:
            QMessageBox.warning(self, "Ошибка", "Нет запретов или задач для отчёта")
            return

        report = "=== ОТЧЁТ О ЗАПРЕТАХ И ЗАДАЧАХ ===\n\n"
        report += f"Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        report += "ЗАПРЕТЫ:\n"
        for i, prohib in enumerate(self.prohibitions, 1):
            report += f"{i}. {prohib}\n\n"

        report += "\nЗАДАЧИ:\n"
        for i, task in enumerate(self.tasks, 1):
            report += f"{i}. {task}\n\n"

        report += "=== КОНЕЦ ОТЧЁТА ==="

        self.prohibition_report.setPlainText(report)
        self.log("Сгенерирован отчёт о запретах и задачах")
        self.status_label.setText("Отчёт сгенерирован")

    def save_api_settings(self):
        """Save API settings"""
        api_key = self.api_key_input.text().strip()
        endpoint = self.api_endpoint_input.text().strip()
        timeout = self.api_timeout_input.text().strip()

        if not api_key or not endpoint:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля API")
            return

        self.log(f"API настройки сохранены: endpoint={endpoint}, timeout={timeout}")
        QMessageBox.information(self, "Успех", "API настройки сохранены")
        self.status_label.setText("API настройки сохранены")

    def test_connection(self):
        """Test connection"""
        # Simulate connection test
        self.is_connected = not self.is_connected
        self.update_connection_status(self.is_connected)

        status = "Подключено" if self.is_connected else "Отключено"
        self.log(f"Тест соединения: {status}")
        QMessageBox.information(self, "Тест соединения", f"Статус: {status}")

    def update_connection_status(self, connected):
        """Update connection status indicator"""
        if connected:
            self.connection_indicator.setText("● Подключено")
            self.connection_indicator.setStyleSheet("color: green; font-weight: bold;")
            self.connection_status_label.setText("Статус: Подключено")
            self.connection_status_label.setStyleSheet("padding: 10px; background-color: #4CAF50; color: white;")
        else:
            self.connection_indicator.setText("● Отключено")
            self.connection_indicator.setStyleSheet("color: red; font-weight: bold;")
            self.connection_status_label.setText("Статус: Отключено")
            self.connection_status_label.setStyleSheet("padding: 10px; background-color: #f44336; color: white;")

    def save_all_settings(self):
        """Save all settings"""
        settings = {
            "api_key": self.api_key_input.text(),
            "api_endpoint": self.api_endpoint_input.text(),
            "api_timeout": self.api_timeout_input.text(),
            "auto_save": self.auto_save_checkbox.isChecked(),
            "connections": self.connections,
            "roles": self.roles,
            "prohibitions": self.prohibitions,
            "tasks": self.tasks
        }

        try:
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            self.log("Все настройки сохранены в settings.json")
            QMessageBox.information(self, "Успех", "Все настройки сохранены")
            self.status_label.setText("Настройки сохранены")
        except Exception as e:
            self.log(f"Ошибка сохранения настроек: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить настройки: {str(e)}")

    def load_settings(self):
        """Load settings"""
        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                settings = json.load(f)

            self.api_key_input.setText(settings.get("api_key", ""))
            self.api_endpoint_input.setText(settings.get("api_endpoint", ""))
            self.api_timeout_input.setText(settings.get("api_timeout", "30"))
            self.auto_save_checkbox.setChecked(settings.get("auto_save", False))

            self.connections = settings.get("connections", [])
            self.roles = settings.get("roles", [])
            self.prohibitions = settings.get("prohibitions", [])
            self.tasks = settings.get("tasks", [])

            # Update UI lists
            self.conn_list.clear()
            for conn in self.connections:
                self.conn_list.addItem(conn)

            self.roles_list.clear()
            for role in self.roles:
                self.roles_list.addItem(f"{role['name']} ({role['model']})")

            self.prohibitions_list.clear()
            for prohib in self.prohibitions:
                self.prohibitions_list.addItem(prohib[:50] + "..." if len(prohib) > 50 else prohib)

            self.tasks_list.clear()
            for task in self.tasks:
                self.tasks_list.addItem(task[:50] + "..." if len(task) > 50 else task)

            self.log("Настройки загружены из settings.json")
            QMessageBox.information(self, "Успех", "Настройки загружены")
            self.status_label.setText("Настройки загружены")
        except FileNotFoundError:
            self.log("Файл settings.json не найден")
            QMessageBox.warning(self, "Внимание", "Файл настроек не найден")
        except Exception as e:
            self.log(f"Ошибка загрузки настроек: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить настройки: {str(e)}")

    def log(self, message):
        """Add message to logs"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        self.logs_display.append(log_entry)

    def clear_logs(self):
        """Clear logs"""
        self.logs.clear()
        self.logs_display.clear()
        self.log("Логи очищены")

    def export_logs(self):
        """Export logs to file"""
        try:
            filename = f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(self.logs))
            self.log(f"Логи экспортированы в {filename}")
            QMessageBox.information(self, "Успех", f"Логи экспортированы в {filename}")
            self.status_label.setText(f"Логи экспортированы: {filename}")
        except Exception as e:
            self.log(f"Ошибка экспорта логов: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать логи: {str(e)}")

    def save_data(self):
        """Save all data"""
        self.save_all_settings()

    def load_data(self):
        """Load all data"""
        self.load_settings()

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "О программе",
            "<h2>Арбитр - Система управления чатами</h2>"
            "<p>Версия 1.0.0</p>"
            "<p>Система для управления множественными чатами с нейросетями, "
            "включающая арбитража ответов через GPT.</p>"
            "<p><b>Возможности:</b></p>"
            "<ul>"
            "<li>Управление клиентскими чатами</li>"
            "<li>Основной чат с мультимодельной поддержкой</li>"
            "<li>Управление ролями и промптами</li>"
            "<li>Система запретов и задач</li>"
            "<li>Арбитраж ответов через GPT</li>"
            "<li>Полное логирование</li>"
            "</ul>"
        )
