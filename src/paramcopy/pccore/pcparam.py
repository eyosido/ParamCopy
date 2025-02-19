# ---------------
# ParamCopy - Substance 3D Designer plugin
# (c) 2019-2025 Eyosido Software SARL
# ---------------

from paramcopy.pccore.pchelper import PCHelper

class PCParam:
# A parameter with value independent of the node it comes from
    def __init__(self, propertyId, propertyLabel, inheritanceMethod, value, groupName = None):
        self.id = propertyId
        self.label = propertyLabel
        self.inheritanceMethod = inheritanceMethod
        self.value = value
        self.groupName = groupName

    def getName(self):
        return self.label if self.label and len(self.label) > 0 else self.id

class PCParamCollection:
# A collection of parameter values (PCParam) that can be stored in memory and is independent from the nodes
# parameters come from.
    def __init__(self):
        self.params = {} # key: input param id, val: PCParam
    
    def paramNames(self):
        names = ""
        first = True
        for param in self.params.values():
            name = param.getName()
            if first:
                names += name
                first = False
            else:
                names += "," + name
                
        return PCHelper.croppedText(names, 200)