# ---------------
# ParamCopy - Substance 3D Designer plugin
# (c) 2019-2025 Eyosido Software SARL
# ---------------

import importlib

import sd
from sd.context import Context
from sd.api.sdpackage import SDPackage
from sd.api.sdarray import SDArray
from sd.api.sdgraph import SDGraph
from sd.api.sdapplication import SDApplication

from paramcopy.pccore import pclog, pcdata, pchelper, pcparam, pccopier, pcnodeid, pcprefs, pcstatemgr, pcinspector
from paramcopy.pcui import pcuimgr, pctoolbar, paramdlg, copydlg, pastedlg, paramtree, prefsdlg, statesdlg, newstatedlg, clipboardsdlg

def initializeSDPlugin():
    # module reloads enable modifications without restarting the host, used for development only
    # importlib.reload(pclog)
    # importlib.reload(pcdata)
    # importlib.reload(pchelper)
    # importlib.reload(pcparam)
    # importlib.reload(pccopier)
    # importlib.reload(pcnodeid)
    # importlib.reload(pcprefs)
    # importlib.reload(pcstatemgr)
    # importlib.reload(pcinspector)

    # importlib.reload(pcuimgr)
    # importlib.reload(pctoolbar)
    # importlib.reload(paramdlg)
    # importlib.reload(copydlg)
    # importlib.reload(pastedlg)
    # importlib.reload(paramtree)
    # importlib.reload(prefsdlg)
    # importlib.reload(statesdlg)
    # importlib.reload(newstatedlg)
    # importlib.reload(clipboardsdlg)

    cleanGlobals()
    pclog.PCLogger.instance().log(pcdata.PCData.APP_NAME + " starting")

    pcprefs.PCPrefs.instance()
    pcUiMgr = pcuimgr.PCUIMgr.instance()
    pcUiMgr.setupUI()

def cleanGlobals():
    pcuimgr.PCUIMgr.inst = None
    pccopier.PCCopier.inst = None
    pcprefs.PCPrefs.inst = None
    pcstatemgr.PCStateMgr.inst = None

def uninitializeSDPlugin():
    pcUiMgr = pcuimgr.PCUIMgr.instance()
    pcUiMgr.removeUI()
    cleanGlobals()
    pclog.log(pcdata.PCData.APP_NAME + " ending")
    pclog.PCLogger.destroyLogger()
