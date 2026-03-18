from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from confluent_kafka import Consumer, KafkaError, TopicPartition
from dotenv import load_dotenv
from openai import OpenAI


DERIVED_TOPICS = [
    "claims.enriched.curated",
    "claims.risk.alerts",
    "claims.sla.breaches",
    "providers.risk.scores",
]

COPILOT_DEFAULT_MODEL = "gpt-5-mini"
REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = REPO_ROOT / ".env"


@dataclass
class KafkaSettings:
    bootstrap_servers: str
    api_key: str
    api_secret: str


@dataclass
class CopilotSettings:
    api_key: str
    model: str


def load_settings() -> KafkaSettings:
    load_dotenv(ENV_FILE, override=True)
    return KafkaSettings(
        bootstrap_servers=require_env("KAFKA_BOOTSTRAP_SERVERS"),
        api_key=require_env("KAFKA_API_KEY"),
        api_secret=require_env("KAFKA_API_SECRET"),
    )


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def optional_env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def build_consumer(settings: KafkaSettings) -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": settings.bootstrap_servers,
            "security.protocol": "SASL_SSL",
            "sasl.mechanism": "PLAIN",
            "sasl.username": settings.api_key,
            "sasl.password": settings.api_secret,
            "group.id": f"claimshield-dashboard-{uuid.uuid4()}",
            "auto.offset.reset": "latest",
            "enable.auto.commit": False,
            "session.timeout.ms": 6000,
        }
    )


def load_copilot_settings() -> CopilotSettings | None:
    load_dotenv(ENV_FILE, override=True)
    api_key = optional_env("OPENAI_API_KEY")
    if not api_key:
        return None
    model = optional_env("CLAIMSHIELD_COPILOT_MODEL", COPILOT_DEFAULT_MODEL) or COPILOT_DEFAULT_MODEL
    return CopilotSettings(api_key=api_key, model=model)


def decode_confluent_payload(raw_value: bytes | None) -> dict[str, Any] | None:
    if raw_value is None:
        return None
    if len(raw_value) < 6 or raw_value[0] != 0:
        return None
    try:
        payload = raw_value[5:].decode("utf-8")
        return json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def fetch_recent_records(
    consumer: Consumer,
    topic: str,
    max_records: int = 50,
    poll_timeout: float = 0.5,
) -> list[dict[str, Any]]:
    metadata = consumer.list_topics(topic=topic, timeout=10)
    if topic not in metadata.topics:
        return []

    partitions = sorted(metadata.topics[topic].partitions.keys())
    assignments: list[TopicPartition] = []

    for partition in partitions:
        low, high = consumer.get_watermark_offsets(
            TopicPartition(topic, partition),
            timeout=10,
        )
        start = max(low, high - max_records)
        assignments.append(TopicPartition(topic, partition, start))

    consumer.assign(assignments)

    records: list[dict[str, Any]] = []
    empty_polls = 0
    while empty_polls < 3 and len(records) < max_records * max(1, len(partitions)):
        message = consumer.poll(poll_timeout)
        if message is None:
            empty_polls += 1
            continue
        if message.error():
            if message.error().code() == KafkaError._PARTITION_EOF:
                empty_polls += 1
                continue
            raise RuntimeError(message.error().str())

        payload = decode_confluent_payload(message.value())
        if payload is None:
            continue

        records.append(
            {
                **payload,
                "_topic": message.topic(),
                "_partition": message.partition(),
                "_offset": message.offset(),
                "_key": message.key().decode("utf-8") if message.key() else None,
            }
        )

    consumer.unassign()
    return records


@st.cache_data(ttl=10, show_spinner=False)
def load_dashboard_data() -> dict[str, pd.DataFrame]:
    settings = load_settings()
    consumer = build_consumer(settings)
    try:
        frames: dict[str, pd.DataFrame] = {}
        for topic in DERIVED_TOPICS:
            records = fetch_recent_records(consumer, topic)
            frames[topic] = pd.DataFrame(records)
        return frames
    finally:
        consumer.close()


def metric_value(df: pd.DataFrame, column: str | None = None, high_risk: bool = False) -> int:
    if df.empty:
        return 0
    if high_risk and "severity" in df.columns:
        return int(df[df["severity"].isin(["high", "critical"])].shape[0])
    if column and column in df.columns:
        return int(df[column].nunique())
    return int(df.shape[0])


