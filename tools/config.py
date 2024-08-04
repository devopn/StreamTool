import json
import os
from PyQt5 import QtCore

class ConfigTool:
    appdata = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.ConfigLocation)
    st = os.path.join(appdata, "streamtool")
    cj = os.path.join(appdata, "streamtool", "config.json")
    @staticmethod
    def read() -> dict:
        appdata = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.ConfigLocation)
        config = None
        if os.path.exists(ConfigTool.cj):
            file = open(ConfigTool.cj, "r")
            data = file.read()
            file.close()
            if data:
                config = json.loads(data)
        return config
    
    def write(data: dict):
        appdata = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.ConfigLocation)
        if not os.path.exists(ConfigTool.st):
            os.mkdir(ConfigTool.st)
        json.dump(data, open(ConfigTool.cj, "w"), indent=4)