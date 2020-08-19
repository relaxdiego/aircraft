import logging
import unittest
from unittest.mock import (
    create_autospec,
    call,
    patch,
)
from uuid import uuid4

from src.charm import (
    _get_charm_context,
    _configure_logging,
    _run_hook,
    CharmContext,
    dispatch,
    JujuLogHandler,
    log,
)


class DispatchTest(unittest.TestCase):

    @patch('src.charm._run_hook', spec_set=True)
    @patch('src.charm.inspect', spec_set=True)
    @patch('src.charm._get_charm_context', spec_set=True)
    @patch('src.charm._configure_logging', spec_set=True)
    def test__it_dispatches_the_hook_correctly(
            self,
            mock_configure_logging_func,
            mock_get_charm_context_func,
            mock_inspect,
            mock_run_hook_func):
        # Exercise
        dispatch()

        # Assert
        assert mock_configure_logging_func.call_count == 1
        assert mock_configure_logging_func.call_args == call(log)

        assert mock_get_charm_context_func.call_count == 1
        assert mock_get_charm_context_func.call_args == call()

        assert mock_run_hook_func.call_count == 1
        assert mock_run_hook_func.call_args == call(
            mock_inspect.getmodule.return_value,
            mock_get_charm_context_func.return_value
        )


class ConfigureLoggingTest(unittest.TestCase):

    def test__it_configures_the_log_level_and_handler(self):
        # Setup
        mock_log = create_autospec(log, spec_set=True)

        # Exercise
        _configure_logging(mock_log)

        # Assert
        assert mock_log.setLevel.call_count == 1
        assert mock_log.setLevel.call_args == call(logging.DEBUG)

        assert mock_log.addHandler.call_count == 1
        call_arg = mock_log.addHandler.call_args[0][0]
        assert isinstance(call_arg, JujuLogHandler)


class GetCharmContextTest(unittest.TestCase):

    @patch('src.charm.os.environ', spec_set=True)
    def test__it_returns_a_charm_context_object(
            self,
            mock_os_environ):
        # Setup
        mock_os_environ.get.return_value = str(uuid4())

        # Exercise
        ctx = _get_charm_context()

        # Assert
        assert isinstance(ctx, CharmContext)
        assert ctx.hook_path == mock_os_environ.get.return_value


class RunHookTest(unittest.TestCase):

    @patch('src.charm.getattr')
    def test__it_runs_an_existing_hook(
            self,
            mock_getattr_func):
        # Setup
        ctx = CharmContext(
            hook_path=f"hooks/{uuid4()}"
        )
        mock_mod = create_autospec(object)
        mock_hook = mock_getattr_func.return_value

        # Exercise
        _run_hook(mock_mod, ctx)

        # Assert
        assert mock_hook.call_count == 1
        assert mock_hook.call_args == call(ctx)

    @patch('src.charm.getattr')
    def test__it_does_not_fail_if_hook_is_not_found(
            self,
            mock_getattr_func):
        # Setup
        ctx = CharmContext(
            hook_path=f"hooks/{uuid4()}"
        )
        mock_mod = create_autospec(object)
        mock_getattr_func.return_value = None

        # Exercise
        _run_hook(mock_mod, ctx)

        # Assert
        assert mock_getattr_func.call_count == 1
