"""Logging system for the application."""

from datetime import datetime
from typing import List, Callable, Optional
from pathlib import Path


class Logger:
    """Application logger with export capabilities."""

    def __init__(self):
        self.logs: List[str] = []
        self.callbacks: List[Callable[[str], None]] = []

    def log(self, message: str) -> None:
        """Add a log entry."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)

        # Notify all callbacks
        for callback in self.callbacks:
            callback(log_entry)

    def register_callback(self, callback: Callable[[str], None]) -> None:
        """Register a callback to be called when new log is added."""
        self.callbacks.append(callback)

    def clear(self) -> None:
        """Clear all logs."""
        self.logs.clear()
        self.log("Логи очищены")

    def export(self, filepath: Optional[str] = None) -> str:
        """Export logs to a file."""
        if filepath is None:
            filepath = f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(self.logs))
            self.log(f"Логи экспортированы в {filepath}")
            return filepath
        except Exception as e:
            error_msg = f"Ошибка экспорта логов: {str(e)}"
            self.log(error_msg)
            raise Exception(error_msg)

    def get_logs(self) -> List[str]:
        """Get all log entries."""
        return self.logs.copy()

    def get_recent_logs(self, count: int = 100) -> List[str]:
        """Get recent log entries."""
        return self.logs[-count:]
