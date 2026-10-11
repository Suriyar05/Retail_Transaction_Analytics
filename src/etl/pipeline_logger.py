from datetime import datetime

from sqlalchemy import text

from src.api.database import engine


def start_pipeline_run(pipeline_name: str) -> int:
    """
    Creates a new pipeline run record and returns its run_id.
    """

    query = text("""
        INSERT INTO pipeline_runs (
            pipeline_name,
            start_time,
            status
        )
        VALUES (
            :pipeline_name,
            :start_time,
            :status
        )
    """)

    with engine.begin() as connection:

        result = connection.execute(
            query,
            {
                "pipeline_name": pipeline_name,
                "start_time": datetime.now(),
                "status": "RUNNING"
            }
        )

        return result.lastrowid


def complete_pipeline_run(
    run_id: int,
    records_read: int,
    records_inserted: int,
    records_rejected: int = 0
):
    """
    Marks a pipeline run as successfully completed.
    """

    query = text("""
        UPDATE pipeline_runs
        SET
            end_time = :end_time,
            status = :status,
            records_read = :records_read,
            records_inserted = :records_inserted,
            records_rejected = :records_rejected
        WHERE run_id = :run_id
    """)

    with engine.begin() as connection:

        connection.execute(
            query,
            {
                "run_id": run_id,
                "end_time": datetime.now(),
                "status": "SUCCESS",
                "records_read": records_read,
                "records_inserted": records_inserted,
                "records_rejected": records_rejected
            }
        )


def fail_pipeline_run(
    run_id: int,
    error_message: str
):
    """
    Marks a pipeline run as failed.
    """

    query = text("""
        UPDATE pipeline_runs
        SET
            end_time = :end_time,
            status = :status,
            error_message = :error_message
        WHERE run_id = :run_id
    """)

    with engine.begin() as connection:

        connection.execute(
            query,
            {
                "run_id": run_id,
                "end_time": datetime.now(),
                "status": "FAILED",
                "error_message": error_message
            }
        )