import json
import random
import time
import uuid
from datetime import timedelta

import boto3
from botocore.config import Config

from constants import (
    BATCH_SIZE,
    BASE_TIME,
    BUCKET,
    DELAY,
    MINIO_ACCESS_KEY,
    MINIO_ENDPOINT,
    MINIO_REGION,
    MINIO_SECRET_KEY,
    PAGES,
    TOTAL_EVENTS,
    TRACK_EVENTS,
    USER_AGENTS,
    USERS,
)

def create_event(seq: int) -> dict:
    """Generate events and stream them to MinIO in batches"""
    ts = BASE_TIME + timedelta(seconds=seq * 3)
    ts_str = ts.strftime("%Y-%m-%dT%H:%M:%S") + f".{random.randint(0, 999):03d}Z"

    user = random.choice(USERS)
    etype = random.choices(["track", "identify", "page"], weights=[70, 15, 15])[0]

    evt: dict = {
        "messageId": str(uuid.uuid4()),
        "type": etype,
        "userId": user,
        "anonymousId": f"anon_{uuid.uuid4().hex[:12]}",
        "timestamp": ts_str,
        "sentAt": ts_str,
        "receivedAt": ts_str,
        "context": {
            "library": {"name": "analytics.js", "version": "2.11.1"},
            "userAgent": random.choice(USER_AGENTS),
            "ip": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
            "locale": random.choice(["en-US", "en-GB", "de-DE", "fr-FR", "es-ES", "it-IT", "pt-BR"]),
        },
    }

    if etype == "track":
        name, props_fn = random.choice(TRACK_EVENTS)
        evt["event"] = name
        evt["properties"] = props_fn()
    elif etype == "identify":
        evt["traits"] = {
            "email": f"{user}@example.com",
            "name": f"User {user[-4:]}",
            "plan": random.choice(["free", "pro", "enterprise"]),
            "company": random.choice(["Acme Corp", "Globex", "Initech", "Umbrella", "Stark Industries"]),
            "created_at": "2023-01-01T00:00:00Z",
        }
    else:
        page = random.choice(PAGES)
        slug = page.lower().replace(" ", "-")
        evt["name"] = page
        evt["properties"] = {
            "url": f"https://app.example.com/{slug}",
            "title": f"{page} | ExampleApp",
            "path": f"/{slug}",
            "referrer": random.choice(["", "https://google.com", "https://twitter.com", "https://app.example.com"]),
        }

    return evt


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name=MINIO_REGION,
        config=Config(signature_version="s3v4"),
    )


def main() -> None:
    s3 = get_s3_client()
    total_batches = (TOTAL_EVENTS + BATCH_SIZE - 1) // BATCH_SIZE

    print(f"Generating {TOTAL_EVENTS:,} events → {total_batches} files of {BATCH_SIZE:,} in s3://{BUCKET}")
    print(f"Delay: {DELAY}s/batch  ETA: ~{total_batches * DELAY:.0f}s")
    print()

    overall_start = time.time()

    for batch_idx in range(total_batches):
        offset = batch_idx * BATCH_SIZE
        count = min(BATCH_SIZE, TOTAL_EVENTS - offset)

        body = "\n".join(json.dumps(create_event(offset + i)) for i in range(count)).encode()
        key = f"{BASE_TIME.strftime('%Y/%m/%d')}/batch-{batch_idx:04d}.jsonl"

        s3.put_object(Bucket=BUCKET, Key=key, Body=body)

        elapsed = time.time() - overall_start
        pct = (batch_idx + 1) / total_batches * 100
        print(f"[{elapsed:6.1f}s] {pct:5.1f}%  batch {batch_idx+1:4d}/{total_batches}  {key}  ({count:,} events, {len(body):,} B)")

        if DELAY > 0 and batch_idx < total_batches - 1:
            time.sleep(DELAY)

    total_elapsed = time.time() - overall_start
    print(f"\nDone: {TOTAL_EVENTS:,} events in {total_elapsed:.1f}s ({TOTAL_EVENTS / total_elapsed:,.0f} events/s)")


if __name__ == "__main__":
    main()