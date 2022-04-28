# ---------------
# ParamCopy - Substance 3D Designer plugin
# (c) 2019-2022 Eyosido Software SARL
# ---------------

from sd.api.sdnode import SDNode
from sd.api.sddefinition import SDDefinition
from sd.api.sdproperty import SDProperty, SDPropertyCategory
from sd.api.sdresource import SDResource

from sd.api.sdvaluearray import SDValueArray
from sd.api.sdvaluebool import SDValueBool
from sd.api.sdvaluebool2 import SDValueBool2
from sd.api.sdvaluebool3 import SDValueBool3
from sd.api.sdvaluebool4 import SDValueBool4
from sd.api.sdvaluecolorrgb import SDValueColorRGB
from sd.api.sdvaluecolorrgba import SDValueColorRGBA
from sd.api.sdvaluedouble import SDValueDouble
from sd.api.sdvaluedouble2 import SDValueDouble2
from sd.api.sdvaluedouble3 import SDValueDouble3
from sd.api.sdvaluedouble4 import SDValueDouble4
from sd.api.sdvalueenum import SDValueEnum
from sd.api.sdvaluefloat import SDValueFloat
from sd.api.sdvaluefloat2 import SDValueFloat2
from sd.api.sdvaluefloat3 import SDValueFloat3
from sd.api.sdvaluefloat4 import SDValueFloat4
from sd.api.sdvalueint import SDValueInt
from sd.api.sdvalueint2 import SDValueInt2
from sd.api.sdvalueint3 import SDValueInt3
from sd.api.sdvalueint4 import SDValueInt4
from sd.api.sdvaluematrix import SDValueMatrix
from sd.api.sdvaluestring import SDValueString
from sd.api.sdvaluestruct import SDValueStruct
from sd.api.sdvalueusage import SDValueUsage
from sd.api.sdvaluetexture import SDValueTexture
from sd.api.sdvaluevector import SDValueVector

from paramcopy.pccore import pclog

