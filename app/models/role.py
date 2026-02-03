"""Role model for managing AI roles and prompts."""

from datetime import datetime
from typing import Optional


class Role:
    """Represents an AI role with associated configuration."""

    def __init__(
        self,
        name: str,
        necessity: str,
        model: str,
        creation: str,
        timestamp: Optional[str] = None
    ):
        self.name = name
        self.necessity = necessity
        self.model = model
        self.creation = creation
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convert role to dictionary."""
        return {
            "name": self.name,
            "necessity": self.necessity,
            "model": self.model,
            "creation": self.creation,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Role':
        """Create role from dictionary."""
        return cls(
            name=data["name"],
            necessity=data["necessity"],
            model=data["model"],
            creation=data["creation"],
            timestamp=data.get("timestamp")
        )

    def __str__(self) -> str:
        return f"{self.name} ({self.model})"
