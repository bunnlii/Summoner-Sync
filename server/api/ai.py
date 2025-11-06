# summsync/api/ai.py
import os, json, logging
import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from typing import Any, Dict
from store.session import query_session
from api.shared import ok, bad, parse_body, short_error

logger = logging.getLogger(__name__)
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-west-2")
MODEL_ID       = os.environ.get("MODEL_ID")
br = boto3.client(
    "bedrock-runtime",
    region_name=BEDROCK_REGION,
    config=Config(retries={"max_attempts": 3, "mode": "standard"}, read_timeout=30, connect_timeout=5), # Will attempt 5 times w/ 30 seconds timeouts
)

def ep_ai_insight(event: Dict[str, Any]): # This endpoint will call the bedrock deepseek model to prompt with coaching message, then return insights
    if not MODEL_ID:
        return bad(500, "MODEL_ID env var is not set")
    body = parse_body(event)

    prompt = body.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        return bad(400, "prompt (string) is required")

    session_id = body.get("sessionId")
    players_ctx = query_session(session_id) if session_id else [] # Will query this session

    system_msgs = [{"text": "Be concise and precise"}]
    if players_ctx:
        ctx = json.dumps({"players": players_ctx})[:15000]
        system_msgs.append({"text": f"Context JSON:\n{ctx}"})

    # Actual Model Call
    try:
        resp = br.converse(
            modelId=MODEL_ID,
            system=system_msgs,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 3000, "temperature": 0.3, "topP": 0.9},
        )
        out_msg = (resp.get("output") or {}).get("message") or {}
        pieces = out_msg.get("content") or []
        text_parts = [p["text"] for p in pieces if isinstance(p, dict) and "text" in p]
        answer = "\n".join(text_parts).strip()
        return ok({"answer": answer, "modelId": MODEL_ID, "playersUsed": len(players_ctx)})
    except (ClientError, BotoCoreError) as e:
        logger.exception("Bedrock error")
        return bad(502, f"Bedrock error: {short_error(e)}")
    except Exception as e:
        logger.exception("Unexpected error")
        return bad(500, f"Internal error: {type(e).__name__}")
