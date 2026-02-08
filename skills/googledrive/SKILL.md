---
name: googledrive
description: Google Drive integration for file upload, download, search, and management. Uses Google Drive API v3 with OAuth2 authentication. Use when user mentions Google Drive, cloud storage, or file sharing.
license: MIT
metadata:
  author: opencngsm
  version: "3.0"
  requires: google-api-python-client==2.108.0, google-auth-oauthlib==1.1.0
compatibility: Requires Google Cloud project with Drive API enabled
---

# Google Drive Skill

## When to use this skill

Use this skill when the user wants to:
- Upload files to Google Drive
- Download files from Drive
- Search for files
- List files and folders
- Share files (get shareable links)
- Manage Drive storage
- Create folders

## Setup

1. **Create Google Cloud project:**
   - Visit: https://console.cloud.google.com/
   - Create new project
   - Enable Google Drive API

2. **Create OAuth2 credentials:**
   - Go to "Credentials" → "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app"
   - Download JSON file as `credentials.json`

3. **Install dependencies:**
   ```bash
   pip install google-api-python-client==2.108.0 google-auth-oauthlib==1.1.0
   ```

4. **First run (authentication):**
   - Run any Drive operation
   - Browser will open for Google login
   - Grant permissions
   - Token saved to `token.json`

## How to use

### Upload file

```python
from skills.googledrive.googledrive_skill import GoogleDriveSkill

drive = GoogleDriveSkill(
    credentials_path='credentials.json'
)

# Upload file
file_id = await drive.upload_file(
    file_path='document.pdf',
    folder_id=None,  # Root folder
    description='Important document'
)

print(f"Uploaded: {file_id}")
```

### Download file

```python
# Download by file ID
await drive.download_file(
    file_id='1abc...xyz',
    output_path='downloaded.pdf'
)

# Download by name
files = await drive.search_files('document.pdf')
if files:
    await drive.download_file(
        file_id=files[0]['id'],
        output_path='document.pdf'
    )
```

### Search files

```python
# Search by name
files = await drive.search_files(
    query='name contains "report"',
    limit=10
)

for file in files:
    print(f"{file['name']} - {file['id']}")

# Search by type
pdfs = await drive.search_files(
    query="mimeType='application/pdf'",
    limit=20
)
```

### List files

```python
# List all files
files = await drive.list_files(limit=50)

# List files in folder
folder_files = await drive.list_files(
    folder_id='1abc...xyz',
    limit=100
)
```

### Share file

```python
# Get shareable link
link = await drive.share_file(
    file_id='1abc...xyz',
    permission='reader'  # reader, writer, commenter
)

print(f"Share link: {link}")
```

### Create folder

```python
# Create folder
folder_id = await drive.create_folder(
    name='My Folder',
    parent_folder_id=None  # Root
)
```

## Features

- ✅ Upload files (any type)
- ✅ Download files
- ✅ Search files (by name, type, date)
- ✅ List files and folders
- ✅ Create folders
- ✅ Share files (get links)
- ✅ Delete files
- ✅ Move files
- ✅ OAuth2 authentication
- ✅ Token caching

## Search Queries

### By name
```python
query = "name contains 'report'"
query = "name = 'exact-name.pdf'"
```

### By type
```python
query = "mimeType='application/pdf'"
query = "mimeType='image/jpeg'"
query = "mimeType='application/vnd.google-apps.folder'"
```

### By date
```python
query = "modifiedTime > '2024-01-01T00:00:00'"
query = "createdTime < '2024-12-31T23:59:59'"
```

### Combined
```python
query = "name contains 'report' and mimeType='application/pdf'"
```

## MIME Types

- **Documents**: `application/vnd.google-apps.document`
- **Spreadsheets**: `application/vnd.google-apps.spreadsheet`
- **Presentations**: `application/vnd.google-apps.presentation`
- **PDF**: `application/pdf`
- **Images**: `image/jpeg`, `image/png`
- **Folders**: `application/vnd.google-apps.folder`

## Implementation

See [googledrive_skill.py](googledrive_skill.py) for the complete implementation.

## Examples

```python
# Example 1: Backup files
drive = GoogleDriveSkill('credentials.json')

for file in ['doc1.pdf', 'doc2.pdf']:
    file_id = await drive.upload_file(file)
    link = await drive.share_file(file_id)
    print(f"Backup: {link}")

# Example 2: Download reports
reports = await drive.search_files(
    query="name contains 'report' and mimeType='application/pdf'"
)

for report in reports:
    await drive.download_file(
        file_id=report['id'],
        output_path=f"reports/{report['name']}"
    )

# Example 3: Organize files
folder_id = await drive.create_folder('2024 Reports')

for file in await drive.search_files('report'):
    await drive.move_file(file['id'], folder_id)
```

## Troubleshooting

### "credentials.json not found"
- Download OAuth2 credentials from Google Cloud Console
- Place in project root or specify path

### "Token expired"
- Delete `token.json`
- Re-authenticate on next run

### "API not enabled"
- Enable Google Drive API in Cloud Console
- Wait a few minutes for activation

### "Insufficient permissions"
- Check OAuth scopes in credentials
- Re-authenticate with correct scopes

## Security

- ⚠️ Never commit `credentials.json` or `token.json`
- ✅ Add to `.gitignore`
- ✅ Use service accounts for production
- ✅ Limit OAuth scopes to minimum needed

## Scopes

- **Read-only**: `https://www.googleapis.com/auth/drive.readonly`
- **Full access**: `https://www.googleapis.com/auth/drive`
- **File-specific**: `https://www.googleapis.com/auth/drive.file`

## References

- [Google Drive API v3](https://developers.google.com/drive/api/v3/about-sdk)
- [OAuth2 setup](https://developers.google.com/drive/api/v3/about-auth)
- [Search query syntax](https://developers.google.com/drive/api/v3/search-files)
