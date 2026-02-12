import json
import os
import sys
import threading
import time
import urllib.request
import urllib.error
import argparse
import base64
import json
import uvicorn
from dotenv import load_dotenv
load_dotenv()


def wait_for_server(url: str, timeout: float = 30, interval: float = 0.5) -> None:
    """Block until the server responds or timeout is reached."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(url, timeout=2)
            return
        except (urllib.error.URLError, ConnectionError, OSError):
            time.sleep(interval)
    raise TimeoutError(f"Server at {url} did not start within {timeout}s")


def send_task(port: int, command: str) -> None:
    """Send execute_task request to the running server."""
    url = f"http://127.0.0.1:{port}/execute_task"
    payload = json.dumps({"command": command}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode()
        print(f"[entrypoint] Response ({resp.status}): {body}", flush=True)

def decode_b64_json(b64_str):
    if b64_str is None:
        return {}
    try:
        decoded = base64.b64decode(b64_str).decode("utf-8")
        return json.loads(decoded)
    except Exception as e:
        print(f"Failed to decode base64 json: {e}", file=sys.stderr)
        return {}


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--b64-task-config", type=str, default=None, help="Base64 encoded task config JSON string (overrides config file).")
    parser.add_argument("--b64-browser-config", type=str, default=None, help="Base64 encoded browser config JSON string (overrides config file).")
    parser.add_argument("--b64-agent-config", type=str, default=None, help="Base64 encoded agent config JSON string (overrides config file).")
    args = parser.parse_args()

    if args.b64_task_config:
        task_config = decode_b64_json(args.b64_task_config)
        print("=== TASK CONFIG ===")
        print(json.dumps(task_config, indent=2))
        print("===================")
        task="{}. FIRST GO TO '{}' NO QUOTES. {}".format(
            task_config.get("parameters").get("creds", "No credentials provided for this task."),
            task_config.get("default_url", "about:blank"),
            task_config.get("task", "YOU WERE PROVIDED WITH NO TASK. PRINT 'NO TASK PROVIDED' AND TERMINATE IMMEDIATELY.")
        )
    else:
        print("No task config provided via --b64-task-config. Exiting.")
        exit(1)

    port = int(os.environ.get("PORT", 8000))
    command = os.environ.get(
        "TASK_COMMAND",
        task
    )

    config = uvicorn.Config(
        "ae.server.api_routes:app",
        host="127.0.0.1",
        port=port,
        loop="asyncio",
    )
    server = uvicorn.Server(config)

    # Run the server in a background thread so we can send the request
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    try:
        print(f"[entrypoint] Waiting for server on port {port}…", flush=True)
        wait_for_server(f"http://127.0.0.1:{port}/")
        print(f"[entrypoint] Server ready, sending task", flush=True)
        send_task(port, command)
    except Exception as e:
        print(f"[entrypoint] Error: {e}", flush=True)
        sys.exit(1)

    # Keep alive until the server exits
    thread.join()


if __name__ == "__main__":
    main()
