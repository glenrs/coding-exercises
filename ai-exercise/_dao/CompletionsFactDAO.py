
from _data_models import PromptConfig
from .ABCDAO import ABCDAO

from _data_models import CompletionsFact


__all__ = "CompletionsFactDAO",


class CompletionsFactDAO(ABCDAO):

    @property
    def table_class(self):
        return CompletionsFact
    