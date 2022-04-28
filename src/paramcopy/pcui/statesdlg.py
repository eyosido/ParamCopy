# ---------------
# ParamCopy - Substance 3D Designer plugin
# (c) 2019-2022 Eyosido Software SARL
# ---------------

from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItemIterator, QAbstractItemView
from PySide2.QtCore import Qt, QTimer

from paramcopy.pccore import pclog
from paramcopy.pccore.pcdata import PCData
from paramcopy.pccore.pcstatemgr import PCStateMgr, PCNodeStateSet
from paramcopy.pccore.pchelper import PCHelper
from paramcopy.pccore.pcprefs import PCPrefs

class PCStatesTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(("Variation Name", "Nodes", "Context"))
        self.header().resizeSection(0,230)
        self.header().resizeSection(1,40)
        #self.setDragEnabled(True)
        #self.setDragDropMode(QAbstractItemView.InternalMove)
        #elf.setAcceptDrops(True)

    def addNodeStateSet(self, nodeStateSet):
        treeItem = QtWidgets.QTreeWidgetItem(self)
        treeItem.setCheckState(0, Qt.Unchecked)
        #treeItem.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)

        # Data
        treeItem.setData(0, Qt.UserRole, nodeStateSet)

        # Name
        treeItem.setText(0, nodeStateSet.name)

        # Node count
        treeItem.setText(1, str(len(nodeStateSet.nodeStates)))

        # Context
        contextPath = "PACKAGE: "
        if nodeStateSet.packageName and len(nodeStateSet.packageName) > 0:
            contextPath += nodeStateSet.packageName
        else:
            contextPath += "(no name)"

        contextPath += " > GRAPH: " + nodeStateSet.graphName
        treeItem.setText(2, contextPath)

    # def dragEnterEvent(self, event):
    #     self.draggedItem = self.currentItem()
    #     super().dragEnterEvent(event)

    # def dropEvent(self, event):
    #     droppedIndex = self.indexAt(event.pos())
    #     if not droppedIndex.isValid():
    #         return

    #     if self.draggedItem:
    #         dParent = self.draggedItem.parent()
    #         if dParent:
    #             if self.itemFromIndex(droppedIndex.parent()) != dParent:
    #                 return
    #             dParent.removeChild(self.draggedItem)
    #             dParent.insertChild(droppedIndex.row(), self.draggedItem)

class PCStatesDlg(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.treeWidget = PCStatesTreeWidget(self)
        self.setupStaticFields()

    def setupStaticFields(self):
        self.setObjectName("PCStatesDlg")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint) # remove the Help icon in title bar
        self.setWindowTitle(PCData.APP_NAME + " - Variations")
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
        self.b_recall = QtWidgets.QPushButton(self.gp_operations)
        self.b_recall.setGeometry(QtCore.QRect(10, 10, 111, 23))
        self.b_recall.setObjectName("b_recall")
        self.b_del = QtWidgets.QPushButton(self.gp_operations)
        self.b_del.setGeometry(QtCore.QRect(160, 10, 111, 23))
        self.b_del.setObjectName("b_del")
        self.b_del_all = QtWidgets.QPushButton(self.gp_operations)
        self.b_del_all.setGeometry(QtCore.QRect(310, 10, 111, 23))
        self.b_del_all.setObjectName("b_del_all")
        self.verticalLayout.addWidget(self.gp_operations)
        self.bb_close = QtWidgets.QDialogButtonBox(self)
        self.bb_close.setOrientation(QtCore.Qt.Horizontal)
        self.bb_close.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.bb_close.setObjectName("bb_close")
        self.verticalLayout.addWidget(self.bb_close)

        self.l_status.setText(QtWidgets.QApplication.translate("PCStatesDlg", "", None, -1))
        self.b_recall.setText(QtWidgets.QApplication.translate("PCStatesDlg", "Recall Variation(s)", None, -1))
        self.b_del.setText(QtWidgets.QApplication.translate("PCStatesDlg", "Delete Variation(s)", None, -1))
        self.b_del_all.setText(QtWidgets.QApplication.translate("PCStatesDlg", "Delete All", None, -1))

        self.setupDynamicFields()

        self.b_recall.clicked.connect(self.onRecall)
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
        stateMgr = PCStateMgr.instance()
        for nodeStateSet in stateMgr.nodeStateSets.values():
            self.treeWidget.addNodeStateSet(nodeStateSet)
    
    def onRecall(self):
        proceed = True
        if PCPrefs.instance().optionalConfirmations:
            proceed = PCHelper.askYesNoQuestion("Recall selected variations?", True, self)

        if proceed:
            self.setStatus("Recalling variation(s)...")
            QTimer.singleShot(1, lambda:self.doRecall())

    def doRecall(self):
        iter = QTreeWidgetItemIterator(self.treeWidget)
        variationCount = 0
        while iter.value():
            treeItem = iter.value()
            if treeItem.checkState(0) == Qt.Checked:
                variationCount += 1
                nodeStateSet = treeItem.data(0, Qt.UserRole)
                misses = nodeStateSet.recallNodeStates()
                if misses > 0:
                    PCHelper.displayInfoMsg("Partial variation recall, " + str(misses) + " node(s) could not be found and have not been restored.", self)
            iter += 1
        
        if misses > 0:
            status = "Partial variation recall complete."
        else:
            status = str(variationCount) + " variation(s) successfully recalled!"
        self.setStatus(status)

        self.computeGraphIfNeeded()

    def computeGraphIfNeeded(self):
        if PCPrefs.instance().computeGraphAfterVariationRecall:
            PCHelper.computeCurrentGraph()

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
            PCHelper.displayErrorMsg("There is currently no variation to delete.")
            return

        if not self.anySelected():
            PCHelper.displayErrorMsg("No variation selected.")
            return

        if PCHelper.askYesNoQuestion("Delete selected variation(s)?", False, self):
            iter = QTreeWidgetItemIterator(self.treeWidget)
            pcStateMgr = PCStateMgr.instance()
            indicesToDelete = []
            while iter.value():
                treeItem = iter.value()
                if treeItem.checkState(0) == Qt.Checked:
                    nodeStateSet = treeItem.data(0, Qt.UserRole)
                    if pcStateMgr.deleteStateSet(nodeStateSet.name):
                        indicesToDelete.append(self.treeWidget.indexOfTopLevelItem(treeItem))
                iter += 1

            for i in reversed(indicesToDelete): # need to delete from down to top as indices change after each removal
                self.treeWidget.takeTopLevelItem(i)

            self.clearStatus()

    def onDeleteAll(self):
        if not self.anyItem():
            PCHelper.displayErrorMsg("There is currently no variation to delete.")
            return
            
        if PCHelper.askYesNoQuestion("Delete all variations?", False, self):
            PCStateMgr.instance().deleteAll()
            self.treeWidget.clear()
            self.clearStatus()

    def onClose(self):
        self.close()
