"""Main Chat tab - primary chat interface with AI responses."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QGroupBox
)
from PySide6.QtCore import Signal, QTimer


class MainChatTab(QWidget):
    """Tab for main chat interface."""

    # Signals
    message_sent = Signal(str)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("<h2>Основной чат</h2>")
        layout.addWidget(title)

        # Main chat display
        chat_group = self._create_chat_display()
        layout.addWidget(chat_group)

        # AI responses section
        qa_group = self._create_qa_section()
        layout.addWidget(qa_group)

        # Role task section
        role_task_group = self._create_role_task_section()
        layout.addWidget(role_task_group)

        # Input section
        input_layout = self._create_input_section()
        layout.addLayout(input_layout)

    def _create_chat_display(self) -> QGroupBox:
        """Create main chat display section."""
        group = QGroupBox("Чат (роли/этапы выделяются отдельно/дата-время)")
        layout = QVBoxLayout()

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        group.setLayout(layout)
        return group

    def _create_qa_section(self) -> QGroupBox:
        """Create Q&A display section."""
        group = QGroupBox("1. Ответы всех нейросетей")
        layout = QVBoxLayout()

        self.qa_display = QTextEdit()
        self.qa_display.setReadOnly(True)
        self.qa_display.setPlaceholderText(
            "Здесь будут отображаться ответы от всех нейросетей"
        )
        layout.addWidget(self.qa_display)

        group.setLayout(layout)
        return group

    def _create_role_task_section(self) -> QGroupBox:
        """Create role task section."""
        group = QGroupBox("2. Роль-задание (обратная связь от нейросети что роль задаёт)")
        layout = QVBoxLayout()

        self.role_task_display = QTextEdit()
        self.role_task_display.setReadOnly(True)
        layout.addWidget(self.role_task_display)

        group.setLayout(layout)
        return group

    def _create_input_section(self) -> QHBoxLayout:
        """Create input section."""
        layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Введите сообщение...")
        self.message_input.returnPressed.connect(self._on_send_message)
        layout.addWidget(self.message_input)

        send_btn = QPushButton("Отправить")
        send_btn.clicked.connect(self._on_send_message)
        layout.addWidget(send_btn)

        return layout

    def _on_send_message(self):
        """Handle sending a message."""
        text = self.message_input.text().strip()
        if not text:
            return

        # Send message through controller
        message = self.controller.send_message(text)

        # Display in chat
        self.chat_display.append(message.format())
        self.message_input.clear()

        # Emit signal
        self.message_sent.emit(text)

        # Simulate arbiter response after delay
        QTimer.singleShot(1000, lambda: self._show_responses(text))

    def _show_responses(self, original_msg: str):
        """Show AI responses and arbiter feedback."""
        messages = self.controller.get_messages()

        # Get recent AI responses
        ai_responses = [m for m in messages if m.message_type.value == "ai_response"]
        arbiter_messages = [m for m in messages if m.message_type.value == "arbiter"]

        # Display in chat
        if arbiter_messages:
            latest_arbiter = arbiter_messages[-1]
            self.chat_display.append(latest_arbiter.format())

        # Display AI responses
        if ai_responses:
            self.qa_display.clear()
            for response in ai_responses[-len(self.controller.get_roles()):]:
                self.qa_display.append(f"{response.format()}\n")

            # Update role task display
            self.role_task_display.append(
                f"[{response.timestamp}] Роли обработали запрос: {original_msg}\n"
            )

    def clear_chat(self):
        """Clear all chat displays."""
        self.chat_display.clear()
        self.qa_display.clear()
        self.role_task_display.clear()
