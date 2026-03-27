# Security

Do not commit:
- `.env`
- WordPress credentials
- `BRIDGE_SECRET`

Recommended:
- Deploy behind HTTPS
- Use a dedicated WordPress user
- Keep default publishing set to `draft`
- Monitor logs for `WP_BRIDGE_AUTH_FAIL`
