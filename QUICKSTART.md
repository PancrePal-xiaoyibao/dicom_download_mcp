# Quick Start Guide

## Installation

### 1. Install Dependencies
```bash
cd /Users/qinxiaoqiang/Downloads/dicom_mcp

# Install the MCP server
pip install -e .

# Install Playwright browsers (one-time setup)
playwright install chromium
```

### 2. Verify Installation
```bash
# Check if the server can be imported
python -c "from dicom_mcp.server import mcp; print('✓ MCP server ready')"

# Check if dicom_download is accessible
python -c "from common_utils import extract_share_id; print('✓ dicom_download accessible')"
```

## Running the Server

### Option A: Standalone (for testing)
```bash
python -m dicom_mcp.server
```

### Option B: With Claude Desktop
1. Edit `~/.config/Claude/claude_desktop_config.json` (or equivalent for your OS)
2. Add the server configuration:
```json
{
  "mcpServers": {
    "dicom-downloader": {
      "command": "python",
      "args": ["-m", "dicom_mcp.server"],
      "env": {
        "PYTHONPATH": "/Users/qinxiaoqiang/Downloads/dicom_mcp:/Users/qinxiaoqiang/Downloads/dicom_download"
      }
    }
  }
}
```
3. Restart Claude Desktop
4. The "dicom-downloader" tool should appear in Claude

## Basic Usage Examples

### Example 1: Download from a Single URL (Auto-detect provider)
```python
# In Claude, use this prompt:
# "Download DICOM images from https://zlyy.tjmucih.cn/viewer?share_id=ABC123"

# The server will automatically:
# 1. Detect provider as "tz" (天肿)
# 2. Download to ./dicom_downloads/zlyy.tjmucih.cn_ABC123_xxxxx/
# 3. Create a ZIP archive
# 4. Return success status with file count
```

### Example 2: Batch Download Multiple URLs
```python
# Prompt:
# "Download from these three URLs to ./my_studies/:
#  - https://zlyy.tjmucih.cn/viewer?share_id=STUDY1
#  - https://ylyyx.shdc.org.cn/viewer?share_id=STUDY2
#  - https://zhyl.nyfy.com.cn/viewer?share_id=STUDY3"

# Each URL goes to its own subdirectory
```

### Example 3: Download in Non-Headless Mode (with browser UI)
```python
# Prompt:
# "Download from https://example.com/viewer with browser UI visible"

# Server will run Playwright in non-headless mode for manual interaction
```

### Example 4: Check Provider Capabilities
```python
# Prompt:
# "What providers are supported and what domains do they cover?"

# This calls list_supported_providers() to show available options
```

### Example 5: Validate a URL
```python
# Prompt:
# "Is https://unknown-hospital.com/viewer supported?"

# Responds with validation result and available alternatives
```

### Example 6: Custom Scan Parameters
```python
# Prompt:
# "Download DICOM from [URL] with 5 scan rounds 
#  and 50ms delay between frames for complete capture"

# Server will use:
# - max_rounds=5 (more iterations = more complete)
# - step_wait_ms=50 (more delay = more stable capture)
```

### Example 7: Fast Download
```python
# Prompt:
# "Quick download from [URL], prioritize speed over completeness"

# Server will use:
# - max_rounds=2 (fewer iterations = faster)
# - step_wait_ms=30 (less delay = faster)
```

## Common Tasks

### Task 1: Download Diagnostic Sequences Only
```
Claude Prompt:
"Download DICOM from [URL] in diagnostic mode 
(faster, diagnostic sequences only, not all sequences)"
```

The MCP server will:
- Set `mode="diag"` parameter
- Pass to underlying provider script
- Return only diagnostic sequence files

### Task 2: Batch Download Without ZIP
```
Claude Prompt:
"Download from these URLs to ./downloads but 
don't create ZIP files, just leave the directories"
```

The MCP server will:
- Set `create_zip=False`
- Return directory paths for each download
- Skip ZIP archive creation

### Task 3: Handle Protected URLs
```
Claude Prompt:
"Download from https://example.medicalimagecloud.com/viewer 
with password: MY_SECRET_CODE"
```

The MCP server will:
- Pass password to cloud provider
- Authenticate and download
- Return downloaded files

### Task 4: List All Provider Domains
```
Claude Prompt:
"Show me all supported medical imaging providers 
and their website domains"
```

