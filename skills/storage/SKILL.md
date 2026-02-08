---
name: storage
description: Local file storage operations using Python stdlib. Read, write, list, search, and manage files without external dependencies. Use when user mentions file operations, local storage, or file management.
license: MIT
metadata:
  author: opencngsm
  version: "3.0"
  requires: Python stdlib only (os, pathlib, shutil)
compatibility: Cross-platform (Windows, Linux, macOS)
---

# Storage Skill

## When to use this skill

Use this skill when the user wants to:
- Read files from disk
- Write files to disk
- List directory contents
- Search for files
- Copy, move, or delete files
- Create directories
- Check file existence
- Get file metadata (size, modified time)

## Setup

No setup required! Uses Python standard library only.

## How to use

### Read file

```python
from skills.storage.storage_skill import StorageSkill

storage = StorageSkill()

# Read text file
content = await storage.read_file('document.txt')

# Read binary file
data = await storage.read_file('image.png', binary=True)

# Read JSON
import json
data = json.loads(await storage.read_file('data.json'))
```

### Write file

```python
# Write text
await storage.write_file(
    'output.txt',
    'Hello, World!'
)

# Write binary
await storage.write_file(
    'image.png',
    image_bytes,
    binary=True
)

# Write JSON
import json
await storage.write_file(
    'data.json',
    json.dumps({'key': 'value'})
)
```

### List files

```python
# List directory
files = await storage.list_files('.')

for file in files:
    print(f"{file['name']} - {file['size']} bytes")

# List with filter
txt_files = await storage.list_files(
    '.',
    pattern='*.txt'
)
```

### Search files

```python
# Search by name
results = await storage.search_files(
    directory='.',
    pattern='report*.pdf',
    recursive=True
)

# Search by extension
py_files = await storage.search_files(
    directory='src',
    pattern='*.py',
    recursive=True
)
```

### File operations

```python
# Copy file
await storage.copy_file('source.txt', 'destination.txt')

# Move file
await storage.move_file('old_path.txt', 'new_path.txt')

# Delete file
await storage.delete_file('unwanted.txt')

# Check existence
exists = await storage.file_exists('document.pdf')
```

### Directory operations

```python
# Create directory
await storage.create_directory('new_folder')

# Create nested directories
await storage.create_directory('path/to/nested/folder')

# Delete directory
await storage.delete_directory('old_folder')
```

### File metadata

```python
# Get file info
info = await storage.get_file_info('document.pdf')

print(f"Size: {info['size']} bytes")
print(f"Modified: {info['modified']}")
print(f"Created: {info['created']}")
print(f"Is directory: {info['is_dir']}")
```

## Features

- ✅ Read text and binary files
- ✅ Write files (create or overwrite)
- ✅ List directory contents
- ✅ Search files (with patterns)
- ✅ Recursive search
- ✅ Copy, move, delete files
- ✅ Create/delete directories
- ✅ File metadata (size, dates)
- ✅ Path validation
- ✅ Cross-platform paths
- ✅ No external dependencies

## File Patterns

### Glob patterns
```python
'*.txt'           # All .txt files
'report*.pdf'     # Files starting with 'report'
'**/*.py'         # All .py files (recursive)
'data_[0-9].csv'  # data_0.csv, data_1.csv, etc.
```

## Implementation

See [storage_skill.py](storage_skill.py) for the complete implementation.

## Examples

```python
# Example 1: Backup files
storage = StorageSkill()

files = await storage.search_files('.', '*.txt')
await storage.create_directory('backup')

for file in files:
    await storage.copy_file(
        file['path'],
        f"backup/{file['name']}"
    )

# Example 2: Clean old files
import time
from datetime import datetime, timedelta

files = await storage.list_files('temp')
cutoff = datetime.now() - timedelta(days=7)

for file in files:
    if file['modified'] < cutoff:
        await storage.delete_file(file['path'])

# Example 3: Organize files by type
files = await storage.list_files('downloads')

for file in files:
    ext = file['name'].split('.')[-1]
    folder = f'organized/{ext}'
    
    await storage.create_directory(folder)
    await storage.move_file(
        file['path'],
        f"{folder}/{file['name']}"
    )
```

## Troubleshooting

### "File not found"
- Verify file path is correct
- Use absolute paths for clarity
- Check file permissions

### "Permission denied"
- Check file/directory permissions
- Run with appropriate user
- Verify disk is not read-only

### "Directory not empty"
- Use `delete_directory(recursive=True)`
- Or delete contents first

### "Disk full"
- Check available disk space
- Clean up temporary files
- Use different drive

## Best Practices

- ✅ Use `pathlib.Path` for cross-platform paths
- ✅ Validate paths before operations
- ✅ Handle exceptions gracefully
- ✅ Close file handles properly
- ✅ Use context managers (`with` statement)
- ⚠️ Be careful with `delete` operations
- ⚠️ Validate user input for paths

## Security

- ⚠️ Validate file paths (prevent directory traversal)
- ⚠️ Check file permissions before operations
- ⚠️ Sanitize filenames from user input
- ✅ Use absolute paths when possible
- ✅ Limit file sizes for uploads
- ✅ Validate file types

## Cross-Platform

```python
from pathlib import Path

# Good (cross-platform)
path = Path('folder') / 'file.txt'

# Bad (Windows-only)
path = 'folder\\file.txt'

# Bad (Unix-only)
path = 'folder/file.txt'
```

## References

- [Python pathlib docs](https://docs.python.org/3/library/pathlib.html)
- [Python os docs](https://docs.python.org/3/library/os.html)
- [Python shutil docs](https://docs.python.org/3/library/shutil.html)
