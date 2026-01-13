# DICOM MCP Server

**English | [中文](README_CN.md)**

A Model Context Protocol (MCP) server for downloading DICOM medical images from multiple Chinese hospital imaging systems.

## Overview

This MCP server wraps the [dicom_download](https://github.com/hengqujushi/dicom_download) project, providing a clean interface for LLMs and AI agents to download DICOM images from supported medical imaging providers.

### Supported Providers

- **tz** (天肿): Tianjin Medical University Cancer Institute - zlyy.tjmucih.cn
- **fz** (复肿): Fudan University Cancer Hospital - ylyyx.shdc.org.cn
- **nyfy** (宁夏总医院): Ningxia General Hospital - zhyl.nyfy.com.cn
- **cloud**: Cloud-based DICOM services (*.medicalimagecloud.com and others)

## Installation

### Prerequisites

- Python 3.9+
- Playwright (for browser automation)

### Setup

```bash
# Install the package in development mode
pip install -e .

# Install Playwright browsers (required once)
playwright install chromium
```

## Usage

### As an MCP Server

```bash
# Start the MCP server (stdio transport)
dicom-mcp

# Or with explicit Python
python -m dicom_mcp.server
```

### Integration with Claude/LLM

#### Method 1: Local Python Deployment

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "dicom-downloader": {
      "command": "python",
      "args": ["-m", "dicom_mcp.server"],
      "env": {
        "PYTHONPATH": "/path/to/dicom_mcp"
      }
    }
  }
}
```

#### Method 2: NPX Deployment (Recommended)

Using npx, you can run the MCP server directly without manual setup:

```json
{
  "mcpServers": {
    "dicom-downloader": {
      "command": "npx",
      "args": ["-y", "dicom-mcp"],
      "env": {
        "DICOM_DEFAULT_OUTPUT_DIR": "./dicom_downloads",
        "DICOM_DEFAULT_MAX_ROUNDS": "3",
        "DICOM_DEFAULT_STEP_WAIT_MS": "40"
      }
    }
  }
}
```

This method:
- Automatically handles Python dependency detection
- Installs required packages on first run
- No manual PYTHONPATH configuration needed
- Works across different operating systems
- Supports environment variables for default parameters:
  - `DICOM_DEFAULT_OUTPUT_DIR`: Default directory for downloaded files (default: `./dicom_downloads`)
  - `DICOM_DEFAULT_MAX_ROUNDS`: Default scan rounds (default: `3`)
  - `DICOM_DEFAULT_STEP_WAIT_MS`: Default delay between frames in ms (default: `40`)

**Note:** First run may take 2-3 minutes as it installs Python dependencies. Subsequent runs will be faster.

## Real-Time Progress Feedback

Downloads now display real-time progress information:

```
======================================================================
🚀 DICOM 下载开始
======================================================================
📍 下载数量: 2 个URL
📁 输出目录: ./dicom_downloads
⚙️  扫描次数: 3, 帧间延迟: 40ms
⏳ 请稍候，下载中... (可能需要 2-10 分钟)

   >>> 打开检查页面: https://ylyyx.shdc.org.cn/viewer?...
   [1/2] provider=fz
   >>> 已进入 viewer iframe
   
