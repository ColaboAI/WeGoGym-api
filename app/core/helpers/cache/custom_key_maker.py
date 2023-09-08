import inspect
from typing import Any, Callable, OrderedDict
from fastapi import Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.helpers.cache.base.key_maker import ArgType
from .base import BaseKeyMaker

from inspect import Parameter, Signature
from typing import Mapping, Type

SigParameters = Mapping[str, Parameter]
SigReturnType = Type[object]
ALWAYS_IGNORE_ARG_TYPES = [Response, Request, AsyncSession]


class CustomKeyMaker(BaseKeyMaker):
    async def make(self, prefix, ignore_arg_types, function: Callable, *args, **kwargs) -> str:
        if not ignore_arg_types:
            ignore_arg_types = []
        ignore_arg_types.extend(ALWAYS_IGNORE_ARG_TYPES)
        ignore_arg_types = list(set(ignore_arg_types))
        prefix = f"{prefix}::" if prefix else ""
        path = f"{prefix}{function.__module__}.{function.__name__}"

        sig = inspect.signature(function)
        sig_params = sig.parameters
        func_args = self.get_func_args(sig, *args, **kwargs)
        args_str = self.get_args_str(sig_params, func_args, ignore_arg_types)
        return f"{path}({args_str})"

    def get_func_args(self, sig: Signature, *args: list, **kwargs: dict) -> "OrderedDict[str, Any]":
        """Return a dict object containing the name and value of all function arguments."""
        func_args = sig.bind(*args, **kwargs)
        func_args.apply_defaults()
        return func_args.arguments

    def get_args_str(
        self,
        sig_params: SigParameters,
        func_args: "OrderedDict[str, Any]",
        ignore_arg_types: list[ArgType],
    ) -> str:
        """Return a string with the name and value of all args whose type is not included in `ignore_arg_types`"""
        return ",".join(
            f"{arg}={val}" for arg, val in func_args.items() if sig_params[arg].annotation not in ignore_arg_types
        )
