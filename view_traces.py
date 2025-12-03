#!/usr/bin/env python
"""
Utility to view and analyze traces from the traces/ directory.

Usage:
    python view_traces.py                    # Show latest trace
    python view_traces.py --summary          # Show summary only
    python view_traces.py --file traces/trace_20231129_143022.jsonl
    python view_traces.py --last 5           # Show last 5 spans
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict


def parse_timestamp(ts_str: str) -> datetime:
    """Parse OpenTelemetry timestamp."""
    return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))


def format_duration(start: str, end: str) -> str:
    """Calculate and format duration."""
    start_dt = parse_timestamp(start)
    end_dt = parse_timestamp(end)
    duration = (end_dt - start_dt).total_seconds()

    if duration < 1:
        return f"{duration*1000:.0f}ms"
    return f"{duration:.2f}s"


def print_span_summary(span: Dict, indent: int = 0):
    """Print a concise summary of a span."""
    prefix = "  " * indent
    name = span.get("name", "unknown")

    start = span.get("start_time", "")
    end = span.get("end_time", "")
    duration = format_duration(start, end) if start and end else "?"

    attrs = span.get("attributes", {})

    # Determine span type
    if "invoke_agent" in name:
        print(f"{prefix}🤖 {name} ({duration})")
        if tokens_in := attrs.get("gen_ai.usage.input_tokens"):
            tokens_out = attrs.get("gen_ai.usage.output_tokens")
            print(f"{prefix}   Tokens: {tokens_in} in, {tokens_out} out")

    elif "chat" in name:
        model = attrs.get("gen_ai.request.model", "unknown")
        print(f"{prefix}💬 {name} ({duration})")
        print(f"{prefix}   Model: {model}")
        if tokens_in := attrs.get("gen_ai.usage.input_tokens"):
            tokens_out = attrs.get("gen_ai.usage.output_tokens")
            print(f"{prefix}   Tokens: {tokens_in} in, {tokens_out} out")

    elif "tool" in name.lower():
        print(f"{prefix}🔧 {name} ({duration})")
        if tool_input := attrs.get("gen_ai.tool.input"):
            print(f"{prefix}   Input: {tool_input[:80]}...")

    else:
        print(f"{prefix}📝 {name} ({duration})")


def load_traces(file_path: Path) -> List[Dict]:
    """Load all traces from the file (handles multi-line JSON objects)."""
    traces = []

    if not file_path.exists():
        print(f"❌ Trace file not found: {file_path}")
        return traces

    with open(file_path, 'r') as f:
        content = f.read()

    # Parse multi-line JSON objects (not strict JSONL)
    depth = 0
    start_pos = None

    for i, char in enumerate(content):
        if char == '{':
            if depth == 0:
                start_pos = i
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0 and start_pos is not None:
                try:
                    obj = json.loads(content[start_pos:i+1])
                    # Filter out metrics objects, only keep trace spans
                    if obj.get("name") and obj.get("context"):
                        traces.append(obj)
                except json.JSONDecodeError:
                    pass
                start_pos = None

    return traces


def show_summary(traces: List[Dict]):
    """Show a summary of all traces."""
    print("\n📊 Trace Summary")
    print("=" * 60)
    print(f"Total spans: {len(traces)}")

    # Count by type
    agent_calls = sum(1 for t in traces if "invoke_agent" in t.get("name", ""))
    llm_calls = sum(1 for t in traces if "chat" in t.get("name", ""))
    tool_calls = sum(1 for t in traces if "tool" in t.get("name", "").lower())

    print(f"Agent invocations: {agent_calls}")
    print(f"LLM calls: {llm_calls}")
    print(f"Tool calls: {tool_calls}")

    # Total tokens
    total_in = sum(t.get("attributes", {}).get(
        "gen_ai.usage.input_tokens", 0) for t in traces)
    total_out = sum(t.get("attributes", {}).get(
        "gen_ai.usage.output_tokens", 0) for t in traces)

    if total_in or total_out:
        print(f"\nTotal tokens: {total_in} in, {total_out} out")

    print()


def main():
    parser = argparse.ArgumentParser(description="View OpenTelemetry traces")
    parser.add_argument(
        "--file", help="Path to specific trace file (default: latest in traces/)")
    parser.add_argument("--last", type=int, help="Show only last N traces")
    parser.add_argument("--summary", action="store_true",
                        help="Show summary only")
    parser.add_argument("--tools-only", action="store_true",
                        help="Show only tool calls")

    args = parser.parse_args()

    # Determine which file to read
    if args.file:
        file_path = Path(args.file)
    else:
        # Find the latest trace file in traces/ directory
        traces_dir = Path("traces")
        if not traces_dir.exists():
            print("❌ No traces directory found. Run the CLI first to generate traces.")
            return

        trace_files = sorted(traces_dir.glob("trace_*.jsonl"), reverse=True)
        if not trace_files:
            print("❌ No trace files found in traces/ directory.")
            return

        file_path = trace_files[0]
        print(f"📁 Reading latest trace file: {file_path}\n")

    # Load traces
    traces = load_traces(file_path)

    if not traces:
        print("No traces found.")
        return

    # Show summary
    if args.summary:
        show_summary(traces)
        return

    # Filter traces
    if args.tools_only:
        traces = [t for t in traces if "tool" in t.get("name", "").lower()]

    if args.last:
        traces = traces[-args.last:]

    # Show summary first
    show_summary(traces)

    # Show individual traces
    print("📋 Traces")
    print("=" * 60)

    # Group by trace_id
    by_trace = {}
    for span in traces:
        trace_id = span.get("context", {}).get("trace_id", "unknown")
        if trace_id not in by_trace:
            by_trace[trace_id] = []
        by_trace[trace_id].append(span)

    # Print each trace
    for i, (trace_id, spans) in enumerate(by_trace.items(), 1):
        print(f"\nTrace {i}: {trace_id}")
        print("-" * 60)

        # Sort spans by parent relationship
        root_spans = [s for s in spans if s.get("parent_id") is None]
        child_spans = [s for s in spans if s.get("parent_id") is not None]

        for root in root_spans:
            print_span_summary(root, indent=0)

            # Find and print children
            root_span_id = root.get("context", {}).get("span_id")
            for child in child_spans:
                if child.get("parent_id") == root_span_id:
                    print_span_summary(child, indent=1)

    print()


if __name__ == "__main__":
    main()
