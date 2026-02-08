"""
OpenCngsm v3.0 - Google Drive Skill
Native Python implementation using google-api-python-client
"""
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from typing import List, Dict, Optional
from pathlib import Path
import io
import os
import logging

logger = logging.getLogger(__name__)


class GoogleDriveSkill:
    """
    Google Drive integration using official Python client
    
    Features:
    - Upload/download files
    - Create folders
    - List files and folders
    - Share files
    - Delete files
    - OAuth2 authentication
    
    Setup:
    1. Go to https://console.cloud.google.com/
    2. Create project and enable Google Drive API
    3. Create OAuth 2.0 credentials
    4. Download credentials.json
    """
    
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(
        self,
        credentials_path: str = 'credentials.json',
        token_path: str = 'token.json'
    ):
        """
        Initialize Google Drive skill
        
        Args:
            credentials_path: Path to OAuth credentials JSON
            token_path: Path to save/load token
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.credentials = None
        self.service = None
    
    async def authenticate(self) -> bool:
        """
        Authenticate with Google Drive
        
        Returns:
            True if successful
        """
        try:
            # Load existing token
            if os.path.exists(self.token_path):
                self.credentials = Credentials.from_authorized_user_file(
                    self.token_path,
                    self.SCOPES
                )
            
            # Refresh or get new token
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path,
                        self.SCOPES
                    )
                    self.credentials = flow.run_local_server(port=0)
                
                # Save token
                with open(self.token_path, 'w') as token:
                    token.write(self.credentials.to_json())
            
            # Build service
            self.service = build('drive', 'v3', credentials=self.credentials)
            
            logger.info("✅ Authenticated with Google Drive")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to authenticate: {e}")
            return False
    
    async def list_files(
        self,
        folder_id: str = 'root',
        page_size: int = 100,
        query: Optional[str] = None
    ) -> List[Dict]:
        """
        List files in folder
        
        Args:
            folder_id: Folder ID ('root' for root folder)
            page_size: Max files to return
            query: Custom query filter
        
        Returns:
            List of file dictionaries
        """
        try:
            if not self.service:
                await self.authenticate()
            
            # Build query
            if not query:
                query = f"'{folder_id}' in parents and trashed=false"
            
            results = self.service.files().list(
                q=query,
                pageSize=page_size,
                fields="files(id, name, mimeType, size, createdTime, modifiedTime, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"✅ Listed {len(files)} files")
            return files
        
        except Exception as e:
            logger.error(f"❌ Failed to list files: {e}")
            return []
    
    async def upload_file(
        self,
        file_path: str,
        folder_id: str = 'root',
        name: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Upload file to Drive
        
        Args:
            file_path: Path to file to upload
            folder_id: Destination folder ID
            name: Custom file name (default: original filename)
        
        Returns:
            File metadata dictionary or None
        """
        try:
            if not self.service:
                await self.authenticate()
            
            file_metadata = {
                'name': name or Path(file_path).name,
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(file_path, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink, size'
            ).execute()
            
            logger.info(f"✅ Uploaded {file.get('name')} ({file.get('size')} bytes)")
            return file
        
        except Exception as e:
            logger.error(f"❌ Failed to upload: {e}")
            return None
    
    async def download_file(
        self,
        file_id: str,
        destination: str
    ) -> bool:
        """
        Download file from Drive
        
        Args:
            file_id: File ID to download
            destination: Local path to save file
        
        Returns:
            True if successful
        """
        try:
            if not self.service:
                await self.authenticate()
            
            request = self.service.files().get_media(fileId=file_id)
            
            with io.FileIO(destination, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        logger.info(f"Download progress: {int(status.progress() * 100)}%")
            
            logger.info(f"✅ Downloaded to {destination}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to download: {e}")
            return False
    
    async def create_folder(
        self,
        folder_name: str,
        parent_id: str = 'root'
    ) -> Optional[Dict]:
        """
        Create folder in Drive
        
        Args:
            folder_name: Name of new folder
            parent_id: Parent folder ID
        
        Returns:
            Folder metadata or None
        """
        try:
            if not self.service:
                await self.authenticate()
            
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id, name, webViewLink'
            ).execute()
            
            logger.info(f"✅ Created folder {folder_name}")
            return folder
        
        except Exception as e:
            logger.error(f"❌ Failed to create folder: {e}")
            return None
    
    async def delete_file(self, file_id: str) -> bool:
        """
        Delete file permanently
        
        Args:
            file_id: File ID to delete
        
        Returns:
            True if successful
        """
        try:
            if not self.service:
                await self.authenticate()
            
            self.service.files().delete(fileId=file_id).execute()
            
            logger.info(f"✅ Deleted file {file_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to delete: {e}")
            return False
    
    async def share_file(
        self,
        file_id: str,
        email: Optional[str] = None,
        role: str = 'reader'
    ) -> Optional[str]:
        """
        Share file with user or make public
        
        Args:
            file_id: File ID to share
            email: Email to share with (None = public)
            role: 'reader', 'writer', or 'commenter'
        
        Returns:
            Share link or None
        """
        try:
            if not self.service:
                await self.authenticate()
            
            permission = {
                'type': 'user' if email else 'anyone',
                'role': role
            }
            
            if email:
                permission['emailAddress'] = email
            
            self.service.permissions().create(
                fileId=file_id,
                body=permission,
                fields='id'
            ).execute()
            
            # Get share link
            file = self.service.files().get(
                fileId=file_id,
                fields='webViewLink'
            ).execute()
            
            link = file.get('webViewLink')
            logger.info(f"✅ Shared file: {link}")
            return link
        
        except Exception as e:
            logger.error(f"❌ Failed to share: {e}")
            return None


# Skill metadata
SKILL_NAME = "googledrive"
SKILL_CLASS = GoogleDriveSkill
SKILL_DESCRIPTION = "Upload, download, and manage Google Drive files using official API"


# Auto-register
from . import register_skill
register_skill(SKILL_NAME, SKILL_CLASS, SKILL_DESCRIPTION)
