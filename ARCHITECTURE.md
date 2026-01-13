# DICOM MCP Server Architecture

## Overview

This MCP server provides a standardized interface for downloading DICOM medical images from multiple Chinese hospital imaging systems. It wraps the `dicom_download` project and exposes its functionality as Model Context Protocol tools.

## Design Goals

1. **Multi-Provider Support**: Handle diverse imaging systems (天肿, 复肿, 宁夏总医院, cloud-based)
2. **Batch Processing**: Support downloading from multiple URLs efficiently
3. **Auto-Detection**: Automatically identify the correct provider for a given URL
4. **Async Operation**: Leverage Python async/await for concurrent downloads
5. **Clean Interface**: Provide simple, well-typed MCP tools for LLM integration

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│         MCP Client (Claude, etc.)                       │
└────────────────────┬────────────────────────────────────┘
                     │ MCP Protocol (stdio/HTTP)
                     │
┌────────────────────▼────────────────────────────────────┐
│         DICOM MCP Server (dicom_mcp/server.py)          │
├─────────────────────────────────────────────────────────┤
│  ├─ Tool: download_dicom()          - Single URL        │
│  ├─ Tool: batch_download_dicom()    - Multiple URLs     │
│  ├─ Tool: detect_provider_from_url()- Provider ID       │
│  ├─ Tool: list_supported_providers()- Provider list     │
│  └─ Tool: validate_url()            - URL validation    │
├─────────────────────────────────────────────────────────┤
│  Utilities:                                             │
│  ├─ detect_provider()    - Auto-detect provider        │
│  ├─ run_multi_download() - Execute downloads           │
│  └─ count_files_recursive() - Count results            │
└────────────────────┬────────────────────────────────────┘
                     │ subprocess.run()
                     │
┌────────────────────▼────────────────────────────────────┐
│      Underlying dicom_download Project                  │
├─────────────────────────────────────────────────────────┤
│  ├─ multi_download.py    - Multi-URL router             │
│  ├─ common_utils.py      - Shared utilities             │
│  ├─ tjmucih_download_dicom.py  - 天肿 provider         │
│  ├─ shdc_download_dicom.py     - 复肿 provider         │
│  ├─ nyfy_download_dicom.py     - 宁夏总医院 provider   │
│  └─ cloud-dicom-downloader/    - Cloud provider        │
└──────────────────────────────────────────────────────────┘
```

## Component Details

### 1. MCP Server (`dicom_mcp/server.py`)

**Responsibilities:**
- Register tools with MCP framework
- Handle input validation
- Execute downloads via subprocess
- Format and return results

**Key Functions:**

#### Provider Detection
```python
detect_provider(url: str) -> str
```
Maps domains to provider identifiers:
- `zlyy.tjmucih.cn` → "tz"
- `ylyyx.shdc.org.cn` → "fz"  
- `zhyl.nyfy.com.cn` → "nyfy"
- `*.medicalimagecloud.com` → "cloud"

#### Download Execution
```python
async def run_multi_download(
    urls: list[str],
    output_parent: str,
    ...
) -> list[DownloadResult]
```
- Creates temporary URL list file
- Invokes `multi_download.py` as subprocess
- Tracks results per URL
- Cleans up temporary files

### 2. Data Models

#### DownloadRequest
```python
@dataclass
class DownloadRequest:
    url: str                    # Required
    output_dir: str            # Default: "./dicom_downloads"
    provider: Optional[str]    # Default: "auto"
    mode: str                  # Default: "all" | "diag" | "nondiag"
    headless: bool             # Default: True
    password: Optional[str]    # For protected shares
    create_zip: bool           # Default: True
```

#### DownloadResult
```python
@dataclass
class DownloadResult:
    success: bool              # Download success/failure
    url: str                   # Source URL
    output_dir: str            # Download directory
    zip_path: Optional[str]    # ZIP archive path if created
    message: str               # Status/error message
    file_count: Optional[int]  # Number of files
```

### 3. MCP Tools

#### Tool 1: `download_dicom`
- **Input**: DownloadRequest
- **Output**: DownloadResult
- **Use**: Download from a single URL
- **Auto-detection**: Supports "auto" provider mode

#### Tool 2: `batch_download_dicom`
- **Input**: BatchDownloadRequest (list of URLs)
- **Output**: List[DownloadResult]
- **Use**: Download from multiple URLs with consistent settings
- **Efficiency**: Processes URLs sequentially via underlying script

#### Tool 3: `detect_provider_from_url`
- **Input**: url string
- **Output**: Provider detection result with info
- **Use**: Identify provider without downloading

#### Tool 4: `list_supported_providers`
- **Input**: None
- **Output**: List[ProviderInfo]
- **Use**: Query available providers and their domains

#### Tool 5: `validate_url`
- **Input**: url string
- **Output**: Validation result
- **Use**: Check if URL is from supported provider

## Data Flow

### Single Download Flow
```
User Request
    ↓
