import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog,QPushButton,QMessageBox,QLabel,QGridLayout,QGroupBox,QVBoxLayout
from PyQt5.QtGui import QIcon
import mdfreader,os,pandas
from fractions import Fraction


class App(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'Hydraulic labcar'
        self.left = 100
        self.top = 100
        self.width = 400
        self.height = 200
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createLayout()
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.GridGroupBox)
        self.setLayout(windowLayout)


        self.show()
    
    def createLayout(self):
        self.GridGroupBox = QGroupBox("Convert")
        layout = QGridLayout()
        layout.addWidget(QLabel('MDF .dat File'),0,0)
        self.txt=QLineEdit()
        layout.addWidget(self.txt,0,1)
        self.sel=QPushButton('Select')
        layout.addWidget(self.sel,0,2)
        self.sel.clicked.connect(self.openFileNameDialog)
        layout.addWidget(QLabel('Gear Ratio E/P'),1,0)
        self.ratio=QLineEdit()
        layout.addWidget(self.ratio,1,1)
        self.convert=QPushButton('Convert')
        layout.addWidget(self.convert,1,2)
        self.convert.clicked.connect(self.doParser)
        self.GridGroupBox.setLayout(layout)
    def doParser(self):
        s=self.txt.text()
        if(s==""):
            QMessageBox.warning(self,'Warning', 'Please select the source file.')
        elif(self.ratio.text()==""):
            QMessageBox.warning(self,'Warning', 'Please enter the gear ratio.')
        else:
            self.parseMDF(s)
    def openFileNameDialog(self):    
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","MDF Files (*.dat)", options=options)
        if fileName:
            self.txt.setText(fileName)
    def parseMDF(self,filename):
        if(os.path.exists(filename)):
            mdf=mdfreader.mdf(filename,channelList=['Epm_nEng','InjCtl_qSetUnBal'])
            mdf.convertToPandas(0.1)
            df=mdf['master_group']
            try:
                r=float(Fraction(self.ratio.text()))
                df['Epm_nEng']=df['Epm_nEng'].apply(lambda x : round(x/r))
                df.columns=['Speed','q']
                df.to_csv(filename+".csv",index = False)
                QMessageBox.information(self,'Finished.','OK.')
            except PermissionError:
                QMessageBox.warning(self,'Warning', 'The file is opened, please close it and try again.')
        else:
            QMessageBox.warning(self,'Warning','Cannot file the file you specified!') 
    def openFileNamesDialog(self):    
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)", options=options)
        if files:
            print(files)
 
    def saveFileDialog(self):    
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            parseMDF(self.txt.text)
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())