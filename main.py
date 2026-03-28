from fastapi import FastAPI, HTTPException, Header, Request
from dotenv import load_dotenv
import os
import logging
import requests
from pydantic import BaseModel
from typing import Literal, Optional, List

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger("wp_bridge")

app = FastAPI(title="ChatGPT WordPress Publishing Bridge")

WP_BASE_URL = os.getenv("WP_BASE_URL", "").rstrip("/")
WP_USERNAME = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")
BRIDGE_SECRET = os.getenv("BRIDGE_SECRET", "")


class PublishRequest(BaseModel):
    title: str
    html: str
    status: Literal["draft", "publish", "private"] = "draft"
    content_type: Literal["page", "post"] = "page"
    slug: Optional[str] = None
    excerpt: Optional[str] = None


class TranscriptMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class PublishTranscriptRequest(BaseModel):
    title: str
    messages: List[TranscriptMessage]
    status: Literal["draft", "publish", "private"] = "draft"
    content_type: Literal["page", "post"] = "page"
    slug: Optional[str] = None
    intro: Optional[str] = None


def wp_endpoint(content_type: str) -> str:
    if content_type == "post":
        return f"{WP_BASE_URL}/wp-json/wp/v2/posts"
    return f"{WP_BASE_URL}/wp-json/wp/v2/pages"


def verify_secret(x_bridge_secret: Optional[str], client_ip: str):
    if not BRIDGE_SECRET:
        logger.error("BRIDGE_SECRET not configured")
        raise HTTPException(status_code=500, detail="BRIDGE_SECRET not configured")

    if x_bridge_secret != BRIDGE_SECRET:
        logger.warning(f"WP_BRIDGE_AUTH_FAIL from {client_ip}")
        raise HTTPException(status_code=401, detail="Invalid bridge secret")


def render_transcript_html(
    title: str,
    messages: List[TranscriptMessage],
    intro: Optional[str] = None
) -> str:
    parts = [
        "<!doctype html>",
        "<html>",
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{title}</title>",
        """
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                max-width: 900px;
                margin: 40px auto;
                padding: 0 16px;
                color: #111;
                background: #fff;
            }
            h1 { margin-bottom: 0.25em; }
            .intro { color: #444; margin-bottom: 2em; }
            .msg {
                border-top: 1px solid #ddd;
                padding: 16px 0;
            }
            .role {
                font-weight: bold;
                margin-bottom: 8px;
            }
            .user .role { color: #0b57d0; }
            .assistant .role { color: #198754; }
            .content { white-space: pre-wrap; }
        </style>
        """,
        "</head>",
        "<body>",
        f"<h1>{title}</h1>",
    ]

    if intro:
        parts.append(f'<div class="intro">{intro}</div>')

    for msg in messages:
        css_class = "user" if msg.role == "user" else "assistant"
        role_label = "Jacob" if msg.role == "user" else "ChatGPT"
        parts.append(f'<section class="msg {css_class}">')
        parts.append(f'<div class="role">{role_label}</div>')
        parts.append(f'<div class="content">{msg.content}</div>')
        parts.append("</section>")

    parts.extend(["</body>", "</html>"])
    return "\n".join(parts)


def publish_to_wordpress(
    content_type: str,
    title: str,
    html: str,
    status: str,
    slug: Optional[str],
    excerpt: Optional[str]
):
    if not WP_BASE_URL or not WP_USERNAME or not WP_APP_PASSWORD:
        logger.error("WordPress credentials not configured")
        raise HTTPException(status_code=500, detail="WordPress credentials not configured")

    payload = {
        "title": title,
        "content": html,
        "status": status,
    }

    if slug:
        payload["slug"] = slug
    if excerpt:
        payload["excerpt"] = excerpt

    logger.info(f"Publishing {content_type} '{title}' to WordPress")

    try:
        response = requests.post(
            wp_endpoint(content_type),
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            json=payload,
            timeout=30,
        )
    except requests.RequestException as exc:
        logger.error(f"WordPress request failed: {exc}")
        raise HTTPException(status_code=502, detail=f"WordPress request failed: {exc}")

    if response.status_code not in (200, 201):
        logger.error(
            f"WordPress publish failed status={response.status_code} body={response.text}"
        )
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()

    logger.info(
        f"WordPress publish success id={data.get('id')} status={data.get('status')}"
    )

    return {
        "ok": True,
        "id": data.get("id"),
        "status": data.get("status"),
        "link": data.get("link"),
    }


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/publish")
def publish(
    req: PublishRequest,
    request: Request,
    x_bridge_secret: Optional[str] = Header(default=None),
):
    verify_secret(x_bridge_secret, request.client.host)
    return publish_to_wordpress(
        content_type=req.content_type,
        title=req.title,
        html=req.html,
        status=req.status,
        slug=req.slug,
        excerpt=req.excerpt,
    )


@app.post("/publish_transcript")
def publish_transcript(
    req: PublishTranscriptRequest,
    request: Request,
    x_bridge_secret: Optional[str] = Header(default=None),
):
    verify_secret(x_bridge_secret, request.client.host)

    html = render_transcript_html(
        title=req.title,
        messages=req.messages,
        intro=req.intro,
    )

    return publish_to_wordpress(
        content_type=req.content_type,
        title=req.title,
        html=html,
        status=req.status,
        slug=req.slug,
        excerpt=None,
    )