class PCInspector:
    class NodeDesc:
        def __init__(self):
            self.className = ""
            self.identifier = ""
            self.definition = None # DefinitionDesc
            self.packagePath = ""
            self.annotationProperties = None # list of PropertyDesc
            self.inputProperties  = None # list of PropertyDesc
            self.outputProperties  = None # list of PropertyDesc
            self.referencedResource = None # NodeDesc

    class DefinitionDesc:
        def __init__(self):
            self.className = ""
            self.description = ""
            self.identifier = ""
            self.label = ""
            self.annotationProperties = None # list of PropertyDesc
            self.inputProperties  = None # list of PropertyDesc
            self.outputProperties  = None # list of PropertyDesc

    class PropertyDesc:
        def __init__(self):
            self.className = ""
            self.defaultValue = None # ValueDesc
            self.description = ""
            self.identifier = ""
            self.isConnectable = ""
            self.isFunctionOnly = ""
            self.isReadOnly = ""
            self.isVariadic = ""
            self.value = None # ValueDesc

    class ValueDesc:
        def __init__(self, sdValue):
            self.typeStr, self.valueStr = PCInspector.typeAndValueAndStrings(sdValue)
 
    @classmethod
    def nodeDesc(cls, node):
        nodeDesc = PCInspector.NodeDesc()
        nodeDesc.className = node.getClassName()
        nodeDesc.identifier = node.getIdentifier()

        if isinstance(node, SDResource):
            nodeDesc.packagePath = node.getPackage().getFilePath()

        if isinstance(node, SDNode) and node.getDefinition():
            nodeDesc.definition = cls.definitionDesc(node.getDefinition())

        nodeDesc.annotationProperties = cls.propertiesDesc(node, SDPropertyCategory.Annotation)
        nodeDesc.inputProperties = cls.propertiesDesc(node, SDPropertyCategory.Input)
        nodeDesc.outputProperties = cls.propertiesDesc(node, SDPropertyCategory.Output)

        if isinstance(node, SDNode):
            res = node.getReferencedResource()
            if res:
                nodeDesc.referencedResource = cls.nodeDesc(res)
        return nodeDesc

    @classmethod
    def propertiesDesc(cls, holder, category):
        propertiesDesc = []
        properties = holder.getProperties(category)
        if properties:
            propertiesCount = properties.getSize()
            for i in range(0, propertiesCount):
                prop = properties.getItem(i)
                propDesc = cls.propertyDesc(prop, holder, category)
                propertiesDesc.append(propDesc)
        return propertiesDesc

    @classmethod
    def propertyDesc(cls, prop, holder, category):
        propertyDesc = PCInspector.PropertyDesc()
        propertyDesc.className = prop.getClassName()
        if prop.getDefaultValue():
            propertyDesc.defaultValue = cls.valueDesc(prop.getDefaultValue())
        propertyDesc.description = prop.getDescription()
        propertyDesc.identifier = prop.getId()
        propertyDesc.isConnectable = cls.boolStr(prop.isConnectable())
        propertyDesc.isFunctionOnly = cls.boolStr(prop.isFunctionOnly())
        propertyDesc.isPrimary = cls.boolStr(prop.isPrimary())
        propertyDesc.isReadOnly = cls.boolStr(prop.isReadOnly())
        propertyDesc.isVariadic =  cls.boolStr(prop.isVariadic())

        # Value, we cannot get value on SDDefinition instances
        if not isinstance(holder, SDDefinition):
            propValue = holder.getPropertyValueFromId(propertyDesc.identifier, category)
            if propValue:
                propertyDesc.value = cls.valueDesc(propValue)
        
        return propertyDesc

    @classmethod
    def definitionDesc(cls, definition):
        definitionDesc = PCInspector.DefinitionDesc()   
        definitionDesc.className = definition.getClassName()
        definitionDesc.description = definition.getDescription()
        definitionDesc.identifier = definition.getId()
        definitionDesc.label = definition.getLabel()

        definitionDesc.annotationProperties = cls.propertiesDesc(definition, SDPropertyCategory.Annotation)
        definitionDesc.inputProperties = cls.propertiesDesc(definition, SDPropertyCategory.Input)
        definitionDesc.outputProperties = cls.propertiesDesc(definition, SDPropertyCategory.Output)

    @classmethod
    def valueDesc(cls, sdValue):
        valueDesc = PCInspector.ValueDesc(sdValue)
        return valueDesc if len(valueDesc.typeStr) > 0 and len(valueDesc.valueStr) > 0 else None

    @classmethod
    def log(cls, node):
        nodeDesc = cls.nodeDesc(node)
        cls.logNodeDesc("", nodeDesc)

    @classmethod
    def logNodeDesc(cls, indent, nodeDesc):
        localIndent = indent + "    "
        pclog.log("Classname: " + nodeDesc.className)
        pclog.log("Identifier: " + nodeDesc.identifier)

        if len(nodeDesc.packagePath) > 0:
            pclog.log("Package: " + nodeDesc.packagePath)

        if nodeDesc.definition:
            pclog.log("")
            pclog.log("Definition:")
            cls.logDefinitionDesc(localIndent, nodeDesc.definition)

        if len(nodeDesc.annotationProperties) > 0:
            pclog.log("")
            pclog.log("Annotation properties:")
            cls.logPropertiesDesc(localIndent, nodeDesc.annotationProperties)
        if len(nodeDesc.inputProperties) > 0:
            pclog.log("")
            pclog.log("Input properties:")
            cls.logPropertiesDesc(localIndent, nodeDesc.inputProperties)
        if len(nodeDesc.outputProperties) > 0:
            pclog.log("")
            pclog.log("Output properties:")
            cls.logPropertiesDesc(localIndent, nodeDesc.outputProperties)

        if nodeDesc.referencedResource:
            pclog.log("")
            pclog.log("Referenced resource:")
            cls.logNodeDesc(localIndent, nodeDesc.referencedResource)

    @classmethod
    def logDefinitionDesc(cls, indent, definitionDesc):
        pclog.log(indent + "Classname: " + definitionDesc.className)
        pclog.log(indent + "Identifier: " + definitionDesc.identifier)
        pclog.log(indent + "Label: " + definitionDesc.label)
        pclog.log(indent + "Description: " + definitionDesc.description)
        localIndent = indent + "    "

        if len(definitionDesc.annotationProperties) > 0:
            pclog.log("")
            pclog.log(indent + "Annotation properties:")
            cls.logPropertiesDesc(localIndent, definitionDesc.annotationProperties)
        if len(definitionDesc.inputProperties) > 0:
            pclog.log("")
            pclog.log(indent + "Input properties:")
            cls.logPropertiesDesc(localIndent, definitionDesc.inputProperties)
        if len(definitionDesc.outputProperties) > 0:
            pclog.log("")
            pclog.log(indent + "Output properties:")
            cls.logPropertiesDesc(localIndent, definitionDesc.outputProperties)

    @classmethod
    def logPropertiesDesc(cls, indent, propertiesDesc):
        for propDesc in propertiesDesc:
            pclog.log("")
            pclog.log(indent + "Identifier: " + propDesc.identifier)
            pclog.log(indent + "Description: " + propDesc.description)
            pclog.log(indent + "Classname: " + propDesc.className)
            if propDesc.defaultValue:
                pclog.log(indent + "Default value: (" + propDesc.defaultValue.typeStr + ") " + propDesc.defaultValue.valueStr)
            if propDesc.value:
                pclog.log(indent + "Value: (" + propDesc.value.typeStr + ") " + propDesc.value.valueStr)
            pclog.log(indent + "Connectable: " + propDesc.isConnectable)
            pclog.log(indent + "Function-only: " + propDesc.isFunctionOnly)
            pclog.log(indent + "Read-only: " + propDesc.isReadOnly)
            pclog.log(indent + "Variadic: " + propDesc.isVariadic)

    @classmethod
    def boolStr(cls, boolValue):
       return "Yes" if boolValue else "No"

    @classmethod
    def typeAndValueAndStrings(cls, sdValue):
        typeStr = ""
        valueStr = ""
        if isinstance(sdValue,SDValueArray):
            typeStr = "Array"
        elif isinstance(sdValue, SDValueBool):
            typeStr = "Bool"
            valueStr = cls.boolStr(sdValue.get())
        elif isinstance(sdValue, SDValueBool2):
            typeStr = "Bool2"
            valueStr = "x:" + cls.boolStr(sdValue.get().x) + " y:" + cls.boolStr(sdValue.get().y)
        elif isinstance(sdValue, SDValueBool3):
            typeStr = "Bool3"
            valueStr = "x:" + cls.boolStr(sdValue.get().x) + " y:" + cls.boolStr(sdValue.get().y)+ " z:" + cls.boolStr(sdValue.get().z)
        elif isinstance(sdValue, SDValueBool4):
            typeStr = "Bool4"
            valueStr = "w:" + cls.boolStr(sdValue.get().w) + " x:" + cls.boolStr(sdValue.get().x) + " y:" + cls.boolStr(sdValue.get().y)+ " z:" + cls.boolStr(sdValue.get().z)
        elif isinstance(sdValue, SDValueColorRGB):
            typeStr = "ColorRGB"
            valueStr = "R:" + str(sdValue.get().r) + " G:" + str(sdValue.get().g) + " B:" + str(sdValue.get().b)
        elif isinstance(sdValue, SDValueColorRGBA):
            typeStr = "ColorRGBA"
            valueStr = "R:" + str(sdValue.get().r) + " G:" + str(sdValue.get().g) + " B:" + str(sdValue.get().b) + " A:" + str(sdValue.get().a)       
        elif isinstance(sdValue, SDValueDouble):
            typeStr = "Double"
            valueStr = str(sdValue.get())
        elif isinstance(sdValue, SDValueDouble2):
            typeStr = "Double2"
            valueStr = "x:" + str(sdValue.get().x) + " y:" + str(sdValue.get().y)
        elif isinstance(sdValue, SDValueDouble3):
            typeStr = "Double3"
            valueStr = "x:" + str(sdValue.get().x) + " y:" + str(sdValue.get().y) + " z:" + str(sdValue.get().z)
        elif isinstance(sdValue, SDValueDouble4):
            typeStr = "Double4"
            valueStr = "w:" + str(sdValue.get().w) + "x:" + str(sdValue.get().x) + " y:" + str(sdValue.get().y) + " z:" + str(sdValue.get().z)
        elif isinstance(sdValue, SDValueEnum):
            typeStr = "Enum"
            valueStr = str(sdValue.get())
        elif isinstance(sdValue, SDValueFloat):
            typeStr = "Float"
            valueStr = str(sdValue.get())
        elif isinstance(sdValue, SDValueFloat2):
            typeStr = "Float2"
            valueStr = "x:" + str(sdValue.get().x) + " y:" + str(sdValue.get().y)
        elif isinstance(sdValue, SDValueFloat3):
            typeStr = "Float3"
            valueStr = "x:" + str(sdValue.get().x) + " y:" + str(sdValue.get().y) + " z:" + str(sdValue.get().z)
        elif isinstance(sdValue, SDValueFloat4):
            typeStr = "Float4"
            valueStr = "w:" + str(sdValue.get().w) + "x:" + str(sdValue.get().x) + " y:" + str(sdValue.get().y) + " z:" + str(sdValue.get().z)
        elif isinstance(sdValue, SDValueInt):
            typeStr = "Integer"
            valueStr = str(sdValue.get())
        elif isinstance(sdValue, SDValueInt2):
            typeStr = "Integer2"
            valueStr = "x:" + str(sdValue.get().x) + " y:" + str(sdValue.get().y)
        elif isinstance(sdValue, SDValueInt3):
            typeStr = "Integer3"
            valueStr = "x:" + str(sdValue.get().x) + " y:" + str(sdValue.get().y) + " z:" + str(sdValue.get().z)
        elif isinstance(sdValue, SDValueInt4):
            typeStr = "Integer4"
            valueStr = "w:" + str(sdValue.get().w) + "x:" + str(sdValue.get().x) + " y:" + str(sdValue.get().y) + " z:" + str(sdValue.get().z)
        elif isinstance(sdValue, SDValueMatrix):
            rows = sdValue.getRowCount()
            cols = sdValue.getColumnCount()
            typeStr = "Matrix (" + str(rows) + " rows, " + str(cols) + " cols)"  
            for row in range(0, rows):
                for col in range(0, cols):
                    _,v = cls.typeAndValueAndStrings(sdValue.getItem(col,row))
                    valueStr += "(" + str(col) + "," + str(row) + "):" + v + " "
            valueStr = valueStr[:-1] # remove trailing space
        elif isinstance(sdValue, SDValueString):
            typeStr = "String"
            valueStr = sdValue.get()
        elif isinstance(sdValue, SDValueStruct):
            typeStr = "Struct"
        elif isinstance(sdValue, SDValueUsage):
            typeStr = "Usage"
        elif isinstance(sdValue, SDValueVector):
            typeStr = "Vector"
        
        return typeStr, valueStr



