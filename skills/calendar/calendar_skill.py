"""
OpenCngsm v3.0 - Google Calendar Skill
OAuth2 authentication and Calendar API v3 integration
"""
import os
import pickle
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import logging

logger = logging.getLogger(__name__)


class CalendarSkill:
    """
    Google Calendar integration with OAuth2
    
    Features:
    - Create, list, update, delete events
    - Reminders (email, popup)
    - Attendees
    - Recurring events
    - All-day events
    """
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token_calendar.json'):
        """
        Initialize Calendar skill
        
        Args:
            credentials_path: Path to OAuth2 credentials JSON
            token_path: Path to save/load token
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """OAuth2 authentication flow"""
        creds = None
        
        # Load token if exists
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("🔄 Refreshing Google Calendar token...")
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}\n"
                        "Download from: https://console.cloud.google.com/"
                    )
                
                logger.info("🔐 Starting OAuth2 flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
            
            logger.info("✅ Google Calendar authenticated")
        
        self.service = build('calendar', 'v3', credentials=creds)
    
    async def create_event(
        self,
        summary: str,
        start_time: datetime = None,
        end_time: datetime = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
        all_day: bool = False,
        description: str = None,
        location: str = None,
        attendees: List[str] = None,
        reminders: Dict = None,
        recurrence: List[str] = None,
        timezone: str = 'America/Fortaleza'
    ) -> str:
        """
        Create calendar event
        
        Args:
            summary: Event title
            start_time: Start datetime (for timed events)
            end_time: End datetime (for timed events)
            start_date: Start date (for all-day events)
            end_date: End date (for all-day events)
            all_day: If True, create all-day event
            description: Event description
            location: Event location
            attendees: List of email addresses
            reminders: Reminder configuration
            recurrence: Recurrence rules (RRULE format)
            timezone: Timezone (default: America/Fortaleza)
        
        Returns:
            Event ID
        
        Example:
            event_id = await calendar.create_event(
                summary='Team Meeting',
                start_time=datetime(2024, 3, 15, 14, 0),
                end_time=datetime(2024, 3, 15, 15, 0),
                description='Quarterly review',
                location='Conference Room A',
                attendees=['user@example.com'],
                reminders={
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10}
                    ]
                }
            )
        """
        event = {'summary': summary}
        
        # Time/Date
        if all_day or (start_date and end_date):
            event['start'] = {'date': start_date.isoformat() if start_date else start_time.date().isoformat()}
            event['end'] = {'date': end_date.isoformat() if end_date else end_time.date().isoformat()}
        else:
            if not start_time or not end_time:
                raise ValueError("start_time and end_time required for timed events")
            
            event['start'] = {
                'dateTime': start_time.isoformat(),
                'timeZone': timezone,
            }
            event['end'] = {
                'dateTime': end_time.isoformat(),
                'timeZone': timezone,
            }
        
        # Optional fields
        if description:
            event['description'] = description
        
        if location:
            event['location'] = location
        
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        
        if reminders:
            event['reminders'] = reminders
        else:
            event['reminders'] = {'useDefault': True}
        
        if recurrence:
            event['recurrence'] = recurrence
        
        try:
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            logger.info(f"✅ Event created: {event['id']}")
            return event['id']
        except HttpError as error:
            logger.error(f"❌ Failed to create event: {error}")
            raise
    
    async def list_events(
        self,
        max_results: int = 10,
        time_min: datetime = None,
        time_max: datetime = None
    ) -> List[Dict]:
        """
        List upcoming events
        
        Args:
            max_results: Maximum number of events
            time_min: Start time filter (default: now)
            time_max: End time filter
        
        Returns:
            List of event dictionaries
        
        Example:
            events = await calendar.list_events(max_results=10)
            for event in events:
                print(f"{event['summary']} - {event['start']['dateTime']}")
        """
        if time_min is None:
            time_min = datetime.utcnow()
        
        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z' if time_max else None,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            logger.info(f"📅 Found {len(events)} events")
            return events
        except HttpError as error:
            logger.error(f"❌ Failed to list events: {error}")
            raise
    
    async def get_today_events(self) -> List[Dict]:
        """Get today's events"""
        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return await self.list_events(
            time_min=start_of_day,
            time_max=end_of_day,
            max_results=100
        )
    
    async def update_event(
        self,
        event_id: str,
        summary: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
        description: str = None,
        location: str = None,
        timezone: str = 'America/Fortaleza'
    ) -> Dict:
        """
        Update existing event
        
        Args:
            event_id: Event ID to update
            summary: New title
            start_time: New start time
            end_time: New end time
            description: New description
            location: New location
            timezone: Timezone
        
        Returns:
            Updated event dictionary
        """
        try:
            # Get current event
            event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
            
            # Update fields
            if summary:
                event['summary'] = summary
            if start_time:
                event['start']['dateTime'] = start_time.isoformat()
                event['start']['timeZone'] = timezone
            if end_time:
                event['end']['dateTime'] = end_time.isoformat()
                event['end']['timeZone'] = timezone
            if description:
                event['description'] = description
            if location:
                event['location'] = location
            
            # Update event
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"✅ Event updated: {event_id}")
            return updated_event
        except HttpError as error:
            logger.error(f"❌ Failed to update event: {error}")
            raise
    
    async def delete_event(self, event_id: str):
        """
        Delete event
        
        Args:
            event_id: Event ID to delete
        """
        try:
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            logger.info(f"🗑️ Event deleted: {event_id}")
        except HttpError as error:
            logger.error(f"❌ Failed to delete event: {error}")
            raise
    
    async def get_event(self, event_id: str) -> Dict:
        """Get event by ID"""
        try:
            event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
            return event
        except HttpError as error:
            logger.error(f"❌ Failed to get event: {error}")
            raise


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        calendar = CalendarSkill()
        
        # Create event
        event_id = await calendar.create_event(
            summary='Test Meeting',
            start_time=datetime.now() + timedelta(hours=1),
            end_time=datetime.now() + timedelta(hours=2),
            description='Test event from OpenCngsm'
        )
        
        print(f"Created event: {event_id}")
        
        # List events
        events = await calendar.list_events(max_results=5)
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"{event['summary']} - {start}")
    
    asyncio.run(main())
