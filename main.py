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

ssh = SshTool()

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
        self.update()
        self.ui.buttonDisable.clicked.connect(self.remove)

    def update(self):
        self.ui.listStreams.clear()
        data = ssh.list_streams()
        for line in data.split("\n"):
            if "stream" in line:
                self.ui.listStreams.addItem(line)

    def remove(self):
        selected = self.ui.listStreams.selectedItems()
        for item in selected:
            a = item.text().strip().split(".")[0]
            ssh.kill_stream(a)
            self.update()

    
        

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
        try:
            ssh.start()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e) + "\n\nПроверьте конфигурацию и перезапустите программу")
            cfg = Configurator(self)
            cfg.show()
            cfg.exec_()

        # bind menu elements
        self.ui.action_config.triggered.connect(self.showConfig)
        self.ui.action_streams.triggered.connect(self.showStreams)


        # bind buttons
        self.ui.buttonTemplateAdd.clicked.connect(self.addTemplate)
        self.ui.buttonTemplateEdit.clicked.connect(self.editTemplate)
        self.ui.buttonTemplateDelete.clicked.connect(self.deleteTemplate)
        self.ui.buttonDateDelete.clicked.connect(self.deleteDate)
        self.ui.buttonDateSave.clicked.connect(self.saveDate)

        # check threads
        self.checkCPUTimer = QtCore.QTimer(self)
        self.checkCPUTimer.setInterval(10000)
        self.checkCPUTimer.timeout.connect(self.checkThreads)
        self.checkCPUTimer.start()
        self.checkThreads()

        # bind calendar
        self.ui.calendar.selectionChanged.connect(self.updateDate)

        
        self.updateTemplates()
        self.show()

    def updateDate(self):
        date = self.ui.calendar.selectedDate().toString("dd-MM-yyyy")
        streams = ssh.get_streams(date)
        self.ui.listDateInfo.clear()
        for stream in streams.split("\n"):
            self.ui.listDateInfo.addItem(stream)

    def checkThreads(self):
        result = ssh.execute("screen -ls")
        result = result.split("\n")
        result = len([x for x in result if "stream" in x])
        self.ui.statusbar.showMessage(str(result) + " активных потоков")

    def updateTemplates(self):
        templates = TemplateTool.read()
        if not templates:
            return
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
        name = self.ui.listTemplates.currentItem().text()
        # Ask
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText("Удалить шаблон?")
        msg.setWindowTitle("Подтверждение")
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msg.setDefaultButton(QtWidgets.QMessageBox.No)
        result = msg.exec_()
        if result == QtWidgets.QMessageBox.Yes:
            TemplateTool.delete(name)
            self.updateTemplates()

    def saveDate(self):
        date = self.ui.calendar.selectedDate().toString("dd.MM.yyyy")
        templates = TemplateTool.read()
        item = self.ui.listTemplates.currentItem()
        if not item:
            q = QtWidgets.QMessageBox()
            q.setIcon(QtWidgets.QMessageBox.Warning)
            q.setText("Выберите шаблон")
            q.setWindowTitle("Подтверждение")
            q.setStandardButtons(QtWidgets.QMessageBox.Ok)
            q.setDefaultButton(QtWidgets.QMessageBox.Ok)
            q.exec_()
            return

        if not templates:
            return
        if item:
            template:list[dict] = templates.get(item.text())
            if template:
                for t in template:
                    ssh.create_stream(t.get("filename"), f'{t.get("time")} {date}', t.get("duration"), t.get("key"))
            self.updateDate()
    
    def deleteDate(self):
        date = self.ui.calendar.selectedDate().toString("dd-MM-yyyy")
        # ask
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText("Удалить дату?")
        msg.setWindowTitle("Подтверждение")
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msg.setDefaultButton(QtWidgets.QMessageBox.No)
        result = msg.exec_()
        if result == QtWidgets.QMessageBox.Yes:
            ssh.delete_stream(date)
        self.updateDate()


    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    a = app.exec_()
    ssh.stop()
    sys.exit()