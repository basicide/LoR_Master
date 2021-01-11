from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import constants as cs
import os
import sys
from inspectorWidget import InspectorWidget

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 450)
        # setting status bar message
        self.statusBar().showMessage("Version: 0.1.0 beta")
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 5)
        #self.progressBar.setFormat('Connected')
        #self.progressBar.setTextVisible(False)
        self.progressBar.setValue(5)
        self.progressBar.setHidden(True)
        self.statusBar().addPermanentWidget(self.progressBar)

class Inspector(InspectorWidget):
    def __init__(self, window):
        super().__init__()
        self.parentWindow = window

    def inspectPushButtonClicked(self):
        self.parentWindow.progressBar.setValue(0)
        self.parentWindow.progressBar.setHidden(False)
        return super().inspectPushButtonClicked()

    def showlog(self, opponentName, outcome, deckCode, factions, opDeckCode, opFactions, totalTurn, num):
        self.parentWindow.progressBar.setValue(num)
        return super().showlog(opponentName, outcome, deckCode, factions, opDeckCode, opFactions, totalTurn, num)


app = QApplication(sys.argv)
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
app.setApplicationName(cs.DISPLAY_TITLE)
app.setWindowIcon(QIcon('test.jpg'))
app.setStyle('Fusion')
window = Window()
inspectorWidget = Inspector(window)
window.setCentralWidget(inspectorWidget)
window.show()
sys.exit(app.exec())