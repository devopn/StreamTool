from itertools import tee
from PyQt5 import QtWidgets, QtCore
from pyui.main import Ui_MainWindow
from pyui.config import Ui_Configurator
from pyui.streams import Ui_Streams
from pyui.template import Ui_Template

from tools.config import ConfigTool
from tools.ssh import SshTool
from tools.template_editor import TemplateTool
import sys
import re



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

class TemplateEditor(QtWidgets.QDialog):

    def __init__(self, parent=None, name=None):
        super(TemplateEditor, self).__init__(parent)
        self.ui = Ui_Template()
        self.ui.setupUi(self)
        self.ui.buttonSave.clicked.connect(self.save)
        if name:
            data = TemplateTool.read()
            self.ui.edit_title.setText(name)
            templates = data.get(name)
            if templates:
                for i, template in enumerate(templates):
                    self.ui.tableSchedule.insertRow(i)
                    self.ui.tableSchedule.setItem(i, 0, QtWidgets.QTableWidgetItem(template.get("time")))
                    self.ui.tableSchedule.setItem(i, 1, QtWidgets.QTableWidgetItem(str(template.get("duration"))))
                    self.ui.tableSchedule.setItem(i, 2, QtWidgets.QTableWidgetItem(template.get("filename")))
                    self.ui.tableSchedule.setItem(i, 3, QtWidgets.QTableWidgetItem(template.get("key")))
    
    def show_error(self, message):
        QtWidgets.QMessageBox.critical(self, "Error", message)

    def save(self):
        table = self.ui.tableSchedule
        data = []
        for i in range(table.rowCount()):
            a = table.item(i, 0)
            b = table.item(i, 1)
            c = table.item(i, 2)
            d = table.item(i, 3)

            if a:
                if not a or not b or not c or not d:
                    self.show_error("Заполните все поля в выбранных строках")
                    return

                if not re.match(r"^\d{2}:\d{2}$", a.text()):
                    self.show_error("Неверное время в строке {}".format(i+1))
                    return
                
                if not b.text().isdigit():
                    self.show_error("Неверная длительность в строке {}".format(i+1))
                    return

                data.append({
                    "time": a.text(),
                    "duration": int(b.text()),
                    "filename": c.text(),
                    "key": d.text()
                })
        # print(data)
        TemplateTool.write(self.ui.edit_title.text(), data)
        self.close()


class Ui(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # bind menu elements
        self.ui.action_config.triggered.connect(self.showConfig)
        self.ui.action_streams.triggered.connect(self.showStreams)


        # bind buttons
        self.ui.buttonTemplateAdd.clicked.connect(self.addTemplate)
        self.ui.buttonTemplateEdit.clicked.connect(self.editTemplate)
        self.ui.buttonTemplateDelete.clicked.connect(self.deleteTemplate)
        self.ui.buttonDateDelete.clicked.connect(self.deleteDate)
        self.ui.buttonDateSave.clicked.connect(self.saveDate)
        
        self.updateTemplates()
        self.show()

    def updateTemplates(self):
        templates = TemplateTool.read()
        self.ui.listTemplates.clear()
        for temp_name in templates.keys():
            self.ui.listTemplates.addItem(temp_name)

    def showConfig(self):
        configurator = Configurator(self)
        configurator.show()

    def showStreams(self):
        streams = Streams(self)
        streams.show()


    def addTemplate(self):
        template = TemplateEditor(self)
        template.show()
        template.exec_()
        self.updateTemplates()

    def editTemplate(self):
        name = self.ui.listTemplates.currentItem().text()
        template = TemplateEditor(self, name)
        template.show()
        template.exec_()
        self.updateTemplates()

    def deleteTemplate(self):
        pass

    def saveDate(self):
        pass
    
    def deleteDate(self):
        pass

    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    sys.exit(app.exec_())