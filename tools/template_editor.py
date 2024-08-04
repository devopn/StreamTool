import json
from PyQt5 import QtCore
import os

class TemplateTool:
    appdata = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.ConfigLocation)
    tj = os.path.join(appdata, "streamtool", "templates.json")
    st = os.path.join(appdata, "streamtool")
    @staticmethod
    def read() -> dict:
        
        data = {}
        
        if os.path.exists(TemplateTool.tj):
            file = open(TemplateTool.tj, "r")
            file_data = file.read()
            print(file_data)
            file.close()
            if file_data:
                data = json.loads(file_data)
        return data
    
    def write(name:str, template: dict):
        if not os.path.exists(TemplateTool.st):
            os.mkdir(TemplateTool.st)
        data = TemplateTool.read()
        data[name] = template
        json.dump(data, open(TemplateTool.tj, "w"), indent=4)

    def delete(name:str):
        data = TemplateTool.read()
        if data:
            del data[name]
            json.dump(data, open(TemplateTool.tj, "w"), indent=4)