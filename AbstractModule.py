from abc import ABCMeta, abstractmethod


class AbstractModule:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, module):
        self.MODULE = module
        self.STATUS = True

    @abstractmethod
    def activate(self):
        self.STATUS = True

    @abstractmethod
    def deactivate(self):
        self.STATUS = False

    def get_mod(self):
        return self.MODULE

    def get_status(self):
        return self.STATUS

    def set_status(self, status):
        self.STATUS = status
