"""Client Chat tab - manages connections, search, and team calls."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QGroupBox, QMessageBox
)
from PySide6.QtCore import Signal


class ClientChatTab(QWidget):
    """Tab for client chat management."""

    # Signals
    connection_added = Signal(str)
    search_requested = Signal(str)
    team_call_added = Signal(str)
    roles_started = Signal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("<h2>Клиентский чат</h2>")
        layout.addWidget(title)

        # Connection section
        conn_group = self._create_connection_section()
        layout.addWidget(conn_group)

        # Search section
        search_group = self._create_search_section()
        layout.addWidget(search_group)

        # Team calls section
        calls_group = self._create_team_calls_section()
        layout.addWidget(calls_group)

        # Start button
        start_btn = QPushButton("4. /start - вся вкладка роли отправилась")
        start_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; "
            "padding: 10px; font-weight: bold;"
        )
        start_btn.clicked.connect(self._on_start_roles)
        layout.addWidget(start_btn)

        layout.addStretch()

    def _create_connection_section(self) -> QGroupBox:
        """Create connection management section."""
        group = QGroupBox("1. Добавление соединения")
        layout = QVBoxLayout()

        self.conn_input = QLineEdit()
        self.conn_input.setPlaceholderText("Введите URL или имя соединения")
        self.conn_input.returnPressed.connect(self._on_add_connection)
        layout.addWidget(self.conn_input)

        add_btn = QPushButton("Добавить соединение")
        add_btn.clicked.connect(self._on_add_connection)
        layout.addWidget(add_btn)

        self.conn_list = QListWidget()
        layout.addWidget(QLabel("Активные соединения:"))
        layout.addWidget(self.conn_list)

        # Add delete button
        delete_btn = QPushButton("Удалить соединение")
        delete_btn.clicked.connect(self._on_delete_connection)
        layout.addWidget(delete_btn)

        group.setLayout(layout)
        return group

    def _create_search_section(self) -> QGroupBox:
        """Create search section."""
        group = QGroupBox("2. Вопрос (поиск фильтров+процедура поиска)")
        layout = QVBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите поисковый запрос")
        self.search_input.returnPressed.connect(self._on_search)
        layout.addWidget(self.search_input)

        search_btn = QPushButton("Поиск")
        search_btn.clicked.connect(self._on_search)
        layout.addWidget(search_btn)

        group.setLayout(layout)
        return group

    def _create_team_calls_section(self) -> QGroupBox:
        """Create team calls section."""
        group = QGroupBox("3. Командный вызов (с самым строгим процессом)")
        layout = QVBoxLayout()

        self.team_calls_list = QListWidget()
        layout.addWidget(QLabel("Список командных вызовов:"))
        layout.addWidget(self.team_calls_list)

        add_btn = QPushButton("Добавить командный вызов")
        add_btn.clicked.connect(self._on_add_team_call)
        layout.addWidget(add_btn)

        delete_btn = QPushButton("Удалить командный вызов")
        delete_btn.clicked.connect(self._on_delete_team_call)
        layout.addWidget(delete_btn)

        group.setLayout(layout)
        return group

    def _on_add_connection(self):
        """Handle adding a connection."""
        conn = self.conn_input.text().strip()
        if not conn:
            QMessageBox.warning(self, "Ошибка", "Введите соединение")
            return

        if self.controller.add_connection(conn):
            self.conn_list.addItem(conn)
            self.conn_input.clear()
            self.connection_added.emit(conn)
        else:
            QMessageBox.warning(self, "Ошибка", "Соединение уже существует")

    def _on_delete_connection(self):
        """Handle deleting a connection."""
        current_item = self.conn_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Выберите соединение для удаления")
            return

        row = self.conn_list.currentRow()
        conn = current_item.text()
        self.controller.router.remove_connection(conn)
        self.conn_list.takeItem(row)

    def _on_search(self):
        """Handle search request."""
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Ошибка", "Введите поисковый запрос")
            return

        self.search_requested.emit(query)
        QMessageBox.information(
            self,
            "Поиск",
            f"Поиск выполнен для: {query}\n\n(Здесь будут результаты поиска)"
        )

    def _on_add_team_call(self):
        """Handle adding a team call."""
        call_name = f"Командный вызов #{self.team_calls_list.count() + 1}"
        self.team_calls_list.addItem(call_name)
        self.team_call_added.emit(call_name)

    def _on_delete_team_call(self):
        """Handle deleting a team call."""
        current_row = self.team_calls_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите вызов для удаления")
            return

        self.team_calls_list.takeItem(current_row)

    def _on_start_roles(self):
        """Handle starting all roles."""
        roles = self.controller.start_all_roles()

        if not roles:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Нет доступных ролей. Создайте роли на вкладке 'I Роль'"
            )
            return

        msg = f"Отправлено {len(roles)} ролей:\n\n"
        for role in roles:
            msg += f"- {role.name} ({role.model})\n"

        QMessageBox.information(self, "/start", msg)
        self.roles_started.emit()

    def load_connections(self):
        """Load connections from controller."""
        self.conn_list.clear()
        connections = self.controller.get_connections()
        for conn in connections:
            self.conn_list.addItem(conn)
