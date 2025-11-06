# summsync/store/session.py
import os, json, time, datetime, boto3
from typing import Any, Dict, List, Optional

dynamo = boto3.client("dynamodb")
SESS_TABLE        = os.environ.get("SESS_TABLE", "SummsyncSessions")
SESSION_TTL_SECS  = int(os.environ.get("SESSION_TTL_SECS", "3600"))

def _now_iso():
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

def _expires_at():
    return int(time.time()) + SESSION_TTL_SECS

def _player_key(name: str, tag: str) -> str:
    return f"{name.strip().upper()}#{tag.strip().upper()}"

def put_session_player(session_id: str, puuid: str, name: str, tag: str, stats: dict, mastery: list):
    dynamo.put_item(
        TableName=SESS_TABLE,
        Item={
            "sessionId": {"S": session_id},
            "puuid": {"S": puuid},
            "playerName": {"S": name},
            "gameTag": {"S": tag},
            "playerKey": {"S": _player_key(name, tag)},
            "updatedAt": {"S": _now_iso()},
            "expiresAt": {"N": str(_expires_at())},  # enable TTL on this attribute
            "stats": {"S": json.dumps(stats or {})},
            "mastery": {"S": json.dumps(mastery or [])},
        },
    )

def query_session(session_id: str) -> List[Dict[str, Any]]:
    r = dynamo.query(
        TableName=SESS_TABLE,
        KeyConditionExpression="sessionId = :s",
        ExpressionAttributeValues={":s": {"S": session_id}},
    )
    items = r.get("Items", [])
    out = []
    for it in items:
        out.append({
            "puuid": it["puuid"]["S"],
            "playerName": it["playerName"]["S"],
            "gameTag": it["gameTag"]["S"],
            "stats": json.loads(it["stats"]["S"]),
            "mastery": json.loads(it["mastery"]["S"]),
            "updatedAt": it["updatedAt"]["S"],
        })
    return out

def get_item_by_puuid(session_id: str, puuid: str) -> Optional[Dict[str, Any]]:
    r = dynamo.get_item(
        TableName=SESS_TABLE,
        Key={"sessionId": {"S": session_id}, "puuid": {"S": puuid}}
    )
    it = r.get("Item")
    if not it:
        return None
    return {
        "puuid": it["puuid"]["S"],
        "playerName": it["playerName"]["S"],
        "gameTag": it["gameTag"]["S"],
        "stats": json.loads(it["stats"]["S"]),
        "mastery": json.loads(it["mastery"]["S"]),
        "updatedAt": it["updatedAt"]["S"],
    }

def get_session_player(session_id: str, name: str, tag: str) -> Optional[Dict[str, Any]]:
    pkey = _player_key(name, tag)
    for it in query_session(session_id):
        if _player_key(it["playerName"], it["gameTag"]) == pkey:
            return it
    return None
