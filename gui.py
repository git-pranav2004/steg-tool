import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QTextEdit,
    QVBoxLayout, QFileDialog, QMessageBox, QHBoxLayout, QFrame,
    QProgressBar, QSplitter, QGroupBox, QScrollArea, QStatusBar,
    QMainWindow, QMenuBar, QAction, QToolBar
)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from stegano import embed_message, extract_message


class SteganoWorker(QThread):
    """Worker thread for steganography operations to prevent GUI freezing"""
    finished = pyqtSignal(str)  # Success message
    error = pyqtSignal(str)     # Error message
    progress = pyqtSignal(int)  # Progress value
    
    def __init__(self, operation, image_path, output_path=None, message=None):
        super().__init__()
        self.operation = operation
        self.image_path = image_path
        self.output_path = output_path
        self.message = message
    
    def run(self):
        try:
            if self.operation == "embed":
                self.progress.emit(25)
                embed_message(self.image_path, self.output_path, self.message)
                self.progress.emit(100)
                self.finished.emit("Message successfully embedded and saved!")
            elif self.operation == "extract":
                self.progress.emit(25)
                extracted_msg = extract_message(self.image_path)
                self.progress.emit(100)
                self.finished.emit(f"Extracted message: {extracted_msg}")
        except Exception as e:
            self.error.emit(str(e))


class StegApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_path = None
        self.worker = None
        self.init_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_status_bar()
        self.apply_dark_theme()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Steganography Tool - Hide Secrets in Images")
        self.setGeometry(200, 100, 1000, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main splitter for better layout management
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel for image preview
        left_panel = self.create_image_panel()
        
        # Right panel for controls
        right_panel = self.create_control_panel()
        
        # Add panels to splitter
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([500, 500])
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(main_splitter)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        central_widget.setLayout(main_layout)
    
    def create_image_panel(self):
        """Create the image preview panel"""
        group_box = QGroupBox("Image Preview")
        group_box.setFont(QFont("Segoe UI", 10, QFont.Bold))
        
        layout = QVBoxLayout()
        
        # Image display with scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumSize(400, 400)
        
        self.img_label = QLabel("No image selected\n\nClick 'Open Image' to get started")
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setMinimumSize(380, 380)
        self.img_label.setFrameShape(QFrame.Box)
        self.img_label.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                border: 2px dashed #555;
                color: #888;
                font-size: 14px;
                border-radius: 8px;
            }
        """)
        
        scroll_area.setWidget(self.img_label)
        layout.addWidget(scroll_area)
        
        # Image info label
        self.img_info_label = QLabel("No image loaded")
        self.img_info_label.setFont(QFont("Segoe UI", 9))
        self.img_info_label.setStyleSheet("color: #888; padding: 5px;")
        layout.addWidget(self.img_info_label)
        
        group_box.setLayout(layout)
        return group_box
    
    def create_control_panel(self):
        """Create the control panel with buttons and text area"""
        group_box = QGroupBox("Controls")
        group_box.setFont(QFont("Segoe UI", 10, QFont.Bold))
        
        layout = QVBoxLayout()
        
        # File operations group
        file_group = QGroupBox("File Operations")
        file_layout = QHBoxLayout()
        
        self.open_button = QPushButton("📂 Open Image")
        self.open_button.setToolTip("Select an image file to work with")
        self.open_button.clicked.connect(self.open_image)
        
        self.clear_button = QPushButton("🗑️ Clear")
        self.clear_button.setToolTip("Clear current image and message")
        self.clear_button.clicked.connect(self.clear_all)
        
        file_layout.addWidget(self.open_button)
        file_layout.addWidget(self.clear_button)
        file_group.setLayout(file_layout)
        
        # Message input group
        msg_group = QGroupBox("Secret Message")
        msg_layout = QVBoxLayout()
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("✍️  Type your secret message here...\n\nTip: Longer messages may affect image quality.")
        self.text_edit.setFont(QFont("Consolas", 10))
        self.text_edit.setMaximumHeight(150)
        
        # Character counter
        self.char_counter = QLabel("Characters: 0")
        self.char_counter.setFont(QFont("Segoe UI", 8))
        self.char_counter.setStyleSheet("color: #888;")
        self.text_edit.textChanged.connect(self.update_char_counter)
        
        msg_layout.addWidget(self.text_edit)
        msg_layout.addWidget(self.char_counter)
        msg_group.setLayout(msg_layout)
        
        # Operations group
        ops_group = QGroupBox("Steganography Operations")
        ops_layout = QVBoxLayout()
        
        self.embed_button = QPushButton("🧩 Embed Message & Save")
        self.embed_button.setToolTip("Hide the message in the image")
        self.embed_button.clicked.connect(self.embed_message)
        
        self.extract_button = QPushButton("🔍 Extract Message")
        self.extract_button.setToolTip("Extract hidden message from image")
        self.extract_button.clicked.connect(self.extract_message)
        
        ops_layout.addWidget(self.embed_button)
        ops_layout.addWidget(self.extract_button)
        ops_group.setLayout(ops_layout)
        
        # Apply button styling
        buttons = [self.open_button, self.clear_button, self.embed_button, self.extract_button]
        for btn in buttons:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(35)
            btn.setFont(QFont("Segoe UI", 10))
        
        # Add all groups to main layout
        layout.addWidget(file_group)
        layout.addWidget(msg_group)
        layout.addWidget(ops_group)
        layout.addStretch()
        
        group_box.setLayout(layout)
        return group_box
    
    def setup_menu(self):
        """Setup application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        open_action = QAction('Open Image', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Setup toolbar with quick actions"""
        toolbar = QToolBar()
        toolbar.setMovable(False)

        # Set toolbar button style to show text with white color
        toolbar.setStyleSheet("""
            QToolButton {
                color: white;
                font-weight: bold;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #444;
            }
        """)
        
        open_action = QAction('📂 Open', self)
        open_action.triggered.connect(self.open_image)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        embed_action = QAction('🧩 Embed', self)
        embed_action.triggered.connect(self.embed_message)
        toolbar.addAction(embed_action)
        
        extract_action = QAction('🔍 Extract', self)
        extract_action.triggered.connect(self.extract_message)
        toolbar.addAction(extract_action)
        
        self.addToolBar(toolbar)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")
        self.setStatusBar(self.status_bar)
    
    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #fbfbfb;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #2b2b2b;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #fbfbfb;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
            QTextEdit {
                background-color: #2b2b2b;
                color: #fbfbfb;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
            }
            QLabel {
                color: #000000;
            }
            QMenuBar {
                background-color: #2b2b2b;
                color: #fbfbfb;
            }
            QMenuBar::item:selected {
                background-color: #0078d7;
            }
            QMenu {
                background-color: #2b2b2b;
                color: #fbfbfb;
                border: 1px solid #555;
            }
            QMenu::item:selected {
                background-color: #0078d7;
            }
            QToolBar {
                background-color: #2b2b2b;
                border: none;
            }
            QStatusBar {
                background-color: #2b2b2b;
                color: #fbfbfb;
            }
            QProgressBar {
                border: 1px solid #555;
                border-radius: 4px;
                text-align: center;
                background-color: #2b2b2b;
            }
            QProgressBar::chunk {
                background-color: #0078d7;
                border-radius: 3px;
            }
        """)
    
    def update_char_counter(self):
        """Update character counter"""
        char_count = len(self.text_edit.toPlainText())
        self.char_counter.setText(f"Characters: {char_count}")
    
    def open_image(self):
        """Open and display an image file"""
        supported_formats = "Images (*.png *.bmp *.jpg *.jpeg *.gif *.tiff)"
        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", supported_formats)
        
        if path:
            try:
                self.image_path = path
                pixmap = QPixmap(path)
                
                if pixmap.isNull():
                    QMessageBox.warning(self, "Error", "Could not load the selected image.")
                    return
                
                # Scale image to fit label while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    self.img_label.size(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                
                self.img_label.setPixmap(scaled_pixmap)
                
                # Update image info
                file_size = os.path.getsize(path) / 1024  # KB
                self.img_info_label.setText(
                    f"File: {os.path.basename(path)} | "
                    f"Size: {pixmap.width()}x{pixmap.height()} | "
                    f"File Size: {file_size:.1f} KB"
                )
                
                self.status_bar.showMessage(f"Image loaded: {os.path.basename(path)}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
    
    def clear_all(self):
        """Clear current image and message"""
        self.image_path = None
        self.img_label.setPixmap(QPixmap())
        self.img_label.setText("No image selected\n\nClick 'Open Image' to get started")
        self.text_edit.clear()
        self.img_info_label.setText("No image loaded")
        self.status_bar.showMessage("Ready")
    
    def embed_message(self):
        """Embed message into image"""
        if not self.image_path:
            QMessageBox.warning(self, "Error", "Please select an image first.")
            return
        
        message = self.text_edit.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, "Error", "Please enter a message to embed.")
            return
        
        out_path, _ = QFileDialog.getSaveFileName(
            self, "Save Steganographic Image", 
            os.path.splitext(self.image_path)[0] + "_with_message.png",
            "PNG Files (*.png)"
        )
        
        if out_path:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.set_buttons_enabled(False)
            
            self.worker = SteganoWorker("embed", self.image_path, out_path, message)
            self.worker.finished.connect(self.on_operation_finished)
            self.worker.error.connect(self.on_operation_error)
            self.worker.progress.connect(self.progress_bar.setValue)
            self.worker.start()
    
    def extract_message(self):
        """Extract message from image"""
        if not self.image_path:
            QMessageBox.warning(self, "Error", "Please select an image first.")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.set_buttons_enabled(False)
        
        self.worker = SteganoWorker("extract", self.image_path)
        self.worker.finished.connect(self.on_extract_finished)
        self.worker.error.connect(self.on_operation_error)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.start()
    
    def on_operation_finished(self, message):
        """Handle successful operation completion"""
        self.progress_bar.setVisible(False)
        self.set_buttons_enabled(True)
        QMessageBox.information(self, "Success", f"✅ {message}")
        self.status_bar.showMessage("Operation completed successfully")
    
    def on_extract_finished(self, message):
        """Handle successful extraction"""
        self.progress_bar.setVisible(False)
        self.set_buttons_enabled(True)
        
        # Display extracted message in a larger dialog
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Extracted Message")
        msg_box.setText("🗝️ Hidden message found:")
        msg_box.setDetailedText(message.replace("Extracted message: ", ""))
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec_()
        
        self.status_bar.showMessage("Message extracted successfully")
    
    def on_operation_error(self, error_message):
        """Handle operation errors"""
        self.progress_bar.setVisible(False)
        self.set_buttons_enabled(True)
        QMessageBox.critical(self, "Error", f"❌ Operation failed:\n{error_message}")
        self.status_bar.showMessage("Operation failed")
    
    def set_buttons_enabled(self, enabled):
        """Enable or disable buttons during operations"""
        self.open_button.setEnabled(enabled)
        self.embed_button.setEnabled(enabled)
        self.extract_button.setEnabled(enabled)
        self.clear_button.setEnabled(enabled)
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Steganography Tool", 
                         "Steganography Tool v2.0\n\n"
                         "A modern GUI application for hiding and extracting\n"
                         "secret messages in images using steganography.\n\n"
                         "Features:\n"
                         "• Hide text messages in images\n"
                         "• Extract hidden messages\n"
                         "• Support for multiple image formats\n"
                         "• Modern dark theme interface\n"
                         "• Progress tracking\n\n"
                         "Built with PyQt5 and Python")
    
    def closeEvent(self, event):
        """Handle application close event"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(self, "Confirm Exit", 
                                       "An operation is in progress. Are you sure you want to exit?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.worker.terminate()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Steganography Tool")
    app.setApplicationVersion("2.0")
    
    # Set application icon if available
    try:
        app.setWindowIcon(QIcon("hidden.png"))
    except:
        pass
    
    window = StegApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()