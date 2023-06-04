from abc import ABC, abstractmethod
from typing import Any, Dict


class WorkflowHandler(ABC):
    """
        Abstract class for implementing self-contained trigger for specific workflow.
    """

    def __init__(self, name, group, system):
        """
            Extend the constructor to push any additional info required to trigger this workflow.
        """
        self.name = name
        self.group = group
        self.system = system

    @abstractmethod
    def run(self, data: Dict):
        """
            Trigger this workflow
        """
        pass

    def __repr__(self):
        return f'<{self.__class__.__name__} system=`{self.system}` group=`{self.group}` name=`{self.name}`>'
