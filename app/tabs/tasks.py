"""Tasks tab - manage prohibitions and tasks."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTextEdit, QGroupBox, QListWidget, QMessageBox
)
from PySide6.QtCore import Signal


class TasksTab(QWidget):
    """Tab for managing prohibitions and tasks."""

    # Signals
    prohibition_added = Signal(str)
    task_added = Signal(str)
    report_generated = Signal(str)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("<h2>II Запреты/Задачи</h2>")
        layout.addWidget(title)

        # Prohibitions section
        prohib_group = self._create_prohibitions_section()
        layout.addWidget(prohib_group)

        # Tasks section
        tasks_group = self._create_tasks_section()
        layout.addWidget(tasks_group)

        # Report section
        report_group = self._create_report_section()
        layout.addWidget(report_group)

    def _create_prohibitions_section(self) -> QGroupBox:
        """Create prohibitions management section."""
        group = QGroupBox("1. окно со списком о запретен (промпта)")
        layout = QVBoxLayout()

        self.prohibition_input = QTextEdit()
        self.prohibition_input.setPlaceholderText("Введите запрет...")
        self.prohibition_input.setMaximumHeight(80)
        layout.addWidget(self.prohibition_input)

        add_btn = QPushButton("Добавить запрет")
        add_btn.clicked.connect(self._on_add_prohibition)
        layout.addWidget(add_btn)

        layout.addWidget(QLabel("Список запретов:"))

        self.prohibitions_list = QListWidget()
        layout.addWidget(self.prohibitions_list)

        delete_btn = QPushButton("Удалить запрет")
        delete_btn.clicked.connect(self._on_delete_prohibition)
        layout.addWidget(delete_btn)

        group.setLayout(layout)
        return group

    def _create_tasks_section(self) -> QGroupBox:
        """Create tasks management section."""
        group = QGroupBox("2. Задача запрета (алгоритма ответа нейросети)")
        layout = QVBoxLayout()

        self.task_input = QTextEdit()
        self.task_input.setPlaceholderText("Опишите задачу запрета...")
        self.task_input.setMaximumHeight(80)
        layout.addWidget(self.task_input)

        add_btn = QPushButton("Добавить задачу")
        add_btn.clicked.connect(self._on_add_task)
        layout.addWidget(add_btn)

        layout.addWidget(QLabel("Список задач:"))

        self.tasks_list = QListWidget()
        layout.addWidget(self.tasks_list)

        delete_btn = QPushButton("Удалить задачу")
        delete_btn.clicked.connect(self._on_delete_task)
        layout.addWidget(delete_btn)

        group.setLayout(layout)
        return group

    def _create_report_section(self) -> QGroupBox:
        """Create report generation section."""
        group = QGroupBox("3. Создание отчёта запрета (алгоритма ответа нейросети)")
        layout = QVBoxLayout()

        generate_btn = QPushButton("Сгенерировать отчёт")
        generate_btn.clicked.connect(self._on_generate_report)
        layout.addWidget(generate_btn)

        self.report_display = QTextEdit()
        self.report_display.setReadOnly(True)
        layout.addWidget(self.report_display)

        group.setLayout(layout)
        return group

    def _on_add_prohibition(self):
        """Handle adding a prohibition."""
        text = self.prohibition_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите запрет")
            return

        # Add through controller
        prohibition = self.controller.add_prohibition(text)

        # Update list
        self.prohibitions_list.addItem(str(prohibition))
        self.prohibition_input.clear()

        self.prohibition_added.emit(text)

    def _on_delete_prohibition(self):
        """Handle deleting a prohibition."""
        current_row = self.prohibitions_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запрет для удаления")
            return

        if self.controller.delete_prohibition(current_row):
            self.prohibitions_list.takeItem(current_row)

    def _on_add_task(self):
        """Handle adding a task."""
        text = self.task_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите задачу")
            return

        # Add through controller
        task = self.controller.add_task(text)

        # Update list
        self.tasks_list.addItem(str(task))
        self.task_input.clear()

        self.task_added.emit(text)

    def _on_delete_task(self):
        """Handle deleting a task."""
        current_row = self.tasks_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите задачу для удаления")
            return

        if self.controller.delete_task(current_row):
            self.tasks_list.takeItem(current_row)

    def _on_generate_report(self):
        """Handle generating a report."""
        prohibitions = self.controller.get_prohibitions()
        tasks = self.controller.get_tasks()

        if not prohibitions and not tasks:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Нет запретов или задач для отчёта"
            )
            return

        # Generate report through controller
        report = self.controller.generate_prohibition_report()

        # Display report
        self.report_display.setPlainText(report)

        self.report_generated.emit(report)

    def load_data(self):
        """Load prohibitions and tasks from controller."""
        # Load prohibitions
        self.prohibitions_list.clear()
        prohibitions = self.controller.get_prohibitions()
        for prohib in prohibitions:
            self.prohibitions_list.addItem(str(prohib))

        # Load tasks
        self.tasks_list.clear()
        tasks = self.controller.get_tasks()
        for task in tasks:
            self.tasks_list.addItem(str(task))
