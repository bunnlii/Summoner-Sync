# summsync/api/shared.py
import json, base64, os, logging
from typing import Any, Dict
from core.player import Player

logger = logging.getLogger(__name__)

def cors():
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "content-type,authorization",
        "Access-Control-Allow-Methods": "POST,OPTIONS",
    }

def ok(payload, code=200):  # General Request Succeeded
    return {"statusCode": code, "headers": cors(), "body": json.dumps(payload)}

def bad(code, msg): # General Request Failed
    return {"statusCode": code, "headers": cors(), "body": json.dumps({"error": msg})}

def parse_body(event) -> Dict[str, Any]: # Parses the body
    raw = event.get("body") or ""
    if event.get("isBase64Encoded"):
        raw = base64.b64decode(raw).decode("utf-8")
    return json.loads(raw or "{}")

def short_error(e: Exception) -> str:
    try:
        resp = e.response
        code = resp["Error"]["Code"]
        msg = resp["Error"].get("Message") or resp["Error"].get("message") or str(e)
        return f"{code}: {msg}"
    except Exception:
        return str(e)

def compute_player_bundle(name: str, tag: str, mastery_count: int): # Will apply Player Class and operation to all Players
    p = Player(name, tag) # Initalizes Player Class
    p.matchHistory() # Will search match history for stats and important info

    total_games = int(getattr(p, "wins", 0)) + int(getattr(p, "loses", 0))
    puuid = getattr(p, "puuid", None)

    if total_games == 0:
        return {"puuid": puuid, "error": {"code": "NO_RECENT_MATCHES", "message": "No recent matches returned"}}

    stats = p.returnPlayerStats() # Will retreive stats from player class

    mastery = []
    try:
        mr = p.topMastery(int(mastery_count)) # Will attempt to retreive top X champion masteries for player
        if isinstance(mr, dict) and mr.get("statusCode") == 200:
            mastery = json.loads(mr.get("body", "[]"))
    except Exception as e:
        logger.warning("Mastery parse failed for %s#%s: %s", name, tag, e)

    return {"puuid": puuid, "stats": stats, "mastery": mastery}
