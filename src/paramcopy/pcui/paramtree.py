# ---------------
# ParamCopy - Substance 3D Designer plugin
# (c) 2019-2022 Eyosido Software SARL
# ---------------

import sd
if sd.getContext().getSDApplication().getVersion() < "14.0.0":
    from PySide2 import QtCore, QtWidgets
    from PySide2.QtCore import Qt
    from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItemIterator
else:
    from PySide6 import QtCore, QtWidgets
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItemIterator
    
from sd.api.sdnode import SDNode
from sd.api.sdproperty import SDProperty, SDPropertyCategory, SDPropertyInheritanceMethod
from sd.api.apiexception import APIException

from paramcopy.pccore import pclog
from paramcopy.pccore.pcdata import PCData
from paramcopy.pccore.pchelper import PCHelper
from paramcopy.pccore.pcstatemgr import PCNodeState

class PCParamTreeWidget(QtWidgets.QTreeWidget):
    class PCItemData:
    # set into tree item data Qt.UserRole at column 0

        # Entry types
        ET_PARAM_TYPE = 0   # Base Parameter or Specific Parameter (container)
        ET_PARAM_GROUP = 1  # parameter group name (container)
        ET_PARAM = 2        # parameter name (leaf)
        ET_PARAM_FCT = 3    # parameter driven by function (leaf)

        # Param types
        PT_BASE = 0         # Base Parameter
        PT_SPECIFIC = 1     # Specific Parameter

        def __init__(self, entryType = -1, paramType = -1, propertyId = None):
            self.entryType = entryType
            self.paramType = paramType
            self.propertyId = propertyId 
        
        def isBaseParam(self):
            return self.paramType == PCParamTreeWidget.PCItemData.PT_BASE

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(("Parameter Name", "Inheritance Method  ", "Parameter ID"))
        self.header().resizeSection(1,120)
        self.header().resizeSection(0,240)
        self.showIdCol(False)
        self.itemChanged.connect(self.onItemChanged)
        self.ignoreItemChangedNotifs = False
        self.baseParamTreeItem = None
        self.instanceParamTreeItem = None
        self.paramGroupDict = {} # gathers parameter groups. Key: group name, value: PCItemData

    # --- Public
    def clearTree(self):
        self.clear()
        self.baseParamTreeItem = None
        self.instanceParamTreeItem = None
        self.paramGroupDict = {}

    def showIdCol(self, show):
        if show:
            self.header().showSection(2)       
        else:
            self.header().hideSection(2)

    def populateFromNode(self, node, selectItems):
        self.clearTree()

        properties = node.getProperties(SDPropertyCategory.Input)
        if properties:
            p = 0
            psize = properties.getSize()
            self.ignoreItemChangedNotifs = True

            while p < psize:
                prop = properties.getItem(p)
                if prop.getType().getClassName() != "SDTypeTexture": # do not process node inputs
                    
                    propertyId = prop.getId()
                    if not PCHelper.isHiddenParam(node, propertyId):
                        self.addNodeProperty(node, prop)
                p += 1

            self.ignoreItemChangedNotifs = False
            if selectItems:
                self.processAllItems(expand = True, check = True)
            else:
                self.processAllItems(expand = True, uncheck = True)

    def populateFromNodeState(self, nodeState):
        self.clearTree()
        self.ignoreItemChangedNotifs = True

        for propertyId in nodeState.state.params.keys():
            self.addNodeStateProperty(nodeState, propertyId)                    

        self.ignoreItemChangedNotifs = False
        self.processAllItems(expand = True, check = True)

    def retrieveCheckedProperties(self):
        propertyIds = []
        iter = QTreeWidgetItemIterator(self)
        while iter.value():
            treeItem = iter.value()
            if treeItem.checkState(0) == Qt.Checked:
                pcItemData = treeItem.data(0, Qt.UserRole)
                # exclude non-leaves (they are not properties) and params driven by functions
                if treeItem.childCount() == 0 and not self.isTreeItemFunctionParam(treeItem):
                    propertyIds.append(pcItemData.propertyId)
            iter += 1
        return propertyIds

    def selectAll(self):
        self.processAllItems(check = True)

    def deselectAll(self):
        self.processAllItems(uncheck = True)

    def expandAll(self):
        self.processAllItems(expand = True)

    def collapseAll(self):
        self.processAllItems(collapse = True)

    # --- slots    
    def onItemChanged(self, treeItem):
        if self.ignoreItemChangedNotifs:
            return

        if treeItem.childCount() > 0:
            checkState = treeItem.checkState(0)
            if checkState != Qt.PartiallyChecked:
                self.checkChildren(treeItem, checkState)

        self.setParentTreeItemsCheckStateBasedOnSiblings(treeItem)

    # --- Private
    def setParentTreeItemsCheckStateBasedOnSiblings(self, treeItem):
        # check whether all sibling have the same state, if so set the parent state
        self.ignoreItemChangedNotifs = True
        ti = treeItem
        while ti.parent():
            parent = ti.parent()
            state = self.haveSiblingsSameState(ti)
            parent.setCheckState(0, state)
            ti = parent
        self.ignoreItemChangedNotifs = False

    def createParamGroupTreeItem(self, pcItemData, groupName, displayGroupName, parentTreeItem):
        treeItem = self.createUITreeItem(pcItemData, displayGroupName, None, -1, parentTreeItem)
        self.paramGroupDict[groupName] = treeItem
        return treeItem

    def getParamTypeTreeItem(self, isBaseParam):
        return self.getBaseParamsTreeItem() if isBaseParam else self.getInstanceParamsTreeItem()

    def getParentGroupTreeItem(self, groupName, paramType):
        paramGroupTreeItem = self.paramGroupDict.get(groupName)
        if not paramGroupTreeItem:
            # param group tree item does not yet exist, create it
            # check if this is a first or second level group
            secondLevelGroupName = None
            sep = groupName.find("/")
            if sep != -1:
                firstLevelGroupName = groupName[:sep]
                secondLevelGroupName = groupName[(sep+1):]
            else:
                firstLevelGroupName = groupName
 
            pcItemData = PCParamTreeWidget.PCItemData(PCParamTreeWidget.PCItemData.ET_PARAM_GROUP, paramType)
            baseParentTreeItem = self.getParamTypeTreeItem(pcItemData.isBaseParam())
            parentTreeItem = None
            
            if secondLevelGroupName:
                # check whether first level group exists
                firstLevelGroupTreeItem = self.paramGroupDict.get(firstLevelGroupName)
                if not firstLevelGroupTreeItem:
                    # create first level group
                    firstLevelGroupTreeItem = self.createParamGroupTreeItem(PCParamTreeWidget.PCItemData(PCParamTreeWidget.PCItemData.ET_PARAM_GROUP, paramType), firstLevelGroupName, firstLevelGroupName, baseParentTreeItem)
                parentTreeItem = firstLevelGroupTreeItem
                displayGroupName = secondLevelGroupName
            else:
                parentTreeItem = baseParentTreeItem
                displayGroupName = groupName

            paramGroupTreeItem = self.createParamGroupTreeItem(PCParamTreeWidget.PCItemData(PCParamTreeWidget.PCItemData.ET_PARAM_GROUP, paramType), groupName, displayGroupName, parentTreeItem)

        return paramGroupTreeItem

    def addNodeStateProperty(self, nodeState, propertyId):
        propertyData = nodeState.state.params[propertyId]

        paramName = propertyData.getName()
        propertyId = propertyData.id
        isBaseParam = PCHelper.isBaseParameter(propertyId)
        entryType = PCParamTreeWidget.PCItemData.ET_PARAM

        paramType = PCParamTreeWidget.PCItemData.PT_BASE if isBaseParam else PCParamTreeWidget.PCItemData.PT_SPECIFIC
        pcItemData = PCParamTreeWidget.PCItemData(entryType, paramType, propertyId)

        groupName = propertyData.groupName
        if groupName:
            parentTreeItem = self.getParentGroupTreeItem(groupName, paramType)
        else:
            parentTreeItem = self.getParamTypeTreeItem(pcItemData.isBaseParam())

        treeItem = self.createUITreeItem(pcItemData, paramName, propertyId, propertyData.inheritanceMethod, parentTreeItem)
        return treeItem

    def addNodeProperty(self, node, prop):
        paramName = PCHelper.getPropertyOrDefinitionName(prop)
        propertyId = prop.getId()
        isBaseParam = PCHelper.isBaseParameter(propertyId)
        isParamFunction = PCHelper.isInputParamFunctionDriven(node, prop)
    
        if isParamFunction:
            paramName += " (function)"
            entryType = PCParamTreeWidget.PCItemData.ET_PARAM_FCT
        else:
            entryType = PCParamTreeWidget.PCItemData.ET_PARAM

        paramType = PCParamTreeWidget.PCItemData.PT_BASE if isBaseParam else PCParamTreeWidget.PCItemData.PT_SPECIFIC
        pcItemData = PCParamTreeWidget.PCItemData(entryType, paramType, propertyId)

        groupName = PCHelper.getParamGroupName(node, propertyId)
        if groupName:
            parentTreeItem = self.getParentGroupTreeItem(groupName, paramType)
        else:
            parentTreeItem = self.getParamTypeTreeItem(pcItemData.isBaseParam())

        inheritanceMethod = -1
        if not isParamFunction:
            inheritanceMethod = PCHelper.getInheritanceMethod(node, propertyId)

        treeItem = self.createUITreeItem(pcItemData, paramName, propertyId, inheritanceMethod, parentTreeItem)
        return treeItem

    def getBaseParamsTreeItem(self):
        if not self.baseParamTreeItem:
            pcItemData = PCParamTreeWidget.PCItemData(PCParamTreeWidget.PCItemData.ET_PARAM_TYPE, PCParamTreeWidget.PCItemData.PT_BASE)
            self.baseParamTreeItem = self.createUITreeItem(pcItemData, "Base Parameters")
        return self.baseParamTreeItem

    def getInstanceParamsTreeItem(self):
        if not self.instanceParamTreeItem:
            pcItemData = PCParamTreeWidget.PCItemData(PCParamTreeWidget.PCItemData.ET_PARAM_TYPE, PCParamTreeWidget.PCItemData.PT_SPECIFIC)
            self.instanceParamTreeItem = self.createUITreeItem(pcItemData, "Specific Parameters")
        return self.instanceParamTreeItem

    def isTreeItemFunctionParam(self, treeItem):
         return treeItem.data(0, Qt.UserRole).entryType ==  PCParamTreeWidget.PCItemData.ET_PARAM_FCT

    def checkChildren(self, parentItem, checkState):
        self.ignoreItemChangedNotifs = True

        childCount = parentItem.childCount()
        for c in range(0, childCount):
            child = parentItem.child(c)

            if not self.isTreeItemFunctionParam(child):
                child.setCheckState(0, checkState)

            if child.childCount() > 0:
                self.checkChildren(child, checkState)
                self.ignoreItemChangedNotifs = True

        self.ignoreItemChangedNotifs = False

    def haveSiblingsSameState(self, treeItem):
        # return whether siblings are all checked or unchecked
        parentItem = treeItem.parent()
        childCount = parentItem.childCount()
        checkedCount = 0
        uncheckedCount = 0
        for c in range(0, childCount):
            state = parentItem.child(c).checkState(0)
            if state == Qt.Checked:
                checkedCount += 1
            elif state == Qt.Unchecked:
                uncheckedCount += 1
        
        if checkedCount == childCount:
            ret = Qt.Checked
        elif uncheckedCount == childCount:
            ret = Qt.Unchecked
        else:
            ret = Qt.PartiallyChecked
        return ret 
            
    def createUITreeItem(self, pcItemData, name, propertyId = None, inheritanceMethod = -1, parentItem=None):
        if parentItem:
            treeItem = QtWidgets.QTreeWidgetItem(parentItem)
        else:
            treeItem = QtWidgets.QTreeWidgetItem(self)

        treeItem.setText(0, name)
        treeItem.setData(0, Qt.UserRole, pcItemData)

        if inheritanceMethod != -1:
            treeItem.setText(1, PCHelper.inheritanceMethodLabel(inheritanceMethod))
            treeItem.setData(1, Qt.UserRole, inheritanceMethod)

        if propertyId and not pcItemData.paramType == PCParamTreeWidget.PCItemData.PT_BASE:
            # we show the id only for specific params as this provides not relevant info for base params
            treeItem.setText(2, propertyId)

        return treeItem

    def processAllItems(self, expand = False, collapse = False, check = False, uncheck = False):
        iter = QTreeWidgetItemIterator(self)
        self.ignoreItemChangedNotifs = True

        while iter.value():
            treeItem = iter.value()
            hasChildren = treeItem.childCount() > 0

            if expand:
                if hasChildren:
                    self.expandItem(treeItem)
            elif collapse:
                if hasChildren:
                    self.collapseItem(treeItem)

            if check or uncheck:
                # check/uncheck param if not function driven
                if treeItem.data(0, Qt.UserRole).entryType != PCParamTreeWidget.PCItemData.ET_PARAM_FCT:
                    checkStateToSet = Qt.Checked if check else Qt.Unchecked
                    treeItem.setCheckState(0, checkStateToSet)

            iter += 1

        self.ignoreItemChangedNotifs = False