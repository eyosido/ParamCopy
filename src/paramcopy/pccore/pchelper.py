# ---------------
# ParamCopy - Substance 3D Designer plugin
# (c) 2019-2025 Eyosido Software SARL
# ---------------

import os
from pathlib import Path

import sd
if sd.getContext().getSDApplication().getVersion() < "14.0.0":
    from PySide2 import QtCore, QtWidgets, QtGui, QtSvg
    from PySide2.QtGui import QPixmap
else:
    from PySide6 import QtCore, QtWidgets, QtGui, QtSvg
    from PySide6.QtGui import QPixmap
    
import sd
from sd.context import Context
from sd.api.sdapplication import SDApplication
from sd.api.sduimgr import SDUIMgr
from sd.api.apiexception import APIException
from sd.api.sdapiobject import SDApiError
from sd.api.sdgraph import SDGraph
from sd.api.sdproperty import SDProperty, SDPropertyCategory, SDPropertyInheritanceMethod

from paramcopy.pccore.pcdata import PCData
from paramcopy.pccore import pclog

class PCHelper:

    @classmethod
    def iconFullPath(cls, filename):
        path = os.path.dirname(os.path.dirname(__file__)) # go one folder up
        path = os.path.join(path, "pcui/img/" + filename)
        return path

    @classmethod
    def loadSvgAsPixmap(cls, filename, width, height):
        path = cls.iconFullPath(filename)
        pixmap = None
        svgRenderer = QtSvg.QSvgRenderer(path)
        if svgRenderer and svgRenderer.isValid():
            pixmap = QtGui.QPixmap(QtCore.QSize(width, height))
            pixmap.fill(QtCore.Qt.transparent)
            painter = QtGui.QPainter(pixmap)
            svgRenderer.render(painter)
            painter.end()

        return pixmap

    @classmethod
    def loadPngAsPixmap(cls, filename):
        path = cls.iconFullPath(filename)
        pixmap = QtGui.QPixmap(path)
        return pixmap

    @classmethod
    def displayErrorMsg(cls, msg, parent = None):
        p = parent if parent else sd.getContext().getSDApplication().getQtForPythonUIMgr().getMainWindow()
        QtWidgets.QMessageBox.critical(p, PCData.APP_NAME, msg)

    @classmethod
    def displayInfoMsg(cls, msg, parent = None):
        p = parent if parent else sd.getContext().getSDApplication().getQtForPythonUIMgr().getMainWindow()
        QtWidgets.QMessageBox.information(p, PCData.APP_NAME, msg)

    @classmethod
    def askYesNoQuestion(cls, msg, canBeDisabled = True, parent = None):
        p = parent if parent else sd.getContext().getSDApplication().getQtForPythonUIMgr().getMainWindow()
        if canBeDisabled:
            msg += "\n\n(optional confirmations can be disabled in Preferences)\n"
        return QtWidgets.QMessageBox.question(p, PCData.APP_NAME, msg) == QtWidgets.QMessageBox.Yes

    @classmethod
    def inheritanceMethodLabel(cls, inheritanceMethod):
        if inheritanceMethod == SDPropertyInheritanceMethod.Absolute:
            label = "Absolute"
        elif inheritanceMethod == SDPropertyInheritanceMethod.RelativeToParent:
            label = "Relative to Parent"
        else:
            label = "Relative to Input"
        return label

    @classmethod
    def logSDException(cls, e):
        errCode = e.mErrorCode
        pclog.log("SD Exception, error code = " + str(errCode))

    @classmethod
    def isInputParamFunctionDriven(cls, node, inputParamProperty):
        # Tells whether the property representing an input param of the given node is driven by a function
        propGraph = node.getPropertyGraph(inputParamProperty)
        functionOnly = inputParamProperty.isFunctionOnly()
        return  propGraph and not functionOnly # ignore function props of graphs having subgraphs like pixel processor

    @classmethod
    def getPropertyOrDefinitionName(cls, sdObj):
        name = sdObj.getLabel()
        objId = sdObj.getId()
        if not name or len(name) == 0:
            name = objId
        return name

    @classmethod
    def isBaseParameter(cls, paramId):
        return paramId[0] == '$'

    @classmethod
    def hasCurrentGraph(cls):
        return cls.getCurrentGraph() != None

    @classmethod
    def getCurrentGraph(cls):
        return sd.getContext().getSDApplication().getQtForPythonUIMgr().getCurrentGraph()

    @classmethod
    def checkCurrentGraph(cls):
        hasCurrentgraph =  cls.hasCurrentGraph()
        if not hasCurrentgraph:
            PCHelper.displayErrorMsg("This function requires a current graph, please open a create a Substance graph.")
        return hasCurrentgraph

    @classmethod
    def computeCurrentGraph(cls):
        cls.getCurrentGraph().compute()

    @classmethod
    def getPackageId(cls, package):
        # a package has no id property so we use the file path
        return package.getFilePath()

    @classmethod
    def getPackageName(cls, package):
        # a package has no id property so we use the file path
        return Path(package.getFilePath()).stem

    @classmethod
    def getInheritanceMethod(cls, node, propertyId):
        # some params may not have inheritance method (i.e. Gradient RGBA of Gradient Map) so
        # we silently handle the exception when this occurs
        inheritanceMethod = -1
        try:
            inheritanceMethod = node.getInputPropertyInheritanceMethodFromId(propertyId)
        except APIException:
            pass
        finally:
            return inheritanceMethod

    @classmethod
    def getParamAnnotationValue(cls, node, propertyId, annotationId):
        annotationVal = None
        try:
            graph = node.getReferencedResource()
            if isinstance(graph, SDGraph):
                prop = graph.getPropertyFromId(propertyId, SDPropertyCategory.Input)
                if prop:
                    annotationVal = graph.getPropertyAnnotationValueFromId(prop, annotationId)
        except APIException:
            pass
        finally:
            return annotationVal

    @classmethod
    def getParamGroupName(cls, node, propertyId):
        val = cls.getParamAnnotationValue(node, propertyId, "group")
        return val.get() if val else None

    @classmethod
    def isHiddenParam(cls, node, propertyId):
        # we assume param is hidden if it contains "0" or "false" in the "visible_if" annotation field
        hidden = False
        val = cls.getParamAnnotationValue(node, propertyId, "visible_if")
        if val:
            valStr = val.get().strip()
            if valStr == "0" or valStr == "false":
                hidden = True
        return hidden
    
    @classmethod
    def croppedText(cls, text, maxLen = 70):
        if text and len(text) > maxLen:
            finalText = text[:maxLen] + "(...)"
        else:
            finalText = text
        return finalText