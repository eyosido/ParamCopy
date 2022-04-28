# ---------------
# ParamCopy - Substance 3D Designer plugin
# (c) 2019-2022 Eyosido Software SARL
# ---------------

from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Qt, QTimer
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItemIterator, QSizePolicy, QCheckBox

from sd.api.sdnode import SDNode

from paramcopy.pccore import pclog
from paramcopy.pccore.pcdata import PCData
from paramcopy.pccore.pchelper import PCHelper
from paramcopy.pccore.pccopier import PCCopier
from paramcopy.pccore.pcprefs import PCPrefs

from paramcopy.pcui.paramtree import PCParamTreeWidget
from paramcopy.pcui.paramdlg import PCParamDlgBase

class PCPasteDlg(PCParamDlgBase):
    def __init__(self, parent=None):
        super().__init__(False, parent)
        self.setupStaticFields("PCPasteDlg", PCData.APP_NAME + " - Paste")

    def setupStaticFields(self, dlgName, title):
        super().setupStaticFields(dlgName, title)
        self.resize(500, 600)

#    def show(self, sourceNode, destNodes):
    def show(self, sourceNodeState, destNodes):
        self.clearStatus()
        self.destNodes = destNodes
        self.sourceNodeState = sourceNodeState

        nodeCount = destNodes.getSize()
        #paramCount = len(copier.clipboard)
        paramCount = len(sourceNodeState.state.params)
        
        nodeStr = " node"
        if nodeCount > 1:
            nodeStr += "s"

        parameterStr = " parameter"
        if paramCount > 1:
            parameterStr += "s"
            
        #sourceNodeName = PCHelper.getPropertyOrDefinitionName(sourceNode.getDefinition())
        sourceNodeName = sourceNodeState.nodeIdentifier.getName()
        self.l_node_desc.setText(str(paramCount) + parameterStr + " from " + sourceNodeName + " to paste into " + str(nodeCount) + nodeStr + ".")
        
        #self.treeWidget.populateFromPropertyIds(sourceNode, copier.clipboard)
        self.treeWidget.populateFromNodeState(sourceNodeState)
        return super().show()

    def setupDynamicFields(self):
        super().setupDynamicFields()

        self.gb_advanced.setMinimumSize(QtCore.QSize(0, 150))

        baseY = 30
        spacingY = 24
        self.chk_same_type = QtWidgets.QCheckBox("Paste only into nodes of the same type as the source node", self.gb_advanced)
        self.chk_same_type.setToolTip("Parameters will be pasted only into nodes having the same type as the source. For instance,\n"
"if parameters are copied from a Blend node, they will be pasted only into other Blend nodes\n"
"if this option is selected.")
        self.chk_same_type.setGeometry(QtCore.QRect(20, baseY + spacingY, 470, 17))

        self.chk_paste_same_id = QtWidgets.QCheckBox("Enable pasting Specific Parameters with same ID for different type nodes", self.gb_advanced)
        self.chk_paste_same_id.setToolTip("By default, only Base Parameters are copied between nodes of different types, and all parameters between\n"
"nodes of the same type. This option enables to copy Specific Parameters between nodes of different types\n"
"when those have identical parameter IDs. This must be used with caution as differently typed nodes may\n"
"use the same IDs for parameters having different meaning and scaling properties per node type.")
        self.chk_paste_same_id.setGeometry(QtCore.QRect(20, baseY + (2*spacingY), 470, 17))
        self.l_paste_same_id = QtWidgets.QLabel("NOTE: nodes of different types may use a same ID for parametters with different meanings."
            "\nIt is recommended to use this option only with nodes where parameters having a same ID\nalso share a same purpose and scale.", self.gb_advanced)
        self.l_paste_same_id.setGeometry(QtCore.QRect(20, baseY + (3*spacingY)-10, 470, 60))

        self.chk_same_type.stateChanged.connect(self.onExclusiveChkStateChange)
        self.chk_paste_same_id.stateChanged.connect(self.onExclusiveChkStateChange)

    def onExclusiveChkStateChange(self, state):
        chk = self.sender()
        if chk == self.chk_same_type:
            other = self.chk_paste_same_id
        else:
            other = self.chk_same_type
        
        if state == Qt.Checked:
            otherNewState = Qt.Unchecked if chk.checkState() == Qt.Checked else Qt.Checked
            other.setCheckState(otherNewState)

    def onOK(self):
        propertyIds = self.treeWidget.retrieveCheckedProperties()
        if propertyIds and len(propertyIds) > 0:
            pasteOptions = PCCopier.PasteOptions()
            pasteOptions.sameTypeAsSource = self.chk_same_type.checkState() == Qt.Checked
            pasteOptions.crossTypeSpecificParamsCopy = self.chk_paste_same_id.checkState() == Qt.Checked

            self.setStatus("Pasting parameters...")
            QTimer.singleShot(1, lambda:self.doPaste(propertyIds, pasteOptions))
        else:
            self.close()
            QTimer.singleShot(1, lambda:self.warnNoSelection())            

    def doPaste(self, propertyIds, pasteOptions):
        #PCCopier.instance().pasteDataInto(propertyIds, self.destNodes, pasteOptions)
        PCCopier.instance().pasteNodeStateInto(self.sourceNodeState, self.destNodes, pasteOptions, propertyIds)
        QTimer.singleShot(1, lambda:self.computeGraphIfNeeded())
        self.close()

    def computeGraphIfNeeded(self):
        if PCPrefs.instance().computeGraphAfterPaste:
            PCHelper.computeCurrentGraph()

    def warnNoSelection(self):
        PCHelper.displayInfoMsg("No parameters were selected, nothing has been pasted.")

