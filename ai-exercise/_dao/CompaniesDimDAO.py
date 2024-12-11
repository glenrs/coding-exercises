
from _data_models import PromptConfig
from .ABCDAO import ABCDAO

from _data_models import CompaniesDim


__all__ = "CompaniesDimDAO",


class CompaniesDimDAO(ABCDAO):

    @property
    def table_class(self):
        return CompaniesDim
    
    def find_or_write(self, domain):
        record = self.query.filter(CompaniesDim.Domain == domain).one_or_none()
        if record is None:
            return self.write(Domain=domain)
        else:
            return record.ID

    