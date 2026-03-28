**Version:** 1.0.0  
**Status:** Production-ready

# chatgpt-wp-bridge

A lightweight bridge that allows ChatGPT (Custom GPT or API) to publish HTML content directly to a WordPress site via the REST API.

---

## Features

- Publish HTML pages and posts to WordPress
- Publish full chat transcripts
- Secure endpoint using a shared secret
- Designed for use with Custom GPT actions
- Supports Apache reverse proxy + systemd deployment

---

## Architecture

```
ChatGPT (Custom GPT)
        ↓
   HTTPS Request
        ↓
chatgpt-wp-bridge (FastAPI)
        ↓
 WordPress REST API
```
 
---

## Repository Structure

```
chatgpt-wp-bridge/
├── main.py
├── openapi.yaml
├── requirements.txt
├── .env.example
├── README.md
├── SECURITY.md
├── fail2ban_setup.md
├── custom_gpt_instructions.txt
├── deploy/
│   ├── apache-chatgpt-wp-bridge.conf
│   └── chatgpt-wp-bridge.service
```

---

## Prerequisites

Before using this bridge, ensure you have:

- A WordPress site with REST API enabled
- A WordPress user account
- A WordPress **Application Password** (required)
- Python 3.9+
- A server (for production)

---

## Quick Start

```bash
git clone https://github.com/standupjah/chatgpt-wp-bridge
cd chatgpt-wp-bridge

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env

uvicorn main:app --port 8000

```

---

## Environment Variables

Create a `.env` file based on `.env.example`:

```
WP_BASE_URL=https://your-site.com
WP_USERNAME=your-username
WP_APP_PASSWORD=your-application-password
BRIDGE_SECRET=your-secret-key
```

---

## Installation

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Running Locally

```
uvicorn main:app --reload --port 8000
```

Health check:

```
curl http://localhost:8000/health
```

---

## API Endpoints

### POST /publish

Publish HTML content to WordPress.

### POST /publish_transcript

Publish a formatted chat transcript.

### GET /health

Returns status of the bridge.

---

## Example Requests

### Publish a Page/Post (Change your-secret)

```
curl -X POST http://localhost:8000/publish \
  -H "Content-Type: application/json" \
  -H "X-Bridge-Secret: your-secret" \
  -d '{
    "title": "Test Post",
    "content": "<p>Hello world</p>",
    "status": "draft"
  }'
```

### Publish a Transcript (Change your-secret)

```
curl -X POST http://localhost:8000/publish_transcript \                                                          -H "Content-Type: application/json" \
  -H "X-Bridge-Secret: your-secret" \
  -d '{                                                               
    "title":"Transcript Test",
    "status":"draft",
    "content_type":"page",
    "intro":"A formatted transcript test.",
    "messages":[
      {"role":"user","content":"Hello ChatGPT"},
      {"role":"assistant","content":"Hello!"}
    ]
  }'
```

---

## WordPress Integration

The bridge publishes to:

- `/wp-json/wp/v2/posts`
- `/wp-json/wp/v2/pages`

Authentication is done via WordPress Application Passwords.

---

## Custom GPT Setup

1. Import `openapi.yaml`
2. Set server URL to your bridge endpoint
3. Add header:
   - `X-Bridge-Secret: your-secret`

---

## Deployment

### Systemd

Copy service file:

```
sudo cp deploy/chatgpt-wp-bridge.service /etc/systemd/system/
sudo systemctl daemon-reexec
sudo systemctl enable chatgpt-wp-bridge
sudo systemctl start chatgpt-wp-bridge
```

### Apache Reverse Proxy

Enable required modules:

```
a2enmod proxy proxy_http headers
```

Use provided config in `deploy/apache-chatgpt-wp-bridge.conf`.

---

## Notes

- Content is published as raw HTML
- Ensure only trusted sources can access the bridge
- Use HTTPS in production
