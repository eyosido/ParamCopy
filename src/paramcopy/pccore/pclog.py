# ---------------
# ParamCopy - Substance 3D Designer plugin
# (c) 2019-2025 Eyosido Software SARL
# ---------------

import logging
import sd
from paramcopy.pccore.pcdata import PCData

class PCLogger:
    internal_instance = None

    @classmethod
    # simplified singleton
    def instance(cls):
        if cls.internal_instance == None:  
            cls.internal_instance = PCLogger()
        return cls.internal_instance

    @classmethod
    def destroyLogger(cls):
        if cls.internal_instance and cls.internal_instance.nativeLogger:
            cls.internal_instance.nativeLogger.removeHandler(cls.internal_instance.handler)
        cls.internal_instance = None

    def __init__(self):
        self.useNativeLogger = isinstance(sd.getContext().getLogger(), logging.Logger)
        self.nativeLogger = None
        if self.useNativeLogger:
            self.nativeLogger = logging.getLogger(PCData.APP_NAME)
            self.handler = sd.getContext().createRuntimeLogHandler()
            self.nativeLogger.addHandler(self.handler)
            self.nativeLogger.setLevel(logging.INFO)
            self.nativeLogger.propagate = False

    def log(self, msg):
        if self.useNativeLogger:
            # SD 2020 API
            self.nativeLogger.info(msg)
        else:
            # SD 2019 API
            from sd.logger import LogLevel
            sd.getContext().getLogger().log(msg, LogLevel.Info, PCData.APP_NAME)

def log(msg):
    PCLogger.instance().log(msg)
