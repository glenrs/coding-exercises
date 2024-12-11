
from _data_models import PromptConfig
from .ABCDAO import ABCDAO


__all__ = "PromptConfigDAO",


class PromptConfigDAO(ABCDAO):

    @property
    def table_class(self):
        return PromptConfig
    
    # TODO: introduce error handling with wrapper
    def latest_model_by_name(self, name):
        return self.query.filter(PromptConfig.Name == name).one()