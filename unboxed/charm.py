#!/usr/bin/env python3
import json
import logging
import os
import subprocess

log = logging.getLogger()


def main():
    log.setLevel(logging.DEBUG)
    log.addHandler(JujuLogHandler())

    event_name = os.environ.get('JUJU_DISPATCH_PATH', 'UNKNOWN!')
    log.debug(f"event_name={event_name}")

    event_handlers = {
        "hooks/install": an_event_handler,
        "hooks/leader-elected": an_event_handler,
        "hooks/config-changed": an_event_handler,
        "hooks/start": an_event_handler
    }

    event_handler = event_handlers.get(event_name, None)

    if event_handler:
        event_handler(event_name)


def an_event_handler(event_name):
    log.debug(f"Handling {event_name}")
    log.debug(json.dumps(dict(os.environ)))


class JujuLogHandler(logging.Handler):

    def __init__(self, level=logging.DEBUG):
        super().__init__(level)

    def emit(self, record):
        subprocess.run(f"juju-log -l {record.levelname} '{self.format(record)}'",
                       shell=True, check=True)


if __name__ == "__main__":
    main()
