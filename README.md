# wp-bridge-apache

A small FastAPI bridge that lets a Custom GPT publish HTML pages or formatted chat transcripts to WordPress through the WordPress REST API.

## Features

- Publish raw HTML to WordPress with `/publish`
- Publish formatted chat transcripts with `/publish_transcript`
- `.env` loading with `python-dotenv`
- Auth-protected with `X-Bridge-Secret`
- Logging compatible with Fail2ban
- Deployment examples for systemd and Apache
- MIT licensed

## Repo structure

```text
wp-bridge-apache/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── openapi.yaml
├── custom_gpt_instructions.txt
├── fail2ban_setup.md
├── LICENSE
├── SECURITY.md
└── deploy/
    ├── wp-bridge.service
    └── apache-wp-bridge.conf
```

## Quick start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`, then run:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Test publish endpoint:

```bash
curl -X POST http://127.0.0.1:8000/publish \
  -H "Content-Type: application/json" \
  -H "X-Bridge-Secret: your-secret-here" \
  -d '{
    "title": "Test Page",
    "html": "<h1>Hello from bridge</h1>",
    "status": "draft",
    "content_type": "page"
  }'
```

Test transcript endpoint:

```bash
curl -X POST http://127.0.0.1:8000/publish_transcript \
  -H "Content-Type: application/json" \
  -H "X-Bridge-Secret: your-secret-here" \
  -d '{
    "title": "Transcript Test",
    "status": "draft",
    "content_type": "page",
    "intro": "A formatted transcript test.",
    "messages": [
      {"role": "user", "content": "What is imagination?"},
      {"role": "assistant", "content": "Imagination can be approached as a meaning-forming faculty."}
    ]
  }'
```

## Custom GPT setup

1. Replace the server URL in `openapi.yaml` with your public HTTPS bridge URL.
2. Create a Custom GPT.
3. Import `openapi.yaml` into the action setup.
4. In action authentication, choose API key auth with a custom header.
5. Set header name to `X-Bridge-Secret`.
6. Set the value to your `BRIDGE_SECRET`.
7. Paste in `custom_gpt_instructions.txt`.

## VPS deployment with Apache

Suggested layout:

```text
/opt/wp-bridge/
├── main.py
├── requirements.txt
├── .env
└── venv/
```

Install dependencies:

```bash
python3 -m venv /opt/wp-bridge/venv
/opt/wp-bridge/venv/bin/pip install -r /opt/wp-bridge/requirements.txt
```

Create a service account if desired:

```bash
sudo useradd --system --home /opt/wp-bridge --shell /usr/sbin/nologin wpbridge
sudo chown -R wpbridge:wpbridge /opt/wp-bridge
```

Copy `deploy/wp-bridge.service` to:

```text
/etc/systemd/system/wp-bridge.service
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable wp-bridge
sudo systemctl start wp-bridge
sudo systemctl status wp-bridge
```

Enable the needed Apache modules:

```bash
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod headers
sudo a2enmod ssl
```

Copy `deploy/apache-wp-bridge.conf` to your Apache sites config, enable it, and reload Apache:

```bash
sudo cp deploy/apache-wp-bridge.conf /etc/apache2/sites-available/wp-bridge.conf
sudo a2ensite wp-bridge
sudo systemctl reload apache2
```

Then add TLS with your normal Apache or Let's Encrypt workflow.

## GitHub checklist

- commit the repo files
- do **not** commit `.env`
- add the MIT `LICENSE`
- add a short repo description
- set the repo visibility you want
