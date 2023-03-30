from abc import ABC, abstractmethod
from typing import Callable, Type

ArgType = Type[object]


class BaseKeyMaker(ABC):
    @abstractmethod
    async def make(
        self,
        prefix: str | None,
        ignore_arg_types: list[ArgType],
        function: Callable,
        *args,
        **kwargs
    ) -> str:
        ...
