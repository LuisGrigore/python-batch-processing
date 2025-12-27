import pytest
from unittest.mock import MagicMock
from queue import Empty

from batch_processing.batch_processor.batch_processor import BatchProcessor
from batch_processing.batch_processor.context import BatchProcessorContext
from batch_processing.batch_processor.configuration import ProcessorConfig
from batch_processing.batch_processor.exception_info import ExceptionInfo
from batch_processing.batch_processor.worker_reported_error import WorkerReportedError
from batch_processing.context import ControlContext
from batch_processing.configuration import FailurePolicy, SharedConfig


class TestBatchProcessor:
    def test_start(self):
        pool = MagicMock()
        monitor = MagicMock()
        config = ProcessorConfig(shared=SharedConfig(), on_worker_exception=FailurePolicy.IGNORE)
        control_ctx = ControlContext()
        ctx = BatchProcessorContext(config, control_ctx)
        processor = BatchProcessor(pool, monitor, ctx)
        
        processor.start()
        
        assert control_ctx.stop_event.is_set() == False
        assert control_ctx.abort_event.is_set() == False
        pool.start.assert_called_once()
        monitor.start.assert_called_once()

    def test_stop_no_exceptions(self):
        pool = MagicMock()
        monitor = MagicMock()
        config = ProcessorConfig(shared=SharedConfig(), on_worker_exception=FailurePolicy.IGNORE)
        control_ctx = ControlContext()
        ctx = BatchProcessorContext(config, control_ctx)
        processor = BatchProcessor(pool, monitor, ctx)
        
        processor.stop()
        
        monitor.stop.assert_called_once()
        pool.stop.assert_called_once()
        pool.cleanup.assert_called_once()
        assert control_ctx.stop_event.is_set()

    def test_stop_with_fatal_exception(self):
        pool = MagicMock()
        monitor = MagicMock()
        config = ProcessorConfig(shared=SharedConfig(), on_worker_exception=FailurePolicy.IGNORE)
        control_ctx = ControlContext()
        control_ctx.fatal_exception = RuntimeError("fatal")
        ctx = BatchProcessorContext(config, control_ctx)
        processor = BatchProcessor(pool, monitor, ctx)
        
        with pytest.raises(RuntimeError, match="fatal"):
            processor.stop()

    def test_poll_exceptions(self):
        pool = MagicMock()
        monitor = MagicMock()
        config = ProcessorConfig(shared=SharedConfig(), on_worker_exception=FailurePolicy.IGNORE)
        control_ctx = ControlContext()
        ctx = BatchProcessorContext(config, control_ctx)
        exc = ValueError("error")
        exception_info = ExceptionInfo.from_exception(exc, "test_item")
        ctx.error_queue.get_nowait = MagicMock(side_effect=[exception_info, Empty()])
        processor = BatchProcessor(pool, monitor, ctx)
        
        exceptions = processor.poll_exceptions()
        
        assert len(exceptions) == 1
        assert exceptions[0] == exception_info

    def test_put(self):
        pool = MagicMock()
        monitor = MagicMock()
        config = ProcessorConfig(shared=SharedConfig(), on_worker_exception=FailurePolicy.IGNORE)
        control_ctx = ControlContext()
        ctx = BatchProcessorContext(config, control_ctx)
        processor = BatchProcessor(pool, monitor, ctx)
        
        processor.put("test_item")
        
        assert ctx.in_queue.get() == "test_item"

    def test_get(self):
        pool = MagicMock()
        monitor = MagicMock()
        config = ProcessorConfig(shared=SharedConfig(), on_worker_exception=FailurePolicy.IGNORE)
        control_ctx = ControlContext()
        ctx = BatchProcessorContext(config, control_ctx)
        ctx.out_queue.put("result")
        processor = BatchProcessor(pool, monitor, ctx)
        
        result = processor.get()
        
        assert result == "result"

    def test_get_nowait(self):
        pool = MagicMock()
        monitor = MagicMock()
        config = ProcessorConfig(shared=SharedConfig(), on_worker_exception=FailurePolicy.IGNORE)
        control_ctx = ControlContext()
        ctx = BatchProcessorContext(config, control_ctx)
        ctx.out_queue.get_nowait = MagicMock(return_value="result")
        processor = BatchProcessor(pool, monitor, ctx)
        
        result = processor.get_nowait()
        
        assert result == "result"

    def test_context_manager(self):
        pool = MagicMock()
        monitor = MagicMock()
        config = ProcessorConfig(shared=SharedConfig(), on_worker_exception=FailurePolicy.IGNORE)
        control_ctx = ControlContext()
        ctx = BatchProcessorContext(config, control_ctx)
        processor = BatchProcessor(pool, monitor, ctx)
        
        with processor as p:
            assert p is processor
            pool.start.assert_called_once()
            monitor.start.assert_called_once()
        
        monitor.stop.assert_called_once()
        pool.stop.assert_called_once()
        pool.cleanup.assert_called_once()

    def test_handle_worker_exceptions_abort(self):
        pool = MagicMock()
        monitor = MagicMock()
        config = ProcessorConfig(shared=SharedConfig(), on_worker_exception=FailurePolicy.ABORT)
        control_ctx = ControlContext()
        ctx = BatchProcessorContext(config, control_ctx)
        exc = ValueError("error")
        exception_info = ExceptionInfo.from_exception(exc, "test_item")
        ctx.error_queue.get_nowait = MagicMock(side_effect=[exception_info, Empty()])
        processor = BatchProcessor(pool, monitor, ctx)
        
        processor._handle_worker_exceptions()
        
        assert isinstance(processor._fatal_exception, WorkerReportedError)
        assert control_ctx.abort_event.is_set()
        assert control_ctx.stop_event.is_set()

    def test_handle_worker_exceptions_ignore(self):
        pool = MagicMock()
        monitor = MagicMock()
        config = ProcessorConfig(shared=SharedConfig(), on_worker_exception=FailurePolicy.IGNORE)
        control_ctx = ControlContext()
        ctx = BatchProcessorContext(config, control_ctx)
        exc = ValueError("error")
        exception_info = ExceptionInfo.from_exception(exc, "test_item")
        ctx.error_queue.get_nowait = MagicMock(side_effect=[exception_info, Empty()])
        processor = BatchProcessor(pool, monitor, ctx)
        
        processor._handle_worker_exceptions()
        
        assert processor._fatal_exception is None
        assert not control_ctx.abort_event.is_set()
        assert not control_ctx.stop_event.is_set()