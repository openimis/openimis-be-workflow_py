from abc import ABC, abstractmethod
from typing import Dict
from django.utils.functional import classproperty


class WorkflowAdaptor(ABC):
    """
    Abstract class for implementing specific workflow system integration.
    """

    @classmethod
    @classproperty
    @abstractmethod
    def system(cls) -> str:
        """
            Property describing a keyword to refer to this workflow system
        """
        pass

    @classmethod
    @abstractmethod
    def get_groups(cls) -> Dict:
        """
             Get all available groups from this workflow system as result dict
        """
        pass

    @classmethod
    @abstractmethod
    def get_workflows(cls, name: str = None, group: str = None) -> Dict:
        """
            Get all available workflows from this workflow system as result dict
        """
        pass
