import json
import os
from PyQt5 import QtCore

class ConfigTool:

    @staticmethod
    def read() -> dict:
        appdata = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.ConfigLocation)
        config = None
        if os.path.exists(appdata+"/streamtool/config.json"):
            file = open(appdata+"/streamtool/config.json", "r")
            data = file.read()
            file.close()
            if data:
                config = json.loads(data)
        return config
    
    def write(data: dict):
        appdata = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.ConfigLocation)
        if not os.path.exists(appdata+"/streamtool"):
            os.mkdir(appdata+"/streamtool")
        json.dump(data, open(appdata+"/streamtool/config.json", "w"), indent=4)