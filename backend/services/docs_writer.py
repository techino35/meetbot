import json
from datetime import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build
from loguru import logger

from backend.config import get_settings
from backend.models import MeetingStructure

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]


async def write_to_google_docs(filename: str, transcript: str, structure: MeetingStructure) -> str:
    """
    Google Docsに議事録を書き込む。

    Args:
        filename: アップロードされたファイル名
        transcript: 文字起こしテキスト
        structure: 構造化済みMeetingStructure
    Returns:
        Google DocsのURL
    """
    settings = get_settings()

    creds_dict = json.loads(settings.google_credentials_json)
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=SCOPES
    )

    docs_service = build("docs", "v1", credentials=credentials)
    drive_service = build("drive", "v3", credentials=credentials)

    title = f"議事録 - {filename} ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]
    logger.info(f"Created Google Doc: {doc_id}")

    if settings.google_drive_folder_id:
        drive_service.files().update(
            fileId=doc_id,
            addParents=settings.google_drive_folder_id,
            removeParents="root",
            fields="id, parents",
        ).execute()

    requests = _build_document_content(structure, transcript)
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": requests}
    ).execute()

    return f"https://docs.google.com/document/d/{doc_id}/edit"


def _build_document_content(structure: MeetingStructure, transcript: str) -> list:
    requests = []
    index = 1

    def insert_text(text: str, style: str = "NORMAL_TEXT") -> None:
        nonlocal index
        requests.append({"insertText": {"location": {"index": index}, "text": text}})
        if style != "NORMAL_TEXT":
            requests.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": index, "endIndex": index + len(text)},
                    "paragraphStyle": {"namedStyleType": style},
                    "fields": "namedStyleType",
                }
            })
        index += len(text)

    insert_text("要約\n", "HEADING_1")
    for line in structure.summary:
        insert_text(f"• {line}\n")

    insert_text("\n議論ポイント\n", "HEADING_1")
    for point in structure.discussion_points:
        insert_text(f"• {point}\n")

    insert_text("\nアクションアイテム\n", "HEADING_1")
    if structure.action_items:
        for item in structure.action_items:
            insert_text(f"• [{item.owner}] {item.action} (期限: {item.deadline})\n")
    else:
        insert_text("なし\n")

    insert_text("\n決定事項\n", "HEADING_1")
    if structure.decisions:
        for d in structure.decisions:
            insert_text(f"• {d}\n")
    else:
        insert_text("なし\n")

    insert_text("\n文字起こし（全文）\n", "HEADING_1")
    insert_text(transcript + "\n")

    return requests
