# Python Batch Processing – Efficient Multiprocessing Library

**Python Batch Processing** is a robust and efficient batch processing library for Python that leverages multiprocessing and asynchronous programming to handle large-scale data processing tasks. This library provides a high-level API for distributing work across multiple worker processes, with built-in monitoring and error handling capabilities.

## Features

- **Multiprocessing Support**: Utilizes Python's multiprocessing module to run tasks in separate processes, maximizing CPU utilization.
- **Asynchronous Processing**: Supports async/await patterns for non-blocking operations.
- **Worker Pool Management**: Automatically manages a pool of worker processes with restart capabilities.
- **Monitoring System**: Includes a monitoring thread that watches for worker failures and can restart dead workers or abort on critical errors.
- **Flexible Error Handling**: Configurable failure policies (IGNORE, ABORT, RESTART) for worker exceptions and deaths.
- **Iterable Batch Processing**: Process large iterables in batches with concurrent queuing and result collection.
- **Context Manager Support**: Easy setup and teardown with Python's context manager protocol.
- **Type Safety**: Full type hints for better IDE support and code reliability.

## Installation

You can install directly from GitHub using pip:

```bash
pip install git+https://github.com/LuisGrigore/python-batch-processing.git
```

### Requirements

- Python ≥ 3.8

### Dependencies

### Running

| Name | Version used |
|------|--------------|
| (No external dependencies) | - |

### Development

| Name | Version used |
|------|--------------|
| pytest | 9.0.2 |
| iniconfig | 2.3.0 |
| packaging | 25.0 |
| pluggy | 1.6.0 |
| Pygments | 2.19.2 |

## Usage – Synchronous Mode

### Basic Batch Processing

```python
from batch_processing.batch_processor import BatchProcessor
from batch_processing.worker_pool import WorkerPool
from batch_processing.monitor import WorkerMonitor
from batch_processing.batch_processor.context import BatchProcessorContext
from batch_processing.batch_processor.configuration import ProcessorConfig
from batch_processing.context import ControlContext
from batch_processing.configuration import FailurePolicy, SharedConfig

# Define your worker function
def process_item(item):
    return item * 2

# Create a worker factory
def worker_factory():
    return process_item

# Set up components
pool = WorkerPool(n_workers=4, worker_factory=worker_factory, worker_timeout=10.0)
config = ProcessorConfig(shared=SharedConfig(), on_worker_exception=FailurePolicy.ABORT)
control_ctx = ControlContext()
ctx = BatchProcessorContext(config, control_ctx)
monitor = WorkerMonitor(pool, ctx)

processor = BatchProcessor(pool, monitor, ctx)

# Process items
with processor:
    processor.put("item1")
    processor.put("item2")
    result1 = processor.get()
    result2 = processor.get()
```

## Usage – Asynchronous Mode

### Iterable Batch Processing

```python
import asyncio
from batch_processing.iterable_batch_processor import IterableBatchProcessor
from batch_processing.batch_processor import BatchProcessor
from batch_processing.worker_pool import WorkerPool
from batch_processing.monitor import WorkerMonitor
from batch_processing.batch_processor.context import BatchProcessorContext
from batch_processing.batch_processor.configuration import ProcessorConfig
from batch_processing.context import ControlContext
from batch_processing.configuration import FailurePolicy, SharedConfig

async def main():
    # Define your worker function
    def process_item(item):
        return item * 2

    # Create a worker factory
    def worker_factory():
        return process_item

    # Set up components
    pool = WorkerPool(n_workers=4, worker_factory=worker_factory, worker_timeout=10.0)
    config = ProcessorConfig(shared=SharedConfig(), on_worker_exception=FailurePolicy.ABORT)
    control_ctx = ControlContext()
    ctx = BatchProcessorContext(config, control_ctx)
    monitor = WorkerMonitor(pool, ctx)

    processor = BatchProcessor(pool, monitor, ctx)

    # Process iterable
    iterable_processor = IterableBatchProcessor(processor, ["item1", "item2", "item3"], n_items=2)
    results = await iterable_processor.process()
    print(results)  # ["processed_item1", "processed_item2"]

asyncio.run(main())
```

## API

### Main Classes and Methods

| Class | Method | Description |
|-------|--------|------------|
| `BatchProcessor` | `put(item)` | Submits an item for processing. |
|  | `get()` | Retrieves a processed result. |
|  | `close()` | Releases resources. |
| `IterableBatchProcessor` | `process()` | Processes an iterable asynchronously and returns results. |
| `WorkerPool` | `start()` | Starts the worker pool. |
|  | `stop()` | Stops the worker pool. |
| `WorkerMonitor` | `start()` | Starts monitoring workers. |
|  | `stop()` | Stops monitoring. |
| `BatchProcessorContext` | - | Context for batch processing configuration. |
| `ProcessorConfig` | - | Configuration for the processor. |
| `ControlContext` | - | Control context for shared state. |
| `SharedConfig` | - | Shared configuration options. |

## Best Practices

- Always **close the processor** after use:

```python
processor.close()
```

- Configure **failure policies** appropriately for your use case (IGNORE, ABORT, RESTART).
- Use **context managers** for automatic resource management.
- Monitor worker **timeouts** and adjust based on your processing needs.
- For large iterables, use `IterableBatchProcessor` for efficient asynchronous processing.