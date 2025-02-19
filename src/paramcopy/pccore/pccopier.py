# ---------------
# ParamCopy - Substance 3D Designer plugin
# (c) 2019-2025 Eyosido Software SARL
# ---------------

from sd.api.apiexception import APIException
from sd.api.sdproperty import SDProperty, SDPropertyCategory

from paramcopy.pccore.pchelper import PCHelper
from paramcopy.pccore.pcnodeid import PCNodeIdentifier
from paramcopy.pccore.pcstatemgr import PCNodeState
from paramcopy.pccore.pcparam  import PCParam, PCParamCollection

class PCCopier:
    inst = None

    class PasteOptions:
        def __init__(self):
            self.sameTypeAsSource = False # only node with same type as source will be pasted into
            self.crossTypeSpecificParamsCopy = False # copy specific params even for nodes of different types (are always copied for nodes of same type)

    @classmethod
    def instance(cls):
        if cls.inst == None:
            cls.inst = PCCopier()
        return cls.inst

    def __init__(self):
        self.currentClipboard = None
        self.clipboards = {} # key: clipboard name, val=PCNodeState

    def setClipboard(self, node, propertyIds, clipboardName = None):
        clipboard = PCNodeState(node)
        clipboard.storeState(node, propertyIds=propertyIds)
        if clipboardName:
            self.clipboards[clipboardName] = clipboard
        self.currentClipboard = clipboard

    def setCurrentClipboard(self, clipboardName):
        clipboard = self.clipboards.get(clipboardName)
        if clipboard:
            self.currentClipboard = clipboard

    def clipboardExists(self, clipboardName):
        clipboard = self.clipboards.get(clipboardName)
        return clipboard != None

    def deleteClipboard(self, clipboardName):
        if self.clipboards.get(clipboardName):
            del self.clipboards[clipboardName]
            return True
        else:
            return False

    def deleteAllClipboards(self):
        self.clipboards = {}

    def pasteNodeStateInto(self, sourceNodeState, destNodes, pasteOptions, propertyIds = None):
        destNodeCount = destNodes.getSize()
        for n in range(0, destNodeCount):
            destNode = destNodes.getItem(n)
            srcAndDestHaveSameNodeType = sourceNodeState.nodeIdentifier.haveSameNodeType(destNode)
            doPaste = srcAndDestHaveSameNodeType if pasteOptions.sameTypeAsSource else True
            if doPaste:
                copyBaseAndSpecific = srcAndDestHaveSameNodeType or pasteOptions.crossTypeSpecificParamsCopy
                sourceNodeState.recallInto(destNode, copyBaseAndSpecific, propertyIds)    


