from threading import Thread
import pytest
import time
from unittest.mock import MagicMock, patch
from queue import Queue

from src.batch_processing.monitor.monitor import WorkerMonitor
from src.batch_processing.monitor.context import MonitorContext
from src.batch_processing.monitor.configuration import MonitorConfig
from src.batch_processing.context import ControlContext
from src.batch_processing.configuration import FailurePolicy, SharedConfig
from src.batch_processing.worker_pool.worker_fatal_error import WorkerFatalError


class TestWorkerMonitor:
	def test_start_starts_thread(self):
		pool = MagicMock()
		config = MonitorConfig(shared=SharedConfig(), on_worker_death=FailurePolicy.IGNORE)
		control_ctx = ControlContext()
		ctx = MonitorContext(config, control_ctx)
		monitor = WorkerMonitor(pool, ctx)
		
		monitor.start()
		assert monitor._thread is not None
		assert monitor._thread.is_alive()
		
		ctx.stop_event.set()
		monitor.stop()

	def test_stop_joins_thread(self):
		pool = MagicMock()
		config = MonitorConfig(shared=SharedConfig(), on_worker_death=FailurePolicy.IGNORE)
		control_ctx = ControlContext()
		ctx = MonitorContext(config, control_ctx)
		monitor = WorkerMonitor(pool, ctx)
		
		monitor.start()
		time.sleep(0.1)  # Let thread start
		ctx.stop_event.set()
		monitor.stop()
		is_alive: bool = False
		if (monitor._thread):
			monitor_thread: Thread = monitor._thread
			is_alive = monitor_thread.is_alive()
		assert not is_alive

	def test_loop_ignore_policy(self):
		pool = MagicMock()
		fatal_error = WorkerFatalError(123, 1)
		pool.fatal_errors.return_value = [fatal_error]
		config = MonitorConfig(shared=SharedConfig(), on_worker_death=FailurePolicy.IGNORE)
		control_ctx = ControlContext()
		ctx = MonitorContext(config, control_ctx)
		monitor = WorkerMonitor(pool, ctx)
		
		def mock_sleep(_):
			ctx.stop_event.set()
		
		with patch('time.sleep', side_effect=mock_sleep):
			monitor._loop()
		
		assert monitor.events.qsize() == 0
		pool.fatal_errors.assert_not_called()
		pool.restart_dead.assert_not_called()
		assert not ctx.abort_event.is_set()
		assert ctx.stop_event.is_set()  # Set by mock

	def test_loop_abort_policy(self):
		pool = MagicMock()
		fatal_error = WorkerFatalError(123, 1)
		pool.fatal_errors.return_value = [fatal_error]
		config = MonitorConfig(shared=SharedConfig(), on_worker_death=FailurePolicy.ABORT)
		control_ctx = ControlContext()
		ctx = MonitorContext(config, control_ctx)
		monitor = WorkerMonitor(pool, ctx)
		
		def mock_sleep(_):
			ctx.stop_event.set()
		
		with patch('time.sleep', side_effect=mock_sleep):
			monitor._loop()
		
		assert monitor.events.qsize() == 1
		event = monitor.events.get()
		assert event == fatal_error
		pool.restart_dead.assert_not_called()
		assert ctx.abort_event.is_set()
		assert ctx.stop_event.is_set()
		assert ctx.fatal_exception == fatal_error

	def test_loop_restart_policy(self):
		pool = MagicMock()
		fatal_error = WorkerFatalError(123, 1)
		pool.fatal_errors.return_value = [fatal_error]
		pool.restart_dead.return_value = 1
		config = MonitorConfig(shared=SharedConfig(), on_worker_death=FailurePolicy.RESTART)
		control_ctx = ControlContext()
		ctx = MonitorContext(config, control_ctx)
		monitor = WorkerMonitor(pool, ctx)
		
		def mock_sleep(_):
			ctx.stop_event.set()
		
		with patch('time.sleep', side_effect=mock_sleep):
			monitor._loop()
		
		assert monitor.events.qsize() == 1
		event = monitor.events.get()
		assert event == fatal_error
		pool.restart_dead.assert_called_once()
		assert not ctx.abort_event.is_set()
		assert ctx.stop_event.is_set()