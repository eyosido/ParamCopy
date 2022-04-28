# ---------------
# ParamCopy - Substance 3D Designer plugin
# (c) 2019-2022 Eyosido Software SARL
# ---------------

import os, json
from paramcopy.pccore import pclog

class PCPrefs:
    # Persistent preferences

    """
    1: initial version
    """
    VERSION = "1"
    FILENAME = "pcprefs.json"

    inst = None

    @classmethod
    def instance(cls):
        if not cls.inst:
            cls.inst = PCPrefs()
        return cls.inst

    def __init__(self):
        self.setupDefaults()
        self.load()

    def setupDefaults(self):
        self.version = self.__class__.VERSION
        self.computeGraphAfterRSRoll = True # compute graph after random seed roll
        self.computeGraphAfterPaste = True
        self.computeGraphAfterVariationRecall = True
        self.optionalConfirmations = True
        self.copyDlgSelectAll = True
        
        self.copyParamsShortcut = "Ctrl+Alt+C"
        self.pasteParamsShortcut = "Ctrl+Alt+V"
        self.rollRandomSeedsShortcut = "R"
        self.storeVariationShortcut = "Shift+V"
        self.showVariationsShortcut = "Alt+V"

    @classmethod
    def filename(cls):
        path = os.path.dirname(os.path.dirname(__file__)) # go one folder up
        path = os.path.join(path, PCPrefs.FILENAME)
        return path

    def load(self):
        path = self.__class__.filename()
        if os.path.exists(path):
            try:
                with open(path, "r") as readFile:
                    j = json.load(readFile)
                self.__dict__.update(j)
                self.version = self.__class__.VERSION # force current version
            except:
                pclog.log("Error loading preferences.")

    def save(self):
        path = self.__class__.filename()
        try:
            with open(path, "w") as writeFile: 
                json.dump(self.__dict__, writeFile)
        except:
            pclog.log("Error saving preferences.")
