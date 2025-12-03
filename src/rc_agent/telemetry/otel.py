"""OpenTelemetry tracing setup for the Release Copilot agent.

This module provides initialization of OpenTelemetry tracing for CLI-based
agent applications using Microsoft Agent Framework.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource

# Global flag to track if tracing has been initialized
_tracing_initialized = False


def init_tracing(
    output_file: Optional[str] = None,
    enable_console: bool = False
) -> trace.Tracer:
    """
    Initialize OpenTelemetry tracing with file and/or console output.

    This function sets up:
    - A TracerProvider with service.name resource attribute
    - File exporter for writing traces to a local JSONL file (default)
    - Optional ConsoleSpanExporter for outputting traces to stdout
    - BatchSpanProcessor for efficient span processing
    - Integration with Microsoft Agent Framework observability

    The function is idempotent - calling it multiple times will not
    re-initialize the tracing infrastructure.

    Args:
        output_file: Path to write traces to. If None, a timestamped file will be 
                    created in the traces/ directory (e.g., traces/trace_20231129_143022.jsonl).
        enable_console: Whether to also output traces to console. Default False.

    Returns:
        trace.Tracer: A tracer instance for the release-copilot-agent service

    Example:
        >>> from rc_agent.telemetry import init_tracing
        >>> # Write to timestamped file in traces/ (default)
        >>> tracer = init_tracing()
        >>> 
        >>> # Write to both file and console
        >>> tracer = init_tracing(enable_console=True)
        >>> 
        >>> # Write to custom file location
        >>> tracer = init_tracing(output_file="logs/my_trace.jsonl")
    """
    global _tracing_initialized

    if _tracing_initialized:
        # Already initialized, just return a tracer
        return trace.get_tracer("release-copilot-agent")

    # Create our TracerProvider FIRST before calling setup_observability
    resource = Resource.create({"service.name": "release-copilot-agent"})
    provider = TracerProvider(resource=resource)

    # Determine output file path
    if output_file is None:
        # Create timestamped file in traces/ directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        traces_dir = Path("traces")
        traces_dir.mkdir(exist_ok=True)
        file_path = traces_dir / f"trace_{timestamp}.jsonl"
    else:
        file_path = Path(output_file)
        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

    # Open file in write mode (keep reference to prevent closing)
    file_handle = open(file_path, "w", encoding="utf-8")
    file_exporter = ConsoleSpanExporter(out=file_handle)
    file_processor = BatchSpanProcessor(file_exporter)
    provider.add_span_processor(file_processor)
    print(f"✓ Traces will be written to: {file_path.absolute()}")

    # Add console exporter if enabled
    if enable_console:
        console_exporter = ConsoleSpanExporter()
        console_processor = BatchSpanProcessor(console_exporter)
        provider.add_span_processor(console_processor)
        print("✓ Traces will also be written to console")

    # Set the global tracer provider BEFORE calling setup_observability
    trace.set_tracer_provider(provider)

    # Now enable Agent Framework observability
    # Suppress metrics console output by redirecting to a persistent devnull
    try:
        from agent_framework.observability import setup_observability

        # Save current stdout/stderr
        old_stdout, old_stderr = sys.stdout, sys.stderr

        # Create a persistent devnull that won't be closed
        # This prevents "I/O operation on closed file" errors
        devnull = open(os.devnull, 'w')
        sys.stdout = sys.stderr = devnull

        # Call setup_observability (it will capture the devnull file handles)
        setup_observability(enable_sensitive_data=True)

        # Restore stdout/stderr (but don't close devnull - it's still in use)
        sys.stdout, sys.stderr = old_stdout, old_stderr
    except ImportError:
        # If agent_framework.observability is not available, that's okay
        pass

    # Mark as initialized
    _tracing_initialized = True

    # Return a tracer instance
    return trace.get_tracer("release-copilot-agent")
