#!/usr/bin/env python3
import json
import logging
import os

from unboxed import dispatch

log = logging.getLogger()


# To have a hook be called by Juju, just define a function with the pattern
# `hook_<HOOKNAME>` where `<HOOKNAME>` is one of the hooks defined in this post
# https://discourse.juju.is/t/charm-hooks/1040 but with hyphens converted
# to underscores.
#
# Each hook will be passed a `CharmContext` instance which should (eventually)
# provide just enough information for it to do its job. See src/unboxed for
# more information on `CharmContext`.
#
# Other than that, it's all just Python. You can add 3rd-party libraries
# by adding them to the `runtime_requirements` list in `setup.py`.


def hook_config_changed(context):
    log.debug(f"Hello from {context.hook_name}")


def hook_install(context):
    log.debug(f"Hello from {context.hook_name}")
    log.debug(json.dumps(dict(os.environ)))


def hook_start(context):
    log.debug(f"Hello from {context.hook_name}")


if __name__ == "__main__":
    dispatch()
