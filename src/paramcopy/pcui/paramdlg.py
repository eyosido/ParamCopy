# ---------------
# ParamCopy - Substance 3D Designer plugin
# (c) 2019-2022 Eyosido Software SARL
# ---------------

import sd
if sd.getContext().getSDApplication().getVersion() < "14.0.0":
    from PySide2 import QtCore, QtWidgets
    from PySide2.QtCore import Qt
    from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItemIterator, QSizePolicy
else:
    from PySide6 import QtCore, QtWidgets
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItemIterator, QSizePolicy

from sd.api.sdnode import SDNode

from paramcopy.pccore import pclog
from paramcopy.pccore.pcdata import PCData
from paramcopy.pccore.pchelper import PCHelper
from paramcopy.pccore.pccopier import PCCopier

from paramcopy.pcui.paramtree import PCParamTreeWidget

class PCParamDlgBase(QtWidgets.QDialog):
    def __init__(self, isCopyDlg, parent=None):
        self.isCopyDlg = isCopyDlg
        super().__init__(parent)

    def setupStaticFields(self, dlgName, title):
        self.setObjectName(dlgName)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint) # remove the Help icon in title bar
        self.setWindowTitle(title)
        self.resize(500, 560)

        self.setSizeGripEnabled(True)
        self.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)

        self.verticalLayout.setObjectName("verticalLayout")
        self.l_node_desc = QtWidgets.QLabel(self)
        self.l_node_desc.setMinimumSize(QtCore.QSize(0, 20))
        self.l_node_desc.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.l_node_desc.setObjectName("l_node_desc")
        self.verticalLayout.addWidget(self.l_node_desc)
        self.gb_select = QtWidgets.QGroupBox(self)
        self.gb_select.setTitle("")
        self.gb_select.setFlat(True)
        self.gb_select.setObjectName("gb_select")
        self.b_select_all = QtWidgets.QPushButton(self.gb_select)
        self.b_select_all.setGeometry(QtCore.QRect(0, 10, 75, 23))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.b_select_all.sizePolicy().hasHeightForWidth())
        self.b_select_all.setSizePolicy(sizePolicy)
        self.b_select_all.setObjectName("b_select_all")
        self.b_deselect_all = QtWidgets.QPushButton(self.gb_select)
        self.b_deselect_all.setGeometry(QtCore.QRect(110, 10, 75, 23))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.b_deselect_all.sizePolicy().hasHeightForWidth())
        self.b_deselect_all.setSizePolicy(sizePolicy)
        self.b_deselect_all.setObjectName("b_deselect_all")
        self.b_expand_all = QtWidgets.QPushButton(self.gb_select)
        self.b_expand_all.setGeometry(QtCore.QRect(220, 10, 75, 23))
        self.b_expand_all.setObjectName("b_expand_all")
        self.b_collapse_all = QtWidgets.QPushButton(self.gb_select)
        self.b_collapse_all.setGeometry(QtCore.QRect(330, 10, 75, 23))
        self.b_collapse_all.setObjectName("b_collapse_all")
        self.verticalLayout.addWidget(self.gb_select)

        if self.isCopyDlg:
            self.hl_clipboard = QtWidgets.QHBoxLayout()
            self.hl_clipboard.setObjectName("hl_clipboard")
            self.l_clipboards = QtWidgets.QLabel(self)
            self.l_clipboards.setObjectName("l_clipboards")
            self.hl_clipboard.addWidget(self.l_clipboards)
            self.le_clipboard_name = QtWidgets.QLineEdit(self)
            self.le_clipboard_name.setObjectName("le_clipboard_name")
            self.hl_clipboard.addWidget(self.le_clipboard_name)
            self.verticalLayout.addLayout(self.hl_clipboard)

        self.chk_show_advanced = QtWidgets.QCheckBox(self)
        self.chk_show_advanced.setObjectName("chk_show_advanced")
        self.verticalLayout.addWidget(self.chk_show_advanced)
        self.gb_advanced = QtWidgets.QGroupBox(self)
        self.gb_advanced.setMinimumSize(QtCore.QSize(0, 60))
        self.gb_advanced.setObjectName("gb_advanced")
        self.chk_display_ids = QtWidgets.QCheckBox(self.gb_advanced)
        self.chk_display_ids.setGeometry(QtCore.QRect(20, 30, 151, 17))
        self.chk_display_ids.setObjectName("chk_display_ids")
        self.verticalLayout.addWidget(self.gb_advanced)
        self.hl_bottom = QtWidgets.QHBoxLayout()
        self.hl_bottom.setObjectName("hl_bottom")
        self.l_status = QtWidgets.QLabel(self)
        self.l_status.setObjectName("l_status")
        self.hl_bottom.addWidget(self.l_status)
        self.bb_ok_cancel = QtWidgets.QDialogButtonBox(self)
        self.bb_ok_cancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.bb_ok_cancel.setObjectName("bb_ok_cancel")
        self.hl_bottom.addWidget(self.bb_ok_cancel)
        self.verticalLayout.addLayout(self.hl_bottom)

        self.l_node_desc.setText(QtWidgets.QApplication.translate(dlgName, "<node desc>", None, -1))
        self.b_select_all.setText(QtWidgets.QApplication.translate(dlgName, "Select All", None, -1))
        self.b_deselect_all.setText(QtWidgets.QApplication.translate(dlgName, "Deselect All", None, -1))
        self.b_expand_all.setText(QtWidgets.QApplication.translate(dlgName, "Expand All", None, -1))
        self.b_collapse_all.setText(QtWidgets.QApplication.translate(dlgName, "Collapse All", None, -1))
        self.chk_show_advanced.setText(QtWidgets.QApplication.translate(dlgName, "Show advanced options", None, -1))
        self.gb_advanced.setTitle(QtWidgets.QApplication.translate(dlgName, "Advanced options", None, -1))
        self.chk_display_ids.setToolTip(QtWidgets.QApplication.translate(dlgName, "Display the IDs (Identifiers) of parameters in the above tree view. Parameter IDs are unique,\n"
"internal parameter names. If during pasting you are using the option to paste Specific Parameters\n"
"between different node types based on identical parameter IDs, you may want to check which IDs\n"
"are matching between node types.", None, -1))
        self.chk_display_ids.setText(QtWidgets.QApplication.translate(dlgName, "Display parameter IDs", None, -1))
        self.l_status.setText(QtWidgets.QApplication.translate(dlgName, "<status>", None, -1))

        if self.isCopyDlg:
            self.l_clipboards.setText(QtWidgets.QApplication.translate("Dialog", "Store as named clipboard:", None, -1))
            self.le_clipboard_name.setToolTip(QtWidgets.QApplication.translate("Dialog", "Name of the clipboard to store this parameter copy as (opotional)", None, -1))
            self.le_clipboard_name.setPlaceholderText(QtWidgets.QApplication.translate("Dialog", "Clipboard name", None, -1))

        self.setupDynamicFields()

        self.chk_show_advanced.stateChanged.connect(self.onShowAdvancedStateChanged)
        self.showAdvancedOptions(False)

        self.chk_display_ids.stateChanged.connect(self.onDisplayParamIds)

        self.b_select_all.clicked.connect(self.onSelectAll)
        self.b_deselect_all.clicked.connect(self.onDeselectAll)
        self.b_expand_all.clicked.connect(self.onExpandAll)
        self.b_collapse_all.clicked.connect(self.onCollapseAll)

        self.bb_ok_cancel.rejected.connect(self.onClose)
        self.bb_ok_cancel.accepted.connect(self.onOK)

    def setupDynamicFields(self):
        self.treeWidget = PCParamTreeWidget(self)
        self.verticalLayout.insertWidget(2, self.treeWidget)
        self.clearStatus()

    def setStatus(self, text):
        self.l_status.setText(text)

    def clearStatus(self):
        self.setStatus("")

    def showAdvancedOptions(self, show):
        self.gb_advanced.setEnabled(show)

    def onShowAdvancedStateChanged(self, state):
        show = state == Qt.Checked
        self.showAdvancedOptions(show)

    def onDisplayParamIds(self, state):
        show = state == Qt.Checked
        self.treeWidget.showIdCol(show)

    def onSelectAll(self):
        self.treeWidget.selectAll()

    def onDeselectAll(self):
        self.treeWidget.deselectAll()

    def onExpandAll(self):
        self.treeWidget.expandAll()

    def onCollapseAll(self):
        self.treeWidget.collapseAll()

    def onClose(self):
        self.close()
