"""Roles tab - manage AI roles and prompts."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QComboBox, QGroupBox, QListWidget, QMessageBox
)
from PySide6.QtCore import Signal


class RolesTab(QWidget):
    """Tab for managing AI roles."""

    # Signals
    role_created = Signal(str)
    role_updated = Signal(int)
    role_deleted = Signal(int)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("<h2>I Роль</h2>")
        layout.addWidget(title)

        # Role necessity section
        necessity_group = self._create_necessity_section()
        layout.addWidget(necessity_group)

        # Model selection
        model_group = self._create_model_section()
        layout.addWidget(model_group)

        # Creation section
        creation_group = self._create_creation_section()
        layout.addWidget(creation_group)

        # Roles list
        roles_group = self._create_roles_list()
        layout.addWidget(roles_group)

        layout.addStretch()

    def _create_necessity_section(self) -> QGroupBox:
        """Create role necessity section."""
        group = QGroupBox("1. Надобности свой пройт")
        layout = QVBoxLayout()

        self.necessity_input = QTextEdit()
        self.necessity_input.setPlaceholderText("Опишите необходимость роли...")
        self.necessity_input.setMaximumHeight(100)
        layout.addWidget(self.necessity_input)

        group.setLayout(layout)
        return group

    def _create_model_section(self) -> QGroupBox:
        """Create model selection section."""
        group = QGroupBox("2. Выбор модели (заглавный/заутверждённый)")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Выберите модель:"))

        self.model_combo = QComboBox()
        settings = self.controller.get_settings()
        self.model_combo.addItems(settings.get("available_models", []))
        layout.addWidget(self.model_combo)

        group.setLayout(layout)
        return group

    def _create_creation_section(self) -> QGroupBox:
        """Create prompt creation section."""
        group = QGroupBox("3. Промпт (каждой нейросети своё ''создание'' возможность изменить)")
        layout = QVBoxLayout()

        self.creation_input = QTextEdit()
        self.creation_input.setPlaceholderText("Введите промпт для создания...")
        layout.addWidget(self.creation_input)

        # Buttons
        btn_layout = QHBoxLayout()

        save_btn = QPushButton("Сохранить создание")
        save_btn.clicked.connect(self._on_save_role)
        btn_layout.addWidget(save_btn)

        edit_btn = QPushButton("Изменить создание")
        edit_btn.clicked.connect(self._on_edit_role)
        btn_layout.addWidget(edit_btn)

        layout.addLayout(btn_layout)
        group.setLayout(layout)
        return group

    def _create_roles_list(self) -> QGroupBox:
        """Create saved roles list."""
        group = QGroupBox("Сохранённые роли")
        layout = QVBoxLayout()

        self.roles_list = QListWidget()
        self.roles_list.itemClicked.connect(self._on_role_selected)
        layout.addWidget(self.roles_list)

        # Delete button
        delete_btn = QPushButton("Удалить роль")
        delete_btn.clicked.connect(self._on_delete_role)
        layout.addWidget(delete_btn)

        group.setLayout(layout)
        return group

    def _on_save_role(self):
        """Handle saving a new role."""
        necessity = self.necessity_input.toPlainText().strip()
        model = self.model_combo.currentText()
        creation = self.creation_input.toPlainText().strip()

        if not necessity or not creation:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        # Add role through controller
        role = self.controller.add_role(necessity, model, creation)

        # Update list
        self.roles_list.addItem(str(role))

        # Clear inputs
        self.necessity_input.clear()
        self.creation_input.clear()

        QMessageBox.information(self, "Успех", f"Роль сохранена: {role.name}")
        self.role_created.emit(role.name)

    def _on_edit_role(self):
        """Handle editing an existing role."""
        current_row = self.roles_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите роль для редактирования")
            return

        necessity = self.necessity_input.toPlainText().strip()
        model = self.model_combo.currentText()
        creation = self.creation_input.toPlainText().strip()

        if not necessity or not creation:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        # Update role through controller
        role = self.controller.update_role(current_row, necessity, model, creation)

        if role:
            # Update list
            self.roles_list.item(current_row).setText(str(role))
            QMessageBox.information(self, "Успех", f"Роль обновлена: {role.name}")
            self.role_updated.emit(current_row)

    def _on_delete_role(self):
        """Handle deleting a role."""
        current_row = self.roles_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите роль для удаления")
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить эту роль?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.controller.delete_role(current_row):
                self.roles_list.takeItem(current_row)
                self._clear_inputs()
                self.role_deleted.emit(current_row)

    def _on_role_selected(self, item):
        """Handle role selection from list."""
        row = self.roles_list.row(item)
        roles = self.controller.get_roles()

        if 0 <= row < len(roles):
            role = roles[row]
            self.necessity_input.setPlainText(role.necessity)
            self.model_combo.setCurrentText(role.model)
            self.creation_input.setPlainText(role.creation)

    def _clear_inputs(self):
        """Clear all input fields."""
        self.necessity_input.clear()
        self.creation_input.clear()

    def load_roles(self):
        """Load roles from controller."""
        self.roles_list.clear()
        roles = self.controller.get_roles()
        for role in roles:
            self.roles_list.addItem(str(role))
