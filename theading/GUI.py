import sys
from PySide.QtGui import QButtonGroup,QSpacerItem, QComboBox,QRadioButton,QFormLayout,QHBoxLayout, QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog,QPushButton,QMessageBox,QLabel,QGridLayout,QGroupBox,QVBoxLayout
from PySide.QtGui import QIcon
import mdfreader,os,pandas
from fractions import Fraction
import ASAP3_full
import SpdCtl		
import time

class App(QWidget):
 
    def __init__(self):
        super(App,self).__init__()
        self.title = 'Hydraulic labcar'
        self.left = 100
        self.top = 100
        self.width = 600
        self.height = 400
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
        self.GridGroupBox = QGroupBox("ESD tranisent control")
        l1 = QLabel("HOST PORT")

        h1=QHBoxLayout()

        a3host = QLineEdit('127.0.0.1')
        a3col = QLabel(':')
        a3port = QLineEdit('22222')
        h1.addWidget(a3host)
        h1.addWidget(a3col)
        h1.addWidget(a3port)
        
        l3 = QLabel("COM port")
        

        hbb=QHBoxLayout()
        comport = QComboBox()
        #comport.addItem('COM1')
        comport.addItems(['COM1','COM2','COM3','COM4','COM5'])
        l4=QLabel("Baue rate")
        comBaud=QComboBox()
        comBaud.addItems(['9600'])
        hbb.addWidget(comport)
        hbb.addWidget(l4)
        hbb.addWidget(comBaud)

        l4 = QLabel("Profile CSV")
        self.prof = QLineEdit()
        hb=QHBoxLayout()
        btnSel=QPushButton("Select")
        btnSel.clicked.connect(self.openFileNameDialog)
        hb.addWidget(self.prof)
        hb.addWidget(btnSel)

        l5=QLabel("INCA Label")
        self.label=QLineEdit("PhyMod_trq2qBas_MAP")
        self.labelType=QComboBox()
        l6=QLabel("Type")
        self.labelType.addItems([r'MAP/CURVE','Single'])
        h2=QHBoxLayout()
        h2.addWidget(self.label)
        h2.addWidget(l6)
        h2.addWidget(self.labelType)
        
        fbox = QFormLayout()
        fbox.addRow(l1,h1)
        fbox.addRow(l3,hbb)
        fbox.addRow(l4,hb)
        fbox.addRow(l5,h2)
        hbox = QHBoxLayout()
        
        init=QPushButton("Init")
        HeatBeat=QPushButton("Heart beat")
        run=QPushButton("Run")        
        stop=QPushButton("Stop")
        hbox.addWidget(init)
        hbox.addWidget(stop)
        hbox.addWidget(run)
        hbox.addWidget(HeatBeat)
        fbox.addRow(QLabel("control"),hbox)
        
        
        self.GridGroupBox.setLayout(fbox)
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
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","CSV Files (*.csv)", options=options)
        if fileName:
            self.prof.setText(fileName)
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
    def spdinit(self):
        mSerial=SpdCtl.SpdCtl()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())