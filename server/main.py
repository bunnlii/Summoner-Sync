# summsync/main.py
import json
from typing import Any, Dict
from api.create import ep_create
from api.stats import ep_stats
from api.mastery import ep_mastery
from api.ai import ep_ai_insight

def _cors():
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "content-type,authorization",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    }

def _ok(payload, code=200):
    return {"statusCode": code, "headers": _cors(), "body": json.dumps(payload)}

def _extract_method_path(event):
    """
    Normalize METHOD + PATH across HTTP API (v2) and REST API (v1),
    stripping stage prefixes and supporting {proxy+}.
    """
    rc = event.get("requestContext", {}) or {}

    # METHOD
    method = (rc.get("http", {}).get("method") or event.get("httpMethod") or "GET").upper()

    # PATH candidates
    path = (event.get("rawPath") or event.get("path") or rc.get("http", {}).get("path") or "/")

    # REST API proxy support
    resource = event.get("resource") or rc.get("resourcePath")
    if resource and resource.endswith("/{proxy+}"):
        proxy = (event.get("pathParameters") or {}).get("proxy")
        if proxy:
            path = "/" + proxy

    # Strip stage (/prod, /dev, $default)
    stage = rc.get("stage")
    if stage and path.startswith(f"/{stage}/"):
        path = path[len(stage) + 1 :]  # remove "/{stage}"

    # Normalize trailing slash
    if path != "/" and path.endswith("/"):
        path = path[:-1]

    return method, path

# --- tiny test/echo endpoints ---
def ep_test(event):
    return _ok({"message": "hello world"})

def ep_echo(event):
    m, p = _extract_method_path(event)
    return _ok({
        "method": m,
        "path": p,
        "rawPath": event.get("rawPath"),
        "stage": event.get("requestContext", {}).get("stage"),
        "routeKey": event.get("requestContext", {}).get("routeKey"),
        "resource": event.get("resource"),
    })

def handler(event: Dict[str, Any], context):
    method, path = _extract_method_path(event)

    if method == "OPTIONS":
        return _ok("", 200)

    routes = {
        # debug + test
        ("GET",  "/"):                 ep_test,
        ("GET",  "/summsync/test"):    ep_test,
        ("POST", "/summsync/test"):    ep_test,   # optional
        ("GET",  "/summsync/_echo"):   ep_echo,
        ("POST", "/summsync/_echo"):   ep_echo,

        # your real routes
        ("POST", "/summsync/player/create"):   ep_create,
        ("POST", "/summsync/player/stats"):    ep_stats,
        ("POST", "/summsync/player/mastery"):  ep_mastery,
        ("POST", "/summsync/ai-insight"):      ep_ai_insight,
    }

    fn = routes.get((method, path))
    if not fn:
        # Helpful 404 payload to see what we actually received
        return _ok({"error": "NO_ROUTE", "saw": {"method": method, "path": path}}, 404)
    return fn(event)
