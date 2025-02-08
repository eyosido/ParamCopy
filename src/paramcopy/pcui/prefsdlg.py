# ---------------
# ParamCopy - Substance 3D Designer plugin
# (c) 2019-2022 Eyosido Software SARL
# ---------------

import sd
if sd.getContext().getSDApplication().getVersion() < "14.0.0":
    from PySide2 import QtCore, QtWidgets
    from PySide2.QtCore import Qt
else:
    from PySide6 import QtCore, QtWidgets
    from PySide6.QtCore import Qt

from paramcopy.pccore import pclog
from paramcopy.pccore.pcdata import PCData
from paramcopy.pccore.pcprefs import PCPrefs

class PCPrefsDlg(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupStaticFields()

    def setupStaticFields(self):
        self.setObjectName("PCPrefsDlg")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint) # remove the Help icon in title bar
        self.setWindowTitle(PCData.APP_NAME + " - Preferences")
        self.setFixedSize(571, 436)

        self.bb_ok_cancel = QtWidgets.QDialogButtonBox(self)
        self.bb_ok_cancel.setGeometry(QtCore.QRect(220, 400, 341, 32))
        self.bb_ok_cancel.setOrientation(QtCore.Qt.Horizontal)
        self.bb_ok_cancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.bb_ok_cancel.setObjectName("bb_ok_cancel")
        self.gp_compute = QtWidgets.QGroupBox(self)
        self.gp_compute.setGeometry(QtCore.QRect(10, 10, 551, 220))
        self.gp_compute.setObjectName("gp_compute")
        self.l_compute_desc = QtWidgets.QLabel(self.gp_compute)
        self.l_compute_desc.setGeometry(QtCore.QRect(10, 25, 531, 85))
        self.l_compute_desc.setWordWrap(True)
        self.l_compute_desc.setObjectName("l_compute_desc")
        self.chk_compute_on_paste = QtWidgets.QCheckBox(self.gp_compute)
        self.chk_compute_on_paste.setGeometry(QtCore.QRect(10, 120, 350, 20))
        self.chk_compute_on_paste.setObjectName("chk_compute_on_paste")
        self.chk_compute_on_var_recall = QtWidgets.QCheckBox(self.gp_compute)
        self.chk_compute_on_var_recall.setGeometry(QtCore.QRect(10, 148, 350, 23))
        self.chk_compute_on_var_recall.setObjectName("chk_compute_on_var_recall")
        self.chk_compute_on_roll = QtWidgets.QCheckBox(self.gp_compute)
        self.chk_compute_on_roll.setGeometry(QtCore.QRect(10, 180, 350, 20))
        self.chk_compute_on_roll.setToolTip("")
        self.chk_compute_on_roll.setObjectName("chk_compute_on_roll")
        self.chk_optional_confirm = QtWidgets.QCheckBox(self)
        self.chk_optional_confirm.setGeometry(QtCore.QRect(310, 360, 191, 23))
        self.chk_optional_confirm.setObjectName("chk_optional_confirm")
        self.chk_copy_select_all = QtWidgets.QCheckBox(self)
        self.chk_copy_select_all.setGeometry(QtCore.QRect(20, 360, 260, 23))
        self.chk_copy_select_all.setObjectName("chk_copy_select_all")
        self.gb_shortcuts = QtWidgets.QGroupBox(self)
        self.gb_shortcuts.setGeometry(QtCore.QRect(10, 225, 551, 131))
        self.gb_shortcuts.setObjectName("gb_shortcuts")
        self.l_shc_copy_marams = QtWidgets.QLabel(self.gb_shortcuts)
        self.l_shc_copy_marams.setGeometry(QtCore.QRect(10, 30, 101, 20))
        self.l_shc_copy_marams.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.l_shc_copy_marams.setObjectName("l_shc_copy_marams")
        self.le_shc_copy_params = QtWidgets.QLineEdit(self.gb_shortcuts)
        self.le_shc_copy_params.setGeometry(QtCore.QRect(120, 30, 131, 20))
        self.le_shc_copy_params.setText("")
        self.le_shc_copy_params.setObjectName("le_shc_copy_params")
        self.le_shc_paste_params = QtWidgets.QLineEdit(self.gb_shortcuts)
        self.le_shc_paste_params.setGeometry(QtCore.QRect(120, 60, 131, 20))
        self.le_shc_paste_params.setText("")
        self.le_shc_paste_params.setObjectName("le_shc_paste_params")
        self.l_shc_paste_params = QtWidgets.QLabel(self.gb_shortcuts)
        self.l_shc_paste_params.setGeometry(QtCore.QRect(0, 60, 111, 20))
        self.l_shc_paste_params.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.l_shc_paste_params.setObjectName("l_shc_paste_params")
        self.le_shc_roll_seeds = QtWidgets.QLineEdit(self.gb_shortcuts)
        self.le_shc_roll_seeds.setGeometry(QtCore.QRect(120, 90, 131, 20))
        self.le_shc_roll_seeds.setText("")
        self.le_shc_roll_seeds.setObjectName("le_shc_roll_seeds")
        self.l_shc_roll_seeds = QtWidgets.QLabel(self.gb_shortcuts)
        self.l_shc_roll_seeds.setGeometry(QtCore.QRect(0, 90, 111, 16))
        self.l_shc_roll_seeds.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.l_shc_roll_seeds.setObjectName("l_shc_roll_seeds")
        self.le_shc_store_var = QtWidgets.QLineEdit(self.gb_shortcuts)
        self.le_shc_store_var.setGeometry(QtCore.QRect(400, 30, 131, 20))
        self.le_shc_store_var.setText("")
        self.le_shc_store_var.setObjectName("le_shc_store_var")
        self.l_shc_store_var = QtWidgets.QLabel(self.gb_shortcuts)
        self.l_shc_store_var.setGeometry(QtCore.QRect(290, 30, 101, 20))
        self.l_shc_store_var.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.l_shc_store_var.setObjectName("l_shc_store_var")
        self.l_shc_show_var = QtWidgets.QLabel(self.gb_shortcuts)
        self.l_shc_show_var.setGeometry(QtCore.QRect(290, 60, 101, 20))
        self.l_shc_show_var.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.l_shc_show_var.setObjectName("l_shc_show_var")
        self.le_shc_show_var = QtWidgets.QLineEdit(self.gb_shortcuts)
        self.le_shc_show_var.setGeometry(QtCore.QRect(400, 60, 131, 20))
        self.le_shc_show_var.setText("")
        self.le_shc_show_var.setObjectName("le_shc_show_var")
        self.l_version = QtWidgets.QLabel(self)
        self.l_version.setGeometry(QtCore.QRect(20, 400, 201, 16))
        self.l_version.setObjectName("l_version")

        self.gp_compute.setTitle(QtWidgets.QApplication.translate("PCPrefsDlg", "Graph Computation", None, -1))
        self.chk_compute_on_roll.setText(QtWidgets.QApplication.translate("PCPrefsDlg", "Compute current graph after Roll Random Seed operation", None, -1))
        self.chk_compute_on_paste.setText(QtWidgets.QApplication.translate("PCPrefsDlg", "Compute current graph after a Paste operation", None, -1))
        self.l_compute_desc.setText(QtWidgets.QApplication.translate("PCPrefsDlg", "The below options determine whether the current graph should be brought up to date (computed) after specific operations, so the effects are visible on the involved nodes. For large graphs, you may want to disable these options if computation takes too long or is not required. It is to be noted nodes for which computation is wanted need to be connected to an Output node, else these options will have no effect.", None, -1))
        self.chk_compute_on_var_recall.setText(QtWidgets.QApplication.translate("PCPrefsDlg", "Compute current graph after Variation recall", None, -1))
        self.chk_optional_confirm.setToolTip(QtWidgets.QApplication.translate("PCPrefsDlg", "Optional confirmation dialogs on write operations can be enabled/disabled with this option, they appear on certain occasions with a mention saying they can be disabled in Preferences.", None, -1))
        self.chk_optional_confirm.setText(QtWidgets.QApplication.translate("PCPrefsDlg", "Enable optional confirmations", None, -1))
        self.chk_copy_select_all.setToolTip(QtWidgets.QApplication.translate("PCPrefsDlg", "If enabled, the Copy Parameters dialog will select all parameters on opening, else none will be selected.", None, -1))
        self.chk_copy_select_all.setText(QtWidgets.QApplication.translate("PCPrefsDlg", "Select all parameters by default on Copy", None, -1))
        self.gb_shortcuts.setTitle(QtWidgets.QApplication.translate("PCPrefsDlg", "Shortcuts", None, -1))
        self.l_shc_copy_marams.setText(QtWidgets.QApplication.translate("PCPrefsDlg", "Copy Params:", None, -1))
        self.le_shc_copy_params.setPlaceholderText(QtWidgets.QApplication.translate("PCPrefsDlg", "Key sequence", None, -1))
        self.le_shc_paste_params.setPlaceholderText(QtWidgets.QApplication.translate("PCPrefsDlg", "Key sequence", None, -1))
        self.l_shc_paste_params.setText(QtWidgets.QApplication.translate("PCPrefsDlg", "Paste Params:", None, -1))
        self.le_shc_roll_seeds.setPlaceholderText(QtWidgets.QApplication.translate("PCPrefsDlg", "Key sequence", None, -1))
        self.l_shc_roll_seeds.setText(QtWidgets.QApplication.translate("PCPrefsDlg", "Roll Random Seeds:", None, -1))
        self.le_shc_store_var.setPlaceholderText(QtWidgets.QApplication.translate("PCPrefsDlg", "Key sequence", None, -1))
        self.l_shc_store_var.setText(QtWidgets.QApplication.translate("PCPrefsDlg", "Store Variation:", None, -1))
        self.l_shc_show_var.setText(QtWidgets.QApplication.translate("PCPrefsDlg", "Show Variations:", None, -1))
        self.le_shc_show_var.setPlaceholderText(QtWidgets.QApplication.translate("PCPrefsDlg", "Key sequence", None, -1))

        self.l_version.setText(PCData.APP_NAME + " v" + PCData.VERSION)

        self.bb_ok_cancel.rejected.connect(self.onClose)
        self.bb_ok_cancel.accepted.connect(self.onOK)

    def show(self):
        prefs = PCPrefs.instance()
        self.chk_compute_on_roll.setCheckState(Qt.Checked if prefs.computeGraphAfterRSRoll else Qt.Unchecked)
        self.chk_compute_on_paste.setCheckState(Qt.Checked if prefs.computeGraphAfterPaste else Qt.Unchecked)
        self.chk_compute_on_var_recall.setCheckState(Qt.Checked if prefs.computeGraphAfterVariationRecall else Qt.Unchecked)
        self.chk_optional_confirm.setCheckState(Qt.Checked if prefs.optionalConfirmations else Qt.Unchecked)
        self.chk_copy_select_all.setCheckState(Qt.Checked if prefs.copyDlgSelectAll else Qt.Unchecked)

        self.le_shc_copy_params.setText(prefs.copyParamsShortcut)
        self.le_shc_paste_params.setText(prefs.pasteParamsShortcut)
        self.le_shc_roll_seeds.setText(prefs.rollRandomSeedsShortcut)
        self.le_shc_store_var.setText(prefs.storeVariationShortcut)
        self.le_shc_show_var.setText(prefs.showVariationsShortcut)

        super().show()

    def onOK(self):
        prefs = PCPrefs.instance()
        prefs.computeGraphAfterRSRoll = self.chk_compute_on_roll.checkState() == Qt.Checked
        prefs.computeGraphAfterPaste = self.chk_compute_on_paste.checkState() == Qt.Checked
        prefs.computeGraphAfterVariationRecall = self.chk_compute_on_var_recall.checkState() == Qt.Checked
        prefs.optionalConfirmations = self.chk_optional_confirm.checkState() == Qt.Checked
        prefs.copyDlgSelectAll = self.chk_copy_select_all.checkState() == Qt.Checked

        prefs.copyParamsShortcut = self.le_shc_copy_params.text()
        prefs.pasteParamsShortcut = self.le_shc_paste_params.text()
        prefs.rollRandomSeedsShortcut = self.le_shc_roll_seeds.text()
        prefs.storeVariationShortcut = self.le_shc_store_var.text()
        prefs.showVariationsShortcut = self.le_shc_show_var.text()

        self.le_shc_copy_params.setText(prefs.copyParamsShortcut)
        self.le_shc_paste_params.setText(prefs.pasteParamsShortcut)
        self.le_shc_roll_seeds.setText(prefs.rollRandomSeedsShortcut)
        self.le_shc_store_var.setText(prefs.storeVariationShortcut)
        self.le_shc_show_var.setText(prefs.showVariationsShortcut)

        from paramcopy.pcui.pcuimgr import PCUIMgr
        PCUIMgr.instance().setupShortcuts()

        prefs.save()

        self.close()
    
    def onClose(self):
        self.close()
