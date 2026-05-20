import dlt
import time
from datetime import datetime
from dlt.sources.filesystem import filesystem, read_jsonl

POLL_INTERVAL = 5


def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def bucket_to_iceberg() -> None:
    """Continuously poll MinIO events and ingest new event files into Iceberg tables"""
    pipeline = dlt.pipeline(
        pipeline_name="bucket_to_iceberg",
        destination="filesystem",
        dataset_name="events",
    )

    print(f"[{_ts()}] polling s3://events/**/*.jsonl every {POLL_INTERVAL}s — Ctrl+C to stop")

    while True:
        source = (
            filesystem(
                bucket_url="s3://events",
                file_glob="**/*.jsonl",
                incremental=dlt.sources.incremental("modification_date"),
            )
            | read_jsonl()
        )

        load_info = pipeline.run(source, table_name="events", table_format="iceberg")

        n = sum(len(pkg.jobs.get("completed_jobs", [])) for pkg in load_info.load_packages)
        if n:
            label = "file" if n == 1 else "files"
            print(f"\r[{_ts()}] {n} {label} ingested → iceberg.events")
        else:
            print(f"\r[{_ts()}] waiting for new files...", end="", flush=True)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    bucket_to_iceberg()