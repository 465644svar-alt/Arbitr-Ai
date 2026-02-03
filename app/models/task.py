"""Task and Prohibition models."""

from datetime import datetime
from typing import Optional


class Task:
    """Represents a task for neural network algorithm."""

    def __init__(
        self,
        content: str,
        timestamp: Optional[str] = None
    ):
        self.content = content
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convert task to dictionary."""
        return {
            "content": self.content,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Create task from dictionary."""
        return cls(
            content=data["content"],
            timestamp=data.get("timestamp")
        )

    def __str__(self) -> str:
        return self.content[:50] + ("..." if len(self.content) > 50 else "")


class Prohibition:
    """Represents a prohibition/restriction for prompts."""

    def __init__(
        self,
        content: str,
        timestamp: Optional[str] = None
    ):
        self.content = content
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convert prohibition to dictionary."""
        return {
            "content": self.content,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Prohibition':
        """Create prohibition from dictionary."""
        return cls(
            content=data["content"],
            timestamp=data.get("timestamp")
        )

    def __str__(self) -> str:
        return self.content[:50] + ("..." if len(self.content) > 50 else "")
