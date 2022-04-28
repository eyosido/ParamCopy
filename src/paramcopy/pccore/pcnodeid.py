# ---------------
# ParamCopy - Substance 3D Designer plugin
# (c) 2019-2022 Eyosido Software SARL
# ---------------

import sd
from sd.api.sdapplication import SDApplication
from sd.api.sdpackagemgr import SDPackageMgr
from sd.api.sbs.sdsbscompgraph import SDSBSCompGraph

from sd.api.sdpackage import SDPackage
from sd.api.sdnode import SDNode
from sd.api.sdgraph import SDGraph
from sd.api.sduimgr import SDUIMgr
from sd.api.apiexception import APIException

from paramcopy.pccore.pchelper import PCHelper
from paramcopy.pccore import pclog

class PCNodeIdentifier:
    """
    Identifies a graph node through a full path starting from the package
    This is needed to know whether a node whose parameters have been copied
    is still in existance at paste time.
    LIMITATION: if packages have no id (they have not yet been saved), they cannot
    be distinguished from each other
    """
    def __init__(self, node = None, graph = None):
        self.set(node, graph)

    def set(self, node = None, graph = None):
        if not node:
            self.nodeId = None
            self.graphId = None
            self.packageId = None # package id is its file path
            self.defId = None # definition ID and Label are used to determine the node type
            self.defLabel = None
        else:
            self.nodeId = node.getIdentifier()
            if not graph:
                graph = sd.getContext().getSDApplication().getUIMgr().getCurrentGraph()
            self.graphId = graph.getIdentifier()
            self.packageId = PCHelper.getPackageId(graph.getPackage())

            # definition ID and Label are used to determine the node type
            nodeDef = node.getDefinition()
            self.defId = nodeDef.getId()
            self.defLabel = nodeDef.getLabel()

    def __str__(self):
        return self.packageId + "_" + self.graphId + "_" + self.nodeId

    def getName(self):
        return self.defLabel if (self.defLabel and len(self.defLabel) > 0) else self.nodeId

    def haveSameNodeType(self, otherNode):
        # we check id AND label as for sbsar all the ids are same so we distinguish by label
        otherNodeDef = otherNode.getDefinition()
        return self.defId == otherNodeDef.getId() and  self.defLabel == otherNodeDef.getLabel()

    def retrieveNode(self):
        if not self.nodeId:
            return

        node = None
        sdApp = sd.getContext().getSDApplication()

        # try shortcut using current graph
        currentGraph = sdApp.getUIMgr().getCurrentGraph()
        if currentGraph:
            # check we're on the same package
            currentGraphPackageId = PCHelper.getPackageId(currentGraph.getPackage())
            # if package is not save, it has no file path hence no ID, so we cannot use
            # it as a reliable identifier
            if currentGraphPackageId and len(currentGraphPackageId) > 0:
                if currentGraphPackageId == self.packageId:
                    if self.graphId == currentGraph.getIdentifier():
                        try:
                            node = currentGraph.getNodeFromId(self.nodeId)
                        except APIException as e:
                            PCHelper.logSDException(e)
                        finally:
                            return node   

        # find package
        packages = sdApp.getPackageMgr().getUserPackages()
        pkgCount = packages.getSize()
        i = 0
        found = False
        while i < pkgCount and not found:
            pkg = packages.getItem(i)
            if pkg.getFilePath() == self.packageId:
                found = True
            else:
                i += 1
        
        if found:
            # find graph
            found = False
            resources = pkg.getChildrenResources(False)
            resCount = resources.getSize()
            i = 0
            while i < resCount and not found:
                res = resources.getItem(i)
                if isinstance(res, SDSBSCompGraph):
                    if res.getIdentifier() == self.graphId:
                        found = True
                else:
                    i += 1
            
            if found:
                # find node
                node = res.getNodeFromId(self.nodeId)

        return node




