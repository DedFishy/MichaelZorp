import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt

class TransparentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")  # Make background transparent
        self.setGeometry(100, 100, 300, 200)
        self.setWindowTitle("Transparent Window")
        
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TransparentWindow()
    sys.exit(app.exec_())