download_dicom(DownloadRequest)
    ↓
validate_url() → DownloadRequest
    ↓
detect_provider(url) → provider_id
    ↓
run_multi_download([url], ...) 
    ↓
Create temp urls.txt
    ↓
subprocess: multi_download.py --urls-file urls.txt ...
    ↓
extract_share_id(url) → output_dir name
    ↓
count_files_recursive(output_dir)
    ↓
DownloadResult
    ↓
Return to User
```

### Batch Download Flow
```
User Request (list of URLs)
    ↓
batch_download_dicom(BatchDownloadRequest)
    ↓
run_multi_download(urls, ...)
    ↓
Create temp urls.txt with all URLs
    ↓
subprocess: multi_download.py --urls-file urls.txt ...
    ↓
For each URL:
  ├─ detect_provider(url)
  ├─ extract_share_id(url)
  └─ Create results
    ↓
List[DownloadResult]
    ↓
Return to User
```

## Provider-Specific Behavior

Each provider is handled by the underlying `dicom_download` scripts:

### 天肿 (tz)
- Script: `tjmucih_download_dicom.py`
- Modes: diag, nondiag, all
- Browser: Required (Playwright)
- Special: UI-based sequence selection

### 复肿 (fz)
- Script: `shdc_download_dicom.py`
- Features: HD switching, frame-by-frame playback
- Browser: Required (Playwright)
- Optimization: Concurrent frame downloads

### 宁夏总医院 (nyfy)
- Script: `nyfy_download_dicom.py`
- Architecture: WebSocket + h5Cache
- Browser: Required (Playwright)
- Special: Assembles Part10 DICOM format

### Cloud Services (cloud)
- Script: `cloud-dicom-downloader/downloader.py` (subprocess)
- Domains: *.medicalimagecloud.com and hospital clouds
- Auth: May require passwords
- Wrapper: Runs in temporary directory, migrates output

## Error Handling Strategy

1. **URL Validation**: Check format before processing
2. **Provider Detection**: Fallback to "fz" if unknown domain
3. **Subprocess Failures**: Capture stderr, return error message
4. **File Operations**: Graceful handling of missing/full directories
5. **Cleanup**: Always remove temporary files even on failure

## Performance Considerations

1. **Async Processing**: Uses asyncio for subprocess management
2. **Batch Efficiency**: Single `multi_download.py` invocation for multiple URLs
3. **File Counting**: Recursive walk only on demand
4. **Temporary Files**: Auto-cleaned after each batch

## Security

1. **URL Validation**: Only accepts URLs from known providers
2. **Password Handling**: Passed to subprocess, not cached or logged
3. **File Operations**: Limited to configured output directory
4. **Subprocess**: Runs with inherited environment only

## Extension Points

### Adding a New Provider

1. Implement provider script in `dicom_download/`
2. Add domain detection in `detect_provider()`
3. Update `list_supported_providers()` with provider info
4. Test with `validate_url()` and `batch_download_dicom()`

### Custom Download Logic

For providers not in `dicom_download`, create custom implementation:
1. Inherit from base download logic
2. Register new tool with `@mcp.tool()`
3. Handle provider-specific parameters
4. Return standardized DownloadResult

## Integration with Claude Desktop

Configuration in `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "dicom-downloader": {
      "command": "python",
      "args": ["-m", "dicom_mcp.server"],
      "env": {
        "PYTHONPATH": "/path/to/dicom_mcp:/path/to/dicom_download"
      }
    }
  }
}
```

## Testing

Key test scenarios:
1. Provider detection for each domain
2. URL validation with invalid formats
3. Batch download with mixed providers
4. Error handling for failed downloads
5. File counting and ZIP creation

## Future Enhancements

1. **Streaming**: Support streaming responses for large files
2. **Caching**: Cache provider info and URL validation
3. **Retry Logic**: Automatic retry with exponential backoff
4. **Webhooks**: Async download status notifications
5. **Compression**: DICOM compression before transfer
