---
name: email
description: Send and receive emails via SMTP/IMAP with HTML support, attachments, and templates. Uses Python stdlib (no external dependencies). Use when user mentions email, wants to send messages, or check inbox.
license: MIT
metadata:
  author: opencngsm
  version: "3.0"
  requires: Python stdlib only (smtplib, imaplib)
compatibility: Requires email server credentials (SMTP/IMAP)
---

# Email Skill

## When to use this skill

Use this skill when the user wants to:
- Send emails (plain text or HTML)
- Send emails with attachments
- Check inbox for new emails
- Search emails by criteria
- Use email templates
- Send bulk emails

## Setup

1. **Configure email credentials:**
   ```bash
   export EMAIL_ADDRESS="your@email.com"
   export EMAIL_PASSWORD="your_password"
   export SMTP_SERVER="smtp.gmail.com"
   export SMTP_PORT="587"
   export IMAP_SERVER="imap.gmail.com"
   export IMAP_PORT="993"
   ```

2. **For Gmail:**
   - Enable 2-factor authentication
   - Generate app-specific password
   - Use app password instead of regular password

## How to use

### Send email

```python
from skills.email.email_skill import EmailSkill

email = EmailSkill(
    smtp_server='smtp.gmail.com',
    smtp_port=587,
    email_address='your@email.com',
    password='your_password'
)

# Send plain text
await email.send_email(
    to='recipient@example.com',
    subject='Hello',
    body='This is a test email'
)

# Send HTML
await email.send_email(
    to='recipient@example.com',
    subject='Newsletter',
    body='<h1>Welcome!</h1><p>This is HTML email</p>',
    html=True
)

# Send with attachment
await email.send_email(
    to='recipient@example.com',
    subject='Report',
    body='Please see attached report',
    attachments=['report.pdf', 'data.xlsx']
)
```

### Check inbox

```python
# Configure IMAP
email.configure_imap(
    imap_server='imap.gmail.com',
    imap_port=993
)

# Get unread emails
unread = await email.get_unread_emails(limit=10)

for msg in unread:
    print(f"From: {msg['from']}")
    print(f"Subject: {msg['subject']}")
    print(f"Body: {msg['body']}")
```

### Use templates

```python
# Send with template
await email.send_template_email(
    to='user@example.com',
    subject='Welcome {name}!',
    template='welcome.html',
    variables={
        'name': 'John',
        'company': 'OpenCngsm'
    }
)
```

## Features

- ✅ Send plain text emails
- ✅ Send HTML emails
- ✅ Send attachments (multiple files)
- ✅ Check inbox (IMAP)
- ✅ Get unread emails
- ✅ Search emails by criteria
- ✅ Email templates with variables
- ✅ Bulk email sending
- ✅ CC and BCC support
- ✅ No external dependencies (stdlib only)

## Email Providers

### Gmail
```python
smtp_server='smtp.gmail.com'
smtp_port=587
imap_server='imap.gmail.com'
imap_port=993
```

### Outlook/Hotmail
```python
smtp_server='smtp-mail.outlook.com'
smtp_port=587
imap_server='outlook.office365.com'
imap_port=993
```

### Yahoo
```python
smtp_server='smtp.mail.yahoo.com'
smtp_port=587
imap_server='imap.mail.yahoo.com'
imap_port=993
```

## Implementation

See [email_skill.py](email_skill.py) for the complete implementation.

## Examples

See [examples/skills_usage.py](../../examples/skills_usage.py) for email examples.

## Troubleshooting

### "Authentication failed"
- Verify email and password
- For Gmail: use app-specific password
- Enable "less secure apps" if needed

### "Connection refused"
- Check SMTP/IMAP server and port
- Verify firewall settings
- Check internet connection

### "Attachment too large"
- Most servers limit to 25MB
- Compress files or use cloud links

### "HTML not rendering"
- Verify HTML syntax
- Test with simple HTML first
- Check recipient's email client

## Security

- ⚠️ Never commit passwords to git
- ✅ Use environment variables
- ✅ Use app-specific passwords
- ✅ Enable 2FA on email account

## References

- [Python smtplib docs](https://docs.python.org/3/library/smtplib.html)
- [Python imaplib docs](https://docs.python.org/3/library/imaplib.html)
- [Gmail app passwords](https://support.google.com/accounts/answer/185833)
