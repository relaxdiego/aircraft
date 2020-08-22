#!/usr/bin/env python3
import json
from kubernetes import (
    client,
    config,
)
import logging
import os
from pathlib import Path
from subprocess import call
import sys

from unboxed import (
    dispatch,
)

log = logging.getLogger()


# === HOOKS

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
    _load_k8s_client_credentials()

    core_v1 = client.CoreV1Api()
    v1_pod_list = core_v1.list_pod_for_all_namespaces(watch=False)

    log.info('Pods found:')

    for i in v1_pod_list.items:
        log.info(f'  - {i.metadata.name}')

    # Reference: https://discourse.juju.is/t/hook-tools/1163
    call(['status-set', 'active', "Looking good, Bill Ray!"])


# === HELPERS


def _load_k8s_client_credentials():
    user_kubeconfig = Path(os.path.expanduser("~")) / '.kube' / 'config'

    if user_kubeconfig.exists():
        log.debug("Using user kube config")
        config.load_kube_config()
    else:
        # Workaround for bug https://bugs.launchpad.net/juju/+bug/1892255
        os.environ.update(
            dict(
                e.split("=")
                for e in Path("/proc/1/environ").read_text().split("\x00")
                if "KUBERNETES_SERVICE" in e
            )
        )
        log.debug("Using in-cluster kube config")
        try:
            config.load_incluster_config()
        except config.ConfigException:
            log.error("Unable to load in-cluster config file. Exiting.")
            sys.exit(1)


if __name__ == "__main__":
    dispatch()
