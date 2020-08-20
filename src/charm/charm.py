#!/usr/bin/env python3
import json
import logging
import os

from unboxed.dispatcher import dispatch

log = logging.getLogger()


def hook_config_changed(context):
    log.debug(f"Hello from {context.hook_name}")


def hook_install(context):
    log.debug(f"Hello from {context.hook_name}")
    log.debug(json.dumps(dict(os.environ)))


def hook_start(context):
    log.debug(f"Hello from {context.hook_name}")


if __name__ == "__main__":
    dispatch()
