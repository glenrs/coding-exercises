from factories import *
from _data_models import Base

from pytest_factoryboy import register


for table_name, table_object in Base.metadata.tables.items():
    register(TableFactory, table_name, table_object=table_object)

from fixtures import *