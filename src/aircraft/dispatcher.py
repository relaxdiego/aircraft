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

    # Reference: https://docs.python.org/3.7/library/inspect.html
    #
    # NOTE: The inspect module is very much tied to CPython which means
    #       that there is no guarantee that this code will work with any
    #       other implementation of Python (e.g. Jython). On the other
    #       hand, I don't see any need to use anything other than CPython.

    # Get the the FrameInfo named tuple of the prev frame as denoted by [1]
    caller_frame_info = inspect.stack()[1]

    # caller_frame_info[0] refers to the actual frame obj inside FrameInfo
    caller_module = inspect.getmodule(caller_frame_info[0])

    # We then pass the caller's module to _run which will take
    # care of finding the function that corresponds to the provided hook path
    _run(caller_module, ctx)


def _get_charm_context():
    return CharmContext(
        hook_path=os.environ.get('JUJU_DISPATCH_PATH', None)
    )


def _run(caller_mod, ctx):
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
