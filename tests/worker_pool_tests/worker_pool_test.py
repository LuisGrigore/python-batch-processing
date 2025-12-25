import pytest
import time

from src.worker_pool.worker_pool import WorkerPool
from src.worker_pool.worker import IWorker
from src.worker_pool.worker_fatal_error import WorkerFatalError


class DummyWorker(IWorker):
    def __init__(self, exit_code=0):
        self.exit_code = exit_code

    def target(self):
        if self.exit_code != 0:
            import sys
            sys.exit(self.exit_code)
        time.sleep(0.1)


def dummy_worker_factory(exit_code=0):
    def factory():
        return DummyWorker(exit_code)
    return factory


class TestWorkerPool:
    def test_start_creates_workers(self):
        pool = WorkerPool(n_workers=3, worker_factory=dummy_worker_factory(), worker_timeout=1.0)
        pool.start()
        assert len(pool._workers) == 3
        assert all(p.is_alive() for p in pool._workers)
        pool.cleanup()

    def test_stop_joins_workers(self):
        pool = WorkerPool(n_workers=2, worker_factory=dummy_worker_factory(), worker_timeout=1.0)
        pool.start()
        time.sleep(0.2)  # Let workers finish
        pool.stop()
        assert all(not p.is_alive() for p in pool._workers)

    def test_cleanup_terminates_workers(self):
        pool = WorkerPool(n_workers=2, worker_factory=dummy_worker_factory(), worker_timeout=1.0)
        pool.start()
        time.sleep(0.05)  # Let workers start
        pool.cleanup()
        assert all(not p.is_alive() for p in pool._workers)
        assert len(pool._workers) == 0
        assert not pool._started

    def test_restart_dead_restarts_workers(self):
        pool = WorkerPool(n_workers=3, worker_factory=dummy_worker_factory(), worker_timeout=1.0)
        pool.start()
        time.sleep(0.2)  # Let workers finish
        dead_count = pool.restart_dead()
        assert dead_count == 3  # All should be dead
        assert len(pool._workers) == 3
        assert all(p.is_alive() for p in pool._workers)
        pool.cleanup()

    def test_fatal_errors_collects_errors(self):
        pool = WorkerPool(n_workers=2, worker_factory=dummy_worker_factory(exit_code=1), worker_timeout=1.0)
        pool.start()
        time.sleep(0.2)  # Let workers exit
        errors = pool.fatal_errors()
        assert len(errors) == 2
        for error in errors:
            assert isinstance(error, WorkerFatalError)
            assert error.exitcode == 1

    def test_start_already_started_raises(self):
        pool = WorkerPool(n_workers=1, worker_factory=dummy_worker_factory(), worker_timeout=1.0)
        pool.start()
        with pytest.raises(RuntimeError, match="WorkerPool already started"):
            pool.start()
        pool.cleanup()