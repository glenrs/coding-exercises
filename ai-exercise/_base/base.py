from dataclasses import dataclass
from functools import cached_property

from .context import Context


@dataclass
class Base:

    @cached_property
    def context(self):
        return Context()