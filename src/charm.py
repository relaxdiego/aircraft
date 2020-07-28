#!/usr/bin/env python3

# Standard Library imports go here
from collections import namedtuple
import logging
import yaml

# Operator Frmework imports go here
from ops.charm import CharmBase
from ops.main import main
from ops.model import (
    BlockedStatus,
    MaintenanceStatus,
    ModelError,
)

# Imports of your charm's objects go here
# import interfaace_foo


log = logging.getLogger(__name__)


class ChangeMeCharm(CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.start, self.on_start_delegator)

    # DELEGATORS

    # These delegators exist to decouple the actual handlers from the
    # underlying framework which has some very specific requirements that
    # do not always apply to every event. For instance if we were to add
    # an interface in our initializer, we would be forced to write unit
    # tests that mock out that object even for handlers that do not need
    # it. This hard coupling results in verbose tests that contain unused
    # mocks. These tests tend to be hard to follow. To counter that, the
    # logic is moved away from this class.

    def on_start_delegator(self, event):
        on_start_handler(
            model_name=self.model.name,
            app_name=self.app.name,
            unit_name=self.unit.name,
            unit_is_leader=self.unit.is_leader,
            image_meta=_get_image_meta('changeme-image', self),
            set_pod_spec_func=self.model.pod.set_spec,
            set_unit_status_func=_get_unit_status_setter_func(self),
        )


# EVENT HANDLERS
# These event handlers are designed to be stateless and, as much as possible,
# procedural (run from top to bottom). They are stateless since any stored
# states are already handled by the Charm object anyway and also because this
# simplifies testing of said handlers. They are also procedural since they are
# similar to controllers in an MVC app in that they are only concerned with
# coordinating domain models and services.

def on_start_handler(
        model_name,
        app_name,
        unit_name,
        unit_is_leader,
        image_meta,
        set_pod_spec_func,
        set_unit_status_func):
    if not unit_is_leader:
        log.debug("Unit '{}' is not leader. "
                  "Skipping pod configuration".format(unit_name))
        return

    log.debug("Building Juju pod spec")
    juju_pod_spec_dict = _build_juju_pod_spec_dict(
        app_name=app_name,
        image_meta=image_meta,
    )

    log.debug("Configuring pod")
    set_pod_spec_func(juju_pod_spec_dict)
    set_unit_status_func(MaintenanceStatus("Configuring pod"))


# HELPERS

def _build_juju_pod_spec_dict(app_name,
                              image_meta):
    spec = {
        'containers': [{
            'name': app_name,
            'imageDetails': {
                'imagePath': image_meta.registrypath,
                'username': image_meta.username,
                'password': image_meta.password
            },
            'ports': [{
                'containerPort': 3000,
                'protocol': 'TCP'
            }],
            'readinessProbe': {
                'httpGet': {
                    'path': '/api/health',
                    'port': 3000
                },
                'initialDelaySeconds': 10,
                'timeoutSeconds': 30
            }
        }]
    }

    return spec


def _get_image_meta(image_name, charm):
    resources_repo = charm.model.resources

    path = resources_repo.fetch(image_name)
    if not path.exists():
        msg = 'Resource not found at {}'.format(path)
        raise ResourceError(image_name, msg)

    resource_yaml = path.read_text()

    if not resource_yaml:
        msg = 'Resource unreadable at {}'.format(path)
        raise ResourceError(image_name, msg)

    try:
        resource_dict = yaml.safe_load(resource_yaml)
    except yaml.error.YAMLError:
        msg = 'Invalid YAML at {}'.format(path)
        raise ResourceError(image_name, msg)
    else:
        return ImageMeta(**resource_dict)


def _get_unit_status_setter_func(charm):
    def set_unit_status(status):
        charm.unit.status = status

    return set_unit_status


# MODELS

ImageMeta = namedtuple('ImageMeta',
                       [
                           'registrypath',
                           'username',
                           'password'
                       ])


class ResourceError(ModelError):

    def __init__(self, resource_name, message):
        super().__init__(resource_name)
        msg = "{}: {}".format('resource_name', 'message')
        self.status = BlockedStatus(msg)


if __name__ == "__main__":
    main(ChangeMeCharm)
