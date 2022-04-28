# ---------------
# ParamCopy - Substance 3D Designer plugin
# (c) 2019-2022 Eyosido Software SARL
# ---------------

from sd.api.sdpackage import SDPackage
from sd.api.sdnode import SDNode
from sd.api.sdgraph import SDGraph
from sd.api.sdarray import SDArray
from sd.api.sdproperty import SDPropertyCategory
from sd.api.apiexception import APIException

from paramcopy.pccore.pchelper import PCHelper
from paramcopy.pccore.pcnodeid import PCNodeIdentifier
from paramcopy.pccore.pcparam  import PCParam, PCParamCollection

class PCNodeState:
    def __init__(self, node, storeBaseParams = True, storeSpecificParams = True, graph = None):
        self.nodeIdentifier = PCNodeIdentifier(node, graph)
        self.state = PCParamCollection()

    def recallInto(self, destNode, copyBaseAndSpecific = True, propertyIds = None):
        for propertyId, propertyData in self.state.params.items():
            if not propertyIds or (propertyIds and propertyId in propertyIds): # filter properties
                isBaseParam = PCHelper.isBaseParameter(propertyId)
                if copyBaseAndSpecific or isBaseParam:
                    # verify whether property exists in destination node
                    try:
                        destVal = destNode.getInputPropertyValueFromId(propertyId)
                        if destVal:
                            destProp = destNode.getPropertyFromId(propertyId, SDPropertyCategory.Input)
                            isFunctionDriven = PCHelper.isInputParamFunctionDriven(destNode, destProp)
                            if not isFunctionDriven: # make sure not to copy over a user function
                                if propertyData.inheritanceMethod != -1:
                                    #inheritance method is to be set *before* property value
                                    destNode.setInputPropertyInheritanceMethodFromId(propertyData.id, propertyData.inheritanceMethod)

                                destNode.setInputPropertyValueFromId(propertyData.id, propertyData.value)
                    except APIException as e:
                        PCHelper.logSDException(e)
                    finally:
                        pass

    def retrieveNode(self):
        return self.nodeIdentifier.retrieveNode()

    def storeState(self, node, storeBaseParams = True, storeSpecificParams = True, propertyIds = None):
        #if propertyIds are defined, only those will be stored regardless of storeBaseParams/storeSpecificParams
        properties = node.getProperties(SDPropertyCategory.Input)
        if properties:
            p = 0
            psize = properties.getSize()

            while p < psize:
                prop = properties.getItem(p)
                if prop.getType().getClassName() != "SDTypeTexture": # do not process node inputs
                    propertyId = prop.getId()
                    isBaseParam = PCHelper.isBaseParameter(propertyId)

                    if (propertyIds and propertyId in propertyIds) or \
                     (not propertyIds and \
                             ( (isBaseParam and storeBaseParams) or (not isBaseParam and storeSpecificParams) ) \
                     ):                
                        if not PCHelper.isHiddenParam(node, propertyId):
                            groupName = PCHelper.getParamGroupName(node, propertyId)
                            inheritanceMethod = PCHelper.getInheritanceMethod(node, propertyId)
                            value = node.getPropertyValue(prop) #  PCHelper.newPropertyValue(node, prop) ??
                            param = PCParam(propertyId, prop.getLabel(), inheritanceMethod, value, groupName)
                            self.state.params[propertyId] = param
                p += 1

class PCNodeStateSet:
    def __init__(self, graph, stateSetName):
        self.graphName = graph.getIdentifier()
        package = graph.getPackage()
        self.packageName = PCHelper.getPackageName(package)
        self.id =  PCHelper.getPackageId(package) + "_" + graph.getIdentifier() + "_" + stateSetName
        self.name = stateSetName
        self.nodeStates = []

    def storeNodeStates(self, nodeArray, graph, storeBaseParams = True, storeSpecificParams = True):
        size = nodeArray.getSize()
        for n in range(0, size):
            node = nodeArray.getItem(n)
            nodeState = PCNodeState(node, graph)
            nodeState.storeState(node, storeBaseParams, storeSpecificParams)
            self.nodeStates.append(nodeState)

    def recallNodeStates(self):
        misses = 0
        for nodeState in self.nodeStates:
            node = nodeState.retrieveNode()
            if node:
                nodeState.recallInto(node)
            else:
                misses += 1

        return misses

class PCStateMgr:
    """
    Store sets of node states for later recall
    """
    inst = None

    @classmethod
    def instance(cls):
        if not cls.inst:
            cls.inst = PCStateMgr()
        return cls.inst

    def __init__(self):
        self.nodeStateSets = {} # key: state set name, value, PCNodeStateSet
    
    def stateSetNameExists(self, stateSetName):
        return self.nodeStateSets.get(stateSetName) != None

    def addStateSet(self, stateSet):
        self.nodeStateSets[stateSet.name] = stateSet

    def deleteStateSet(self, stateSetName):
        if self.nodeStateSets.get(stateSetName):
            del self.nodeStateSets[stateSetName]
            return True
        else:
            return False

    def deleteAll(self):
        self.nodeStateSets = {}


