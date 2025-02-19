# ---------------
# ParamCopy - Substance 3D Designer plugin
# (c) 2019-2025 Eyosido Software SARL
# ---------------

from functools import partial
import random

import sd
if sd.getContext().getSDApplication().getVersion() < "14.0.0":
    from PySide2.QtCore import QObject, Signal, Slot
    from PySide2.QtWidgets import QToolBar, QAction
    from PySide2.QtGui import QIcon, QPixmap, QKeySequence
else:
    from PySide6.QtCore import QObject, Signal, Slot
    from PySide6.QtWidgets import QToolBar
    from PySide6.QtGui import QIcon, QPixmap, QKeySequence, QAction
    
import sd
from sd.context import Context
from sd.api.sdapplication import SDApplication
from sd.api.sduimgr import SDUIMgr
from sd.api.sdgraph import SDGraph
from sd.api.sddefinition import SDDefinition
from sd.api.sbs.sdsbscompnode import SDSBSCompNode
from sd.api.sdvalueint import SDValueInt

from paramcopy.pccore.pchelper import PCHelper
from paramcopy.pccore import pclog
from paramcopy.pccore.pcdata import PCData
from paramcopy.pccore.pccopier import PCCopier
from paramcopy.pccore.pcprefs import PCPrefs
from paramcopy.pccore.pcstatemgr import PCStateMgr
from paramcopy.pccore.pcinspector import PCInspector

from paramcopy.pcui.pctoolbar import PCGraphCustomToolbarMgr
from paramcopy.pcui.copydlg import PCCopyDlg
from paramcopy.pcui.pastedlg import PCPasteDlg
from paramcopy.pcui.prefsdlg import PCPrefsDlg
from paramcopy.pcui.newstatedlg import PCNewStateDlg
from paramcopy.pcui.statesdlg import PCStatesDlg
from paramcopy.pcui.clipboardsdlg import PCClipboardsDlg