Returns:
- 天肿 (tz): zlyy.tjmucih.cn
- 复肿 (fz): ylyyx.shdc.org.cn
- 宁夏总医院 (nyfy): zhyl.nyfy.com.cn
- Cloud services: *.medicalimagecloud.com, etc.

### Task 5: Optimize Download Speed
```
Claude Prompt:
"Download from [URL] with minimal scans (2 rounds, 30ms delay) for speed"
```

The MCP server will:
- Set `max_rounds=2` (fewer iterations for speed)
- Set `step_wait_ms=30` (shorter delays)
- Download faster but may miss some frames
- Suitable for quick captures

### Task 6: Maximize Data Completeness
```
Claude Prompt:
"Download from [URL] with thorough scanning (5 rounds, 80ms delay) to get all frames"
```

The MCP server will:
- Set `max_rounds=5` (more iterations for completeness)
- Set `step_wait_ms=80` (longer delays for stability)
- Takes longer but captures more data
- Suitable for important medical data

## Troubleshooting

### Issue: "Module not found" error

**Solution**: Ensure PYTHONPATH includes both dicom_mcp and dicom_download:
```bash
export PYTHONPATH="/Users/qinxiaoqiang/Downloads/dicom_mcp:/Users/qinxiaoqiang/Downloads/dicom_download"
python -m dicom_mcp.server
```

### Issue: Playwright browsers not installed

**Solution**: Install Playwright browsers:
```bash
playwright install chromium
# Or for other browsers:
playwright install firefox
```

### Issue: Download fails with "Link expired"

**Reason**: Medical imaging share links typically expire after a certain period (days or weeks)

**Solution**: 
- Get a fresh share link from the medical provider
- Ensure the URL is valid and not too old

### Issue: Cloud provider authentication fails

**Reason**: Some cloud providers require explicit passwords

**Solution**: 
- Use the password parameter in the download request
- Ensure password is correctly encoded (no special characters issues)

### Issue: Headless mode not working on remote server

**Reason**: Remote systems need X11 display or virtual frame buffer

**Solution**:
- Use `headless=True` mode (browser automation without display)
- Or set up a virtual display: `xvfb-run python -m dicom_mcp.server`

## Understanding the Output

When download completes, you'll get:
```json
{
  "success": true,
  "url": "https://zlyy.tjmucih.cn/viewer?share_id=ABC123",
  "output_dir": "/Users/.../dicom_downloads/zlyy.tjmucih.cn_ABC123_xxxxx",
  "zip_path": "/Users/.../dicom_downloads/zlyy.tjmucih.cn_ABC123_xxxxx.zip",
  "message": "Download completed successfully",
  "file_count": 142
}
```

### Interpreting Results

- **success**: Download was successful
- **output_dir**: Where DICOM files are stored (can be directly accessed)
- **zip_path**: Compressed archive of all files (for easy transfer)
- **file_count**: Total number of DICOM files downloaded
- **message**: Status or error details

## File Organization

After download:
```
./dicom_downloads/
├── zlyy.tjmucih.cn_ABC123_xxxxx/        # DICOM files directory
│   ├── 001.dcm
│   ├── 002.dcm
│   └── ... (more DICOM files)
└── zlyy.tjmucih.cn_ABC123_xxxxx.zip     # Compressed archive
```

Each URL gets:
1. Unique subdirectory based on share ID
2. All DICOM files inside
3. Optional ZIP archive for easy sharing

## Next Steps

1. **Test with Real URLs**: Try downloading from a valid share link
2. **Integrate with Claude**: Configure Claude Desktop to access the server
3. **Automate Workflows**: Create Claude prompts for recurring download tasks
4. **Monitor Results**: Check output directories for downloaded DICOM files

## Support Resources

- **MCP Server Issues**: Check ARCHITECTURE.md for design details
- **DICOM Download Issues**: See original [dicom_download README](https://github.com/hengqujushi/dicom_download)
- **Provider-Specific Help**: Refer to your hospital/clinic documentation

## Advanced: Custom Configuration

Create a config file `~/.dicom_mcp_config.json`:
```json
{
  "default_output_dir": "./my_dicom_downloads",
  "default_headless": true,
  "default_mode": "all",
  "timeout_seconds": 600,
  "max_concurrent_downloads": 3
}
```

(Note: Custom config support can be added to `server.py` if needed)
