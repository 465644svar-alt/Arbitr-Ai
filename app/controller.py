"""Main controller coordinating all application components."""

from typing import List, Dict, Optional
import json
from pathlib import Path

from models.role import Role
from models.task import Task, Prohibition
from models.message import Message, MessageType
from logger import Logger
from arbiter import Arbiter
from router import Router


class Controller:
    """
    Main application controller that coordinates all components.
    Manages state, handles business logic, and coordinates data flow.
    """

    def __init__(self):
        # Initialize core components
        self.logger = Logger()
        self.arbiter = Arbiter(self.logger)
        self.router = Router(self.logger)

        # Initialize data
        self.roles: List[Role] = []
        self.tasks: List[Task] = []
        self.prohibitions: List[Prohibition] = []
        self.messages: List[Message] = []
        self.settings: Dict = self._load_default_settings()

        # Connection status
        self.is_connected = False

        self.logger.log("Контроллер инициализирован")

    def _load_default_settings(self) -> Dict:
        """Load default settings."""
        return {
            "api_key": "",
            "api_endpoint": "https://api.openai.com/v1",
            "api_timeout": 30,
            "auto_save": False,
            "access_key": "",
            "available_models": [
                "GPT-4",
                "GPT-3.5-turbo",
                "Claude-3",
                "Claude-2",
                "PaLM-2",
                "Gemini Pro"
            ]
        }

    # Role Management
    def add_role(self, necessity: str, model: str, creation: str) -> Role:
        """Add a new role."""
        role_name = f"Роль #{len(self.roles) + 1}"
        role = Role(
            name=role_name,
            necessity=necessity,
            model=model,
            creation=creation
        )
        self.roles.append(role)
        self.logger.log(f"Добавлена роль: {role_name} ({model})")
        return role

    def get_roles(self) -> List[Role]:
        """Get all roles."""
        return self.roles.copy()

    def update_role(self, index: int, necessity: str, model: str, creation: str) -> Optional[Role]:
        """Update an existing role."""
        if 0 <= index < len(self.roles):
            self.roles[index].necessity = necessity
            self.roles[index].model = model
            self.roles[index].creation = creation
            self.logger.log(f"Обновлена роль: {self.roles[index].name}")
            return self.roles[index]
        return None

    def delete_role(self, index: int) -> bool:
        """Delete a role."""
        if 0 <= index < len(self.roles):
            role = self.roles.pop(index)
            self.logger.log(f"Удалена роль: {role.name}")
            return True
        return False

    def start_all_roles(self) -> List[Role]:
        """Start all configured roles."""
        if not self.roles:
            self.logger.log("Нет ролей для запуска")
            return []

        self.arbiter.set_active_roles(self.roles)
        self.logger.log(f"Запущено {len(self.roles)} ролей")
        return self.roles

    # Task Management
    def add_task(self, content: str) -> Task:
        """Add a new task."""
        task = Task(content=content)
        self.tasks.append(task)
        self.logger.log(f"Добавлена задача: {str(task)}")
        return task

    def get_tasks(self) -> List[Task]:
        """Get all tasks."""
        return self.tasks.copy()

    def delete_task(self, index: int) -> bool:
        """Delete a task."""
        if 0 <= index < len(self.tasks):
            task = self.tasks.pop(index)
            self.logger.log(f"Удалена задача: {str(task)}")
            return True
        return False

    # Prohibition Management
    def add_prohibition(self, content: str) -> Prohibition:
        """Add a new prohibition."""
        prohibition = Prohibition(content=content)
        self.prohibitions.append(prohibition)
        self.arbiter.add_validation_rule(content)
        self.logger.log(f"Добавлен запрет: {str(prohibition)}")
        return prohibition

    def get_prohibitions(self) -> List[Prohibition]:
        """Get all prohibitions."""
        return self.prohibitions.copy()

    def delete_prohibition(self, index: int) -> bool:
        """Delete a prohibition."""
        if 0 <= index < len(self.prohibitions):
            prohibition = self.prohibitions.pop(index)
            self.logger.log(f"Удален запрет: {str(prohibition)}")
            return True
        return False

    def generate_prohibition_report(self) -> str:
        """Generate report of prohibitions and tasks."""
        from datetime import datetime

        report = "=== ОТЧЁТ О ЗАПРЕТАХ И ЗАДАЧАХ ===\n\n"
        report += f"Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        report += "ЗАПРЕТЫ:\n"
        for i, prohib in enumerate(self.prohibitions, 1):
            report += f"{i}. {prohib.content}\n\n"

        report += "\nЗАДАЧИ:\n"
        for i, task in enumerate(self.tasks, 1):
            report += f"{i}. {task.content}\n\n"

        report += "=== КОНЕЦ ОТЧЁТА ==="

        self.logger.log("Сгенерирован отчёт о запретах и задачах")
        return report

    # Message Management
    def send_message(self, content: str) -> Message:
        """Send a user message and get responses."""
        # Create user message
        message = Message(content=content, message_type=MessageType.USER)
        self.messages.append(message)
        self.logger.log(f"Отправлено сообщение: {content[:50]}...")

        # Validate message
        if not self.arbiter.validate_message(message):
            self.logger.log("Сообщение не прошло валидацию")
            return message

        # Route to roles
        if self.roles:
            responses = self.router.broadcast_to_roles(message, self.roles)
            self.messages.extend(responses)

            # Arbitrate responses
            response_dicts = [
                {"model": r.metadata.get("model"), "content": r.content}
                for r in responses
            ]
            arbitration = self.arbiter.arbitrate_responses(response_dicts)

            # Create arbiter message
            arbiter_msg = Message(
                content=f"Проверка вопроса/ответов нейросетей... ✓",
                message_type=MessageType.ARBITER,
                sender="Арбитр GPT"
            )
            self.messages.append(arbiter_msg)

        return message

    def get_messages(self) -> List[Message]:
        """Get all messages."""
        return self.messages.copy()

    # Connection Management
    def add_connection(self, connection: str) -> bool:
        """Add a connection."""
        return self.router.add_connection(connection)

    def get_connections(self) -> List[str]:
        """Get all connections."""
        return self.router.get_connections()

    def test_connection(self) -> bool:
        """Test connection (simulated)."""
        self.is_connected = not self.is_connected
        status = "Подключено" if self.is_connected else "Отключено"
        self.logger.log(f"Тест соединения: {status}")
        return self.is_connected

    # Settings Management
    def update_settings(self, settings: Dict) -> None:
        """Update application settings."""
        self.settings.update(settings)
        self.logger.log("Настройки обновлены")

    def get_settings(self) -> Dict:
        """Get current settings."""
        return self.settings.copy()

    # Data Persistence
    def save_data(self, filepath: str = "settings.json") -> None:
        """Save all data to file."""
        data = {
            "settings": self.settings,
            "roles": [r.to_dict() for r in self.roles],
            "tasks": [t.to_dict() for t in self.tasks],
            "prohibitions": [p.to_dict() for p in self.prohibitions],
            "connections": self.router.get_connections()
        }

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.log(f"Данные сохранены в {filepath}")
        except Exception as e:
            self.logger.log(f"Ошибка сохранения данных: {str(e)}")
            raise

    def load_data(self, filepath: str = "settings.json") -> None:
        """Load data from file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Load settings
            if "settings" in data:
                self.settings.update(data["settings"])

            # Load roles
            if "roles" in data:
                self.roles = [Role.from_dict(r) for r in data["roles"]]

            # Load tasks
            if "tasks" in data:
                self.tasks = [Task.from_dict(t) for t in data["tasks"]]

            # Load prohibitions
            if "prohibitions" in data:
                self.prohibitions = [Prohibition.from_dict(p) for p in data["prohibitions"]]
                # Re-add validation rules
                for prohib in self.prohibitions:
                    self.arbiter.add_validation_rule(prohib.content)

            # Load connections
            if "connections" in data:
                for conn in data["connections"]:
                    self.router.add_connection(conn)

            self.logger.log(f"Данные загружены из {filepath}")
        except FileNotFoundError:
            self.logger.log(f"Файл {filepath} не найден")
            raise
        except Exception as e:
            self.logger.log(f"Ошибка загрузки данных: {str(e)}")
            raise
