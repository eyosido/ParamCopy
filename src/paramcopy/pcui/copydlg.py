# ---------------
# ParamCopy - Substance 3D Designer plugin
# (c) 2019-2025 Eyosido Software SARL
# ---------------

import sd
if sd.getContext().getSDApplication().getVersion() < "14.0.0":
    from PySide2 import QtCore, QtWidgets
    from PySide2.QtCore import Qt
    from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItemIterator, QSizePolicy
    from PySide2.QtCore import Qt, QTimer
else:
    from PySide6 import QtCore, QtWidgets
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItemIterator, QSizePolicy
    from PySide6.QtCore import Qt, QTimer

from sd.api.sdnode import SDNode

from paramcopy.pccore import pclog
from paramcopy.pccore.pcdata import PCData
from paramcopy.pccore.pchelper import PCHelper
from paramcopy.pccore.pccopier import PCCopier
from paramcopy.pccore.pcprefs import PCPrefs

from paramcopy.pcui.paramtree import PCParamTreeWidget
from paramcopy.pcui.paramdlg import PCParamDlgBase

class PCCopyDlg(PCParamDlgBase):
    def __init__(self, parent=None):
        super().__init__(True, parent)

        self.sourceNodeId= None
        self.sourceGraphId = None
        self.sourcePackageId = None # package id is its file path

        self.setupStaticFields("PCCopyDlg", PCData.APP_NAME + " - Copy")

    def show(self, node):
        self.node = node
        definition = node.getDefinition()
        name = definition.getLabel()
        if not name or len(name) == 0:
            name = definition.getId()
        self.l_node_desc.setText("Node: " + name)
        self.treeWidget.populateFromNode(node, PCPrefs.instance().copyDlgSelectAll)
        self.le_clipboard_name.setText("")
        return super().show()

    def onOK(self):
        copier = PCCopier.instance()
        clipboardName = self.le_clipboard_name.text()
        if clipboardName and len(clipboardName) > 0:
            if copier.clipboardExists(clipboardName):
                clipboardName = None
                PCHelper.displayErrorMsg("A clipboard named already exists, please use another name.")
                return

        propertyIds =  self.treeWidget.retrieveCheckedProperties()            
        if propertyIds and len(propertyIds) > 0:
            copier.setClipboard(self.node, propertyIds, clipboardName)
            if clipboardName:
                from paramcopy.pcui.pcuimgr import PCUIMgr
                PCUIMgr.instance().onClipboardsUpdated()
            self.close()
        else:
            self.close()
            QTimer.singleShot(1, lambda:self.warnNoSelection())

    def warnNoSelection(self):
        PCHelper.displayInfoMsg("No parameters were selected, nothing has been copied.")
