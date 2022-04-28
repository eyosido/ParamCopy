# ---------------
# ParamCopy - Substance 3D Designer plugin
# (c) 2019-2022 Eyosido Software SARL
# ---------------

from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import  QDialogButtonBox
from PySide2.QtCore import Qt

from paramcopy.pccore import pclog
from paramcopy.pccore.pcdata import PCData
from paramcopy.pccore.pcstatemgr import PCStateMgr, PCNodeStateSet
from paramcopy.pccore.pchelper import PCHelper

class PCNewStateDlg(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupStaticFields()
        self.nodeArray = None

    def setupStaticFields(self):
        self.setObjectName("PCNewStateDlg")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint) # remove the Help icon in title bar
        self.setWindowTitle(PCData.APP_NAME + " - Store Variation")
        self.setFixedSize(401, 236)

        self.bb_ok_cancel = QtWidgets.QDialogButtonBox(self)
        self.bb_ok_cancel.setGeometry(QtCore.QRect(140, 200, 251, 32))
        self.bb_ok_cancel.setOrientation(QtCore.Qt.Horizontal)
        self.bb_ok_cancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.bb_ok_cancel.setObjectName("bb_ok_cancel")
        self.l_desc = QtWidgets.QLabel(self)
        self.l_desc.setGeometry(QtCore.QRect(10, 10, 371, 31))
        self.l_desc.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.l_desc.setWordWrap(True)
        self.l_desc.setObjectName("l_desc")
        self.le_state_name = QtWidgets.QLineEdit(self)
        self.le_state_name.setGeometry(QtCore.QRect(10, 50, 381, 20))
        self.le_state_name.setObjectName("le_state_name")
        self.gb_params = QtWidgets.QGroupBox(self)
        self.gb_params.setGeometry(QtCore.QRect(10, 90, 381, 101))
        self.gb_params.setObjectName("gb_params")
        self.chk_base_params = QtWidgets.QCheckBox(self.gb_params)
        self.chk_base_params.setGeometry(QtCore.QRect(20, 30, 131, 17))
        self.chk_base_params.setObjectName("chk_base_params")
        self.chk_specific_params = QtWidgets.QCheckBox(self.gb_params)
        self.chk_specific_params.setGeometry(QtCore.QRect(20, 60, 131, 17))
        self.chk_specific_params.setObjectName("chk_specific_params")

        self.l_desc.setText(QtWidgets.QApplication.translate("PCSNewStateDlg", "Please enter a name for this Variation. A Variation stores the state of a set of nodes and can be recalled later.", None, -1))
        self.le_state_name.setPlaceholderText(QtWidgets.QApplication.translate("PCSNewStateDlg", "Variation Name", None, -1))
        self.gb_params.setTitle(QtWidgets.QApplication.translate("PCSNewStateDlg", "Parameters to store", None, -1))
        self.chk_base_params.setText(QtWidgets.QApplication.translate("PCSNewStateDlg", "Base Parameters", None, -1))
        self.chk_specific_params.setText(QtWidgets.QApplication.translate("PCSNewStateDlg", "Specific Parameters", None, -1))

        self.chk_base_params.setCheckState(Qt.Checked)
        self.chk_specific_params.setCheckState(Qt.Checked)

        # be notified on various changes to enable/disable the OK button
        self.le_state_name.textChanged.connect(self.onTextChanged)
        self.chk_base_params.stateChanged.connect(self.onStateChanged)
        self.chk_specific_params.stateChanged.connect(self.onStateChanged)

        self.bb_ok_cancel.rejected.connect(self.onClose)
        self.bb_ok_cancel.accepted.connect(self.onOK)

        self.enableDisableOKButton()

    def show(self, nodeArray):
        self.nodeArray = nodeArray
        self.le_state_name.setFocus()
        self.le_state_name.clear()
        super().show()

    def onTextChanged(self, state):
        self.enableDisableOKButton()

    def onStateChanged(self, text):
        self.enableDisableOKButton()

    def enableDisableOKButton(self):
        text = self.le_state_name.text()
        hasText =  len(text) > 0
        hasBaseParams = self.chk_base_params.checkState() == Qt.Checked
        hasSpecificParams = self.chk_specific_params.checkState() == Qt.Checked
        self.bb_ok_cancel.button(QDialogButtonBox.Ok).setEnabled( hasText and  (hasBaseParams or hasSpecificParams) )

    def onOK(self):
        stateMgr = PCStateMgr.instance()
        originalName = self.le_state_name.text().strip()
        if originalName and len(originalName) > 0:
            name = self.findUniqueName(originalName)
            if name:
                storeBaseParams = self.chk_base_params.checkState() == Qt.Checked
                storeSpecificParams = self.chk_specific_params.checkState() == Qt.Checked
                graph = PCHelper.getCurrentGraph()
                stateSet = PCNodeStateSet(graph, name)
                stateSet.storeNodeStates(self.nodeArray, graph, storeBaseParams, storeSpecificParams)
                stateMgr.addStateSet(stateSet)

                from paramcopy.pcui.pcuimgr import PCUIMgr
                PCUIMgr.instance().onNodeStatesUpdated()
            
        self.close()
    
    def findUniqueName(self, originalName):
        stateMgr = PCStateMgr.instance()
        counter = 2
        name = originalName
        maxCount = 1000
        while stateMgr.stateSetNameExists(name) and counter < maxCount:
            name = originalName + " (" + str(counter) + ")"
            counter += 1
        
        return name if counter < maxCount else None

    def onClose(self):
        self.close()
