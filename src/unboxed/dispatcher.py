#!/usr/bin/env python3
import logging
import os

from dataclasses import (
    dataclass,
    field
)
import inspect
import subprocess


class JujuLogHandler(logging.Handler):

    def __init__(self, level=logging.DEBUG):
        super().__init__(level)

    def emit(self, record):
        subprocess.run(f"juju-log -l {record.levelname} '{self.format(record)}'",
                       shell=True, check=True)


log = logging.getLogger()
log.setLevel(logging.DEBUG)
log.addHandler(JujuLogHandler())


def dispatch():
    ctx = _get_charm_context()

    # Not much explanation for this code right now while I'm
    # re-familiarizing myself with Python's reflection/metaprogramming
    # style. More documentation soon!
    # https://stackoverflow.com/a/1095621
    caller = inspect.stack()[1]
    caller_mod = inspect.getmodule(caller[0])

    _run_hook(caller_mod, ctx)


def _get_charm_context():
    return CharmContext(
        hook_path=os.environ.get('JUJU_DISPATCH_PATH', None)
    )


def _run_hook(caller_mod, ctx):
    log.debug(f"{ctx.hook_path} dispatched by Juju")
    log.debug(f"Looking for function {ctx.hook_name}...")

    # Try to get the hook if it exists
    hook = getattr(caller_mod, ctx.hook_name, None)

    # Call if the hook is found
    if hook:
        log.debug(f"Function {ctx.hook_name} found. Running...")
        hook(ctx)
    else:
        log.debug(f"Function {ctx.hook_name} not found. Ignoring.")


@dataclass
class CharmContext:
    hook_path: str
    hook_name: str = field(init="")

    def __post_init__(self):
        self.hook_name = self.hook_path \
            .replace('hooks/', 'hook_') \
            .replace('-', '_')
