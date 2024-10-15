import utils
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, 
                             QWidget, QTableWidget,QTableWidgetItem, QPushButton, QLineEdit, QTextEdit, QFileDialog)
from PyQt5.QtGui import QFont,QColor,QBrush
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
        self.connectButtons()
        self.setTableHeader()
        pass
    
    def connectButtons(self):
        self.browseButton.clicked.connect(self.browseButonOnClick)
        self.clearButton.clicked.connect(self.clearButonOnClick)
        self.checkButton.clicked.connect(self.checkButonOnClick)
    
    def setTableHeader(self):
        #set header
        self.tableResult.setHorizontalHeaderItem(0, QTableWidgetItem("Module"))
        self.tableResult.setHorizontalHeaderItem(1, QTableWidgetItem("Requriement Specifier"))
        self.tableResult.setHorizontalHeaderItem(2, QTableWidgetItem("Current Version"))
        self.tableResult.setHorizontalHeaderItem(3, QTableWidgetItem("Satisfied"))
    
    def browseButonOnClick(self):
        self.fname , _ = QFileDialog.getOpenFileName(self,"Select a requirement.txt","", "Python Requirement Files (*.txt)")
        if self.fname:
            self.lineLocation.setText(self.fname)
        
            
    def clearButonOnClick(self):
         self.logWindow.setText("")
         self.tableResult.setRowCount(0)
         
    def checkButonOnClick(self):
        if not self.fname:
            self.logWindow.setText("Couldn't locate the file")
            return
        counter =0
        self.logWindow.setText("Checking...")
        reqItems = utils.check_req_file(self.fname)
        for reqItem in reqItems:
            for req in reqItem:
                
                self.tableResult.setRowCount(counter+1)
                self.tableResult.setItem(counter, 0, QTableWidgetItem(str(req.name)))
                self.tableResult.setItem(counter, 1, QTableWidgetItem(str(req.reqSpec)))
                self.tableResult.setItem(counter, 2, QTableWidgetItem(str(req.version)))
                self.tableResult.setItem(counter, 3, QTableWidgetItem(str(req.isSatisfied)))
                if(not req.isSatisfied):
                    # self.tableResult.item(counter,3).setBackground(QT)
                    pass
                counter+=1
        self.logWindow.setText("Done!")
        
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    # window.show()
    
    sys.exit(app.exec_())
    pass

if __name__ == "__main__":
    main()
