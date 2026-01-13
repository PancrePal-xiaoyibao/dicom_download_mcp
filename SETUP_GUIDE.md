# DICOM MCP Setup & Installation Guide

## What You Have

A complete MCP (Model Context Protocol) server package at:
```
/Users/qinxiaoqiang/Downloads/dicom_mcp/
```

This wraps your existing `dicom_download` project and exposes it as MCP tools.

## Installation Steps

### Step 1: Install the Package

```bash
cd /Users/qinxiaoqiang/Downloads/dicom_mcp

# Install in development mode (editable)
pip install -e .

# Verify installation
python -c "from dicom_mcp.server import mcp; print('✓ MCP server installed')"
```

### Step 2: Install Playwright Browsers (One-time)

```bash
# Install Chromium (required for browser automation)
playwright install chromium

# Optional: Install other browsers if needed
# playwright install firefox
```

### Step 3: Verify Paths

The server expects to find `dicom_download` in the parent directory. Verify:

```bash
ls -la /Users/qinxiaoqiang/Downloads/dicom_download/multi_download.py
# Should show: -rw-r--r-- ... multi_download.py
```

If the path is different, edit `dicom_mcp/server.py` line ~15:
```python
DICOM_DOWNLOAD_PATH = Path(__file__).parent.parent.parent / "dicom_download"
```

Change the path as needed.

## Integration with Claude Desktop

### Option A: Using NPX (Recommended)

1. Locate Claude Desktop config directory:
   - **macOS**: `~/Library/Application\ Support/Claude/`
   - **Windows**: `%APPDATA%\Claude\`
   - **Linux**: `~/.config/Claude/`

2. Open or create `claude_desktop_config.json`

3. **⚠️ IMPORTANT: Modify `DICOM_DEFAULT_OUTPUT_DIR` to use an absolute path!**

   Add the server configuration:
```json
{
  "mcpServers": {
    "dicom-downloader": {
      "command": "npx",
      "args": ["-y", "dicom-mcp"],
      "env": {
        "DICOM_DEFAULT_OUTPUT_DIR": "/Users/qinxiaoqiang/Downloads/dicom_downloads",
        "DICOM_DEFAULT_MAX_ROUNDS": "3",
        "DICOM_DEFAULT_STEP_WAIT_MS": "40"
      }
    }
  }
}
```

**Configuration:**
- Replace `/Users/qinxiaoqiang/Downloads/dicom_downloads` with your actual absolute path
- ❌ Do NOT use relative paths like `./dicom_downloads`
- ✅ Use full paths: `/Users/username/...` (macOS/Linux) or `C:\\Users\\username\\...` (Windows)

4. Restart Claude Desktop

5. Verify the server appears in Claude (should show new tools available)

### Option B: Using Local Python Deployment

1. Locate Claude Desktop config directory:
   - **macOS**: `~/Library/Application\ Support/Claude/`
   - **Windows**: `%APPDATA%\Claude\`
   - **Linux**: `~/.config/Claude/`

2. Open or create `claude_desktop_config.json`:

3. Add the server configuration:
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

4. Restart Claude Desktop

5. Verify the server appears in Claude (should show new tools available)

### Option B: Manual Verification

```bash
# Test the server directly
python -m dicom_mcp.server

# If it starts without errors, server is working
# (Press Ctrl+C to stop)
```

## What You Get

### 5 MCP Tools

| Tool | Purpose |
|------|---------|
| `download_dicom` | Download from a single URL |
| `batch_download_dicom` | Download from multiple URLs |
| `detect_provider_from_url` | Identify which provider a URL uses |
| `list_supported_providers` | Show all supported medical centers |
| `validate_url` | Check if a URL is from supported provider |

### Supported Providers

- **天肿** (Tianjin Cancer Institute): zlyy.tjmucih.cn
- **复肿** (Fudan Cancer Hospital): ylyyx.shdc.org.cn  
- **宁夏总医院** (Ningxia General Hospital): zhyl.nyfy.com.cn
- **Cloud**: *.medicalimagecloud.com + others

## Using the Server

### Example 1: Ask Claude

```
User: "Download DICOM images from https://zlyy.tjmucih.cn/viewer?share_id=ABC123"

Claude will:
1. Call the download_dicom tool
2. Auto-detect provider as "tz"
3. Download to ./dicom_downloads/...
4. Create ZIP archive
5. Report success with file count
```

### Example 2: Batch Operations

```
User: "Download from these 3 URLs:
  - https://zlyy.tjmucih.cn/viewer?share_id=STUDY1
  - https://ylyyx.shdc.org.cn/viewer?share_id=STUDY2
  - https://zhyl.nyfy.com.cn/viewer?share_id=STUDY3"

Claude will:
1. Detect each provider automatically
2. Download all three in batch
3. Create separate directories for each
4. Report results for all three
```

### Example 3: Check Capabilities

```
User: "What DICOM providers are supported?"

Claude calls list_supported_providers() and shows:
- All 4 provider types
- Their domains
- Supported features
```

### Example 4: Custom Scan Parameters

```
User: "Download with 5 scan rounds and 50ms delay for complete capture"

Claude will:
1. Call download_dicom with:
   - max_rounds=5 (more iterations = more thorough)
   - step_wait_ms=50 (delay between frames in ms)
2. Perform thorough frame-by-frame capture
3. Return all captured DICOM files
```

### Example 5: Fast Download

```
User: "Quick download, speed is more important than completeness"

Claude will:
1. Call download_dicom with:
   - max_rounds=2 (fewer iterations = faster)
   - step_wait_ms=30 (shorter delays)
