import logging
from os import path
import shlex
from subprocess import run

log = logging.getLogger("aircraft.ssh")


def ssh(user: str, host: str, command: str):
    control_path = path.expanduser("~/.ssh/control-socket_%r@%h:%p")
    options = "-o ControlMaster=auto " \
              "-o ControlPersist=1m " \
              "-o ControlPath={}".format(control_path)
    ssh_str = "ssh {} {}@{} {}".format(options, user, host, command)
    log.debug("Running {}".format(ssh_str))
    return run(shlex.split(ssh_str), capture_output=True, text=True)
