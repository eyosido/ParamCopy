# ---------------
# ParamCopy - Substance 3D Designer plugin
# (c) 2019-2022 Eyosido Software SARL
# ---------------

import os, weakref
from functools import partial

from PySide2.QtCore import QObject
from PySide2.QtWidgets import QToolBar

import sd
from sd.context import Context
from sd.api.sdapplication import SDApplication
from sd.api.sduimgr import SDUIMgr

from paramcopy.pccore import pclog
from paramcopy.pccore.pcdata import PCData

class PCGraphCustomToolbarMgr(QObject):
    """
    Handles a single custom toolbar per graph view used by a single external component
    """
    def __init__(self, callback, toolbarIcon):
        super().__init__()
        self.sdApp = sd.getContext().getSDApplication()
        self.sdUiMgr = self.sdApp.getQtForPythonUIMgr()
        self.toolbars = {} # key: graphViewId, value: weak reference on created toolbar (so we don't prevent Qt to delete the toolbars)
        self.callback = partial(callback) # callback must create/setup a single QToolBar object and return it.
        self.toolbarIcon = toolbarIcon
        self.registerGraphViewCreated()

    # --- Public
    def cleanup(self):
        self.removeAllToolbars()
        if self.graphViewCreatedCbId:
            self.sdUiMgr.unregisterCallback(self.graphViewCreatedCbId)

    # --- Private
    def registerGraphViewCreated(self):
        self.graphViewCreatedCbId = self.sdUiMgr.registerGraphViewCreatedCallback( partial(self.onGraphViewCreated, uiMgr=self.sdUiMgr))

    def removeAllToolbars(self):
        for toolbarRef in self.toolbars.values():
            weakref.proxy(toolbarRef).deleteLater()
        self.toolbars = {}

    def onGraphViewCreated(self, graphViewId, uiMgr):
        if not self.toolbars.get(graphViewId):
            toolbar = self.callback()   # let user create and setup the QToolBar
            toolbar.destroyed.connect(partial(self.onToolbarDestroyed, graphViewId=graphViewId))
            self.toolbars[graphViewId] = toolbar
            self.sdUiMgr.addToolbarToGraphView(graphViewId, toolbar, icon = self.toolbarIcon, tooltip = toolbar.toolTip())

    def onToolbarDestroyed(self, graphViewId):
        # self.sender() is not the toolbar object, so we need to look-up by graphViewId
        if self.toolbars.get(graphViewId):
            del self.toolbars[graphViewId]
