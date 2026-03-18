from __future__ import annotations

import json
import os
import time
from collections.abc import Iterable
from pathlib import Path

from dotenv import load_dotenv

from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient, record_subject_name_strategy
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.serialization import StringSerializer


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"


def load_settings() -> dict[str, str]:
    load_dotenv(REPO_ROOT / ".env")
    settings = {
        "bootstrap.servers": require_env("KAFKA_BOOTSTRAP_SERVERS"),
        "sasl.username": require_env("KAFKA_API_KEY"),
        "sasl.password": require_env("KAFKA_API_SECRET"),
        "schema.registry.url": require_env("SCHEMA_REGISTRY_URL"),
        "schema.registry.key": require_env("SCHEMA_REGISTRY_API_KEY"),
        "schema.registry.secret": require_env("SCHEMA_REGISTRY_API_SECRET"),
    }
    return settings


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def load_schema(schema_file: str) -> str:
    return (SCHEMA_DIR / schema_file).read_text(encoding="utf-8")


def build_producer(schema_file: str) -> SerializingProducer:
    settings = load_settings()
    schema_registry = SchemaRegistryClient(
        {
            "url": settings["schema.registry.url"],
            "basic.auth.user.info": (
                f"{settings['schema.registry.key']}:{settings['schema.registry.secret']}"
            ),
        }
    )
    serializer = JSONSerializer(
        load_schema(schema_file),
        schema_registry,
        lambda payload, _: payload,
        conf={
            "auto.register.schemas": False,
            "use.latest.version": True,
            "subject.name.strategy": record_subject_name_strategy,
        },
    )
    return SerializingProducer(
        {
            "bootstrap.servers": settings["bootstrap.servers"],
            "security.protocol": "SASL_SSL",
            "sasl.mechanism": "PLAIN",
            "sasl.username": settings["sasl.username"],
            "sasl.password": settings["sasl.password"],
            "client.id": "claimshield-producer",
            "acks": "all",
            "key.serializer": StringSerializer("utf_8"),
            "value.serializer": serializer,
        }
    )


def produce_records(
    *,
    topic: str,
    schema_file: str,
    records: Iterable[dict],
    key_field: str,
    sleep_seconds: float = 0.0,
) -> None:
    producer = build_producer(schema_file)
    delivered = 0

    def on_delivery(err, msg) -> None:
        nonlocal delivered
        if err is not None:
            raise RuntimeError(f"Failed to deliver message to {topic}: {err}")
        delivered += 1
        print(
            json.dumps(
                {
                    "topic": msg.topic(),
                    "partition": msg.partition(),
                    "offset": msg.offset(),
                    "key": msg.key().decode("utf-8") if msg.key() else None,
                }
            )
        )

    for record in records:
        producer.produce(
            topic=topic,
            key=str(record[key_field]),
            value=record,
            on_delivery=on_delivery,
        )
        producer.poll(0)
        if sleep_seconds:
            time.sleep(sleep_seconds)

    producer.flush()
    print(f"Delivered {delivered} record(s) to {topic}.")


def produce_record_batches(
    *,
    topic: str,
    schema_file: str,
    batches: Iterable[Iterable[dict]],
    key_field: str,
    sleep_seconds: float = 0.0,
    batch_interval_seconds: float = 0.0,
) -> None:
    producer = build_producer(schema_file)
    delivered = 0
    batch_count = 0

    def on_delivery(err, msg) -> None:
        nonlocal delivered
        if err is not None:
            raise RuntimeError(f"Failed to deliver message to {topic}: {err}")
        delivered += 1

    try:
        for batch_count, records in enumerate(batches, start=1):
            batch_records = list(records)
            if not batch_records:
                continue
            for record in batch_records:
                producer.produce(
                    topic=topic,
                    key=str(record[key_field]),
                    value=record,
                    on_delivery=on_delivery,
                )
                producer.poll(0)
                if sleep_seconds:
                    time.sleep(sleep_seconds)
            producer.flush()
            print(
                json.dumps(
                    {
                        "topic": topic,
                        "batch": batch_count,
                        "records": len(batch_records),
                        "delivered_total": delivered,
                    }
                )
            )
            if batch_interval_seconds:
                time.sleep(batch_interval_seconds)
    finally:
        producer.flush()

    print(
        f"Delivered {delivered} record(s) to {topic} across {batch_count} batch(es)."
    )
