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
        self.lineLocation = self.findChild(QLineEdit, "lineLocation")
        self.logWindow = self.findChild(QTextEdit, "logWindow")
        self.tableResult= self.findChild(QTableWidget, "tableResult")
        self.fname =""
        
        self.initUI()
        self.show()
    
    
        
    def initUI(self):
        self.browseButton.clicked.connect(self.browseButonOnClick)
        self.clearButton.clicked.connect(self.clearButonOnClick)
        self.checkButton.clicked.connect(self.checkButonOnClick)
        pass
    
    def browseButonOnClick(self):
        self.fname , _ = QFileDialog.getOpenFileName(self,"Select a requirement.txt","", "Python Requirement Files (*.txt)")
        if self.fname:
            self.lineLocation.setText(self.fname)
        
            
    def clearButonOnClick(self):
         self.logWindow.setText("")
         
    def checkButonOnClick(self):
        if not self.fname:
            self.logWindow.setText("Couldn't locate the file")
            return
            
        utils.check_req_file(self.fname)
        
        
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    # window.show()
    
    sys.exit(app.exec_())
    pass

if __name__ == "__main__":
    main()

utils.check_reqs(['requests[security] == 2.9.1 ', 'pip[requests]>=20.0'])