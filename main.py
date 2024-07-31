from PyQt5 import QtWidgets, QtCore
from pyui.main import Ui_MainWindow
from pyui.config import Ui_Configurator
from pyui.streams import Ui_Streams
from tools.config import ConfigTool
import json
import sys
import os



class Configurator(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(Configurator, self).__init__(parent)
        self.ui = Ui_Configurator()
        self.ui.setupUi(self)

        # load config
        data = ConfigTool.read()
        if data:
            self.ui.editAddress.setText(data.get("address"))
            self.ui.editLogin.setText(data.get("login"))
            self.ui.editPassword.setText(data.get("password"))

        # bind buttons
        self.ui.buttonBox.accepted.connect(self.accept)

    def accept(self):
        config = {
            "address": self.ui.editAddress.text(),
            "login": self.ui.editLogin.text(),
            "password": self.ui.editPassword.text()
        }
        ConfigTool.write(config)
        super(Configurator, self).accept()

    

class Streams(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(Streams, self).__init__(parent)
        self.ui = Ui_Streams()
        self.ui.setupUi(self)

class Ui(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # bind menu elements
        self.ui.action_config.triggered.connect(self.showConfig)
        self.ui.action_streams.triggered.connect(self.showStreams)


        # bind buttons

        self.show()

    def showConfig(self):
        configurator = Configurator(self)
        configurator.show()

    def showStreams(self):
        streams = Streams(self)
        print(streams)
        streams.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    sys.exit(app.exec_())