======================================================================
✅ 下载完成！处理结果中...
======================================================================
```

**Expected Download Time** (varies by parameters and image size):
- Fast mode (2 rounds, 30ms): 1-5 minutes
- Balanced mode (3 rounds, 40ms): 2-8 minutes  [recommended]
- Complete mode (5 rounds, 80ms): 4-15 minutes
- Deep scan (10 rounds, 100ms): 8-30 minutes

For details, see [PROGRESS_FEEDBACK.md](PROGRESS_FEEDBACK.md)

## Available Tools

### 1. `download_dicom`

Download DICOM images from a single URL.

**Parameters:**
- `url` (required): Medical imaging viewer URL
- `output_dir` (default: `./dicom_downloads`): Directory to save downloaded DICOM files
- `provider` (default: `auto`): Provider type (auto, tz, fz, nyfy, cloud)
- `mode` (default: `all`): Download mode (all, diag, nondiag)
- `headless` (default: `true`): Run browser in headless mode (no UI)
- `password` (optional): Share password/code if required by the site
- `create_zip` (default: `true`): Create ZIP archive of downloaded files
- `max_rounds` (default: `3`): Maximum number of scan rounds (扫描次数) - controls frame-by-frame playback iterations
- `step_wait_ms` (default: `40`): Delay between steps in milliseconds (延迟时间) - delay between frames during playback

**Returns:**
- `success`: Whether download succeeded
- `output_dir`: Directory containing downloaded files
- `zip_path`: Path to ZIP archive if created
- `file_count`: Number of files downloaded
- `message`: Status or error message

### 2. `batch_download_dicom`

Download from multiple URLs in batch.

**Parameters:**
- `urls` (required): List of URLs to download from
- `output_parent` (default: `./dicom_downloads`): Parent directory for all downloads (each URL gets its own subdirectory)
- `provider` (default: `auto`): Provider type (auto, tz, fz, nyfy, cloud)
- `mode` (default: `all`): Download mode (all, diag, nondiag)
- `headless` (default: `true`): Run in headless mode (no UI)
- `create_zip` (default: `true`): Create ZIP archives for each URL
- `max_rounds` (default: `3`): Maximum number of scan rounds (扫描次数) - applied to all URLs
- `step_wait_ms` (default: `40`): Delay between steps in milliseconds (延迟时间) - applied to all URLs

**Returns:**
List of download results for each URL, with success status and file count

### 3. `detect_provider_from_url`

Identify which provider a URL belongs to.

**Parameters:**
- `url` (required): URL to check

**Returns:**
- `detected_provider`: The provider identifier
- `provider_info`: Details about the provider
- `is_auto_detected`: Whether detection was successful

### 4. `list_supported_providers`

Get information about all supported providers.

**Returns:** List of provider information with supported domains and descriptions

### 5. `validate_url`

Check if a URL is from a supported provider.

**Parameters:**
- `url` (required): URL to validate

**Returns:**
- `valid`: Whether URL is from a supported provider
- `provider`: Detected provider if valid
- `error`: Error message if invalid

## Examples

### Single Download

```python
# Download from a single URL
download_dicom(
    url="https://zlyy.tjmucih.cn/viewer?share_id=AAAA",
    output_dir="./my_downloads",
    mode="all",
    create_zip=True
)
```

### Batch Download

```python
# Download from multiple URLs
batch_download_dicom(
    urls=[
        "https://zlyy.tjmucih.cn/viewer?share_id=AAAA",
        "https://ylyyx.shdc.org.cn/viewer?share_id=BBBB",
        "https://zhyl.nyfy.com.cn/viewer?share_id=CCCC"
    ],
    output_parent="./batch_downloads",
    provider="auto",  # Auto-detect for each URL
    create_zip=True
)
```

### With Password

```python
# Download URL that requires a password/share code
download_dicom(
    url="https://example.medicalimagecloud.com/viewer?id=XYZ",
    password="secret123",
    provider="cloud"
)
```

## Architecture

```
dicom_mcp/
├── pyproject.toml          # Project configuration
├── README.md               # This file
└── dicom_mcp/
    ├── __init__.py         # Package initialization
    └── server.py           # MCP server implementation
```

The MCP server acts as a wrapper around the underlying `dicom_download` project, handling:

1. **Tool Registration**: Exposing download functions as MCP tools
2. **Input Validation**: Validating URLs and parameters
3. **Provider Detection**: Auto-detecting the correct provider for a URL
4. **Process Management**: Running the underlying download scripts
5. **Result Formatting**: Returning structured results to the LLM

## Error Handling

The server provides detailed error messages for common issues:

- Invalid URL format
- Unsupported provider domain
- Download failures (expired links, authentication required, etc.)
- File system errors

## Security Considerations

- Passwords are passed to the underlying service but not logged or cached
- URLs are validated before processing
- File operations use temporary directories for intermediate results
- The server runs in read-only mode by default (use only for downloads)

## Limitations

- **Browser Automation**: Some providers require Chromium/Firefox via Playwright
- **Desktop Environment**: Headless mode requires X11 or similar on Linux servers
- **Authentication**: Some URLs require valid share codes or authentication
- **Link Expiration**: Share links may expire after a certain period

## Development

### Running Tests

```bash
# Run with pytest (after installing dev dependencies)
pip install -e ".[dev]"
pytest tests/
```

### Building

```bash
# Build the package
python -m build

# Or with setuptools directly
python setup.py sdist bdist_wheel
```

## License

This MCP server wrapper is provided under the same license as the underlying `dicom_download` project (Apache 2.0). See the original project for details.

## Credits

- Original project: [dicom_download](https://github.com/hengqujushi/dicom_download)
- Cloud provider adapter based on: [cloud-dicom-downloader](https://github.com/Kaciras/cloud-dicom-downloader)

## Support

For issues with:
- **MCP Server**: Check this repository
- **DICOM Downloads**: See the [dicom_download project](https://github.com/hengqujushi/dicom_download)
- **Specific Providers**: Refer to provider-specific documentation
