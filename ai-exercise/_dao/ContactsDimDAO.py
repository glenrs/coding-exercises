
from _data_models import PromptConfig
from .ABCDAO import ABCDAO

from _data_models import ContactsDim


__all__ = "ContactsDimDAO", 


class ContactsDimDAO(ABCDAO):

    @property
    def table_class(self):
        return ContactsDim
    