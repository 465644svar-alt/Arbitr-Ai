"""
Арбитр - Система управления чатами

Десктопное приложение для управления множественными чатами с нейросетями,
включающее арбитраж ответов через GPT.
"""

import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow


def main():
    """Main application entry point."""
    # Create application
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("Арбитр")
    app.setOrganizationName("Arbitr-AI")
    app.setApplicationVersion("2.0.0")

    # Create and show main window
    window = MainWindow()
    if not window.access_granted:
        sys.exit(0)

    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
