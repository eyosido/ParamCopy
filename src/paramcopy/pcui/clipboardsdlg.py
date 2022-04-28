# ---------------
# ParamCopy - Substance 3D Designer plugin
# (c) 2019-2022 Eyosido Software SARL
# ---------------

from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItemIterator, QAbstractItemView
from PySide2.QtCore import Qt, QTimer

from paramcopy.pccore import pclog
from paramcopy.pccore.pcdata import PCData
from paramcopy.pccore.pcstatemgr import PCStateMgr, PCNodeStateSet
from paramcopy.pccore.pchelper import PCHelper
from paramcopy.pccore.pcprefs import PCPrefs
from paramcopy.pccore.pccopier import PCCopier

class PCClipboardsTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(("Clipboard Name", "Params", "Parameter list"))
        self.header().resizeSection(0,230)
        self.header().resizeSection(1,45)

    def addClipboard(self, clipboard, clipboardName):
        treeItem = QtWidgets.QTreeWidgetItem(self)
        treeItem.setCheckState(0, Qt.Unchecked)

        # Data
        treeItem.setData(0, Qt.UserRole, clipboard)

        # Clipboard name
        treeItem.setText(0, clipboardName)

        # Parameter count
        treeItem.setText(1, str(len(clipboard.state.params)))

        # Parameter list
        treeItem.setText(2, clipboard.state.paramNames())

