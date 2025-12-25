import pytest
import asyncio
from unittest.mock import MagicMock
from queue import Empty

from src.batch_processing.iterable_batch_processor.iterable_batch_processor import IterableBatchProcessor


class TestIterableBatchProcessor:
    def test_process_full_batch(self):
        # Mock batch processor
        batch_processor = MagicMock()
        batch_processor.__enter__ = MagicMock(return_value=batch_processor)
        batch_processor.__exit__ = MagicMock(return_value=None)
        batch_processor.put = MagicMock()
        results = ["result1", "result2"]
        result_iter = iter(results)
        def get_nowait():
            try:
                return next(result_iter)
            except StopIteration:
                raise Empty()
        batch_processor.get_nowait = MagicMock(side_effect=get_nowait)

        in_iterable = ["item1", "item2"]
        processor = IterableBatchProcessor(batch_processor, in_iterable, 2)

        result = asyncio.run(processor.process())

        assert result == ["result1", "result2"]
        assert batch_processor.put.call_count == 2
        batch_processor.put.assert_any_call("item1")
        batch_processor.put.assert_any_call("item2")
        assert batch_processor.get_nowait.call_count == 2  # Two results

    def test_process_partial_batch(self):
        # Mock batch processor
        batch_processor = MagicMock()
        batch_processor.__enter__ = MagicMock(return_value=batch_processor)
        batch_processor.__exit__ = MagicMock(return_value=None)
        batch_processor.put = MagicMock()
        results = ["result1", "result2"]
        result_iter = iter(results)
        def get_nowait():
            try:
                return next(result_iter)
            except StopIteration:
                raise Empty()
        batch_processor.get_nowait = MagicMock(side_effect=get_nowait)

        in_iterable = ["item1", "item2", "item3"]
        processor = IterableBatchProcessor(batch_processor, in_iterable, 2)

        result = asyncio.run(processor.process())

        assert result == ["result1", "result2"]
        assert batch_processor.put.call_count == 2
        batch_processor.put.assert_any_call("item1")
        batch_processor.put.assert_any_call("item2")

    def test_process_empty_iterable(self):
        # Mock batch processor
        batch_processor = MagicMock()
        batch_processor.__enter__ = MagicMock(return_value=batch_processor)
        batch_processor.__exit__ = MagicMock(return_value=None)
        batch_processor.put = MagicMock()
        def get_nowait():
            raise Empty()
        batch_processor.get_nowait = MagicMock(side_effect=get_nowait)

        in_iterable = []
        processor = IterableBatchProcessor(batch_processor, in_iterable, 5)

        result = asyncio.run(processor.process())

        assert result == []
        assert batch_processor.put.call_count == 0

    def test_process_n_items_less_than_iterable(self):
        # Mock batch processor
        batch_processor = MagicMock()
        batch_processor.__enter__ = MagicMock(return_value=batch_processor)
        batch_processor.__exit__ = MagicMock(return_value=None)
        batch_processor.put = MagicMock()
        results = ["result1", "result2", "result3"]
        result_iter = iter(results)
        def get_nowait():
            try:
                return next(result_iter)
            except StopIteration:
                raise Empty()
        batch_processor.get_nowait = MagicMock(side_effect=get_nowait)

        in_iterable = ["item1", "item2", "item3", "item4"]
        processor = IterableBatchProcessor(batch_processor, in_iterable, 3)

        result = asyncio.run(processor.process())

        assert result == ["result1", "result2", "result3"]
        assert batch_processor.put.call_count == 3
        batch_processor.put.assert_any_call("item1")
        batch_processor.put.assert_any_call("item2")
        batch_processor.put.assert_any_call("item3")