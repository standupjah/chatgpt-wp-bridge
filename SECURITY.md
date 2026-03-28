# Security Guidelines

## Secrets

- Never commit `.env`
- Protect:
  - `WP_APP_PASSWORD`
  - `BRIDGE_SECRET`

## Access Control

- Use a strong `BRIDGE_SECRET`
- Restrict access via firewall or Apache rules
- Consider IP whitelisting

## Transport Security

- Always use HTTPS in production
- Do not expose the bridge over plain HTTP

## Authentication Failures

Failed authentication attempts are logged and can be used with fail2ban.

See `fail2ban_setup.md` for details.

## WordPress Security

- Use a dedicated WordPress user
- Use Application Passwords only (not main password)
- Limit permissions to necessary roles

## Reverse Proxy

- Use Apache or another reverse proxy
- Ensure headers are properly forwarded
- Avoid direct exposure of the backend service

## Content Safety

- Content is published as raw HTML
- Only send trusted input to the bridge
- Avoid injecting untrusted user content

## Monitoring

- Monitor logs regularly
- Consider rate limiting or fail2ban
