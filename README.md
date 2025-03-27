# splunkbase-mcp

An MCP server for Splunkbase

## Description

This is a Machine Control Protocol (MCP) server that provides programmatic access to Splunkbase functionality. It allows you to search, download, and manage Splunkbase apps through a standardized interface.

## Installation 

Warning: this will store your password on-disk in plaintext. Better methods may come about eventually.

```
uv run mcp install -v "SPLUNKBASE_USERNAME=my_username" -v "SPLUNKBASE_PASSWORD=my_password" splunkbase-mcp.py
```

## Usage

Sample prompt for Claude:

```
Please do the following.
1. Search the web to find what Splunk app is responsible for providing field extractions for the WinEventLog sourcetype 
2. Find the app on Splunkbase and grab its numerical app ID 
3. Use the download_app tool to grab the latest version of the app from Splunkbase and place it in /tmp/apps/
```

## Resources

- `app://{app}/info` - Get detailed information about a Splunkbase app
- `app://{app}/splunk_versions` - Get supported Splunk versions for an app

## Available Tools

### Search
- **search(query: str)** - Search Splunkbase for apps
  - Returns a list of search results

### Version Management
- **get_app_latest_version(app: str | int, splunk_version: str, is_cloud: bool = False)** - Get the latest compatible version of an app
  - Parameters:
    - `app`: App name or numeric ID
    - `splunk_version`: Target Splunk version
    - `is_cloud`: Whether to check Splunk Cloud compatibility
  - Returns version information dictionary

### Download
- **download_app(app: str | int, output_dir: str, version: Optional[str] = None)** - Download a specific app version
  - Parameters:
    - `app`: App name or numeric ID
    - `output_dir`: Directory to save the downloaded app
    - `version`: Optional specific version to download (latest if not specified)
  - Returns success message with download details

## Dependencies

- aiosplunkbase >= 0.1.3
- mcp[cli]
- aiofiles
- Python >= 3.11 