def latest_records_by_key(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty or "_key" not in frame.columns:
        return frame
    sort_columns = [column for column in ["_offset", "_partition"] if column in frame.columns]
    ordered = frame.sort_values(by=sort_columns, ascending=False) if sort_columns else frame
    return ordered.drop_duplicates(subset=["_key"], keep="first")


def dataframe_records(frame: pd.DataFrame, limit: int | None = None) -> list[dict[str, Any]]:
    if frame.empty:
        return []
    filtered = frame[[column for column in frame.columns if not column.startswith("_")]].copy()
    if limit is not None:
        filtered = filtered.head(limit)
    return filtered.where(pd.notna(filtered), None).to_dict(orient="records")


def dataframe_first_record(frame: pd.DataFrame) -> dict[str, Any] | None:
    records = dataframe_records(frame, limit=1)
    return records[0] if records else None


def prepare_claim_details(enriched: pd.DataFrame, alerts: pd.DataFrame, breaches: pd.DataFrame) -> pd.DataFrame:
    if enriched.empty:
        return pd.DataFrame()

    frame = latest_records_by_key(enriched).copy()
    if not alerts.empty and "claim_id" in alerts.columns:
        alert_summary = alerts.groupby("claim_id").agg(
            alert_count=("alert_id", "count"),
            max_severity=("severity", "max"),
        )
        frame = frame.merge(alert_summary, on="claim_id", how="left")
    if not breaches.empty and "claim_id" in breaches.columns:
        breach_summary = breaches.groupby("claim_id").agg(
            breach_count=("breach_id", "count")
        )
        frame = frame.merge(breach_summary, on="claim_id", how="left")

    for column in ["alert_count", "breach_count"]:
        if column in frame.columns:
            frame[column] = frame[column].fillna(0).astype(int)
    if "max_severity" in frame.columns:
        frame["max_severity"] = frame["max_severity"].fillna("none")

    display_columns = [
        "claim_id",
        "provider_id",
        "priority",
        "current_status",
        "provider_risk_tier",
        "alert_count",
        "breach_count",
        "max_severity",
        "submitted_at",
    ]
    return frame[[column for column in display_columns if column in frame.columns]].sort_values(
        by=["alert_count", "breach_count", "submitted_at"],
        ascending=[False, False, False],
    )


def prepare_provider_leaderboard(scores: pd.DataFrame) -> pd.DataFrame:
    if scores.empty:
        return pd.DataFrame()
    scores = latest_records_by_key(scores)
    columns = [
        "provider_id",
        "provider_specialty",
        "provider_region",
        "provider_risk_tier",
        "risk_score",
        "risk_level",
        "total_claims",
        "denied_claims",
        "stale_claims",
        "missing_document_claims",
        "event_time",
    ]
    frame = scores[[column for column in columns if column in scores.columns]].copy()
    if "risk_score" in frame.columns:
        frame = frame.sort_values(by="risk_score", ascending=False)
    return frame


def build_alert_feed_source(alerts: pd.DataFrame, breaches: pd.DataFrame) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    if not alerts.empty:
        feed = latest_records_by_key(alerts).copy()
        feed["feed_type"] = "risk_alert"
        frames.append(feed)
    if not breaches.empty:
        feed = latest_records_by_key(breaches).copy()
        feed["feed_type"] = "sla_breach"
        frames.append(feed)
    if not frames:
        return pd.DataFrame()
    combined = pd.concat(frames, ignore_index=True, sort=False)
    sort_columns = [column for column in ["event_time", "_offset"] if column in combined.columns]
    if sort_columns:
        combined = combined.sort_values(by=sort_columns, ascending=False)
    return combined


def prepare_alert_feed(alerts: pd.DataFrame, breaches: pd.DataFrame) -> pd.DataFrame:
    combined = build_alert_feed_source(alerts, breaches)
    if combined.empty:
        return combined
    display_columns = [
        "feed_type",
        "_key",
        "claim_id",
        "provider_id",
        "severity",
        "alert_type",
        "breach_type",
        "message",
        "current_status",
        "event_time",
    ]
    return combined[[column for column in display_columns if column in combined.columns]].head(20)


def alert_option_label(record: dict[str, Any]) -> str:
    item_type = record.get("feed_type", "event")
    claim_id = record.get("claim_id", "unknown-claim")
    severity = record.get("severity", "n/a")
    status = record.get("current_status", "n/a")
    event_time = record.get("event_time", "n/a")
    return f"{item_type} | {claim_id} | {severity} | {status} | {event_time}"


def build_copilot_context(
    *,
    selected_alert: dict[str, Any],
    enriched: pd.DataFrame,
    alerts: pd.DataFrame,
    breaches: pd.DataFrame,
    scores: pd.DataFrame,
) -> dict[str, Any]:
    claim_id = selected_alert.get("claim_id")
    provider_id = selected_alert.get("provider_id")

    claim_context = dataframe_first_record(enriched[enriched["claim_id"] == claim_id]) if not enriched.empty and "claim_id" in enriched.columns else None
    provider_context = dataframe_first_record(scores[scores["provider_id"] == provider_id]) if not scores.empty and "provider_id" in scores.columns else None
    related_alerts = dataframe_records(alerts[alerts["claim_id"] == claim_id]) if not alerts.empty and "claim_id" in alerts.columns else []
    related_breaches = dataframe_records(breaches[breaches["claim_id"] == claim_id]) if not breaches.empty and "claim_id" in breaches.columns else []

    return {
        "selected_event": {key: value for key, value in selected_alert.items() if not key.startswith("_")},
        "claim_context": claim_context,
        "provider_context": provider_context,
        "related_claim_alerts": related_alerts,
        "related_claim_breaches": related_breaches,
    }


def run_claimshield_copilot(
    *,
    settings: CopilotSettings,
    context: dict[str, Any],
    analyst_question: str,
) -> str:
    client = OpenAI(api_key=settings.api_key)
    user_prompt = [
        "Use only the provided claim, alert, breach, and provider context.",
        "If a fact is missing from the context, say that it is unavailable.",
        "Explain the event for a healthcare claims operations analyst.",
        "",
        "Context JSON:",
        json.dumps(context, indent=2),
    ]
    if analyst_question.strip():
        user_prompt.extend(["", "Analyst question:", analyst_question.strip()])

    response = client.responses.create(
        model=settings.model,
        reasoning={"effort": "low"},
        input=[
            {
                "role": "developer",
                "content": (
                    "You are ClaimShield Copilot, an operations copilot for healthcare claims risk analysts. "
                    "Return concise markdown with exactly these sections: "
                    "### Why it fired, ### Evidence, ### What to do next, ### Urgency. "
                    "Base the answer strictly on the provided context and do not invent workflow steps, statuses, or evidence."
                ),
            },
            {
                "role": "user",
                "content": "\n".join(user_prompt),
            },
        ],
    )
    return (response.output_text or "").strip()


def render_copilot(
    *,
    enriched: pd.DataFrame,
    alerts: pd.DataFrame,
    breaches: pd.DataFrame,
    scores: pd.DataFrame,
    selected_feed_key: str | None = None,
) -> None:
    st.subheader("ClaimShield Copilot")
    st.caption("Explain a live alert using claim, breach, and provider context from the streaming pipeline.")

    copilot_feed = build_alert_feed_source(alerts, breaches).head(20)
    if copilot_feed.empty:
        st.info("No live alerts or breaches are available for explanation yet.")
        return

    option_records = copilot_feed.where(pd.notna(copilot_feed), None).to_dict(orient="records")
    options_by_key = {record.get("_key"): record for record in option_records if record.get("_key")}
    option_keys = list(options_by_key.keys())
    if selected_feed_key in options_by_key:
        st.session_state["claimshield_copilot_selected_key"] = selected_feed_key
    elif (
        st.session_state.get("claimshield_copilot_selected_key") not in options_by_key
        and option_keys
    ):
        st.session_state["claimshield_copilot_selected_key"] = option_keys[0]
    selected_key = st.selectbox(
        "Select an alert or breach",
        options=option_keys,
        format_func=lambda key: alert_option_label(options_by_key[key]),
        key="claimshield_copilot_selected_key",
    )
    selected_alert = options_by_key[selected_key]
    context = build_copilot_context(
        selected_alert=selected_alert,
        enriched=enriched,
        alerts=alerts,
        breaches=breaches,
        scores=scores,
    )

    copilot_settings = load_copilot_settings()
    question_default = "What should the claims team do next?"
    analyst_question = st.text_input(
        "Optional analyst question",
        value=st.session_state.get("claimshield_copilot_question", question_default),
        key="claimshield_copilot_question",
    )

    if not copilot_settings:
        st.info(
            f"Set `OPENAI_API_KEY` to enable ClaimShield Copilot. "
            f"You can also override the model with `CLAIMSHIELD_COPILOT_MODEL` "
            f"(default: `{COPILOT_DEFAULT_MODEL}`)."
        )
    else:
        st.caption(f"Model: `{copilot_settings.model}`")

    if st.button(
        "Explain selected event",
        disabled=copilot_settings is None,
        key="claimshield_copilot_run",
    ):
        with st.spinner("ClaimShield Copilot is reviewing the alert context..."):
            try:
                st.session_state["claimshield_copilot_response"] = run_claimshield_copilot(
                    settings=copilot_settings,
                    context=context,
                    analyst_question=analyst_question,
                )
                st.session_state["claimshield_copilot_response_key"] = selected_key
                st.session_state["claimshield_copilot_error"] = ""
            except Exception as exc:
                st.session_state["claimshield_copilot_error"] = str(exc)
                st.session_state["claimshield_copilot_response"] = ""
                st.session_state["claimshield_copilot_response_key"] = selected_key

    error_message = st.session_state.get("claimshield_copilot_error", "")
    if error_message:
        st.error(error_message)

    response_text = st.session_state.get("claimshield_copilot_response", "")
    response_key = st.session_state.get("claimshield_copilot_response_key")
    if response_text and response_key == selected_key:
        st.markdown(response_text)

    with st.expander("Copilot context"):
        st.json(context)


def render_dashboard(data: dict[str, pd.DataFrame]) -> None:
    enriched = latest_records_by_key(data["claims.enriched.curated"])
    alerts = latest_records_by_key(data["claims.risk.alerts"])
    breaches = latest_records_by_key(data["claims.sla.breaches"])
    scores = latest_records_by_key(data["providers.risk.scores"])

    st.set_page_config(page_title="ClaimShield Risk Command Center", layout="wide")
    st.title("ClaimShield Risk Command Center")
    st.caption("Real-time claims risk intelligence from Confluent Kafka + Flink SQL")

    left, right = st.columns([3, 1])
    with right:
        auto_refresh = st.toggle("Auto refresh", value=True)
        refresh_seconds = st.slider("Refresh interval (seconds)", 5, 30, 10)
        if st.button("Refresh now"):
            load_dashboard_data.clear()
            st.rerun()

    metrics = st.columns(4)
    metrics[0].metric("Total Active Claims", metric_value(enriched, "claim_id"))
    metrics[1].metric("High-Risk Claims", metric_value(alerts, high_risk=True))
    metrics[2].metric("SLA Breaches", metric_value(breaches, "claim_id"))
    flagged_providers = (
        scores[scores["risk_level"].isin(["high", "critical"])]
        if not scores.empty and "risk_level" in scores.columns
        else scores.iloc[0:0]
    )
    metrics[3].metric("Flagged Providers", metric_value(flagged_providers, "provider_id"))

    feed_col, provider_col = st.columns([3, 2])
    with feed_col:
        st.subheader("Live Alert Feed")
        alert_feed = prepare_alert_feed(alerts, breaches)
        if alert_feed.empty:
            st.info("No alert or breach records available yet.")
            selected_feed_key = None
        else:
            st.caption("Select a row to sync it into ClaimShield Copilot.")
            feed_event = st.dataframe(
                alert_feed,
                use_container_width=True,
                hide_index=True,
                key="claimshield_alert_feed_table",
                on_select="rerun",
                selection_mode="single-row",
                column_config={"_key": None},
            )
            selected_rows = []
            if feed_event and hasattr(feed_event, "selection"):
                selected_rows = list(feed_event.selection.rows)
            selected_feed_key = None
            if selected_rows:
                selected_index = selected_rows[0]
                if 0 <= selected_index < len(alert_feed):
                    selected_feed_key = alert_feed.iloc[selected_index]["_key"]

    with provider_col:
        st.subheader("Provider Leaderboard")
        provider_leaderboard = prepare_provider_leaderboard(scores)
        if provider_leaderboard.empty:
            st.info("No provider score records available yet.")
        else:
            st.dataframe(provider_leaderboard, use_container_width=True, hide_index=True)

    st.subheader("Claim Detail Table")
    claim_details = prepare_claim_details(enriched, alerts, breaches)
    if claim_details.empty:
        st.info("No enriched claim records available yet.")
    else:
        st.dataframe(claim_details, use_container_width=True, hide_index=True)

    render_copilot(
        enriched=enriched,
        alerts=alerts,
        breaches=breaches,
        scores=scores,
        selected_feed_key=selected_feed_key,
    )

    if auto_refresh:
        time.sleep(refresh_seconds)
        load_dashboard_data.clear()
        st.rerun()


def main() -> None:
    try:
        render_dashboard(load_dashboard_data())
    except Exception as exc:
        st.set_page_config(page_title="ClaimShield Risk Command Center", layout="wide")
        st.title("ClaimShield Risk Command Center")
        st.error(str(exc))
        st.info("Set Kafka credentials in the local environment or `.env` before launching the dashboard.")


if __name__ == "__main__":
    main()
