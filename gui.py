import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QTextEdit,
    QVBoxLayout, QFileDialog, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QPixmap
from stegano import embed_message, extract_message

class StegApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Steganography Tool")
        self.setGeometry(300, 200, 600, 400)  # Ensure it appears centered

        self.image_path = None

        self.img_label = QLabel("No image selected")
        self.img_label.setFixedHeight(150)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Type your secret message here...")

        open_button = QPushButton("Open Image")
        embed_button = QPushButton("Embed && Save")
        extract_button = QPushButton("Extract")

        open_button.clicked.connect(self.open_image)
        embed_button.clicked.connect(self.embed_message)
        extract_button.clicked.connect(self.extract_message)

        layout = QVBoxLayout()
        layout.addWidget(self.img_label)
        layout.addWidget(self.text_edit)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(open_button)
        btn_layout.addWidget(embed_button)
        btn_layout.addWidget(extract_button)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def open_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.bmp)")
        if path:
            self.image_path = path
            self.img_label.setPixmap(QPixmap(path).scaledToHeight(150))

    def embed_message(self):
        if not self.image_path:
            QMessageBox.warning(self, "Error", "Select an image first.")
            return

        text = self.text_edit.toPlainText()
        if not text:
            QMessageBox.warning(self, "Error", "Please enter a message.")
            return

        out_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png)")
        if out_path:
            try:
                embed_message(self.image_path, out_path, text)
                QMessageBox.information(self, "Done", "Message embedded and saved!")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def extract_message(self):
        if not self.image_path:
            QMessageBox.warning(self, "Error", "Select an image first.")
            return
        try:
            msg = extract_message(self.image_path)
            QMessageBox.information(self, "Extracted Message", msg)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StegApp()
    window.show()
    sys.exit(app.exec_())