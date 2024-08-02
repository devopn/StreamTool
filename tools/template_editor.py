import json
from PyQt5 import QtCore
import os

class TemplateTool:

    @staticmethod
    def read() -> dict:
        appdata = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.ConfigLocation)
        data = None
        if os.path.exists(appdata+"/streamtool/templates.json"):
            file = open(appdata+"/streamtool/templates.json", "r")
            file_data = file.read()
            file.close()
            if file_data:
                data = json.loads(file_data)
        return data
    
    def write(name:str, template: dict):
        appdata = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.ConfigLocation)
        if not os.path.exists(appdata+"/streamtool"):
            os.mkdir(appdata+"/streamtool")
        data = TemplateTool.read()
        if not data:
            data = {}
        data[name] = template
        json.dump(data, open(appdata+"/streamtool/templates.json", "w"), indent=4)

    def delete(name:str):
        appdata = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.ConfigLocation)
        data = TemplateTool.read()
        if data:
            del data[name]
            json.dump(data, open(appdata+"/streamtool/templates.json", "w"), indent=4)