# summsync/api/create.py
import os, json, base64, uuid, logging
from typing import Any, Dict
from core.player import Player
from store.session import put_session_player, get_item_by_puuid
from api.shared import ok, bad, parse_body, compute_player_bundle

logger = logging.getLogger(__name__)
MASTERY_COUNT = int(os.environ.get("MASTERY_COUNT", "3"))
RIOT_API_KEY  = os.environ.get("RIOT_API_KEY")
SESSION_REQUIRED = False  # Auto-Create if not created

def ep_create(event: Dict[str, Any]): # This endpoint will create the important info for all players received from client (Stats + Masteries)
    if not RIOT_API_KEY:
        return bad(500, "Missing or Expired RIOT_API_KEY.")

    # Parse and Split Players
    body = parse_body(event)
    players = body.get("players") or [] # Required
    session_id = body.get("sessionId") or str(uuid.uuid4()) # Optional
    mastery_count = int(body.get("masteryCount", MASTERY_COUNT)) # Optional
    force_refresh = bool(body.get("forceRefresh", False)) # Optional

    if not players:
        return bad(400, "Body must include 'players': a non-empty list of {playerName, gameTag}")

    players_in = body.get("players")

    # If the client accidentally sent players as a JSON string, coerce it
    if isinstance(players_in, str):
        try:
            players_in = json.loads(players_in)
        except Exception:
            return bad(400, "'players' must be an array of objects, not a string")

    # Validate structure
    if not isinstance(players_in, list) or not players_in:
        return bad(400, "`players` must be a non-empty array of {playerName, gameTag}")

    for i, rec in enumerate(players_in):
        if not isinstance(rec, dict):
            return bad(400, f"'players[{i}]' must be an object with playerName and gameTag")
        if "playerName" not in rec or "gameTag" not in rec:
            return bad(400, f"'players[{i}]' is missing playerName and/or gameTag.")


    results = []
    for idx, rec in enumerate(players):
        name = (rec or {}).get("playerName")
        tag  = (rec or {}).get("gameTag")
        if not name or not tag:
            results.append({"index": idx, "error": "playerName and gameTag required"})
            continue

        try:
            bundle = compute_player_bundle(name, tag, mastery_count) # Peform Tasks on each player, then bundle them together
            puuid = bundle.get("puuid")

            if not puuid:
                results.append({"playerName": name, "gameTag": tag,
                                "error": {"code": "NO_PUUID", "message": "Could not resolve PUUID"},
                                "stored": False})
                continue

            if bundle.get("error"):
                results.append({"playerName": name, "gameTag": tag, "puuid": puuid, "error": bundle["error"], "stats": None, "mastery": None, "stored": False})
                continue

            if not force_refresh:
                existing = get_item_by_puuid(session_id, puuid)
                if existing:
                    results.append({
                        "playerName": existing["playerName"], "gameTag": existing["gameTag"],
                        "puuid": puuid, "stats": existing["stats"], "mastery": existing["mastery"],
                        "stored": True, "fromCache": True
                    })
                    continue

            put_session_player(session_id, puuid, name, tag, bundle["stats"], bundle["mastery"])
            results.append({
                "playerName": name, "gameTag": tag, "puuid": puuid,
                "stats": bundle["stats"], "mastery": bundle["mastery"],
                "stored": True, "fromCache": False
            })

        except Exception as e:
            logger.exception("create failed for %s#%s", name, tag)
            results.append({
                "playerName": name, "gameTag": tag,
                "error": {"code": "PROCESSING_ERROR", "message": str(e)},
                "stats": None, "mastery": None, "stored": False
            })

    return ok({"sessionId": session_id, "results": results})
