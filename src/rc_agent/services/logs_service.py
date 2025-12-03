"""Service for accessing job logs data."""

import json
from typing import Optional
from pathlib import Path
from rc_agent.config.settings import settings


class LogsService:
    """Service for retrieving job execution logs."""

    def __init__(self, data_file: Optional[Path] = None):
        """
        Initialize the logs service.

        Args:
            data_file: Path to logs data file. Defaults to settings.data_dir/log.json
        """
        self.data_file = data_file or settings.data_dir / "log.json"

    def get_job_logs(self, job_id: str) -> dict:
        """
        Retrieve the execution logs for a specific job.

        Args:
            job_id: The job ID to retrieve logs for (e.g., 'job-789')

        Returns:
            dict: Job logs information with keys:
                - found (bool): Whether logs were found for the job
                - job_id (str): The job ID if found
                - logs (list): List of log lines if found
                - error/message (str): Error or informational message if not found
        """
        try:
            with open(self.data_file, 'r') as f:
                all_logs = json.load(f)
        except FileNotFoundError:
            return {
                "found": False,
                "error": f"Logs data file not found: {self.data_file}"
            }
        except json.JSONDecodeError as e:
            return {
                "found": False,
                "error": f"Invalid JSON in logs data file: {e}"
            }

        # Look up the job logs
        if job_id in all_logs:
            logs = all_logs[job_id]
            return {
                "found": True,
                "job_id": job_id,
                "logs": logs
            }

        # Job not found
        return {
            "found": False,
            "message": f"No logs found for job '{job_id}'"
        }

    def list_all_job_ids(self) -> list:
        """
        List all available job IDs.

        Returns:
            list: List of all job IDs that have logs
        """
        try:
            with open(self.data_file, 'r') as f:
                all_logs = json.load(f)
                return list(all_logs.keys())
        except (FileNotFoundError, json.JSONDecodeError):
            return []
