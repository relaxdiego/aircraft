import unittest
from unittest.mock import (
    create_autospec,
    call,
    patch,
)
from uuid import uuid4

from aircraft import dispatch

from aircraft.dispatcher import (
    _get_charm_context,
    _run,
    CharmContext,
)


class DispatchTest(unittest.TestCase):

    @patch('unboxed.dispatcher._run', spec_set=True)
    @patch('unboxed.dispatcher.inspect', spec_set=True)
    @patch('unboxed.dispatcher._get_charm_context', spec_set=True)
    def test__it_dispatches_correctly(
            self,
            mock_get_charm_context_func,
            mock_inspect,
            mock_run_func):
        # Exercise
        dispatch()

        # Assert
        assert mock_get_charm_context_func.call_count == 1
        assert mock_get_charm_context_func.call_args == call()

        assert mock_run_func.call_count == 1
        assert mock_run_func.call_args == call(
            mock_inspect.getmodule.return_value,
            mock_get_charm_context_func.return_value
        )


class GetCharmContextTest(unittest.TestCase):

    @patch('unboxed.dispatcher.os.environ', spec_set=True)
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


class RunTest(unittest.TestCase):

    @patch('unboxed.dispatcher.getattr')
    @patch('unboxed.dispatcher.log')
    def test__it_executes_an_existing_function(
            self,
            mock_log,
            mock_getattr_func):
        # Setup
        ctx = CharmContext(
            hook_path=f"hooks/{uuid4()}"
        )
        mock_mod = create_autospec(object)
        mock_func = mock_getattr_func.return_value

        # Exercise
        _run(mock_mod, ctx)

        # Assert
        assert mock_func.call_count == 1
        assert mock_func.call_args == call(ctx)

    @patch('unboxed.dispatcher.getattr')
    @patch('unboxed.dispatcher.log')
    def test__it_skips_execution_if_function_does_not_exist(
            self,
            mock_log,
            mock_getattr_func):
        # Setup
        ctx = CharmContext(
            hook_path=f"hooks/{uuid4()}"
        )
        mock_mod = create_autospec(object)
        mock_getattr_func.return_value = None

        # Exercise
        _run(mock_mod, ctx)

        # Assert
        assert mock_getattr_func.call_count == 1
        assert mock_getattr_func.call_args == call(mock_mod,
                                                   ctx.hook_name,
                                                   None)
