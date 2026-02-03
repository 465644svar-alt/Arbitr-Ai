"""Router for managing message flow between components."""

from typing import Callable, Dict, List, Optional
from models.message import Message, MessageType
from models.role import Role


class Router:
    """
    Routes messages between different components of the system.
    Manages connections and message distribution.
    """

    def __init__(self, logger=None):
        self.logger = logger
        self.connections: List[str] = []
        self.message_handlers: Dict[MessageType, List[Callable]] = {
            MessageType.USER: [],
            MessageType.SYSTEM: [],
            MessageType.ARBITER: [],
            MessageType.AI_RESPONSE: [],
            MessageType.ROLE_TASK: []
        }
        self.active_connections: Dict[str, bool] = {}

    def add_connection(self, connection: str) -> bool:
        """
        Add a new connection.

        Args:
            connection: Connection identifier

        Returns:
            True if connection was added successfully
        """
        if connection in self.connections:
            if self.logger:
                self.logger.log(f"Соединение уже существует: {connection}")
            return False

        self.connections.append(connection)
        self.active_connections[connection] = True

        if self.logger:
            self.logger.log(f"Добавлено соединение: {connection}")

        return True

    def remove_connection(self, connection: str) -> bool:
        """Remove a connection."""
        if connection in self.connections:
            self.connections.remove(connection)
            self.active_connections.pop(connection, None)

            if self.logger:
                self.logger.log(f"Удалено соединение: {connection}")

            return True

        return False

    def register_handler(
        self,
        message_type: MessageType,
        handler: Callable[[Message], None]
    ) -> None:
        """
        Register a message handler for a specific message type.

        Args:
            message_type: Type of message to handle
            handler: Callback function
        """
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []

        self.message_handlers[message_type].append(handler)

        if self.logger:
            self.logger.log(f"Зарегистрирован обработчик для {message_type.value}")

    def route_message(self, message: Message) -> None:
        """
        Route a message to appropriate handlers.

        Args:
            message: Message to route
        """
        if self.logger:
            self.logger.log(f"Маршрутизация сообщения: {message.message_type.value}")

        handlers = self.message_handlers.get(message.message_type, [])

        for handler in handlers:
            try:
                handler(message)
            except Exception as e:
                if self.logger:
                    self.logger.log(f"Ошибка обработчика: {str(e)}")

    def broadcast_to_roles(self, message: Message, roles: List[Role]) -> List[Message]:
        """
        Broadcast a message to all active roles.

        Args:
            message: Message to broadcast
            roles: List of roles to send to

        Returns:
            List of simulated responses
        """
        if self.logger:
            self.logger.log(f"Broadcast сообщения к {len(roles)} ролям")

        responses = []

        for role in roles:
            # Simulate response - in real implementation would call actual AI APIs
            response = Message(
                content=f"[Симуляция ответа от {role.model}]",
                message_type=MessageType.AI_RESPONSE,
                sender=role.name,
                metadata={"role": role.name, "model": role.model}
            )
            responses.append(response)

        if self.logger:
            self.logger.log(f"Получено {len(responses)} ответов")

        return responses

    def get_connections(self) -> List[str]:
        """Get all connections."""
        return self.connections.copy()

    def get_active_connections(self) -> List[str]:
        """Get only active connections."""
        return [conn for conn, active in self.active_connections.items() if active]

    def set_connection_status(self, connection: str, active: bool) -> None:
        """Set connection status."""
        if connection in self.connections:
            self.active_connections[connection] = active
            status = "активно" if active else "неактивно"

            if self.logger:
                self.logger.log(f"Соединение '{connection}': {status}")
