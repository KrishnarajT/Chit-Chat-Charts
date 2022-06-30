from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, Qt, QThread, QUrl, pyqtSlot
from PyQt5.QtWidgets import QFileDialog, QListWidget, QMainWindow
import MakeCharts as mk
import sys, time
from PyQt5.QtCore import QObject, QThread, pyqtSignal


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run(self, requiredGraphs, graphWordsList, graphDestPath, filePath, progressBar, progressLabel, mainTabs, labels, messaging_app):
        progressBar.setValue(0)
        r = mk.read()
        r.make_DataFrames(filePath, progressBar, progressLabel, messaging_app)
        r.calc_statistics(progressBar, progressLabel)
        statistics = r.return_statistics(progressBar, progressLabel)
        for i in range(len(statistics)):
            labels[i].setText(statistics[i])
        r.make_graphs(requiredGraphs, graphWordsList, graphDestPath, progressBar, progressLabel, mainTabs)
        progressBar.setValue(100)
        mainTabs.setCurrentIndex(3)
        self.finished.emit()

class cust_font(QtGui.QFont):
    def __init__(self):
        super().__init__()
        self.setPointSize(16)
        self.setFamily("Noto Sans")

class Ui_mainWindowDialog(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setObjectName("Main Window")
        self.setEnabled(True)
        self.resize(1000, 600)
        self.setMinimumSize(QtCore.QSize(1000, 600))
        self.setMaximumSize(QtCore.QSize(1000, 600))
        self.setAcceptDrops(True)
        self.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.setAutoFillBackground(True)
        self.mainTabs = QtWidgets.QTabWidget(self)
        self.srcFilePath = 'Enter File Path'
        self.graphsDestPath = ''
        self.srcFileName = 'Enter File Path'
        self.MessagingApp = 'Whatsapp'
        self.graphWordsList = []
        self.setupUi()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            links = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    links.append(str(url.toLocalFile()))
                else:
                    links.append(str(url.toString()))
            print(links)
            self.srcFilePath = links[0]
            self.srcFileName = self.srcFilePath.split('/')[-1]
            self.fileDestLabel.setText(self.srcFileName)
        else:
            event.ignore()

    def showSrcDialog(self):
        fname, _ = QFileDialog.getOpenFileUrl(
            self, filter='Message Files (*.json *.txt)')
        self.srcFilePath = fname.toLocalFile()
        self.srcFileName = self.srcFilePath.split('/')[-1]
        self.fileDestLabel.setText(self.srcFileName)
        print(self.srcFilePath, self.srcFileName)

    def showDestDialog(self):
        fname = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.graphsDestPath = fname
        self.graphsDestLabel.setText('...' + self.graphsDestPath[-60:])
        print(self.graphsDestPath)

    def onClickedStartButton(self):
        if self.graphsDestPath != '' and (self.srcFilePath[-4:] == '.txt' or self.srcFilePath[-5:] == '.json'):
            self.mainTabs.setCurrentIndex(1)
            self.preferencesTab.setDisabled(False)
  
    def onClickedGenerateButton(self):
        
        # Getting all the user input from that tab, and assigning variables accordingly
        
        self.messagingApp = self.appSelectionComboBox.currentText()
        # writes lower case strings for each letter typed without the commas or spaces into a list
        self.graphWordsList = [i.strip(' ').lower() 
                                for i in self.graphWordsTextBox.toPlainText().strip(',').split(',')]
        if self.graphWordsList == [''] : self.graphWordsList = []
        required_graphs = []
        
        
        for i in self.checkBoxes:
            if i.isChecked():
                required_graphs.append(i.text())
                
        if required_graphs == []:
            print('You did not select any kind of graph, please select and try again')
            return
        
        # Dubug
        print(self.graphWordsList)
        print(self.messagingApp)
        print(required_graphs)
        

        # Changing the Tab, to show the progressbar, and then beginning new threads to start generating graphs
        
        self.mainTabs.setCurrentIndex(2) # changing tab
        self.thread = QThread() # instantiating a new thread.
        self.worker = Worker() # instantiating a new QObject class, that has our long running functions.
        # The execution of the programs in worker class move to a new thread under the same process  
        self.worker.moveToThread(self.thread) 
        # Every thread has a started signal, we connect it to the long running function, so it knows what to execute
        self.thread.started.connect(lambda : self.worker.run(required_graphs, self.graphWordsList, self.graphsDestPath, self.srcFilePath, self.progressBar, self.progressLabel, self.mainTabs, self.labels, self.messagingApp)) 
        # Obviously, now connecting the finished signal of the worker Qobject to the thread's quit slot, so it knows
        # when to terminate the newly created thread.
        self.worker.finished.connect(self.thread.quit)
        # cleaning up, so that the instantiated Objects are deleted. the finished signal is connected to the deleteLater slot
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # now starting once all the signals and slots are connected safely. The thread now knows where to look for its code to execute, 
        # it then executes it, then once the code is executed, it sends a signal to the quit slot of the thread, terminating it.
        # upon termination, the thread now sends a finished signal, which we conneced to its deleteLater slot, so now the thread can
        # deleted successfully, and the same goes with the instantiated object of the Qobject worker class. These signals and slot mechanisms
        # are defined in the Qobject and Qthread classes, hence making their use seamless and necessary here. 
        
        self.thread.start()

    def setupUi(self):
        
        # Functions to be run on click of the buttons in the UI
                
        def onClickedRadioButton():
            self.selectAllRadioButton = self.sender()
            if self.selectAllRadioButton.isChecked():
                for i in self.checkBoxes:
                    i.setChecked(True)
            else :
                for i in self.checkBoxes:
                    i.setChecked(False)
        
        # seting the main font
        font = cust_font()
        
        # setting the attributes for the main tab
        self.mainTabs.setFont(font)
        self.mainTabs.setGeometry(QtCore.QRect(0, 0, 1000, 600))
        self.mainTabs.setMinimumSize(QtCore.QSize(1000, 600))
        self.mainTabs.setMaximumSize(QtCore.QSize(1000, 600))
        self.mainTabs.setAcceptDrops(True)
        self.mainTabs.setObjectName("mainTabs")
        
        # settings attributes for the new tabs
        self.getStartedTab = QtWidgets.QWidget()
        self.getStartedTab.setObjectName("getStartedTab")
        self.preferencesTab = QtWidgets.QWidget()
        self.preferencesTab.setObjectName("preferencesTab")
        self.resultsTab = QtWidgets.QWidget()
        self.resultsTab.setObjectName("resultsTab")
        self.statisticsTab = QtWidgets.QWidget()
        self.statisticsTab.setObjectName("statisticsTab")
        self.creditsTab = QtWidgets.QWidget()
        self.creditsTab.setObjectName("creditsTab")
        
        # adding new tabs
        self.mainTabs.addTab(self.getStartedTab, "")
        self.mainTabs.addTab(self.preferencesTab, "")
        self.mainTabs.addTab(self.resultsTab, "")
        self.mainTabs.addTab(self.statisticsTab, "")
        self.mainTabs.addTab(self.creditsTab, "")
        
        self.preferencesTab.setDisabled(True)

        # -------------------------------------------------------------------------------------------------
        ## TAB - 1 ## The Getting Started Tab where we will get the file, and set the destination paths.
        # -------------------------------------------------------------------------------------------------
        
        # Setting Labels
    
    
        # Label 1 # 
        
        
        font.setPointSize(36)
        font.setItalic(True)
    
        self.welcomeLabel = QtWidgets.QLabel(self.getStartedTab)
        self.welcomeLabel.setFont(font)
        self.welcomeLabel.setObjectName("welcomeLabel")
        self.welcomeLabel.setGeometry(QtCore.QRect(110, -10, 791, 141))
        self.welcomeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.welcomeLabel.setWordWrap(True)
        
        # Label 2 # 
        
        font = QtGui.QFont()
        font.setPointSize(18)
        
        self.graphDestInfoLabel = QtWidgets.QLabel(self.getStartedTab)
        self.graphDestInfoLabel.setFont(font)
        self.graphDestInfoLabel.setGeometry(QtCore.QRect(200, 250, 631, 101))
        self.graphDestInfoLabel.setAcceptDrops(True)
        self.graphDestInfoLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.graphDestInfoLabel.setWordWrap(True)
        self.graphDestInfoLabel.setObjectName("graphDestInfoLabel")
    
        # Label 3 #
        
        font = QtGui.QFont()
        font.setPointSize(18)
        
        self.fileDestInfoLabel = QtWidgets.QLabel(self.getStartedTab)
        self.fileDestInfoLabel.setGeometry(QtCore.QRect(70, 110, 881, 101))
        self.fileDestInfoLabel.setFont(font)
        self.fileDestInfoLabel.setAcceptDrops(True)
        self.fileDestInfoLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.fileDestInfoLabel.setWordWrap(True)
        self.fileDestInfoLabel.setObjectName("fileDestInfoLabel")
        
        
        # Setting Buttons #
        
        
        self.startButton = QtWidgets.QPushButton(self.getStartedTab)
        self.startButton.setGeometry(QtCore.QRect(410, 440, 191, 71))
        self.startButton.setObjectName("startButton")
        self.startButton.clicked.connect(lambda : self.onClickedStartButton())
        
        self.fileBrowseButton = QtWidgets.QToolButton(self.getStartedTab)
        self.fileBrowseButton.setGeometry(QtCore.QRect(890, 210, 51, 41))
        self.fileBrowseButton.setObjectName("fileBrowseButton")
        self.fileBrowseButton.clicked.connect(lambda : self.showSrcDialog())
        
        self.graphsDestBrowseBtn = QtWidgets.QToolButton(self.getStartedTab)
        self.graphsDestBrowseBtn.setGeometry(QtCore.QRect(890, 360, 51, 41))
        self.graphsDestBrowseBtn.setObjectName("graphsDestBrowseBtn")
        self.graphsDestBrowseBtn.clicked.connect(lambda : self.showDestDialog())

        
        # Setting Text Boxes # 
        
        self.fileDestLabel = QtWidgets.QLabel(self.getStartedTab)
        self.fileDestLabel.setGeometry(QtCore.QRect(100, 210, 741, 41))
        self.fileDestLabel.setObjectName("fileDestLabel")
        self.graphsDestLabel = QtWidgets.QLabel(self.getStartedTab)
        self.graphsDestLabel.setGeometry(QtCore.QRect(100, 360, 741, 41))
        self.graphsDestLabel.setObjectName("graphsDestLabel")
        
            
        # TAB 2 # The tab for setting preferences
            
            
        # Settings Labels #
        
        # Label 1 # 

        font = QtGui.QFont()
        font.setPointSize(18)
        
        self.appSelectionLabel = QtWidgets.QLabel(self.preferencesTab)
        self.appSelectionLabel.setGeometry(QtCore.QRect(20, 20, 501, 51))
        self.appSelectionLabel.setFont(font)
        self.appSelectionLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.appSelectionLabel.setObjectName("appSelectionLabel")
        
        # Label 2 # 

        font = QtGui.QFont()
        font.setPointSize(18)
        
        self.graphSelectionLabel = QtWidgets.QLabel(self.preferencesTab)
        self.graphSelectionLabel.setGeometry(QtCore.QRect(50, 100, 501, 51))
        self.graphSelectionLabel.setFont(font)
        self.graphSelectionLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.graphSelectionLabel.setObjectName("graphSelectionLabel")
        
        # Label 3 #
        
        font = QtGui.QFont()
        font.setPointSize(18)
        
        self.wordUsageInfoLabel = QtWidgets.QLabel(self.preferencesTab)
        self.wordUsageInfoLabel.setGeometry(QtCore.QRect(40, 360, 501, 51))
        self.wordUsageInfoLabel.setFont(font)
        self.wordUsageInfoLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.wordUsageInfoLabel.setObjectName("wordUsageInfoLabel")
        
        # Label 4 # 
        
        font = QtGui.QFont()
        font.setPointSize(14)
        
        self.infoTextLabel = QtWidgets.QLabel(self.preferencesTab)
        self.infoTextLabel.setGeometry(QtCore.QRect(50, 400, 951, 41))
        self.infoTextLabel.setFont(font)
        self.infoTextLabel.setAlignment( QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.infoTextLabel.setObjectName("infoTextLabel")
        
        # Setting the text box so that the user can enter the words that he wants to see the graphs of
        

        self.generateChartsButton = QtWidgets.QPushButton(self.preferencesTab)
        self.generateChartsButton.setGeometry(QtCore.QRect(360, 500, 271, 38))
        
        
        # Setting Check Boxes and other stuff  #
        
        # Setting combo box 
        
        font = QtGui.QFont()
        font.setPointSize(16)
        
        self.appSelectionComboBox = QtWidgets.QComboBox(self.preferencesTab)
        self.appSelectionComboBox.setGeometry(QtCore.QRect(540, 30, 171, 41))
        self.appSelectionComboBox.setFont(font)
        self.appSelectionComboBox.setObjectName("appSelectionComboBox")
        self.appSelectionComboBox.addItem("")
        self.appSelectionComboBox.addItem("")
        self.appSelectionComboBox.addItem("")
        
        # setting Radio Button 
        
        font = QtGui.QFont()
        font.setPointSize(14)
                    
        self.selectAllRadioButton = QtWidgets.QRadioButton(self.preferencesTab)
        self.selectAllRadioButton.setGeometry(QtCore.QRect(570, 110, 191, 41))
        self.selectAllRadioButton.setFont(font)
        self.selectAllRadioButton.setObjectName("selectAllRadioButton")
        self.selectAllRadioButton.toggled.connect(onClickedRadioButton)
        
        # Setting the Various Check Boxes for the selection of the kind of graphs that the user wants. 
        # the text of the actual names of the graphs are given in the retranslateUI function
        
                
        # Setting the graph words Text Box
        
        self.graphWordsTextBox = QtWidgets.QTextEdit(self.preferencesTab)
        self.graphWordsTextBox.setGeometry(QtCore.QRect(40, 450, 901, 41))
        self.graphWordsTextBox.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
        self.graphWordsTextBox.setLineWrapColumnOrWidth(0)
        self.graphWordsTextBox.setObjectName("graphWordsTextBox")

        
        self.checkBox_1 = QtWidgets.QCheckBox(self.preferencesTab, objectName = "checkBox_1")
        self.checkBox_1.setGeometry(QtCore.QRect(10, 160, 321, 41))
        
        self.checkBox_2 = QtWidgets.QCheckBox(self.preferencesTab, objectName = "checkBox_2")
        self.checkBox_2.setGeometry(QtCore.QRect(340, 160, 321, 41))

        self.checkBox_3 = QtWidgets.QCheckBox(self.preferencesTab, objectName = "checkBox_3")
        self.checkBox_3.setGeometry(QtCore.QRect(670, 160, 301, 41))

        self.checkBox_4 = QtWidgets.QCheckBox(self.preferencesTab, objectName = "checkBox_4")
        self.checkBox_4.setGeometry(QtCore.QRect(340, 210, 321, 41))

        self.checkBox_5 = QtWidgets.QCheckBox(self.preferencesTab, objectName = "checkBox_5")
        self.checkBox_5.setGeometry(QtCore.QRect(10, 210, 321, 41))

        self.checkBox_6 = QtWidgets.QCheckBox(self.preferencesTab, objectName = "checkBox_6")
        self.checkBox_6.setGeometry(QtCore.QRect(670, 210, 301, 41))

        self.checkBox_7 = QtWidgets.QCheckBox(self.preferencesTab, objectName = "checkBox_7")
        self.checkBox_7.setGeometry(QtCore.QRect(340, 260, 321, 41))

        self.checkBox_8 = QtWidgets.QCheckBox(self.preferencesTab, objectName = "checkBox_8")
        self.checkBox_8.setGeometry(QtCore.QRect(10, 260, 321, 41))

        self.checkBox_9 = QtWidgets.QCheckBox(self.preferencesTab, objectName = "checkBox_9")
        self.checkBox_9.setGeometry(QtCore.QRect(670, 260, 301, 41))

        self.checkBox_10 = QtWidgets.QCheckBox(self.preferencesTab, objectName = "checkBox_10")
        self.checkBox_10.setGeometry(QtCore.QRect(10, 310, 321, 41))

        self.checkBox_11 = QtWidgets.QCheckBox(self.preferencesTab, objectName = "checkBox_11")
        self.checkBox_11.setGeometry(QtCore.QRect(340, 310, 321, 41))

        self.checkBox_12 = QtWidgets.QCheckBox(self.preferencesTab, objectName = "checkBox_12")
        self.checkBox_12.setGeometry(QtCore.QRect(670, 310, 301, 41))

        self.checkBoxes = [self.checkBox_1, self.checkBox_2, self.checkBox_3, self.checkBox_4, self.checkBox_5, 
                      self.checkBox_6, self.checkBox_7, self.checkBox_8, self.checkBox_9, self.checkBox_10,
                      self.checkBox_11, self.checkBox_12]
        

        print(self.selectAllRadioButton.isChecked())
        
        # TAB 3 # The tab for showing the progress bar for the generation of the charts.
        
        # Settings the Labels
        
        # Label 1 #  showing the text that tells the user that the progress bar is generating charts.

        font.setPointSize(25)
        font.setItalic(True)
        self.generatingChartLabel = QtWidgets.QLabel(self.resultsTab)
        self.generatingChartLabel.setGeometry(QtCore.QRect(110, 120, 800, 100))
        self.generatingChartLabel.setWordWrap(True)
        self.generatingChartLabel.setFont(font)
        self.generatingChartLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.generatingChartLabel.setObjectName("generatingChartLabel")
        
        # Label 2 # showing the progress as text of what is happening.
        
        font.setPointSize(18)
        font.setItalic(False)
        self.progressLabel = QtWidgets.QLabel(self.resultsTab)
        self.progressLabel.setGeometry(QtCore.QRect(260, 340, 501, 51))
        self.progressLabel.setFont(font)
        self.progressLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.progressLabel.setObjectName("progressLabel")
        
        # Label 3 # a random useless tip
        
        font.setPointSize(15)
        self.tipLabel = QtWidgets.QLabel(self.resultsTab)
        self.tipLabel.setGeometry(QtCore.QRect(120, 480, 781, 41))
        self.tipLabel.setFont(font)
        self.tipLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.tipLabel.setObjectName("tipLabel")

        # setting the Buttons and the progress bar

        font = QtGui.QFont()
        font.setPointSize(16)
        
        self.generateChartsButton.setFont(font)
        self.generateChartsButton.setObjectName("generateChartsButton")
        self.generateChartsButton.clicked.connect(lambda : self.onClickedGenerateButton())
        self.progressBar = QtWidgets.QProgressBar(self.resultsTab)
        self.progressBar.setGeometry(QtCore.QRect(100, 250, 811, 31))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")


        # TAB 4 # The tab for showing the General results, has only labels

        # Setting labels
        
        font.setPointSize(14)

        
        # Label 1 #
        
        self.label_1 = QtWidgets.QLabel(self.statisticsTab)
        self.label_1.setGeometry(QtCore.QRect(40, 90, 881, 28))
        self.label_1.setFont(font)
        self.label_1.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.label_1.setObjectName("label_1")
        
        # Label 2 #
        
        self.label_2 = QtWidgets.QLabel(self.statisticsTab)
        self.label_2.setGeometry(QtCore.QRect(40, 120, 881, 28))
        self.label_2.setFont(font)
        self.label_2.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.label_2.setObjectName("label_2")
        
        # Label 3 #
        
        
        self.label_3 = QtWidgets.QLabel(self.statisticsTab)
        self.label_3.setGeometry(QtCore.QRect(40, 150, 881, 28))
        self.label_3.setFont(font)
        self.label_3.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.label_3.setObjectName("label_3")
        
        
        # Label 4 #
        
        
        self.label_4 = QtWidgets.QLabel(self.statisticsTab)
        self.label_4.setGeometry(QtCore.QRect(40, 180, 881, 28))
        self.label_4.setFont(font)
        self.label_4.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.label_4.setObjectName("label_4")
        
        # Label 5 #
        
        
        self.label_5 = QtWidgets.QLabel(self.statisticsTab)
        self.label_5.setGeometry(QtCore.QRect(40, 210, 881, 28))
        self.label_5.setFont(font)
        self.label_5.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.label_5.setObjectName("label_5")
        
        # Label 6 #
        
        
        self.label_6 = QtWidgets.QLabel(self.statisticsTab)
        self.label_6.setGeometry(QtCore.QRect(40, 240, 881, 28))
        self.label_6.setFont(font)
        self.label_6.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.label_6.setObjectName("label_6")
        
        # Label 7 #
        
        self.label_7 = QtWidgets.QLabel(self.statisticsTab)
        self.label_7.setGeometry(QtCore.QRect(40, 270, 881, 28))
        self.label_7.setFont(font)
        self.label_7.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.label_7.setObjectName("label_7")
        
        # Label 8 #
        
        
        self.label_9 = QtWidgets.QLabel(self.statisticsTab)
        self.label_9.setGeometry(QtCore.QRect(40, 300, 881, 28))
        self.label_9.setFont(font)
        self.label_9.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.label_9.setObjectName("label_9")
        
        # Label 10 #
        
        
        self.label_10 = QtWidgets.QLabel(self.statisticsTab)
        self.label_10.setGeometry(QtCore.QRect(40, 330, 881, 28))
        self.label_10.setFont(font)
        self.label_10.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.label_10.setObjectName("label_10")
        
        # Label 11 #
        
        
        self.label_11 = QtWidgets.QLabel(self.statisticsTab)
        self.label_11.setGeometry(QtCore.QRect(40, 360, 881, 28))
        self.label_11.setFont(font)
        self.label_11.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.label_11.setObjectName("label_11")
        
        # Label 12 #

        
        self.label_12 = QtWidgets.QLabel(self.statisticsTab)
        self.label_12.setGeometry(QtCore.QRect(40, 390, 881, 28))
        self.label_12.setFont(font)
        self.label_12.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.label_12.setObjectName("label_12")
        
        
        # Label 13 #
        
        self.label_13 = QtWidgets.QLabel(self.statisticsTab)
        self.label_13.setGeometry(QtCore.QRect(40, 420, 881, 28))
        self.label_13.setFont(font)
        self.label_13.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.label_13.setObjectName("label_13")
        
        # Label 14 #
        
        self.label_14 = QtWidgets.QLabel(self.statisticsTab)
        self.label_14.setGeometry(QtCore.QRect(40, 450, 881, 28))
        self.label_14.setFont(font)
        self.label_14.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.label_14.setObjectName("label_14")
        
        # Label 15 #
        
        self.label_15 = QtWidgets.QLabel(self.statisticsTab)
        self.label_15.setGeometry(QtCore.QRect(40, 480, 881, 28))
        self.label_15.setFont(font)
        self.label_15.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.label_15.setObjectName("label_15")
        
        
        self.labels = [self.label_1, self.label_2, self.label_3, self.label_4, self.label_5, self.label_6, self.label_7, 
                  self.label_9, self.label_10, self.label_11, self.label_12, self.label_13, self.label_14, self.label_15]
        
        # Label 16 # 
        
        font.setPointSize(18)
        self.generalStatsLabel = QtWidgets.QLabel(self.statisticsTab)
        self.generalStatsLabel.setGeometry(QtCore.QRect(230, 10, 501, 51))
        self.generalStatsLabel.setFont(font)
        self.generalStatsLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.generalStatsLabel.setObjectName("generalStatsLabel")


        # TAB 5 # The tab for Credits and general info, also only has labels.

        # Setting the labels

        font.setPointSize(18)
        self.label_8 = QtWidgets.QLabel(self.creditsTab)
        self.label_8.setGeometry(QtCore.QRect(30, 160, 921, 41))
        self.label_8.setFont(font)
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName("label_8")
        
        
        self.label_23 = QtWidgets.QLabel(self.creditsTab)
        self.label_23.setGeometry(QtCore.QRect(40, 220, 921, 41))
        self.label_23.setFont(font)
        self.label_23.setAlignment(QtCore.Qt.AlignCenter)
        self.label_23.setObjectName("label_23")
        
        
        font.setPointSize(18)
        font.setItalic(True)
        
        self.label_24 = QtWidgets.QLabel(self.creditsTab)
        self.label_24.setGeometry(QtCore.QRect(340, 260, 321, 41))
        self.label_24.setFont(font)
        self.label_24.setAlignment(QtCore.Qt.AlignCenter)
        self.label_24.setObjectName("label_24")
        
        
        font.setPointSize(30)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        
        self.label_25 = QtWidgets.QLabel(self.creditsTab)
        self.label_25.setGeometry(QtCore.QRect(30, 40, 911, 41))
        self.label_25.setFont(font)
        self.label_25.setAlignment(QtCore.Qt.AlignCenter)
        self.label_25.setObjectName("label_25")
        
        
        font.setPointSize(18)
        self.label_26 = QtWidgets.QLabel(self.creditsTab)
        self.label_26.setGeometry(QtCore.QRect(40, 330, 921, 41))
        self.label_26.setFont(font)
        self.label_26.setAlignment(QtCore.Qt.AlignCenter)
        self.label_26.setObjectName("label_26")
        
        
        font.setPointSize(18)
        font.setItalic(True)
        self.label_27 = QtWidgets.QLabel(self.creditsTab)
        self.label_27.setGeometry(QtCore.QRect(100, 380, 801, 80))
        self.label_27.setWordWrap(True)
        self.label_27.setFont(font)
        self.label_27.setAlignment(QtCore.Qt.AlignCenter)
        self.label_27.setObjectName("label_27")
        
        
        font.setPointSize(18)
        font.setItalic(True)
        self.label_28 = QtWidgets.QLabel(self.creditsTab)
        self.label_28.setGeometry(QtCore.QRect(30, 490, 921, 41))
        self.label_28.setFont(font)
        self.label_28.setAlignment(QtCore.Qt.AlignCenter)
        self.label_28.setObjectName("label_28")


        # Now that setting the UI elements are done, we can now set the texts, which will be done using this function
        self.retranslateUi()
        self.mainTabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        
        # -------------------------------------------------------------------------------------------------
        # Setting standard elements and their text, that is static and wont really change in any situation.
        # -------------------------------------------------------------------------------------------------

        self.setWindowTitle(_translate("mainWindowDialog", "Chit Chat Charts"))
        self.mainTabs.setWhatsThis(
            _translate(
                "mainWindowDialog",
                "<html><head/><body><p>The Beginning Tab for selecting the File</p><p><br/></p></body></html>",
            )
        )
        self.welcomeLabel.setText(
            _translate("mainWindowDialog", "Welcome to Chit Chat Charts!")
        )
        self.startButton.setText(_translate("mainWindowDialog", "Start"))
        self.fileBrowseButton.setText(_translate("mainWindowDialog", "..."))
        self.graphDestInfoLabel.setText(
            _translate(
                "mainWindowDialog",
                "All your graphs will be exported to a folder. Where do you want this folder to be?",
            )
        )
        self.fileDestInfoLabel.setText(
            _translate(
                "mainWindowDialog",
                "You can drag and drop your messages file anywhere here, browse to its file location or enter the location below!",
            )
        )
        self.fileDestLabel.setText(_translate("mainWindowDialog", self.srcFilePath))
        self.graphsDestLabel.setText(_translate("mainWindowDialog", 'Enter Graph Path'))
        self.graphsDestBrowseBtn.setText(_translate("mainWindowDialog", "..."))
        self.mainTabs.setTabText(
            self.mainTabs.indexOf(self.getStartedTab),
            _translate("mainWindowDialog", "Getting Started"),
        )
        self.appSelectionLabel.setText(
            _translate("mainWindowDialog", "Which App did you get your file from?")
        )
        self.graphSelectionLabel.setText(
            _translate("mainWindowDialog", "What kind of Graphs do you want to see ?")
        )
        self.appSelectionComboBox.setItemText(
            0, _translate("mainWindowDialog", "Whatsapp")
        )
        self.appSelectionComboBox.setItemText(
            1, _translate("mainWindowDialog", "Instagram")
        )
        self.appSelectionComboBox.setItemText(
            2, _translate("mainWindowDialog", "Telegram")
        )
        self.selectAllRadioButton.setText(
            _translate("mainWindowDialog", "Just Select All")
        )
        
        self.infoTextLabel.setText(
            _translate(
                "mainWindowDialog",
                "(just write all the words you want to see graphs of separated by commas, case insensitive)",
            )
        )
        self.generateChartsButton.setText(
            _translate("mainWindowDialog", "Okay! Generate Charts!")
        )
        self.mainTabs.setTabText(
            self.mainTabs.indexOf(self.preferencesTab),
            _translate("mainWindowDialog", "Preferences"),
        )
        self.generatingChartLabel.setText(
            _translate("mainWindowDialog", "Generating Graphs, This should just take a few seconds...")
        )
        self.progressLabel.setText(_translate("mainWindowDialog", "hang on!"))
        self.tipLabel.setText(
            _translate(
                "mainWindowDialog",
                "You will see the general statistics in the next tab once the charts are generated!",
            )
        )
        self.mainTabs.setTabText(
            self.mainTabs.indexOf(self.resultsTab),
            _translate("mainWindowDialog", "Result"),
        )
                
        self.generalStatsLabel.setText(
            _translate("mainWindowDialog", "Here are some General Statistics")
        )
        self.mainTabs.setTabText(
            self.mainTabs.indexOf(self.statisticsTab),
            _translate("mainWindowDialog", "Statistics"),
        )
        self.label_8.setText(
            _translate(
                "mainWindowDialog",
                "The Program is licensed under the GPL and can be used by anyone freely.",
            )
        )
        self.label_23.setText(_translate("mainWindowDialog", "Made by :"))
        self.label_24.setText(_translate("mainWindowDialog", "Krishnaraj PT"))
        self.label_25.setText(_translate("mainWindowDialog", "Chit Chat Charts v1.2.0"))
        self.label_26.setText(
            _translate(
                "mainWindowDialog",
                "Any suggestions to improve the program would be great! You can mail them at :",
            )
        )
        self.label_27.setText(
            _translate("mainWindowDialog", "suggestions.to.kpt@gmail.com \nor visit https://github.com/KrishnarajT/Chit-Chat-Charts")
        )
        self.label_28.setText(
            _translate(
                "mainWindowDialog",
                "Chit Chat Charts is made using PyQt5, and matplotlib with python for its backend.",
            )
        )
        self.mainTabs.setTabText(
            self.mainTabs.indexOf(self.creditsTab),
            _translate("mainWindowDialog", "Credits"),
        )
        
    
    
        # -------------------------------------------------------------------------------------------------
        # Setting the Text for Stuff that can change eventually in future versions. 
        # -------------------------------------------------------------------------------------------------
        
        
        self.checkBox_1.setText(
            _translate("mainWindowDialog", "No. of Messages sent Daily")
        )
        self.checkBox_2.setText(
            _translate("mainWindowDialog", "No. of Messages sent Monthly")
        )
        self.checkBox_3.setText(
            _translate("mainWindowDialog", "No. of Words sent Daily")
        )
        self.checkBox_4.setText(
            _translate("mainWindowDialog", "No. of Words sent Monthly")
        )
        self.checkBox_5.setText(
            _translate("mainWindowDialog", "Percentage of Messages")
        )
        self.checkBox_6.setText(
            _translate("mainWindowDialog", "Percentage of Words")
        )
        self.checkBox_9.setText(
            _translate("mainWindowDialog", "Time Spent Daily")
        )
        self.checkBox_7.setText(
            _translate("mainWindowDialog", "Time Spent Monthly")
        )
        self.checkBox_8.setText(
            _translate("mainWindowDialog", "20 Most Used Words")
        )
        self.checkBox_11.setText(
            _translate("mainWindowDialog", "Length of Each Session")
        )
        self.checkBox_10.setText(
            _translate("mainWindowDialog", "Most Active Hours")
        )
        self.checkBox_12.setText(
            _translate("mainWindowDialog", "Weekly Activity")
        )
        self.wordUsageInfoLabel.setText(
            _translate("mainWindowDialog", "Usage of any particular words over time ?")
        )
        
        
        self.label_1.setText(
            _translate(
                "mainWindowDialog", ""
            )
        )
        self.label_2.setText(
            _translate(
                "mainWindowDialog", ""
            )
        )
        self.label_3.setText(
            _translate(
                "mainWindowDialog", ""
            )
        )
        self.label_6.setText(
            _translate(
                "mainWindowDialog", ""
            )
        )
        self.label_5.setText(
            _translate(
                "mainWindowDialog", ""
            )
        )
        self.label_4.setText(
            _translate(
                "mainWindowDialog", ""
            )
        )
        self.label_7.setText(
            _translate(
                "mainWindowDialog", ""
            )
        )
        self.label_11.setText(
            _translate(
                "mainWindowDialog", ""
            )
        )
        self.label_10.setText(
            _translate(
                "mainWindowDialog", ""
            )
        )
        self.label_9.setText(
            _translate(
                "mainWindowDialog", ""
            )
        )
        self.label_12.setText(
            _translate(
                "mainWindowDialog", ""
            )
        )
        self.label_15.setText(
            _translate(
                "mainWindowDialog", ""
            )
        )
        self.label_14.setText(
            _translate(
                "mainWindowDialog", ""
            )
        )
        self.label_13.setText(
            _translate(
                "mainWindowDialog", ""
            )
        )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_mainWindowDialog()
    ui = ui.show()

    # apply_stylesheet(app, theme='light_pink.xml')
    
    # with open("random.qss", "r") as f:
    #     _style = f.read()
    #     app.setStyleSheet(_style)

    sys.exit(app.exec_())