class PCUIMgr(QObject):
    inst = None

    @classmethod
    def instance(cls):
        if cls.inst == None:  
            cls.inst = PCUIMgr()
        return cls.inst

    def __init__(self):
        super().__init__()
        self.sdApp = sd.getContext().getSDApplication()
        self.sdUiMgr = self.sdApp.getQtForPythonUIMgr()
        self.graphViewCreatedCbId = None
        self.toolbars = None
        self.copyPixmap = None
        self.pastePixmap = None
        self.toolbarMgr = None
        self.copyDlg = None
        self.pasteDlg = None
        self.prefsDlg = None
        self.newStateDlg = None
        self.statesDlg = None
        self.clipboardsDlg = None
        self.shortcutsCreated = False

    def loadSvgToolbarIcon(self, iconName):
        icon = None
        pixmap = PCHelper.loadSvgAsPixmap(iconName + ".svg", PCData.TOOLBAR_ICON_SIZE, PCData.TOOLBAR_ICON_SIZE)
        if pixmap:
            icon = QIcon(pixmap)
        return icon

    def loadPngToolbarIcon(self, iconName):
        pixmap = PCHelper.loadPngAsPixmap(iconName + ".png")
        if pixmap:
            icon = QIcon(pixmap)
        return icon
        
    def setupUI(self):
        # load icons
        self.copyIcon = self.loadSvgToolbarIcon("copy")
        self.pasteIcon = self.loadSvgToolbarIcon("paste")
        self.toolbarIcon = self.loadSvgToolbarIcon("toolbar")
        self.rollIcon = self.loadSvgToolbarIcon("roll")
        self.varitationStoreIcon = self.loadPngToolbarIcon("variation_store")
        self.varitationRecallIcon = self.loadPngToolbarIcon("variation_recall")
        self.clipboardIcon = self.loadPngToolbarIcon("clipboard")

        if self.copyIcon and self.pasteIcon and self.toolbarIcon and self.rollIcon:
            self.toolbarMgr = PCGraphCustomToolbarMgr(self.createToolbar, self.toolbarIcon)
            self.setupMenu()
        else:
            pclog.log("ERROR: cannot find toolbar icons")

        self.toolbarMgr.createToolbarForExistingGraphViews()

    def removeUI(self):
        if self.toolbarMgr:
            self.toolbarMgr.cleanup()
            self.toolbarMgr = None
            pclog.log("removeUI() self.toolbarMgr = None")

        self.copyDlg = None
        self.pasteDlg = None
        self.prefsDlg = None
        self.newStateDlg = None
        self.statesDlg = None
        self.clipboardsDlg = None

        PCCopier.inst = None
        PCStateMgr.inst = None
        
        if self.menu:
            self.removeMenu()
            self.menu = None

        self.shortcutsCreated = False

    def createToolbar(self):
        toolbar = QToolBar(self.sdUiMgr.getMainWindow())
        toolbar.setObjectName(PCData.TOOLBAR_OBJ_NAME)

        copyAction = toolbar.addAction(self.copyIcon, "Copy params")
        copyAction.setToolTip("Copy parameters of the selected node")
        copyAction.triggered.connect(self.onCopy)

        pasteAction = toolbar.addAction(self.pasteIcon, "Paste params")
        pasteAction.setToolTip("Paste parameters into selected node(s)")
        pasteAction.triggered.connect(self.onPaste)

        pasteAction = toolbar.addAction(self.clipboardIcon, "Clipboards")
        pasteAction.setToolTip("Open the Clipboards window")
        pasteAction.triggered.connect(self.onClipboards)

        pasteAction = toolbar.addAction(self.rollIcon, "Roll Random Seeds")
        pasteAction.setToolTip("Roll Random Seeds of selected nodes")
        pasteAction.triggered.connect(self.onRollRandomSeeds)

        pasteAction = toolbar.addAction(self.varitationStoreIcon, "Store Variation")
        pasteAction.setToolTip("Store a variation for the selected nodes")
        pasteAction.triggered.connect(self.onStoreNodeStates)

        pasteAction = toolbar.addAction(self.varitationRecallIcon, "Show/Recall Variations")
        pasteAction.setToolTip("Show/Recall Variations")
        pasteAction.triggered.connect(self.onRecallNodeStates)

        return toolbar

    def setupMenu(self):
        self.menu =  self.sdUiMgr.findMenuFromObjectName(PCData.MENU_OBJ_NAME)
        if self.menu:
            # delete existing menu to start off clean in case of upgrade
            self.sdUiMgr.deleteMenu(self.menu.objectName())

        self.menu = self.sdUiMgr.newMenu(PCData.MENU_TITLE, PCData.MENU_OBJ_NAME)

        paramsSubmenu = self.menu.addMenu("Params")

        self.copyParamsAction = QAction("Copy Node Parameters...", paramsSubmenu)
        self.copyParamsAction.triggered.connect(self.onCopy)
        paramsSubmenu.addAction(self.copyParamsAction)

        self.pasteParamsAction = QAction("Paste Node Parameters...", paramsSubmenu)
        self.pasteParamsAction .triggered.connect(self.onPaste)
        paramsSubmenu.addAction(self.pasteParamsAction)

        self.clipboardsAction = QAction("Clipboards...", paramsSubmenu)
        self.clipboardsAction.triggered.connect(self.onClipboards)
        paramsSubmenu.addAction(self.clipboardsAction)

        statesSubmenu = self.menu.addMenu("Variations")

        self.storeVariationAction = QAction("Store Variation...", statesSubmenu)
        self.storeVariationAction.triggered.connect(self.onStoreNodeStates)
        statesSubmenu.addAction(self.storeVariationAction)

        self.showVariationAction = QAction("Show/Recall Variations...", statesSubmenu)
        self.showVariationAction.triggered.connect(self.onRecallNodeStates)
        statesSubmenu.addAction(self.showVariationAction)

        self.rollRandomSeedAction = QAction("Roll Random Seeds...", self.menu)
        self.rollRandomSeedAction.triggered.connect(self.onRollRandomSeeds)
        self.menu.addAction(self.rollRandomSeedAction)

        # action = QAction("Inspector...", self.menu)
        # action.triggered.connect(self.onInspector)
        # self.menu.addAction(action)

        action = QAction("Preferences...", self.menu)
        action.triggered.connect(self.onPreferences)
        self.menu.addAction(action)

    def removeMenu(self):
        if self.menu:
            self.sdUiMgr.deleteMenu(self.menu.objectName())
            self.menu = None

            self.copyParamsAction = None
            self.pasteParamsAction = None
            self.clipboardsAction = None
            self.storeVariationAction = None
            self.showVariationAction = None
            self.rollRandomSeedAction = None

    def setupShortcuts(self):
        prefs = PCPrefs.instance()
        self.copyParamsAction.setShortcut(QKeySequence(prefs.copyParamsShortcut))
        self.pasteParamsAction.setShortcut(QKeySequence(prefs.pasteParamsShortcut))
        self.storeVariationAction.setShortcut(QKeySequence(prefs.storeVariationShortcut))
        self.showVariationAction.setShortcut(QKeySequence(prefs.showVariationsShortcut))
        self.rollRandomSeedAction.setShortcut(QKeySequence(prefs.rollRandomSeedsShortcut))
        self.shortcutsCreated = True
        pclog.log("Shortcuts created")

    def onCopy(self):
        if not PCHelper.checkCurrentGraph():
            return
        nodes = self.sdUiMgr.getCurrentGraphSelectedNodes()
        if nodes and nodes.getSize() > 0:
            if nodes.getSize() == 1:
                node = nodes.getItem(0)

                definition = node.getDefinition()
                if definition.getId().startswith("sbs::function"):
                    PCHelper.displayErrorMsg("Function nodes cannot be copied.")
                elif not isinstance(node, SDSBSCompNode): # only SDSBSCompNode so we can get input inheritance properties
                    PCHelper.displayErrorMsg("Node type not supported.")
                else:
                    if not self.copyDlg:
                        self.copyDlg = PCCopyDlg(self.sdUiMgr.getMainWindow())
                    self.copyDlg.show(node)
            else:
                PCHelper.displayErrorMsg("Multiple node selected: please select a single node to use the Copy Params functionalty.")
        else:
            PCHelper.displayErrorMsg("No Selection: please select a node to use the Copy Parameters functionalty.")

    def onPaste(self):
        if not PCHelper.checkCurrentGraph():
            return
        nodes = self.sdUiMgr.getCurrentGraphSelectedNodes()
        clipboard = PCCopier.instance().currentClipboard

        if clipboard:
            if nodes and nodes.getSize() > 0:
                if not self.pasteDlg:
                    self.pasteDlg = PCPasteDlg(self.sdUiMgr.getMainWindow())
                self.pasteDlg.show(clipboard, nodes)
            else:
                PCHelper.displayErrorMsg("No Selection: please select a node to use the Paste Parameters functionalty.")
        else:
            PCHelper.displayErrorMsg("No clipboard data: please first copy node parameters before using the Paste functionality.")

    def onStoreNodeStates(self):
        if not PCHelper.checkCurrentGraph():
            return
        nodes = self.sdUiMgr.getCurrentGraphSelectedNodes()
        if nodes and nodes.getSize() > 0:
            if not self.newStateDlg:
                self.newStateDlg = PCNewStateDlg(self.sdUiMgr.getMainWindow())
            self.newStateDlg.show(nodes)
        else:
            PCHelper.displayErrorMsg("No selection: please select one or more nodes to create a new Variation.")

    def onNodeStatesUpdated(self):
        if self.statesDlg:
            self.statesDlg.populate()

    def onRecallNodeStates(self):
        if not PCHelper.checkCurrentGraph():
            return
        stateMgr = PCStateMgr.instance()
        if len(stateMgr.nodeStateSets) > 0:
            if not self.statesDlg:
                self.statesDlg = PCStatesDlg(self.sdUiMgr.getMainWindow())
            self.statesDlg.show()
        else:
            PCHelper.displayErrorMsg("There are currently no Variation being stored.")

    def onRollRandomSeeds(self):
        if not PCHelper.checkCurrentGraph():
            return
        nodes = self.sdUiMgr.getCurrentGraphSelectedNodes()
        prefs = PCPrefs.instance()
        if nodes and nodes.getSize() > 0:
            nodeCount = nodes.getSize()
            proceed = True
            if prefs.optionalConfirmations:
                # ask user confirmation
                if nodeCount == 1:
                    msgPrefix = "The Random Seed base parameter of the selected node is going\nto be updated to a random value."
                else:
                    msgPrefix = "The Random Seed base parameters of the " + str(nodeCount) + " selected nodes\nare going to be updated to random values."
                msg = msgPrefix + " Do you confirm?"
                proceed = PCHelper.askYesNoQuestion(msg)

            if proceed:
                for n in range(0, nodeCount):
                    node = nodes.getItem(n)
                    valInt = random.randint(0,9999)
                    node.setInputPropertyValueFromId("$randomseed", SDValueInt.sNew(valInt))
        else:
            PCHelper.displayErrorMsg("No Selection: please select a node to use the Roll Random Seeds functionalty.")
        
        if prefs.computeGraphAfterRSRoll:
            PCHelper.computeCurrentGraph()

    def onInspector(self):
        if not PCHelper.checkCurrentGraph():
            return

        nodes = self.sdUiMgr.getCurrentGraphSelectedNodes()
        if nodes and nodes.getSize() > 0:
            if nodes.getSize() == 1:
                node = nodes.getItem(0)
                PCInspector.log(node)
            else:
                PCHelper.displayErrorMsg("Multiple node selected: please select a single node to use the Inspector functionalty.")
        else:
            PCHelper.displayErrorMsg("No Selection: please select a node to use the Inspector functionalty.")        

    def onClipboards(self):
        if not PCHelper.checkCurrentGraph():
            return

        copier = PCCopier.instance()
        if len(copier.clipboards) > 0:
            if not self.clipboardsDlg:
                self.clipboardsDlg = PCClipboardsDlg(self.sdUiMgr.getMainWindow())
            self.clipboardsDlg.show()
        else:
            PCHelper.displayErrorMsg("There are currently no clipboard being stored.")

    def onClipboardsUpdated(self):
        if self.clipboardsDlg:
            self.clipboardsDlg.populate()

    def onPreferences(self):
        if not self.prefsDlg:
            self.prefsDlg = PCPrefsDlg(self.sdUiMgr.getMainWindow())
        self.prefsDlg.show()
