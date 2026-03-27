# Fail2ban setup for the WordPress bridge

This bridge logs failed auth attempts in this format:

```text
WP_BRIDGE_AUTH_FAIL from 203.0.113.10
```

## 1. Make sure the bridge logs are written to a file

This repo's systemd service is already configured to write to:

```text
/var/log/wp-bridge.log
```

## 2. Create the filter

Create:

`/etc/fail2ban/filter.d/wp-bridge.conf`

```ini
[Definition]
failregex = WP_BRIDGE_AUTH_FAIL from <HOST>
ignoreregex =
```

## 3. Add the jail

Add to:

`/etc/fail2ban/jail.local`

```ini
[wp-bridge]
enabled = true
port = 8000
filter = wp-bridge
logpath = /var/log/wp-bridge.log
maxretry = 5
findtime = 600
bantime = 3600
backend = auto
```

## 4. Restart Fail2ban

```bash
sudo systemctl restart fail2ban
sudo fail2ban-client status
sudo fail2ban-client status wp-bridge
```

## 5. Test the regex

```bash
sudo fail2ban-regex /var/log/wp-bridge.log /etc/fail2ban/filter.d/wp-bridge.conf
```

## 6. Trigger failures

```bash
for i in {1..6}; do
  curl -X POST http://localhost:8000/publish \
    -H "Content-Type: application/json" \
    -H "X-Bridge-Secret: wrong-secret" \
    -d '{"title":"Fail Test","html":"<h1>Nope</h1>"}'
done
```

## 7. Check jail status

```bash
sudo fail2ban-client status wp-bridge
```

## 8. Unban an IP if needed

```bash
sudo fail2ban-client set wp-bridge unbanip 127.0.0.1
```
