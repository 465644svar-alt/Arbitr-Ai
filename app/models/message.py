"""Message model for chat communication."""

from datetime import datetime
from typing import Optional
from enum import Enum


class MessageType(Enum):
    """Types of messages in the system."""
    USER = "user"
    SYSTEM = "system"
    ARBITER = "arbiter"
    AI_RESPONSE = "ai_response"
    ROLE_TASK = "role_task"


class Message:
    """Represents a chat message."""

    def __init__(
        self,
        content: str,
        message_type: MessageType = MessageType.USER,
        sender: str = "Пользователь",
        timestamp: Optional[str] = None,
        metadata: Optional[dict] = None
    ):
        self.content = content
        self.message_type = message_type
        self.sender = sender
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        """Convert message to dictionary."""
        return {
            "content": self.content,
            "message_type": self.message_type.value,
            "sender": self.sender,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """Create message from dictionary."""
        return cls(
            content=data["content"],
            message_type=MessageType(data["message_type"]),
            sender=data["sender"],
            timestamp=data.get("timestamp"),
            metadata=data.get("metadata", {})
        )

    def format(self) -> str:
        """Format message for display."""
        return f"[{self.timestamp}] {self.sender}: {self.content}"

    def __str__(self) -> str:
        return self.format()
