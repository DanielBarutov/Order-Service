import typing


class UnitOfWorkPort(typing.Protocol):
    async def __call__(self) -> None: ...
