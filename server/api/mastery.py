# summsync/api/mastery.py
from typing import Any, Dict
from store.session import get_session_player
from api.shared import ok, bad, parse_body

def ep_mastery(event: Dict[str, Any]): # This endpoint will return the top masteries for a player from current session
    body = parse_body(event)
    session_id = body.get("sessionId")
    name, tag = body.get("playerName"), body.get("gameTag")
    if not session_id or not name or not tag:
        return bad(400, "sessionId, playerName, and gameTag are required.")

    it = get_session_player(session_id, name, tag)
    if not it:
        return ok({"error": "NOT_FOUND", "message": "Player not found in this session"}, 404)

    return ok({"playerName": it["playerName"], "gameTag": it["gameTag"], "mastery": it["mastery"], "updatedAt": it["updatedAt"]})
