import os
from typing import Type

from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from shioppiomart_recommender.tools.http import pushover_post


class PushoverInput(BaseModel):
    names: str = Field(
        ...,
        description="Newline-separated product names to push, one name per line",
    )
    category: str = Field(..., description="Category those products belong to")


class PushoverTool(BaseTool):
    name: str = "pushover_send_names"
    description: str = (
        "Send the product name list to the Shoppiomart Pushover account. "
        "Call this once with the final names."
    )
    args_schema: Type[BaseModel] = PushoverInput

    def _run(self, names: str, category: str) -> str:
        token = (
            os.getenv("PUSHOVER_TOKEN")
            or os.getenv("PUSHOVER_API_TOKEN")
            or os.getenv("PUSHOVER_APP_TOKEN")
            or ""
        ).strip()
        user = (os.getenv("PUSHOVER_USER") or os.getenv("PUSHOVER_USER_KEY") or "").strip()
        if not token or not user:
            return "PUSHOVER_FAILED: Set PUSHOVER_TOKEN and PUSHOVER_USER in .env"
        lines = [line.strip(" -•\t") for line in names.splitlines() if line.strip()]
        if not lines:
            return "PUSHOVER_FAILED: No product names to send"
        body = "\n".join(f"{i}. {name}" for i, name in enumerate(lines[:12], 1))[:1024]
        try:
            pushover_post(token, user, f"Shoppiomart · {category}", body)
        except Exception as exc:
            return f"PUSHOVER_FAILED: {exc}"
        return f"Pushover sent {min(len(lines), 12)} names for {category}"
