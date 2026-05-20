import os
import random
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "docker" / ".env")

BUCKET = "events"
TOTAL_EVENTS = 100_000
BATCH_SIZE = 1_000
DELAY = 0.5
BASE_TIME = datetime(2026, 1, 1, 0, 0, 0)

MINIO_ENDPOINT = os.environ["MINIO_HOST_ENDPOINT"]
MINIO_ACCESS_KEY = os.environ["MINIO_ROOT_USER"]
MINIO_SECRET_KEY = os.environ["MINIO_ROOT_PASSWORD"]
MINIO_REGION = os.environ["MINIO_REGION_NAME"]

USERS = [f"user_{i:04d}" for i in range(1, 5001)]

TRACK_EVENTS = [
    ("Page Viewed", lambda: {"url": random.choice(["/home", "/dashboard", "/pricing", "/blog", "/settings", "/docs"]), "referrer": random.choice(["https://google.com", "direct", "https://twitter.com", ""])}),
    ("Button Clicked", lambda: {"button": random.choice(["signup", "login", "upgrade", "contact", "demo", "cta"])}),
    ("Form Submitted", lambda: {"form_id": random.choice(["contact", "signup", "newsletter", "checkout", "feedback"])}),
    ("Purchase Completed", lambda: {"revenue": round(random.uniform(9.99, 999.99), 2), "currency": random.choice(["USD", "EUR", "GBP"]), "product_id": random.randint(1, 50)}),
    ("Searched", lambda: {"query": random.choice(["pricing", "features", "docs", "api", "integrations", "support"]), "results_count": random.randint(0, 100)}),
    ("Product Viewed", lambda: {"product_id": random.randint(1, 200), "category": random.choice(["analytics", "marketing", "data", "automation"])}),
    ("Added to Cart", lambda: {"product_id": random.randint(1, 200), "quantity": random.randint(1, 5), "price": round(random.uniform(9.99, 499.99), 2)}),
    ("Signed Up", lambda: {"plan": random.choice(["free", "pro", "enterprise"]), "source": random.choice(["organic", "paid", "referral"])}),
    ("Logged In", lambda: {"method": random.choice(["email", "google", "github", "sso"])}),
    ("Logged Out", lambda: {}),
    ("Subscription Started", lambda: {"plan": random.choice(["pro", "enterprise"]), "billing_cycle": random.choice(["monthly", "annual"])}),
    ("Feature Used", lambda: {"feature": random.choice(["dashboard", "reports", "integrations", "api", "webhooks"])}),
]

PAGES = ["Home", "Dashboard", "Settings", "Pricing", "Blog", "Docs", "Integrations", "API Reference"]

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36",
]