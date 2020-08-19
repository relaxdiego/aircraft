#!/usr/bin/env python3
import json
import logging
import os

log = logging.getLogger()


def hook_install(ctx):
    log.debug(f"Running hook {ctx.hook_path}")
    log.debug(json.dumps(dict(os.environ)))


# =====================================================================
# Unboxed Helpers. These should be moved to their own package once its
# public API has stabilized
# =====================================================================

from dataclasses import (
    dataclass,
    field
)
import inspect
import logging
import subprocess

log = logging.getLogger()


def dispatch():
    _configure_logging(log)

    ctx = _get_charm_context()

    # Not much explanation for this code right now while I'm
    # re-familiarizing myself with Python's reflection/metaprogramming
    # style. More documentation soon!
    # https://stackoverflow.com/a/1095621
    caller = inspect.stack()[1]
    caller_mod = inspect.getmodule(caller[0])

    _run_hook(caller_mod, ctx)


def _configure_logging(log):
    log.setLevel(logging.DEBUG)
    log.addHandler(JujuLogHandler())
    log.debug("Charm logging configured")


def _get_charm_context():
    return CharmContext(
        hook_path=os.environ.get('JUJU_DISPATCH_PATH', None)
    )


def _run_hook(caller_mod, ctx):
    log.debug(f"Attempting to run hook {ctx.hook_path}")

    # Try to get the hook if it exists
    hook = getattr(caller_mod, ctx.hook_name, None)

    # Call if the hook is found
    if hook:
        log.debug("Hook found. Running...")
        hook(ctx)
    else:
        log.debug(f"No hook defined for {ctx.hook_path}")


@dataclass
class CharmContext:
    hook_path: str
    hook_name: str = field(init="")

    def __post_init__(self):
        self.hook_name = str(self.hook_path.replace('hooks/', 'hook_'))


class JujuLogHandler(logging.Handler):

    def __init__(self, level=logging.DEBUG):
        super().__init__(level)

    def emit(self, record):
        subprocess.run(f"juju-log -l {record.levelname} '{self.format(record)}'",
                       shell=True, check=True)

# =====================================================================
# END Unboxed Helpers
# =====================================================================


if __name__ == "__main__":
    dispatch()
