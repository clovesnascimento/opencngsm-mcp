---
name: calendar
description: Google Calendar integration with OAuth2 authentication. Create, list, update, and delete calendar events with reminders, attendees, and recurrence. Use when user mentions calendar, schedule, events, or appointments.
license: MIT
metadata:
  author: opencngsm
  version: "3.0"
  requires: google-api-python-client==2.108.0, google-auth-oauthlib==1.1.0
compatibility: Requires Google Cloud project with Calendar API enabled
---

# Google Calendar Skill

## When to use this skill

Use this skill when the user wants to:
- Create calendar events
- List upcoming events
- Update existing events
- Delete events
- Add event reminders
- Invite attendees to events
- Create recurring events
- Check schedule availability

## Setup

1. **Create Google Cloud project:**
   - Visit: https://console.cloud.google.com/
   - Create new project
   - Enable Google Calendar API

2. **Create OAuth2 credentials:**
   - Go to "Credentials" → "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app"
   - Download JSON file as `credentials.json`

3. **Install dependencies:**
   ```bash
   pip install google-api-python-client==2.108.0 google-auth-oauthlib==1.1.0
   ```

4. **First run (authentication):**
   - Run any Calendar operation
   - Browser will open for Google login
   - Grant Calendar permissions
   - Token saved to `token_calendar.json`

## How to use

### Create event

```python
from skills.calendar.calendar_skill import CalendarSkill
from datetime import datetime, timedelta

calendar = CalendarSkill(credentials_path='credentials.json')

# Simple event
event_id = await calendar.create_event(
    summary='Team Meeting',
    start_time=datetime(2024, 3, 15, 14, 0),
    end_time=datetime(2024, 3, 15, 15, 0)
)

# Event with details
event_id = await calendar.create_event(
    summary='Quarterly Review',
    start_time=datetime.now() + timedelta(days=7),
    end_time=datetime.now() + timedelta(days=7, hours=2),
    description='Q1 2024 review meeting',
    location='Conference Room A',
    attendees=['user@example.com', 'manager@example.com'],
    reminders={
        'useDefault': False,
        'overrides': [
            {'method': 'email', 'minutes': 24 * 60},  # 1 day before
            {'method': 'popup', 'minutes': 10}         # 10 min before
        ]
    }
)
```

### List events

```python
# List next 10 events
events = await calendar.list_events(max_results=10)

for event in events:
    start = event['start'].get('dateTime', event['start'].get('date'))
    print(f"{event['summary']} - {start}")

# List events in date range
from datetime import datetime, timedelta

events = await calendar.list_events(
    time_min=datetime.now(),
    time_max=datetime.now() + timedelta(days=7),
    max_results=50
)
```

### Update event

```python
# Update event
await calendar.update_event(
    event_id='abc123',
    summary='Updated Meeting Title',
    start_time=datetime(2024, 3, 15, 15, 0),  # New time
    end_time=datetime(2024, 3, 15, 16, 0)
)
```

### Delete event

```python
# Delete event
await calendar.delete_event(event_id='abc123')
```

### Get today's events

```python
# Quick helper
today_events = await calendar.get_today_events()

for event in today_events:
    print(f"{event['summary']} at {event['start']['dateTime']}")
```

## Features

- ✅ Create events (single or recurring)
- ✅ List events (with filters)
- ✅ Update events
- ✅ Delete events
- ✅ Add attendees
- ✅ Email reminders
- ✅ Popup reminders
- ✅ Event location
- ✅ Event description
- ✅ All-day events
- ✅ Recurring events (daily, weekly, monthly)
- ✅ OAuth2 authentication
- ✅ Token auto-refresh

## Recurring Events

```python
# Weekly meeting (every Monday at 2pm)
await calendar.create_event(
    summary='Weekly Standup',
    start_time=datetime(2024, 3, 11, 14, 0),  # Monday
    end_time=datetime(2024, 3, 11, 14, 30),
    recurrence=['RRULE:FREQ=WEEKLY;BYDAY=MO;COUNT=10']  # 10 weeks
)

# Daily reminder
await calendar.create_event(
    summary='Daily Check-in',
    start_time=datetime(2024, 3, 15, 9, 0),
    end_time=datetime(2024, 3, 15, 9, 15),
    recurrence=['RRULE:FREQ=DAILY;COUNT=30']  # 30 days
)
```

## All-Day Events

```python
# All-day event
await calendar.create_event(
    summary='Company Holiday',
    start_date=datetime(2024, 12, 25).date(),
    end_date=datetime(2024, 12, 26).date(),
    all_day=True
)
```

## Implementation

See [calendar_skill.py](calendar_skill.py) for the complete implementation.

## Examples

See [examples/calendar_usage.py](examples/calendar_usage.py) for comprehensive examples.

## Troubleshooting

### "credentials.json not found"
- Download OAuth2 credentials from Google Cloud Console
- Place in project root or specify path

### "Token expired"
- Delete `token_calendar.json`
- Re-authenticate on next run

### "Calendar API not enabled"
- Enable Google Calendar API in Cloud Console
- Wait a few minutes for activation

### "Insufficient permissions"
- Check OAuth scopes in credentials
- Re-authenticate with correct scopes

### "Event not found"
- Verify event ID is correct
- Check if event was deleted
- Ensure using correct calendar (primary)

## Security

- ⚠️ Never commit `credentials.json` or `token_calendar.json`
- ✅ Add to `.gitignore`
- ✅ Use service accounts for production
- ✅ Limit OAuth scopes to minimum needed

## Scopes

- **Read-only**: `https://www.googleapis.com/auth/calendar.readonly`
- **Full access**: `https://www.googleapis.com/auth/calendar`
- **Events only**: `https://www.googleapis.com/auth/calendar.events`

## Time Zones

Default timezone: `America/Fortaleza` (Brazil)

Change in code:
```python
event['start']['timeZone'] = 'America/Sao_Paulo'
event['end']['timeZone'] = 'America/Sao_Paulo'
```

## References

- [Google Calendar API v3](https://developers.google.com/calendar/api/v3/reference)
- [OAuth2 setup](https://developers.google.com/calendar/api/quickstart/python)
- [Event resource](https://developers.google.com/calendar/api/v3/reference/events)
- [Recurrence rules](https://datatracker.ietf.org/doc/html/rfc5545#section-3.8.5.3)