2. Complete download quickly
3. Suitable for initial capture or time-sensitive scenarios
```

## Troubleshooting

### Problem: "Module not found: dicom_mcp"

**Fix**: Ensure installation completed:
```bash
cd /Users/qinxiaoqiang/Downloads/dicom_mcp
pip install -e .
```

### Problem: "Cannot find multi_download.py"

**Fix**: Check path in `dicom_mcp/server.py`:
```bash
ls /Users/qinxiaoqiang/Downloads/dicom_download/multi_download.py
```

If missing, adjust DICOM_DOWNLOAD_PATH in server.py

### Problem: "Playwright chromium not found"

**Fix**: Install browsers:
```bash
playwright install chromium
```

### Problem: Server starts but Claude doesn't see tools

**Fix**:
1. Check config in Claude Desktop settings
2. Ensure PYTHONPATH in config is correct
3. Restart Claude Desktop completely
4. Check if server logs show errors:
```bash
python -m dicom_mcp.server 2>&1 | head -50
```

### Problem: Download fails with "Link expired"

**Reason**: Medical share links expire (typically 7-30 days)

**Fix**: Get a new valid share link from the medical provider

## File Organization

After downloading, files are organized as:
```
./dicom_downloads/                    (default output directory)
├── zlyy.tjmucih.cn_STUDY1_xxxxx/     (study 1 DICOM files)
│   ├── 001.dcm
│   ├── 002.dcm
│   └── ...
├── zlyy.tjmucih.cn_STUDY1_xxxxx.zip  (compressed archive)
├── ylyyx.shdc.org.cn_STUDY2_xxxxx/   (study 2)
└── ylyyx.shdc.org.cn_STUDY2_xxxxx.zip
```

## Configuration Options

### Download Parameters

When using tools, you can control:

- **provider**: Auto-detect or specify (auto, tz, fz, nyfy, cloud)
- **mode**: Download mode (all, diag, nondiag) - affects speed
- **headless**: Browser UI visible or hidden
- **output_dir**: Where to save files
- **create_zip**: Generate ZIP archive or just directories
- **password**: For protected shares

### Example with Options

```
Claude: "Download with these settings:
- Provider: auto-detect
- Mode: diag (diagnostic only, faster)
- No browser UI (headless)
- Save to ./studies
- Create ZIP"
```

## Architecture Overview

```
Your Prompt
    ↓
Claude LLM
    ↓
MCP Server (dicom_mcp) ← Your new package
    ↓
dicom_download Scripts ← Your existing scripts
    ↓
Browser (Playwright)
    ↓
Hospital Medical Systems
    ↓
DICOM Files Downloaded
```

## Documentation Files

Inside `/Users/qinxiaoqiang/Downloads/dicom_mcp/`:

| File | Purpose |
|------|---------|
| `README.md` | User-facing overview |
| `QUICKSTART.md` | 5-minute startup guide |
| `ARCHITECTURE.md` | Technical design details |
| `PROJECT_STRUCTURE.md` | Complete file organization |
| `SETUP_GUIDE.md` | This file |
| `pyproject.toml` | Python package config |
| `dicom_mcp/server.py` | Main MCP server code |

Read in order:
1. This file (SETUP_GUIDE.md) - you are here
2. QUICKSTART.md - how to use it
3. README.md - full documentation
4. ARCHITECTURE.md - how it works internally

## Next Steps

1. **Install** (Step 1 above)
2. **Configure Claude** (Step 3 above)
3. **Test** with a sample URL from your hospital's imaging system
4. **Automate** any recurring download tasks

## Support

### For MCP Server Issues
- Check logs: `python -m dicom_mcp.server 2>&1`
- Review ARCHITECTURE.md for implementation details
- Check if Python packages are installed: `pip list | grep mcp`

### For DICOM Download Issues
- Refer to original project: https://github.com/hengqujushi/dicom_download
- Check URL validity (shares may expire)
- Verify provider detection: use `detect_provider_from_url` tool

### For Claude Integration
- Check Claude Desktop config in `~/Library/Application\ Support/Claude/`
- Ensure PYTHONPATH is correct
- Restart Claude after changes

## Quick Commands Reference

```bash
# Install
cd /Users/qinxiaoqiang/Downloads/dicom_mcp && pip install -e .

# Test server directly
python -m dicom_mcp.server

# Install browsers
playwright install chromium

# Check installation
python -c "from dicom_mcp.server import mcp; print('OK')"

# Edit Claude config (macOS)
open ~/Library/Application\ Support/Claude/claude_desktop_config.json

# View logs (if server fails)
python -m dicom_mcp.server 2>&1 | tail -100
```

## You're All Set!

Once installed and configured:
- Claude will see 5 new DICOM tools
- You can download DICOM images using natural language
- Multiple hospitals/providers are supported
- Batch operations are supported
- Results are organized and can be easily archived

## Optional: Advanced Setup

### Run on a Server

If running on a headless server:
1. Use `headless=true` mode (default)
2. Install Playwright with: `playwright install chromium`
3. May need virtual display on Linux:
   ```bash
   xvfb-run python -m dicom_mcp.server
   ```

### Create Custom Tools

To add more tools beyond the basic 5, edit `dicom_mcp/server.py`:
1. Add new `@mcp.tool()` function
2. Define input/output models
3. Restart server
4. New tool appears in Claude

### Docker Deployment

Create a Dockerfile to run the server in container:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e . && playwright install chromium
ENTRYPOINT ["python", "-m", "dicom_mcp.server"]
```

## Summary

```
Status: ✓ Complete MCP Server Created
Location: /Users/qinxiaoqiang/Downloads/dicom_mcp/
Provider: Python FastMCP Framework
Transport: stdio (default for Claude)
Tools: 5 MCP tools for DICOM operations
Providers: 4 hospital systems supported
Documentation: 5 detailed guides included
```

You're ready to start downloading DICOM images via Claude!
