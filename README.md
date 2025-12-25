# Python Batch Processing

A robust and efficient batch processing library for Python that leverages multiprocessing and asynchronous programming to handle large-scale data processing tasks. This library provides a high-level API for distributing work across multiple worker processes, with built-in monitoring and error handling capabilities.

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

### Prerequisites

- Python 3.8 or higher
- pip for package management

### From Source (Local Development)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/python-batch-processing.git
   cd python-batch-processing
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install the package locally:
   ```bash
   pip install -e .
   ```

### Usage in Other Projects

Once installed, you can import and use the package in your projects:

```python
from batch_processing import BatchProcessor, WorkerPool, WorkerMonitor, BatchProcessorContext, ProcessorConfig, ControlContext, FailurePolicy, SharedConfig

# Define your worker function
def process_item(item):
    return item * 2

# Create worker factory
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

## Usage

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
    # Your processing logic here
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

### Iterable Batch Processing

```python
import asyncio
from batch_processing.iterable_batch_processor import IterableBatchProcessor

async def main():
    # Assuming processor is set up as above
    iterable_processor = IterableBatchProcessor(processor, ["item1", "item2", "item3"], n_items=2)
    results = await iterable_processor.process()
    print(results)  # ["processed_item1", "processed_item2"]

asyncio.run(main())
```

### Configuration

```python
from batch_processing.configuration import FailurePolicy, SharedConfig
from batch_processing.monitor.configuration import MonitorConfig
from batch_processing.batch_processor.configuration import BatchProcessorConfig

# Shared configuration
shared_config = SharedConfig(logging=True)

# Monitor configuration
monitor_config = MonitorConfig(
    shared=shared_config,
    on_worker_death=FailurePolicy.RESTART,
    worker_monitoring_frequency=2.0
)

# Batch processor configuration
batch_config = BatchProcessorConfig(
    on_worker_exception=FailurePolicy.ABORT,
    on_worker_death=FailurePolicy.RESTART,
    worker_monitoring_frequency=2.0,
    logging=True,
    worker_timeout=30.0
)
```

## API Reference

### Core Classes

- `WorkerPool`: Manages a pool of worker processes.
- `WorkerMonitor`: Monitors worker health and handles failures.
- `BatchProcessor`: High-level interface for batch processing with context management.
- `IterableBatchProcessor`: Processes large iterables in batches asynchronously.

### Configuration Classes

- `SharedConfig`: Common configuration options.
- `MonitorConfig`: Monitor-specific settings.
- `ProcessorConfig`: Batch processor settings.
- `BatchProcessorConfig`: Combined configuration for full setup.

### Enums

- `FailurePolicy`: Defines how to handle failures (IGNORE, ABORT, RESTART).

## Testing

Run the test suite using pytest:

```bash
python -m pytest tests/
```

The project includes comprehensive unit tests covering all major components.

## Architecture

The library is structured around several key components:

1. **Worker Pool**: Manages process lifecycle and communication.
2. **Monitor**: Watches for process failures and applies configured policies.
3. **Batch Processor**: Provides a clean API for submitting work and retrieving results.
4. **Queues**: Uses multiprocessing-safe queues for inter-process communication.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure all tests pass and add tests for new features.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python's multiprocessing and asyncio modules
- Inspired by the need for efficient batch processing in data-intensive applications