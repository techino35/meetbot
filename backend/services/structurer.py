import json
from loguru import logger
from anthropic import AsyncAnthropic

from backend.config import get_settings
from backend.models import MeetingStructure, ActionItem

MODEL = "claude-opus-4-5"
MAX_TOKENS = 4096

SYSTEM_PROMPT = """あなたは議事録作成の専門家です。
会議の文字起こしテキストを分析し、以下のJSON形式で構造化してください。
必ずJSONのみを返し、前後に説明文を追加しないでください。

{
  "summary": ["要点1", "要点2", ...],
  "discussion_points": ["議論ポイント1", "議論ポイント2", ...],
  "action_items": [
    {"owner": "担当者名", "action": "タスク内容", "deadline": "期限"}
  ],
  "decisions": ["決定事項1", "決定事項2", ...]
}"""


async def structure_transcript(transcript: str) -> MeetingStructure:
    """
    Claude APIで文字起こしを構造化する。

    Args:
        transcript: 文字起こしテキスト
    Returns:
        MeetingStructure
    """
    settings = get_settings()
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    response = await client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"以下の文字起こしを構造化してください:\n\n{transcript}"}]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    data = json.loads(raw)
    logger.info(f"Structured: {len(data.get('action_items', []))} action items, {len(data.get('decisions', []))} decisions")

    return MeetingStructure(
        summary=data.get("summary", []),
        discussion_points=data.get("discussion_points", []),
        action_items=[ActionItem(**item) for item in data.get("action_items", [])],
        decisions=data.get("decisions", []),
    )
