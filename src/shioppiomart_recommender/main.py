#!/usr/bin/env python
import os
import sys
import warnings
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["CREWAI_TRACING_ENABLED"] = "true"
os.environ.pop("OTEL_SDK_DISABLED", None)
if os.getenv("Serper_API_KEY") and not os.getenv("SERPER_API_KEY"):
    os.environ["SERPER_API_KEY"] = os.environ["Serper_API_KEY"]
if os.getenv("PUSHOVER_APP_TOKEN") and not os.getenv("PUSHOVER_TOKEN"):
    os.environ["PUSHOVER_TOKEN"] = os.environ["PUSHOVER_APP_TOKEN"]
if os.getenv("PUSHOVER_USER_KEY") and not os.getenv("PUSHOVER_USER"):
    os.environ["PUSHOVER_USER"] = os.environ["PUSHOVER_USER_KEY"]

from shioppiomart_recommender.crew import ShioppiomartRecommender
from shioppiomart_recommender.tools.http import serper_post

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def _inputs(category: str = "wireless earbuds") -> dict[str, str]:
    today = datetime.now()
    return {
        "category": category,
        "market": "India",
        "current_date": today.strftime("%Y-%m-%d"),
        "current_year": str(today.year),
    }


def run():
    category = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else "wireless earbuds"
    try:
        serper_post("shopping", {"q": category, "num": 5, "gl": "in", "hl": "en"})
    except Exception as exc:
        raise SystemExit(
            "Serper is unreachable (google.serper.dev timed out). "
            "The crew will not run until that connection works. "
            "Switch Wi‑Fi/VPN and try again.\n"
            f"Detail: {exc}"
        ) from exc
    ShioppiomartRecommender().crew().kickoff(inputs=_inputs(category))


def train():
    ShioppiomartRecommender().crew().train(
        n_iterations=int(sys.argv[1]),
        filename=sys.argv[2],
        inputs=_inputs(),
    )


def replay():
    ShioppiomartRecommender().crew().replay(task_id=sys.argv[1])


def test():
    ShioppiomartRecommender().crew().test(
        n_iterations=int(sys.argv[1]),
        eval_llm=sys.argv[2],
        inputs=_inputs(),
    )


def run_with_trigger():
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided.")
    trigger_payload = json.loads(sys.argv[1])
    inputs = {**_inputs(), "crewai_trigger_payload": trigger_payload}
    return ShioppiomartRecommender().crew().kickoff(inputs=inputs)
