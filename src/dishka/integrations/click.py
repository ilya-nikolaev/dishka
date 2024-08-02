__all__ = [
    "FromDishka",
    "inject",
    "setup_dishka",
]

from click import (
    Command,
    Context,
    Group,
    get_current_context,
)

from dishka import Container, FromDishka
from .base import is_dishka_injected, wrap_injection

CONTAINER_NAME = "dishka_container"


def inject(func):
    return wrap_injection(
        func=func,
        container_getter=lambda _, __: get_current_context().meta[
            CONTAINER_NAME
        ],
        remove_depends=True,
        is_async=False,
    )


def _inject_commands(context: Context, command: Command) -> None:
    if isinstance(command, Command) and not is_dishka_injected(
        command.callback,
    ):
        command.callback = inject(command.callback)

    if isinstance(command, Group):
        for command_name in command.list_commands(context):
            child_command = command.get_command(context, command_name)
            _inject_commands(context, child_command)


def setup_dishka(
    container: Container,
    context: Context,
    *,
    finalize_container: bool = True,
    auto_inject: bool = False,
) -> None:
    context.meta[CONTAINER_NAME] = container

    if finalize_container:
        context.call_on_close(container.close)

    if auto_inject:
        _inject_commands(context, context.command)