class PCClipboardsDlg(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.treeWidget = PCClipboardsTreeWidget(self)
        self.setupStaticFields()

    def setupStaticFields(self):
        self.setObjectName("PCClipboardsDlg")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint) # remove the Help icon in title bar
        self.setWindowTitle(PCData.APP_NAME + " - Clipboards")
        self.resize(652, 404)
        self.setModal(False)

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.l_status = QtWidgets.QLabel(self)
        self.l_status.setMinimumSize(QtCore.QSize(0, 30))
        self.l_status.setAlignment(QtCore.Qt.AlignCenter)
        self.l_status.setObjectName("l_status")
        self.verticalLayout.addWidget(self.l_status)
        self.gp_operations = QtWidgets.QGroupBox(self)
        self.gp_operations.setTitle("")
        self.gp_operations.setFlat(True)
        self.gp_operations.setObjectName("gp_operations")
        self.b_del = QtWidgets.QPushButton(self.gp_operations)
        self.b_del.setGeometry(QtCore.QRect(300, 10, 111, 23))
        self.b_del.setObjectName("b_del")
        self.b_del_all = QtWidgets.QPushButton(self.gp_operations)
        self.b_del_all.setGeometry(QtCore.QRect(430, 10, 111, 23))
        self.b_del_all.setObjectName("b_del_all")
        self.b_set_current = QtWidgets.QPushButton(self.gp_operations)
        self.b_set_current.setGeometry(QtCore.QRect(0, 10, 151, 23))
        self.b_set_current.setObjectName("b_set_current")
        self.b_paste = QtWidgets.QPushButton(self.gp_operations)
        self.b_paste.setGeometry(QtCore.QRect(170, 10, 111, 23))
        self.b_paste.setObjectName("b_paste")
        self.verticalLayout.addWidget(self.gp_operations)
        self.bb_close = QtWidgets.QDialogButtonBox(self)
        self.bb_close.setOrientation(QtCore.Qt.Horizontal)
        self.bb_close.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.bb_close.setObjectName("bb_close")
        self.verticalLayout.addWidget(self.bb_close)

        self.l_status.setText(QtWidgets.QApplication.translate("PCClipboardDlg", "<status>", None, -1))
        self.b_del.setToolTip(QtWidgets.QApplication.translate("PCClipboardDlg", "Delete selected clipboard(s)", None, -1))
        self.b_del.setText(QtWidgets.QApplication.translate("PCClipboardDlg", "Delete Clipboard(s)", None, -1))
        self.b_del_all.setToolTip(QtWidgets.QApplication.translate("PCClipboardDlg", "Delete all clipboards", None, -1))
        self.b_del_all.setText(QtWidgets.QApplication.translate("PCClipboardDlg", "Delete All", None, -1))
        self.b_set_current.setToolTip(QtWidgets.QApplication.translate("PCClipboardDlg", "Set selected clipboard as current so it can be pasted with subsequent Paste operations", None, -1))
        self.b_set_current.setText(QtWidgets.QApplication.translate("PCClipboardDlg", "Set Current Clipboard", None, -1))
        self.b_paste.setToolTip(QtWidgets.QApplication.translate("PCClipboardDlg", "Paste the selected clipboard into the current node selection using default\n"
"pasting parameters: base parameters are copied regardless of the node type,\n"
"specific parameters are pasted only in nodes of the same type. This function\n"
"does not set/change the current clipboard.", None, -1))
        self.b_paste.setText(QtWidgets.QApplication.translate("PCClipboardDlg", "Paste into selection", None, -1))

        self.setupDynamicFields()

        self.b_set_current.clicked.connect(self.onSetCurrent)
        self.b_paste.clicked.connect(self.onPaste)
        self.b_del.clicked.connect(self.onDelete)
        self.b_del_all.clicked.connect(self.onDeleteAll)
        self.bb_close.rejected.connect(self.onClose)

    def setupDynamicFields(self):
         self.verticalLayout.insertWidget(0, self.treeWidget)

    def show(self):
        self.populate()
        super().show()

    def setStatus(self, text):
         self.l_status.setText(text)

    def clearStatus(self):
        self.setStatus("")

    def populate(self):
        self.treeWidget.clear()
        self.setStatus("")

        copier = PCCopier.instance()
        for clipboardName, clipboard in copier.clipboards.items():
            self.treeWidget.addClipboard(clipboard, clipboardName)
    
    def onSetCurrent(self):
        treeItem = self.getSingleSelectedItem()
        if treeItem:
            clipboardName = treeItem.text(0)
            PCCopier.instance().setCurrentClipboard(clipboardName)
            self.setStatus("Current clipboard set to \"" + clipboardName + "\"")
        else:
            PCHelper.displayErrorMsg("Set Current Clipboard requires a single clipboard to be selected.")

    def onPaste(self):
        treeItem = self.getSingleSelectedItem()
        if treeItem:
            clipboardName = treeItem.text(0)
            proceed = True
            if PCPrefs.instance().optionalConfirmations:
                proceed = PCHelper.askYesNoQuestion("Paste clipboard \"" + clipboardName + "\" into current node selection?", True, self)

            if proceed:
                self.setStatus("Pasting clipboard \"" + clipboardName + "\" into current node selection...")
                QTimer.singleShot(1, lambda:self.doPaste(treeItem.data(0, Qt.UserRole), clipboardName))
        else:
            PCHelper.displayErrorMsg("Pasting clipboard requires a single clipboard to be selected.")

    def doPaste(self, clipboard, clipboardName):
        pasteOptions = PCCopier.PasteOptions()
        pasteOptions.sameTypeAsSource = False
        pasteOptions.crossTypeSpecificParamsCopy = False
        from paramcopy.pcui.pcuimgr import PCUIMgr
        nodes = PCUIMgr.instance().sdUiMgr.getCurrentGraphSelectedNodes()
        PCCopier.instance().pasteNodeStateInto(clipboard, nodes, pasteOptions)
        self.setStatus("Clipboard \"" + clipboardName + "\" has been pasted into current node selection.")
        QTimer.singleShot(1, lambda:self.computeGraphIfNeeded())

    def computeGraphIfNeeded(self):
        if PCPrefs.instance().computeGraphAfterVariationRecall:
            PCHelper.computeCurrentGraph()

    def getSingleSelectedItem(self):
        iter = QTreeWidgetItemIterator(self.treeWidget)
        selectedCount = 0
        selectedItem = None
        while iter.value():
            treeItem = iter.value()
            if treeItem.checkState(0) == Qt.Checked:
                selectedItem = treeItem
                selectedCount += 1
            iter += 1
        return selectedItem if selectedCount == 1 else None

    def anySelected(self):
        iter = QTreeWidgetItemIterator(self.treeWidget)
        while iter.value():
            treeItem = iter.value()
            if treeItem.checkState(0) == Qt.Checked:
                return True
            iter += 1
        return False

    def anyItem(self):
        iter = QTreeWidgetItemIterator(self.treeWidget)
        return iter and iter.value()

    def onDelete(self):
        if not self.anyItem():
            PCHelper.displayErrorMsg("There is currently no clipboard to delete.")
            return

        if not self.anySelected():
            PCHelper.displayErrorMsg("No clipboard selected.")
            return

        if PCHelper.askYesNoQuestion("Delete selected clipboards(s)?", False, self):
            iter = QTreeWidgetItemIterator(self.treeWidget)
            copier = PCCopier.instance()
            indicesToDelete = []
            while iter.value():
                treeItem = iter.value()
                if treeItem.checkState(0) == Qt.Checked:
                    clipboardName = treeItem.text(0)
                    if copier.deleteClipboard(clipboardName):
                        indicesToDelete.append(self.treeWidget.indexOfTopLevelItem(treeItem))
                iter += 1

            for i in reversed(indicesToDelete): # need to delete from down to top as indices change after each removal
                self.treeWidget.takeTopLevelItem(i)

            self.clearStatus()

    def onDeleteAll(self):
        if not self.anyItem():
            PCHelper.displayErrorMsg("There is currently no clipboard to delete.")
            return

        if PCHelper.askYesNoQuestion("Delete all clipboards?", False, self):
            PCCopier.instance().deleteAllClipboards()
            self.treeWidget.clear()
            self.clearStatus()

    def onClose(self):
        self.close()
