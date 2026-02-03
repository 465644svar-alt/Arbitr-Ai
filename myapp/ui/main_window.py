from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox
)
from PySide6.QtGui import QAction

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyApp")
        self.resize(900, 600)

        # --- Menu ---
        file_menu = self.menuBar().addMenu("Файл")
        act_exit = QAction("Выход", self)
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        # --- Status bar ---
        self.statusBar().showMessage("Готово")

        # --- Central UI ---
        root = QWidget()
        layout = QVBoxLayout(root)

        self.label = QLabel("Введите текст и нажмите кнопку:")
        self.input = QLineEdit()
        self.btn = QPushButton("Показать")
        self.btn.clicked.connect(self.on_show)

        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addWidget(self.btn)

        self.setCentralWidget(root)

    def on_show(self):
        text = self.input.text().strip()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите текст.")
            return
        QMessageBox.information(self, "Вы ввели", text)
        self.statusBar().showMessage("Показано сообщение", 2000)
