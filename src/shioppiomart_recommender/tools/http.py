import json
import os
import subprocess
from typing import Any


def _env_first(*names: str) -> str:
    for name in names:
        value = (os.getenv(name) or "").strip()
        if value:
            return value
    return ""


def serper_key() -> str:
    key = _env_first("SERPER_API_KEY", "Serper_API_KEY")
    if not key:
        raise RuntimeError("SERPER_API_KEY is not set")
    return key


def _curl_json(url: str, headers: dict[str, str], body: str) -> tuple[int, str]:
    cmd = [
        "curl",
        "-4",
        "-sS",
        "--connect-timeout",
        "8",
        "--max-time",
        "20",
        "-X",
        "POST",
        url,
        "-w",
        "\n%{http_code}",
    ]
    for key, value in headers.items():
        cmd.extend(["-H", f"{key}: {value}"])
    cmd.extend(["--data-binary", body])
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "curl failed")
    raw = result.stdout.rsplit("\n", 1)
    payload = raw[0] if len(raw) == 2 else ""
    code = int(raw[-1] or "0")
    return code, payload


def serper_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    code, text = _curl_json(
        f"https://google.serper.dev/{path}",
        {"X-API-KEY": serper_key(), "content-type": "application/json"},
        json.dumps(payload),
    )
    if code == 429:
        raise RuntimeError("Serper rate limit (429). Wait a minute and run again.")
    if code >= 400:
        raise RuntimeError(f"Serper HTTP {code}: {text[:200]}")
    data = json.loads(text or "{}")
    if not isinstance(data, dict):
        raise RuntimeError("Serper returned a non-object")
    return data


def pushover_post(token: str, user: str, title: str, message: str) -> str:
    cmd = [
        "curl",
        "-4",
        "-sS",
        "--connect-timeout",
        "8",
        "--max-time",
        "20",
        "-X",
        "POST",
        "https://api.pushover.net/1/messages.json",
        "-d",
        f"token={token}",
        "-d",
        f"user={user}",
        "--data-urlencode",
        f"title={title}",
        "--data-urlencode",
        f"message={message}",
        "-w",
        "\n%{http_code}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Pushover curl failed")
    raw = result.stdout.rsplit("\n", 1)
    text = raw[0] if len(raw) == 2 else ""
    code = int(raw[-1] or "0")
    if code >= 400:
        raise RuntimeError(text[:240] or f"Pushover HTTP {code}")
    return text
