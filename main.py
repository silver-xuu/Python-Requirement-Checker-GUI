import utils
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, 
                             QWidget, QTableWidget, QPushButton, QLineEdit, QTextEdit, QFileDialog)
from PyQt5.QtGui import QFont
from PyQt5 import uic

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # load the ui file
        uic.loadUi("requirement-checker.ui",self)
        self.browseButton = self.findChild(QPushButton,"browseButton")
        self.clearButton = self.findChild(QPushButton,"clearButton")
        self.checkButton = self.findChild(QPushButton,"checkButton")
        self.initUI()
        self.show()
    
    
        
    def initUI(self):
        pass
        
        
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    # window.show()
    
    sys.exit(app.exec_())
    pass

if __name__ == "__main__":
    main()

utils.check_reqs(['requests[security] == 2.9.1 ', 'pip[requests]>=20.0'])